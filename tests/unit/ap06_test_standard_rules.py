from pathlib import Path
from mew_bpmn.builder import SemanticModelBuilder
from mew_bpmn.repository import BPMNRepository
from mew_bpmn.model import *
from mew_rules.standard_rules import create_standard_registry
from mew_rules.evaluator import RuleEvaluator
from mew_rules.model import RuleContext
ROOT=Path('/mnt/data/AP9_1_SEMANTIC_PARSER/reports/Template_Management_RC1.12.6_semantic.json')
def test_catalog_has_36_unique_rules():
 r=create_standard_registry(); assert len(r)==36; assert len({x.definition.rule_id for x in r})==36
def test_baseline_executes_without_rule_errors():
 repo=SemanticModelBuilder().build_from_path(ROOT); s=RuleEvaluator(create_standard_registry()).evaluate(RuleContext(repo)); assert s.selected_rule_count==36; assert s.error_count==0
def test_empty_repository_reports_critical_governance_findings():
 s=RuleEvaluator(create_standard_registry()).evaluate(RuleContext(BPMNRepository())); assert s.finding_count>0; assert s.overall_status in ('FAIL','ERROR')
def test_start_event_incoming_detected():
 repo=BPMNRepository(); st=Event('S',ObjectKind.EVENT,'startEvent',event_kind=EventKind.START); t=Task('T',ObjectKind.TASK,'task'); f=Flow('F',ObjectKind.FLOW,'sequence',flow_kind=FlowKind.SEQUENCE,source_ref='T',target_ref='S'); repo.add(st);repo.add(t);repo.add(f);repo.resolve_relationships(); s=RuleEvaluator(create_standard_registry()).evaluate(RuleContext(repo)); assert any(x.rule_id=='KB-BPMN-011' and x.finding_count for x in s.results)
def test_self_loop_detected():
 repo=BPMNRepository(); t=Task('T',ObjectKind.TASK,'task'); f=Flow('F',ObjectKind.FLOW,'sequence',flow_kind=FlowKind.SEQUENCE,source_ref='T',target_ref='T'); repo.add(t);repo.add(f);repo.resolve_relationships(); s=RuleEvaluator(create_standard_registry()).evaluate(RuleContext(repo)); assert any(x.rule_id=='KB-BPMN-007' and x.finding_count for x in s.results)
