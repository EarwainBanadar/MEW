from __future__ import annotations
from .base import FunctionalRule
from .model import RuleCategory, RuleDefinition, RuleFinding, RuleScope, RuleSeverity
from .registry import RuleRegistry

def _def(i,title,desc,rat,cat,sev,scope):
 return RuleDefinition(i,'1.0.0',title,desc,rat,cat,sev,scope,True,['baseline'],[desc])

def create_baseline_registry():
 r=RuleRegistry()
 d1=_def('KB-EVAL-001','Repository consistency','Repository has no validation errors.','Invalid references make evaluation unreliable.',RuleCategory.STRUCTURAL,RuleSeverity.CRITICAL,RuleScope.REPOSITORY)
 def e1(ctx):
  for err in ctx.repository.validate(): yield RuleFinding(d1.rule_id,d1.severity,err,recommendation='Repair repository consistency before release.')
 r.register(FunctionalRule(d1,e1))
 d2=_def('KB-EVAL-002','Flow references resolve','Every flow source and target exists.','Flows require resolvable endpoints.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.FLOW)
 def e2(ctx):
  ids={o.engineering_id for o in ctx.repository}
  for f in ctx.repository.flows():
   if f.source_ref not in ids or f.target_ref not in ids:
    yield RuleFinding(d2.rule_id,d2.severity,'Unresolved flow endpoint',f.engineering_id,evidence={'source':f.source_ref,'target':f.target_ref})
 r.register(FunctionalRule(d2,e2))
 d3=_def('KB-EVAL-003','No isolated flow nodes','Every flow node has incoming or outgoing connections.','Isolated nodes are usually incomplete model elements.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.OBJECT)
 def e3(ctx):
  for n in ctx.repository.flow_nodes():
   if not n.incoming and not n.outgoing:
    yield RuleFinding(d3.rule_id,d3.severity,'Isolated flow node',n.engineering_id,recommendation='Connect or remove the node.')
 r.register(FunctionalRule(d3,e3))
 d4=_def('KB-EVAL-004','Graph roots exist','The sequence-flow graph has at least one root.','Executable process graphs require an entry point.',RuleCategory.STRUCTURAL,RuleSeverity.ERROR,RuleScope.GRAPH)
 def e4(ctx):
  g=ctx.repository.graph_analysis()
  if not g.roots: yield RuleFinding(d4.rule_id,d4.severity,'No sequence-flow root detected.')
 r.register(FunctionalRule(d4,e4))
 return r
