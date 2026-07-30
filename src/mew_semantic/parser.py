from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

from .geometry import geometry_for
from .model import (
    Diagnostic,
    Geometry,
    GraphicPrimitive,
    SemanticDocument,
    SemanticElement,
    SemanticFlow,
)

SCHEMA_VERSION="0.1.0"
STYLE_KEYS={"fill","stroke","stroke-width","stroke-dasharray","opacity","font-family","font-size","font-weight","text-anchor","marker-start","marker-mid","marker-end"}
SEMANTIC_ATTRS={"data-bpmn-type","data-element-id","data-flow-type","data-source-ref","data-target-ref"}

def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def _local_attrs(el: etree._Element) -> dict[str,str]:
    out={}
    for k,v in el.attrib.items():
        try:
            key=etree.QName(k).localname
        except ValueError:
            key=k
        out[key]=v
    return out

def _style(el: etree._Element) -> dict[str,str]:
    result={}
    if el.get('style'):
        for item in el.get('style').split(';'):
            if ':' in item:
                k,v=item.split(':',1)
                result[k.strip()]=v.strip()
    for k in STYLE_KEYS:
        if el.get(k) is not None:
            result[k]=el.get(k)
    return result

def _metadata(el: etree._Element) -> dict[str,str]:
    return {k:v for k,v in _local_attrs(el).items() if k.startswith('data-') and k not in SEMANTIC_ATTRS}

def _text(el: etree._Element) -> str | None:
    values=[]
    for node in el.iter():
        if etree.QName(node).localname in ('text','tspan') and node.text:
            t=' '.join(node.text.split())
            if t and (not values or values[-1] != t):
                values.append(t)
    return ' '.join(values) if values else None

def _primitive(el: etree._Element, geom: Geometry) -> GraphicPrimitive:
    attrs=_local_attrs(el)
    return GraphicPrimitive(svg_id=el.get('id'),tag=etree.QName(el).localname,geometry=geom,style=_style(el),attributes=attrs)

