
from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Iterable, Iterator, List, Optional

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
        category: Optional[RuleCategory] = None,
        severity: Optional[RuleSeverity] = None,
        enabled_only: bool = False,
        tags: Optional[Iterable[str]] = None,
    ) -> List[Rule]:
        tag_set = set(tags or [])
        result: List[Rule] = []
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

    def manifest(self) -> List[Dict]:
        return [rule.definition.to_dict() for rule in self]
