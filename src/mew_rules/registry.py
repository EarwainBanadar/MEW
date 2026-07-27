
from __future__ import annotations

import builtins
from collections import OrderedDict
from collections.abc import Iterable, Iterator

from .base import Rule
from .model import RuleCategory, RuleSeverity


class RuleRegistryError(RuntimeError):
    pass


class DuplicateRuleIdError(RuleRegistryError):
    pass


class UnknownRuleError(RuleRegistryError):
    pass


class RuleRegistry:
    """Deterministic registry for versioned executable rules."""

    def __init__(self) -> None:
        self._rules: "OrderedDict[str, Rule]" = OrderedDict()

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self) -> Iterator[Rule]:
        for rule_id in sorted(self._rules):
            yield self._rules[rule_id]

    def register(self, rule: Rule) -> None:
        rule_id = rule.definition.rule_id
        if rule_id in self._rules:
            raise DuplicateRuleIdError(rule_id)
        self._rules[rule_id] = rule

    def unregister(self, rule_id: str) -> Rule:
        try:
            return self._rules.pop(rule_id)
        except KeyError as exc:
            raise UnknownRuleError(rule_id) from exc

    def get(self, rule_id: str) -> Rule:
        try:
            return self._rules[rule_id]
        except KeyError as exc:
            raise UnknownRuleError(rule_id) from exc

    def list(
        self,
        *,
        category: RuleCategory | None = None,
        severity: RuleSeverity | None = None,
        enabled_only: bool = False,
        tags: Iterable[str] | None = None,
    ) -> builtins.list[Rule]:
        tag_set = set(tags or [])
        result: list[Rule] = []
        for rule in self:
            definition = rule.definition
            if category is not None and definition.category != category:
                continue
            if severity is not None and definition.severity != severity:
                continue
            if enabled_only and not definition.enabled_by_default:
                continue
            if tag_set and not tag_set.issubset(set(definition.tags)):
                continue
            result.append(rule)
        return result

    def manifest(self) -> builtins.list[dict]:
        return [rule.definition.to_dict() for rule in self]
