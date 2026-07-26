from __future__ import annotations
from collections import Counter,defaultdict
from mew_bpmn.model import Event,EventKind,Gateway,GatewayKind,Task,FlowKind,ObjectKind
from .base import FunctionalRule
from .model import RuleCategory,RuleDefinition,RuleFinding,RuleScope,RuleSeverity
from .registry import RuleRegistry

def D(i,title,desc,cat,sev,scope,tags):
 return RuleDefinition(i,'1.0.0',title,desc,desc,cat,sev,scope,True,tags,[desc])
_ACTIVE_DEFINITION=None
def F(d,msg,obj=None,rec=None,ev=None):
 active=_ACTIVE_DEFINITION or d
 return RuleFinding(active.rule_id,active.severity,msg,obj,recommendation=rec,evidence=ev or {})
def create_standard_registry():
 r=RuleRegistry()
 def add(d,fn):
  def bound(c, _d=d, _fn=fn):
   global _ACTIVE_DEFINITION
   previous=_ACTIVE_DEFINITION; _ACTIVE_DEFINITION=_d
   try: return list(_fn(c))
   finally: _ACTIVE_DEFINITION=previous
  r.register(FunctionalRule(d,bound))
 # Governance / identity
 d=D('KB-BPMN-001','Engineering IDs present','Every object requires a non-empty engineering ID.',RuleCategory.GOVERNANCE,RuleSeverity.CRITICAL,RuleScope.REPOSITORY,['identity']); add(d,lambda c:(F(d,'Missing engineering ID') for o in c.repository if not str(o.engineering_id).strip()))
 d=D('KB-BPMN-002','Engineering IDs unique','Engineering IDs must be globally unique.',RuleCategory.STRUCTURAL,RuleSeverity.CRITICAL,RuleScope.REPOSITORY,['identity']);
 def e(c):
  ids=[o.engineering_id for o in c.repository]
  for x,n in Counter(ids).items():
   if n>1: yield F(d,f'Duplicate engineering ID: {x}',x)
 add(d,e)
 d=D('KB-BPMN-003','Provenance available','Every object should retain source provenance.',RuleCategory.GOVERNANCE,RuleSeverity.WARNING,RuleScope.OBJECT,['provenance']); add(d,lambda c:(F(d,'Missing source provenance',o.engineering_id) for o in c.repository if not o.provenance.svg_id and not o.provenance.source_xpath))
 d=D('KB-BPMN-004','Version metadata present','Every object requires engineering version metadata.',RuleCategory.GOVERNANCE,RuleSeverity.ERROR,RuleScope.OBJECT,['metadata']); add(d,lambda c:(F(d,'Missing version metadata',o.engineering_id) for o in c.repository if not o.metadata.version))
 d=D('KB-BPMN-005','Recognized BPMN types','Unknown BPMN object types are not releaseable.',RuleCategory.QUALITY,RuleSeverity.ERROR,RuleScope.OBJECT,['typing']); add(d,lambda c:(F(d,'Unknown BPMN type',o.engineering_id,ev={'bpmn_type':o.bpmn_type}) for o in c.repository if o.object_kind==ObjectKind.UNKNOWN))
 # References / flows
 d=D('KB-BPMN-006','Flow endpoints resolve','Every flow source and target must resolve.',RuleCategory.SEMANTIC,RuleSeverity.CRITICAL,RuleScope.FLOW,['flow']);
 def e(c):
  ids={o.engineering_id for o in c.repository}
  for f in c.repository.flows():
   if f.source_ref not in ids: yield F(d,'Unresolved source reference',f.engineering_id,ev={'source_ref':f.source_ref})
   if f.target_ref not in ids: yield F(d,'Unresolved target reference',f.engineering_id,ev={'target_ref':f.target_ref})
 add(d,e)
 d=D('KB-BPMN-007','No self-loop sequence flows','Sequence flows should not connect an element to itself.',RuleCategory.QUALITY,RuleSeverity.ERROR,RuleScope.FLOW,['flow']); add(d,lambda c:(F(d,'Self-loop sequence flow',f.engineering_id) for f in c.repository.flows() if f.flow_kind==FlowKind.SEQUENCE and f.source_ref==f.target_ref))
 d=D('KB-BPMN-008','Flow IDs present','Every flow requires an engineering ID.',RuleCategory.GOVERNANCE,RuleSeverity.CRITICAL,RuleScope.FLOW,['flow','identity']); add(d,lambda c:(F(d,'Flow has no ID') for f in c.repository.flows() if not f.engineering_id))
 d=D('KB-BPMN-009','Sequence flows connect flow nodes','Sequence flows must connect BPMN flow nodes.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.FLOW,['flow']);
 def e(c):
  ids={n.engineering_id for n in c.repository.flow_nodes()}
  for f in c.repository.flows():
   if f.flow_kind==FlowKind.SEQUENCE and (f.source_ref not in ids or f.target_ref not in ids): yield F(d,'Sequence flow endpoint is not a flow node',f.engineering_id)
 add(d,e)
 d=D('KB-BPMN-010','No duplicate directed sequence edges','Duplicate sequence edges between identical endpoints are prohibited.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.GRAPH,['flow']);
 def e(c):
  pairs=defaultdict(list)
  for f in c.repository.flows():
   if f.flow_kind==FlowKind.SEQUENCE:pairs[(f.source_ref,f.target_ref)].append(f.engineering_id)
  for p,v in pairs.items():
   if len(v)>1: yield F(d,'Duplicate directed sequence edges',v[0],ev={'edge':p,'flows':v})
 add(d,e)
 # Events
 d=D('KB-BPMN-011','Start events have no incoming sequence flow','Start events must not have incoming sequence flows.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.OBJECT,['event']); add(d,lambda c:(F(d,'Start event has incoming flow',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Event) and n.event_kind==EventKind.START and n.incoming))
 d=D('KB-BPMN-012','Start events have outgoing sequence flow','Start events require at least one outgoing flow.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.OBJECT,['event']); add(d,lambda c:(F(d,'Start event has no outgoing flow',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Event) and n.event_kind==EventKind.START and not n.outgoing))
 d=D('KB-BPMN-013','End events have no outgoing sequence flow','End events must not have outgoing sequence flows.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.OBJECT,['event']); add(d,lambda c:(F(d,'End event has outgoing flow',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Event) and n.event_kind==EventKind.END and n.outgoing))
 d=D('KB-BPMN-014','End events have incoming sequence flow','End events require at least one incoming flow.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.OBJECT,['event']); add(d,lambda c:(F(d,'End event has no incoming flow',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Event) and n.event_kind==EventKind.END and not n.incoming))
 d=D('KB-BPMN-015','Intermediate events are connected','Intermediate events require incoming and outgoing connectivity.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.OBJECT,['event']); add(d,lambda c:(F(d,'Intermediate event is not fully connected',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Event) and n.event_kind in (EventKind.INTERMEDIATE_CATCH,EventKind.INTERMEDIATE_THROW) and (not n.incoming or not n.outgoing)))
 # Gateways
 d=D('KB-BPMN-016','Gateways are connected','Gateways require incoming and outgoing sequence flows.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.OBJECT,['gateway']); add(d,lambda c:(F(d,'Gateway is not fully connected',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Gateway) and (not n.incoming or not n.outgoing)))
 d=D('KB-BPMN-017','Diverging exclusive gateways split','Diverging exclusive gateways should have at least two outgoing flows.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.OBJECT,['gateway']); add(d,lambda c:(F(d,'Exclusive gateway does not split',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Gateway) and n.gateway_kind==GatewayKind.EXCLUSIVE and len(n.incoming)<=1 and len(n.outgoing)<2))
 d=D('KB-BPMN-018','Converging exclusive gateways merge','Converging exclusive gateways should have at least two incoming flows.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.OBJECT,['gateway']); add(d,lambda c:(F(d,'Exclusive gateway does not merge',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Gateway) and len(n.outgoing)<=1 and len(n.incoming)<2))
 d=D('KB-BPMN-019','Parallel gateways are not one-in-one-out','Parallel gateways must model an actual split or join.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.OBJECT,['gateway']); add(d,lambda c:(F(d,'Parallel gateway is structurally redundant',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Gateway) and n.gateway_kind==GatewayKind.PARALLEL and len(n.incoming)==1 and len(n.outgoing)==1))
 d=D('KB-BPMN-020','Gateway degree bounded','Gateways should not exceed twelve incoming or outgoing flows.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.OBJECT,['gateway']); add(d,lambda c:(F(d,'Gateway degree exceeds review threshold',n.engineering_id,ev={'incoming':len(n.incoming),'outgoing':len(n.outgoing)}) for n in c.repository.flow_nodes() if isinstance(n,Gateway) and (len(n.incoming)>12 or len(n.outgoing)>12)))
 # Tasks / naming
 d=D('KB-BPMN-021','Tasks are named','Tasks require a human-readable name.',RuleCategory.GOVERNANCE,RuleSeverity.WARNING,RuleScope.OBJECT,['task','naming']); add(d,lambda c:(F(d,'Unnamed task',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Task) and not (n.name or '').strip()))
 d=D('KB-BPMN-022','Task names are concise','Task names should not exceed 120 characters.',RuleCategory.QUALITY,RuleSeverity.INFO,RuleScope.OBJECT,['task','naming']); add(d,lambda c:(F(d,'Task name exceeds 120 characters',n.engineering_id,ev={'length':len(n.name or '')}) for n in c.repository.flow_nodes() if isinstance(n,Task) and len(n.name or '')>120))
 d=D('KB-BPMN-023','Tasks are connected','Tasks require incoming or outgoing process connectivity.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.OBJECT,['task']); add(d,lambda c:(F(d,'Isolated task',n.engineering_id) for n in c.repository.flow_nodes() if isinstance(n,Task) and not n.incoming and not n.outgoing))
 d=D('KB-BPMN-024','No direct start-to-end trivial process','A process should not consist only of a direct start-to-end flow.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.GRAPH,['graph']);
 def e(c):
  m={n.engineering_id:n for n in c.repository.flow_nodes()}
  for f in c.repository.flows():
   a,b=m.get(f.source_ref),m.get(f.target_ref)
   if isinstance(a,Event) and a.event_kind==EventKind.START and isinstance(b,Event) and b.event_kind==EventKind.END: yield F(d,'Direct start-to-end sequence detected',f.engineering_id)
 add(d,e)
 # Graph
 d=D('KB-BPMN-025','Graph has roots','The sequence-flow graph requires at least one root.',RuleCategory.STRUCTURAL,RuleSeverity.CRITICAL,RuleScope.GRAPH,['graph']); add(d,lambda c:([] if c.repository.graph_analysis().roots else [F(d,'No sequence-flow root detected')]))
 d=D('KB-BPMN-026','Graph has sinks','The sequence-flow graph requires at least one sink.',RuleCategory.STRUCTURAL,RuleSeverity.CRITICAL,RuleScope.GRAPH,['graph']); add(d,lambda c:([] if c.repository.graph_analysis().sinks else [F(d,'No sequence-flow sink detected')]))
 d=D('KB-BPMN-027','No unreachable flow nodes','All flow nodes should be reachable from a graph root.',RuleCategory.QUALITY,RuleSeverity.WARNING,RuleScope.GRAPH,['graph']); add(d,lambda c:(F(d,'Unreachable flow node',x) for x in c.repository.graph_analysis().unreachable))
 d=D('KB-BPMN-028','Cycles require review','Sequence-flow cycles require explicit engineering review.',RuleCategory.GOVERNANCE,RuleSeverity.INFO,RuleScope.GRAPH,['graph','review']); add(d,lambda c:(F(d,'Sequence-flow cycle detected',cycle[0],ev={'cycle':cycle}) for cycle in c.repository.graph_analysis().cycles))
 # Geometry / presentation / release quality
 d=D('KB-BPMN-029','Flow nodes have geometry','Every flow node should have geometric bounds.',RuleCategory.LAYOUT,RuleSeverity.WARNING,RuleScope.OBJECT,['geometry']); add(d,lambda c:(F(d,'Missing node bounds',n.engineering_id) for n in c.repository.flow_nodes() if n.geometry.bounds is None))
 d=D('KB-BPMN-030','Bounds are positive','Node bounds must have positive width and height.',RuleCategory.LAYOUT,RuleSeverity.ERROR,RuleScope.OBJECT,['geometry']); add(d,lambda c:(F(d,'Non-positive node bounds',n.engineering_id) for n in c.repository.flow_nodes() if n.geometry.bounds and (n.geometry.bounds.width<=0 or n.geometry.bounds.height<=0)))
 d=D('KB-BPMN-031','Flows have geometry','Flows should retain path or waypoint geometry.',RuleCategory.LAYOUT,RuleSeverity.WARNING,RuleScope.FLOW,['geometry']); add(d,lambda c:(F(d,'Flow has no path geometry',f.engineering_id) for f in c.repository.flows() if not f.geometry.points and not f.geometry.path_data))
 d=D('KB-BPMN-032','Objects are visible','Releaseable BPMN objects must be visible.',RuleCategory.RELEASE,RuleSeverity.ERROR,RuleScope.OBJECT,['presentation']); add(d,lambda c:(F(d,'Invisible BPMN object',o.engineering_id) for o in c.repository if not o.presentation.visible))
 d=D('KB-BPMN-033','Source SHA available','Objects should retain source SHA-256 provenance.',RuleCategory.RELEASE,RuleSeverity.WARNING,RuleScope.OBJECT,['provenance','release']); add(d,lambda c:(F(d,'Missing source SHA-256',o.engineering_id) for o in c.repository if not o.provenance.source_sha256))
 d=D('KB-BPMN-034','No empty repository','A release repository must contain BPMN objects.',RuleCategory.RELEASE,RuleSeverity.CRITICAL,RuleScope.REPOSITORY,['release']); add(d,lambda c:([] if len(c.repository)>0 else [F(d,'Repository is empty')]))
 d=D('KB-BPMN-035','At least one start event','The model should contain at least one start event.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.REPOSITORY,['event']); add(d,lambda c:([] if any(isinstance(n,Event) and n.event_kind==EventKind.START for n in c.repository.flow_nodes()) else [F(d,'No start event exists')]))
 d=D('KB-BPMN-036','At least one end event','The model should contain at least one end event.',RuleCategory.SEMANTIC,RuleSeverity.ERROR,RuleScope.REPOSITORY,['event']); add(d,lambda c:([] if any(isinstance(n,Event) and n.event_kind==EventKind.END for n in c.repository.flow_nodes()) else [F(d,'No end event exists')]))
 return r
