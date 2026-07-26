from __future__ import annotations
from typing import Dict, Iterable, List
from .base import Rule
from .model import RuleScope

class RuleDispatcher:
    """Validates and groups executable rules by their declared scope."""
    def dispatch_plan(self, rules: Iterable[Rule]) -> Dict[str,List[Rule]]:
        plan={scope.value:[] for scope in RuleScope}
        for rule in sorted(rules,key=lambda r:r.definition.rule_id):
            plan[rule.definition.scope.value].append(rule)
        return plan
    def validate_binding(self, rule: Rule) -> None:
        if not callable(getattr(rule,'evaluate',None)):
            raise TypeError(f'Rule {rule.definition.rule_id} has no evaluator')
