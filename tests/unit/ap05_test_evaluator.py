from pathlib import Path

from mew_bpmn.builder import SemanticModelBuilder
from mew_rules.baseline_rules import create_baseline_registry
from mew_rules.dispatcher import RuleDispatcher
from mew_rules.evaluator import EvaluationPolicy, RuleEvaluator
from mew_rules.model import RuleContext, RuleSeverity

SOURCE=Path('/mnt/data/AP9_1_SEMANTIC_PARSER/reports/Template_Management_RC1.12.6_semantic.json')
def repo(): return SemanticModelBuilder().build_from_path(SOURCE)
def test_dispatch_plan():
 r=create_baseline_registry(); p=RuleDispatcher().dispatch_plan(r)
 assert len(p['repository'])==1 and len(p['flow'])==1 and len(p['object'])==1 and len(p['graph'])==1
def test_baseline_evaluation():
 s=RuleEvaluator(create_baseline_registry()).evaluate(RuleContext(repo()))
 assert s.selected_rule_count==4 and s.error_count==0
 assert s.overall_status in ('PASS','WARNING')
def test_minimum_severity_filter():
 s=RuleEvaluator(create_baseline_registry()).evaluate(RuleContext(repo()),EvaluationPolicy(minimum_severity=RuleSeverity.ERROR))
 assert s.selected_rule_count==3
def test_explicit_disable():
 s=RuleEvaluator(create_baseline_registry()).evaluate(RuleContext(repo()),EvaluationPolicy(disabled_rule_ids={'KB-EVAL-001'}))
 assert s.selected_rule_count==3
def test_deterministic_rule_order():
 s=RuleEvaluator(create_baseline_registry()).evaluate(RuleContext(repo()))
 assert [r.rule_id for r in s.results]==sorted(r.rule_id for r in s.results)
