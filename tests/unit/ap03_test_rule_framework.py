
import pytest

from mew_rules.base import FunctionalRule
from mew_rules.demo import create_demo_registry
from mew_rules.model import (
    RuleCategory, RuleContext, RuleDefinition, RuleFinding,
    RuleScope, RuleSeverity, RuleStatus
)
from mew_rules.registry import (
    DuplicateRuleIdError, RuleRegistry, UnknownRuleError
)


def definition(rule_id="KB-TEST-001", severity=RuleSeverity.ERROR):
    return RuleDefinition(
        rule_id=rule_id,
        version="1.0.0",
        title="Test Rule",
        description="Test description",
        rationale="Test rationale",
        category=RuleCategory.QUALITY,
        severity=severity,
        scope=RuleScope.REPOSITORY,
        tags=["test"],
        acceptance_criteria=["No finding"],
    )


def test_rule_pass():
    rule = FunctionalRule(definition(), lambda ctx: [])
    result = rule.execute(RuleContext(repository=object()))
    assert result.status == RuleStatus.PASS
    assert result.finding_count == 0
    assert result.error_message is None


def test_rule_finding():
    d = definition()
    rule = FunctionalRule(
        d,
        lambda ctx: [
            RuleFinding(
                rule_id=d.rule_id,
                severity=d.severity,
                message="Violation",
                object_id="T001",
            )
        ],
    )
    result = rule.execute(RuleContext(repository=object()))
    assert result.status == RuleStatus.FINDING
    assert result.finding_count == 1
    assert result.findings[0].object_id == "T001"


def test_rule_error_is_captured():
    def broken(ctx):
        raise RuntimeError("boom")
    rule = FunctionalRule(definition(), broken)
    result = rule.execute(RuleContext(repository=object()))
    assert result.status == RuleStatus.ERROR
    assert "boom" in result.error_message


def test_registry_deterministic_and_duplicate_safe():
    registry = RuleRegistry()
    registry.register(FunctionalRule(definition("KB-TEST-002"), lambda ctx: []))
    registry.register(FunctionalRule(definition("KB-TEST-001"), lambda ctx: []))
    assert [r.definition.rule_id for r in registry] == ["KB-TEST-001", "KB-TEST-002"]
    with pytest.raises(DuplicateRuleIdError):
        registry.register(FunctionalRule(definition("KB-TEST-001"), lambda ctx: []))


def test_registry_filters_and_unknown_rule():
    registry = RuleRegistry()
    registry.register(FunctionalRule(definition("KB-TEST-001", RuleSeverity.ERROR), lambda ctx: []))
    registry.register(FunctionalRule(definition("KB-TEST-002", RuleSeverity.WARNING), lambda ctx: []))
    assert len(registry.list(severity=RuleSeverity.WARNING)) == 1
    with pytest.raises(UnknownRuleError):
        registry.get("DOES-NOT-EXIST")


def test_demo_registry_executes():
    registry = create_demo_registry()
    rule = registry.get("KB-RULE-DEMO-001")
    assert rule.execute(RuleContext(repository=object())).status == RuleStatus.PASS
    assert rule.execute(RuleContext(repository=None)).status == RuleStatus.FINDING
