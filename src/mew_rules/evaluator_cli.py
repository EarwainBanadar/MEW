import argparse
import json
from pathlib import Path

from mew_bpmn.builder import SemanticModelBuilder

from .baseline_rules import create_baseline_registry
from .evaluator import EvaluationPolicy, RuleEvaluator
from .model import RuleContext, RuleSeverity


def main():
 p=argparse.ArgumentParser();p.add_argument('semantic_json',type=Path);p.add_argument('-o','--output',type=Path,required=True);p.add_argument('--minimum-severity',choices=[s.value for s in RuleSeverity])
 a=p.parse_args(); repo=SemanticModelBuilder().build_from_path(a.semantic_json)
 pol=EvaluationPolicy(minimum_severity=RuleSeverity(a.minimum_severity) if a.minimum_severity else None)
 result=RuleEvaluator(create_baseline_registry()).evaluate(RuleContext(repo),pol)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result.to_dict(),indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({'overall_status':result.overall_status,'selected_rules':result.selected_rule_count,'findings':result.finding_count,'errors':result.error_count},indent=2))
 return 0 if result.overall_status in ('PASS','WARNING') else 2
if __name__=='__main__':
 raise SystemExit(main())
