
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class RuleCategory(str, Enum):
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    GOVERNANCE = "governance"
    QUALITY = "quality"
    LAYOUT = "layout"
    RELEASE = "release"


class RuleSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RuleStatus(str, Enum):
    PASS = "pass"
    FINDING = "finding"
    SKIPPED = "skipped"
    ERROR = "error"


class RuleScope(str, Enum):
    REPOSITORY = "repository"
    OBJECT = "object"
    FLOW = "flow"
    GRAPH = "graph"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    version: str
    title: str
    description: str
    rationale: str
    category: RuleCategory
    severity: RuleSeverity
    scope: RuleScope
    enabled_by_default: bool = True
    tags: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.rule_id or not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if not self.version or not self.version.strip():
            raise ValueError("version must not be empty")
        if not self.title or not self.title.strip():
            raise ValueError("title must not be empty")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["category"] = self.category.value
        data["severity"] = self.severity.value
        data["scope"] = self.scope.value
        return data


@dataclass(frozen=True)
class RuleFinding:
    rule_id: str
    severity: RuleSeverity
    message: str
    object_id: Optional[str] = None
    location: Optional[str] = None
    recommendation: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class RuleExecutionResult:
    rule_id: str
    rule_version: str
    status: RuleStatus
    findings: List[RuleFinding] = field(default_factory=list)
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    executed_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "status": self.status.value,
            "finding_count": self.finding_count,
            "duration_ms": round(self.duration_ms, 3),
            "error_message": self.error_message,
            "executed_at_utc": self.executed_at_utc,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class RuleContext:
    repository: Any
    configuration: Dict[str, Any] = field(default_factory=dict)
    services: Dict[str, Any] = field(default_factory=dict)

    def require_service(self, name: str) -> Any:
        if name not in self.services:
            raise KeyError(f"Required rule service is missing: {name}")
        return self.services[name]
