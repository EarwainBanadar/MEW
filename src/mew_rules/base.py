from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter
from typing import Callable, Iterable

from .model import (
    RuleContext,
    RuleDefinition,
    RuleExecutionResult,
    RuleFinding,
    RuleStatus,
)


class Rule(ABC):
    """Abstract executable engineering rule."""

    def __init__(self, definition: RuleDefinition) -> None:
        self.definition = definition

    @abstractmethod
    def evaluate(self, context: RuleContext) -> Iterable[RuleFinding]:
        """Return zero or more findings."""

    def execute(self, context: RuleContext) -> RuleExecutionResult:
        started = perf_counter()
        try:
            findings = list(self.evaluate(context))
            status = RuleStatus.FINDING if findings else RuleStatus.PASS
            return RuleExecutionResult(
                rule_id=self.definition.rule_id,
                rule_version=self.definition.version,
                status=status,
                findings=findings,
                duration_ms=(perf_counter() - started) * 1000.0,
            )
        except Exception as exc:  # noqa: BLE001
            return RuleExecutionResult(
                rule_id=self.definition.rule_id,
                rule_version=self.definition.version,
                status=RuleStatus.ERROR,
                findings=[],
                duration_ms=(perf_counter() - started) * 1000.0,
                error_message=f"{type(exc).__name__}: {exc}",
            )


class FunctionalRule(Rule):
    """Adapter for implementing a rule with a Python callable."""

    def __init__(
        self,
        definition: RuleDefinition,
        evaluator: Callable[[RuleContext], Iterable[RuleFinding]],
    ) -> None:
        super().__init__(definition)
        self._evaluator = evaluator

    def evaluate(self, context: RuleContext) -> Iterable[RuleFinding]:
        return self._evaluator(context)
