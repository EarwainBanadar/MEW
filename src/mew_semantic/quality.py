from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Protocol

from .model import SemanticDocument


class QualitySeverity(IntEnum):
    INFO = 10
    WARNING = 20
    ERROR = 30
    CRITICAL = 40


@dataclass(frozen=True, order=True)
class QualityFinding:
    rule_id: str
    severity: QualitySeverity
    message: str
    element_ref: str | None = None
    evidence: str | None = None


@dataclass(frozen=True)
class QualityProfile:
    profile_id: str = "engineering-default"
    fail_at: QualitySeverity = QualitySeverity.ERROR
    disabled_rules: frozenset[str] = field(default_factory=frozenset)
    severity_overrides: dict[str, QualitySeverity] = field(default_factory=dict)


@dataclass(frozen=True)
class QualityResult:
    profile_id: str
    findings: tuple[QualityFinding, ...]
    passed: bool
    score: int
    counts: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["findings"] = [
            {
                **asdict(finding),
                "severity": finding.severity.name.lower(),
            }
            for finding in self.findings
        ]
        return payload


class QualityRule(Protocol):
    rule_id: str
    default_severity: QualitySeverity

    def evaluate(self, document: SemanticDocument) -> tuple[QualityFinding, ...]: ...


@dataclass(frozen=True)
class UnresolvedReferenceRule:
    rule_id: str = "QF-REF-001"
    default_severity: QualitySeverity = QualitySeverity.ERROR

    def evaluate(self, document: SemanticDocument) -> tuple[QualityFinding, ...]:
        return tuple(
            QualityFinding(
                self.rule_id,
                self.default_severity,
                f"Reference target '{reference.target_ref}' cannot be resolved.",
                reference.source_ref,
                reference.attribute,
            )
            for reference in document.references
            if not reference.resolved
        )


@dataclass(frozen=True)
class MissingNameRule:
    rule_id: str = "QF-NAME-001"
    default_severity: QualitySeverity = QualitySeverity.WARNING
    applicable_types: frozenset[str] = frozenset(
        {"task", "userTask", "serviceTask", "subprocess", "process", "lane", "role"}
    )

    def evaluate(self, document: SemanticDocument) -> tuple[QualityFinding, ...]:
        return tuple(
            QualityFinding(
                self.rule_id,
                self.default_severity,
                "Engineering element has no explicit name or readable text.",
                element.engineering_id,
            )
            for element in document.elements
            if element.bpmn_type in self.applicable_types
            and not (element.name or element.text)
        )


@dataclass(frozen=True)
class OrphanElementRule:
    rule_id: str = "QF-GRAPH-001"
    default_severity: QualitySeverity = QualitySeverity.WARNING
    excluded_types: frozenset[str] = frozenset({"process", "pool", "lane", "role", "document"})

    def evaluate(self, document: SemanticDocument) -> tuple[QualityFinding, ...]:
        connected = {
            endpoint
            for flow in document.flows
            for endpoint in (flow.source_ref, flow.target_ref)
        }
        return tuple(
            QualityFinding(
                self.rule_id,
                self.default_severity,
                "Element is not connected to any semantic flow.",
                element.engineering_id,
            )
            for element in document.elements
            if element.bpmn_type not in self.excluded_types
            and element.engineering_id not in connected
        )


@dataclass(frozen=True)
class CrossScopeFlowRule:
    rule_id: str = "QF-SCOPE-001"
    default_severity: QualitySeverity = QualitySeverity.ERROR

    def evaluate(self, document: SemanticDocument) -> tuple[QualityFinding, ...]:
        findings: list[QualityFinding] = []
        for flow in document.flows:
            source_scope = document.index.get(flow.source_ref, {}).get("scope")
            target_scope = document.index.get(flow.target_ref, {}).get("scope")
            if source_scope and target_scope and source_scope != target_scope:
                findings.append(
                    QualityFinding(
                        self.rule_id,
                        self.default_severity,
                        "Flow crosses semantic scopes without an explicit boundary construct.",
                        flow.engineering_id,
                        f"{source_scope}->{target_scope}",
                    )
                )
        return tuple(findings)


DEFAULT_RULES: tuple[QualityRule, ...] = (
    UnresolvedReferenceRule(),
    MissingNameRule(),
    OrphanElementRule(),
    CrossScopeFlowRule(),
)


class EngineeringQualityValidator:
    def __init__(self, rules: tuple[QualityRule, ...] = DEFAULT_RULES):
        self.rules = tuple(sorted(rules, key=lambda rule: rule.rule_id))

    def validate(
        self,
        document: SemanticDocument,
        profile: QualityProfile | None = None,
    ) -> QualityResult:
        active_profile = profile or QualityProfile()
        findings: list[QualityFinding] = []
        for rule in self.rules:
            if rule.rule_id in active_profile.disabled_rules:
                continue
            severity = active_profile.severity_overrides.get(
                rule.rule_id,
                rule.default_severity,
            )
            for finding in rule.evaluate(document):
                findings.append(
                    QualityFinding(
                        finding.rule_id,
                        severity,
                        finding.message,
                        finding.element_ref,
                        finding.evidence,
                    )
                )

        ordered = tuple(
            sorted(
                findings,
                key=lambda item: (
                    -int(item.severity),
                    item.rule_id,
                    item.element_ref or "",
                    item.message,
                ),
            )
        )
        counts = {
            severity.name.lower(): sum(
                finding.severity == severity for finding in ordered
            )
            for severity in QualitySeverity
        }
        passed = not any(
            finding.severity >= active_profile.fail_at for finding in ordered
        )
        weighted_penalty = sum(
            {
                QualitySeverity.INFO: 1,
                QualitySeverity.WARNING: 5,
                QualitySeverity.ERROR: 15,
                QualitySeverity.CRITICAL: 30,
            }[finding.severity]
            for finding in ordered
        )
        return QualityResult(
            profile_id=active_profile.profile_id,
            findings=ordered,
            passed=passed,
            score=max(0, 100 - weighted_penalty),
            counts=counts,
        )


def validate_quality(
    document: SemanticDocument,
    profile: QualityProfile | None = None,
) -> QualityResult:
    return EngineeringQualityValidator().validate(document, profile)