class SemanticSvgParser:
    """Parse semantically annotated BPMN-like SVG into a stable neutral document.

    Scope AP9.1:
    - discovers explicit data-bpmn-type elements and data-flow-type flows;
    - preserves SVG identity, text, geometry, style and metadata;
    - resolves source/target references into an index;
    - reports duplicate IDs, unresolved references and malformed annotations.

    It intentionally does not infer BPMN semantics solely from shape/color. That belongs
    to later rule/object-model work packages and prevents speculative interpretation.
    """
    def __init__(self, strict: bool=False):
        self.strict=strict

    def parse(self, source: str|Path) -> SemanticDocument:
        path=Path(source).resolve()
        parser=etree.XMLParser(remove_blank_text=False, recover=False, huge_tree=True)
        tree=etree.parse(str(path), parser)
        root=tree.getroot()
        diagnostics: list[Diagnostic]=[]

        # XML/SVG ID inventory
        id_nodes=defaultdict(list)
        for e in root.iter():
            if e.get('id'):
                id_nodes[e.get('id')].append(e)
        for id_,nodes in id_nodes.items():
            if len(nodes)>1:
                diagnostics.append(Diagnostic('SEM-ID-001','ERROR',f'Duplicate SVG id: {id_}',id_,tree.getpath(nodes[0])))

        geometry_cache={}
        def geom(e):
            key=id(e)
            if key in geometry_cache:
                return geometry_cache[key]
            child_boxes=[geom(c).bbox for c in e if isinstance(c.tag,str)]
            g=geometry_for(e,child_boxes)
            geometry_cache[key]=g
            return g

        elements=[]
        flows=[]
        engineering_ids=defaultdict(list)
        for el in root.iter():
            if not isinstance(el.tag,str):
                continue
            bpmn_type=el.get('data-bpmn-type')
            flow_type=el.get('data-flow-type')
            xpath=tree.getpath(el)
            if flow_type:
                eid=el.get('data-element-id') or el.get('id')
                src=el.get('data-source-ref'); tgt=el.get('data-target-ref')
                if not eid:
                    diagnostics.append(Diagnostic('SEM-FLOW-001','ERROR','Flow has no engineering or SVG id',None,xpath)); continue
                if not src or not tgt:
                    diagnostics.append(Diagnostic('SEM-FLOW-002','ERROR','Flow lacks source or target reference',eid,xpath))
                flow=SemanticFlow(eid,el.get('id'),flow_type,src or '',tgt or '',_text(el),geom(el),_style(el),_metadata(el),xpath)
                flows.append(flow); engineering_ids[eid].append(('flow',xpath))
            elif bpmn_type:
                eid=el.get('data-element-id') or el.get('id')
                if not eid:
                    diagnostics.append(Diagnostic('SEM-ELEM-001','ERROR','Semantic element has no engineering or SVG id',None,xpath)); continue
                primitives=[]
                for ch in el.iterdescendants():
                    if not isinstance(ch.tag,str): continue
                    tag=etree.QName(ch).localname
                    if tag in {'rect','circle','ellipse','path','polygon','polyline','line','text'}:
                        primitives.append(_primitive(ch,geom(ch)))
                txt=_text(el)
                element=SemanticElement(eid,el.get('id'),bpmn_type,txt,txt,geom(el),_style(el),_metadata(el),primitives,xpath,el.getparent().get('id') if el.getparent() is not None else None)
                elements.append(element); engineering_ids[eid].append(('element',xpath))

        for eid,occ in engineering_ids.items():
            if len(occ)>1:
                diagnostics.append(Diagnostic('SEM-ID-002','ERROR',f'Duplicate engineering id: {eid}',eid,occ[0][1]))

        element_index={e.engineering_id:e for e in elements}
        for fl in flows:
            if fl.source_ref not in element_index:
                diagnostics.append(Diagnostic('SEM-REF-001','ERROR',f'Unresolved source reference {fl.source_ref}',fl.engineering_id,fl.source_xpath))
            if fl.target_ref not in element_index:
                diagnostics.append(Diagnostic('SEM-REF-002','ERROR',f'Unresolved target reference {fl.target_ref}',fl.engineering_id,fl.source_xpath))

        incoming=Counter(); outgoing=Counter()
        for fl in flows:
            outgoing[fl.source_ref]+=1; incoming[fl.target_ref]+=1
        index={}
        for e in elements:
            index[e.engineering_id]={"kind":"element","type":e.bpmn_type,"incoming":incoming[e.engineering_id],"outgoing":outgoing[e.engineering_id]}
        for f in flows:
            index[f.engineering_id]={"kind":"flow","type":f.flow_type,"source":f.source_ref,"target":f.target_ref}

        doc_meta={k:v for k,v in _local_attrs(root).items() if k.startswith('data-')}
        doc_meta.update({"title":next((x.text for x in root if etree.QName(x).localname=='title'),None),"description":next((x.text for x in root if etree.QName(x).localname=='desc'),None)})
        type_counts=Counter(e.bpmn_type for e in elements); flow_counts=Counter(f.flow_type for f in flows); severity=Counter(d.severity for d in diagnostics)
        stats={"semanticElementCount":len(elements),"flowCount":len(flows),"elementTypes":dict(sorted(type_counts.items())),"flowTypes":dict(sorted(flow_counts.items())),"diagnostics":dict(sorted(severity.items())),"svgNodeCount":sum(1 for _ in root.iter()),"svgIdCount":len(id_nodes)}
        doc=SemanticDocument(SCHEMA_VERSION,{"path":str(path),"filename":path.name,"sha256":_sha256(path),"size":path.stat().st_size},doc_meta,elements,flows,diagnostics,index,stats)
        if self.strict and any(d.severity=='ERROR' for d in diagnostics):
            raise ValueError(f'Semantic parsing failed with {severity["ERROR"]} error(s)')
        return doc

def parse_svg(source: str|Path, strict: bool=False) -> SemanticDocument:
    return SemanticSvgParser(strict=strict).parse(source)