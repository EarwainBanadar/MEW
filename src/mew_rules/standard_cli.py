import argparse
import json
from pathlib import Path

from mew_bpmn.builder import SemanticModelBuilder

from .evaluator import RuleEvaluator
from .model import RuleContext
from .standard_rules import create_standard_registry


def main():
 p=argparse.ArgumentParser()
 p.add_argument('semantic_json',type=Path)
 p.add_argument('-o','--output',type=Path,required=True)
 a=p.parse_args()
 repo=SemanticModelBuilder().build_from_path(a.semantic_json)
 res=RuleEvaluator(create_standard_registry()).evaluate(RuleContext(repo))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(res.to_dict(),indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({'rules':res.selected_rule_count,'findings':res.finding_count,'errors':res.error_count,'status':res.overall_status},indent=2))
 return 0 if res.error_count==0 else 2
if __name__=='__main__': raise SystemExit(main())
