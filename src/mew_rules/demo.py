
from __future__ import annotations

from .base import FunctionalRule
from .model import (
    RuleCategory, RuleContext, RuleDefinition, RuleFinding,
    RuleScope, RuleSeverity
)
from .registry import RuleRegistry


def create_demo_registry() -> RuleRegistry:
    registry = RuleRegistry()

    definition = RuleDefinition(
        rule_id="KB-RULE-DEMO-001",
        version="1.0.0",
        title="Repository must be present",
        description="Checks whether a repository object was supplied.",
        rationale="Every engineering rule requires a repository context.",
        category=RuleCategory.GOVERNANCE,
        severity=RuleSeverity.CRITICAL,
        scope=RuleScope.REPOSITORY,
        tags=["demo", "framework"],
        acceptance_criteria=["RuleContext.repository is not None"],
    )

    def evaluator(context: RuleContext):
        if context.repository is None:
            yield RuleFinding(
                rule_id=definition.rule_id,
                severity=definition.severity,
                message="No repository was supplied.",
                recommendation="Provide an AP9.2 BPMNRepository instance.",
            )

    registry.register(FunctionalRule(definition, evaluator))
    return registry
