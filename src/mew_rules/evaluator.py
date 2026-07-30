from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .model import RuleContext, RuleExecutionResult, RuleSeverity, RuleStatus
from .registry import RuleRegistry


@dataclass(frozen=True)
class EvaluationPolicy:
    enabled_rule_ids: set[str] | None = None
    disabled_rule_ids: set[str] = field(default_factory=set)
    minimum_severity: RuleSeverity | None = None
    fail_on_rule_error: bool = True
    stop_on_critical: bool = False

@dataclass
class EvaluationSummary:
    evaluation_id: str
    started_at_utc: str
    completed_at_utc: str
    results: list[RuleExecutionResult]
    selected_rule_count: int
    skipped_rule_count: int
    overall_status: str

    @property
    def finding_count(self): return sum(r.finding_count for r in self.results)
    @property
    def error_count(self): return sum(1 for r in self.results if r.status == RuleStatus.ERROR)
    def to_dict(self):
        return {
          'evaluation_id':self.evaluation_id,'started_at_utc':self.started_at_utc,
          'completed_at_utc':self.completed_at_utc,'selected_rule_count':self.selected_rule_count,
          'skipped_rule_count':self.skipped_rule_count,'finding_count':self.finding_count,
          'error_count':self.error_count,'overall_status':self.overall_status,
          'results':[r.to_dict() for r in self.results]
        }

class RuleEvaluator:
    def __init__(self, registry: RuleRegistry): self.registry=registry
    def _selected(self, policy: EvaluationPolicy):
        rank={RuleSeverity.INFO:0,RuleSeverity.WARNING:1,RuleSeverity.ERROR:2,RuleSeverity.CRITICAL:3}
        out=[]
        for rule in self.registry:
            d=rule.definition
            if not d.enabled_by_default:
                continue
            if policy.enabled_rule_ids is not None and d.rule_id not in policy.enabled_rule_ids:
                continue
            if d.rule_id in policy.disabled_rule_ids:
                continue
            if policy.minimum_severity is not None and rank[d.severity] < rank[policy.minimum_severity]:
                continue
            out.append(rule)
        return out
    def evaluate(self, context: RuleContext, policy: EvaluationPolicy | None=None) -> EvaluationSummary:
        policy=policy or EvaluationPolicy()
        start=datetime.now(timezone.utc)
        rules=self._selected(policy); results=[]
        for rule in rules:
            result=rule.execute(context); results.append(result)
            if policy.stop_on_critical and any(f.severity==RuleSeverity.CRITICAL for f in result.findings):
                break
            if policy.fail_on_rule_error and result.status==RuleStatus.ERROR:
                break
        errors=any(r.status==RuleStatus.ERROR for r in results)
        critical=any(f.severity==RuleSeverity.CRITICAL for r in results for f in r.findings)
        error_findings=any(f.severity==RuleSeverity.ERROR for r in results for f in r.findings)
        warnings=any(f.severity==RuleSeverity.WARNING for r in results for f in r.findings)
        overall='ERROR' if errors else ('FAIL' if critical or error_findings else ('WARNING' if warnings else 'PASS'))
        end=datetime.now(timezone.utc)
        eid=f"EVAL-{start.strftime('%Y%m%dT%H%M%S%fZ')}"
        return EvaluationSummary(eid,start.isoformat(),end.isoformat(),results,len(rules),len(self.registry)-len(rules),overall)
