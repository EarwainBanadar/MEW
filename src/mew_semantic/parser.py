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
    SemanticReference,
    SemanticScope,
)

SCHEMA_VERSION = "0.2.0"
STYLE_KEYS = {
    "fill",
    "stroke",
    "stroke-width",
    "stroke-dasharray",
    "opacity",
    "font-family",
    "font-size",
    "font-weight",
    "text-anchor",
    "marker-start",
    "marker-mid",
    "marker-end",
}
SEMANTIC_ATTRS = {
    "data-bpmn-type",
    "data-element-id",
    "data-flow-type",
    "data-source-ref",
    "data-target-ref",
}
SCOPE_TYPES = {"collaboration", "pool", "participant", "process", "subprocess", "lane"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _local_attrs(element: etree._Element) -> dict[str, str]:
    result = {}
    for key, value in element.attrib.items():
        try:
            local_key = etree.QName(key).localname
        except ValueError:
            local_key = key
        result[local_key] = value
    return result


def _style(element: etree._Element) -> dict[str, str]:
    result = {}
    if element.get("style"):
        for item in element.get("style").split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                result[key.strip()] = value.strip()
    for key in STYLE_KEYS:
        if element.get(key) is not None:
            result[key] = element.get(key)
    return result


def _metadata(element: etree._Element) -> dict[str, str]:
    return {
        key: value
        for key, value in _local_attrs(element).items()
        if key.startswith("data-") and key not in SEMANTIC_ATTRS
    }


def _text(element: etree._Element) -> str | None:
    values = []
    for node in element.iter():
        if etree.QName(node).localname in ("text", "tspan") and node.text:
            text = " ".join(node.text.split())
            if text and (not values or values[-1] != text):
                values.append(text)
    return " ".join(values) if values else None


def _primitive(element: etree._Element, geometry: Geometry) -> GraphicPrimitive:
    return GraphicPrimitive(
        svg_id=element.get("id"),
        tag=etree.QName(element).localname,
        geometry=geometry,
        style=_style(element),
        attributes=_local_attrs(element),
    )


def _engineering_id(element: etree._Element) -> str | None:
    return element.get("data-element-id") or element.get("id")


def _nearest_semantic_ancestor(element: etree._Element) -> etree._Element | None:
    parent = element.getparent()
    while parent is not None:
        if parent.get("data-bpmn-type"):
            return parent
        parent = parent.getparent()
    return None


def _nearest_scope(element: etree._Element, include_self: bool = True) -> etree._Element | None:
    candidate = element if include_self else element.getparent()
    while candidate is not None:
        bpmn_type = (candidate.get("data-bpmn-type") or "").lower()
        if candidate.get("data-scope") == "true" or bpmn_type in SCOPE_TYPES:
            return candidate
        candidate = candidate.getparent()
    return None


def _reference_tokens(value: str) -> list[str]:
    return [token for token in value.replace(",", " ").split() if token]


class SemanticSvgParser:
    """Parse semantically annotated BPMN-like SVG into a stable neutral document.

    The parser preserves explicit annotations and resolves deterministic hierarchy,
    scope membership and declared data-* references. It never infers BPMN semantics
    solely from geometry, shape or color.
    """

    def __init__(self, strict: bool = False):
        self.strict = strict

    def parse(self, source: str | Path) -> SemanticDocument:
        path = Path(source).resolve()
        parser = etree.XMLParser(remove_blank_text=False, recover=False, huge_tree=True)
        tree = etree.parse(str(path), parser)
        root = tree.getroot()
        diagnostics: list[Diagnostic] = []

        id_nodes = defaultdict(list)
        for element in root.iter():
            if element.get("id"):
                id_nodes[element.get("id")].append(element)
        for svg_id, nodes in id_nodes.items():
            if len(nodes) > 1:
                diagnostics.append(
                    Diagnostic(
                        "SEM-ID-001",
                        "ERROR",
                        f"Duplicate SVG id: {svg_id}",
                        svg_id,
                        tree.getpath(nodes[0]),
                    )
                )

        geometry_cache = {}

        def geom(element: etree._Element) -> Geometry:
            key = id(element)
            if key in geometry_cache:
                return geometry_cache[key]
            child_boxes = [geom(child).bbox for child in element if isinstance(child.tag, str)]
            geometry = geometry_for(element, child_boxes)
            geometry_cache[key] = geometry
            return geometry

        elements: list[SemanticElement] = []
        flows: list[SemanticFlow] = []
        engineering_ids = defaultdict(list)
        semantic_nodes: dict[str, etree._Element] = {}

        for element in root.iter():
            if not isinstance(element.tag, str):
                continue
            bpmn_type = element.get("data-bpmn-type")
            flow_type = element.get("data-flow-type")
            xpath = tree.getpath(element)

            if flow_type:
                engineering_id = _engineering_id(element)
                source_ref = element.get("data-source-ref")
                target_ref = element.get("data-target-ref")
                if not engineering_id:
                    diagnostics.append(
                        Diagnostic(
                            "SEM-FLOW-001",
                            "ERROR",
                            "Flow has no engineering or SVG id",
                            None,
                            xpath,
                        )
                    )
                    continue
                if not source_ref or not target_ref:
                    diagnostics.append(
                        Diagnostic(
                            "SEM-FLOW-002",
                            "ERROR",
                            "Flow lacks source or target reference",
                            engineering_id,
                            xpath,
                        )
                    )
                scope_node = _nearest_scope(element, include_self=False)
                flows.append(
                    SemanticFlow(
                        engineering_id=engineering_id,
                        svg_id=element.get("id"),
                        flow_type=flow_type,
                        source_ref=source_ref or "",
                        target_ref=target_ref or "",
                        name=_text(element),
                        geometry=geom(element),
                        style=_style(element),
                        metadata=_metadata(element),
                        source_xpath=xpath,
                        scope_ref=_engineering_id(scope_node) if scope_node is not None else None,
                    )
                )
                engineering_ids[engineering_id].append(("flow", xpath))
                semantic_nodes[engineering_id] = element
                continue

            if not bpmn_type:
                continue

            engineering_id = _engineering_id(element)
            if not engineering_id:
                diagnostics.append(
                    Diagnostic(
                        "SEM-ELEM-001",
                        "ERROR",
                        "Semantic element has no engineering or SVG id",
                        None,
                        xpath,
                    )
                )
                continue

            primitives = []
            for child in element.iterdescendants():
                if not isinstance(child.tag, str):
                    continue
                tag = etree.QName(child).localname
                if tag in {
                    "rect",
                    "circle",
                    "ellipse",
                    "path",
                    "polygon",
                    "polyline",
                    "line",
                    "text",
                }:
                    primitives.append(_primitive(child, geom(child)))

            parent_node = _nearest_semantic_ancestor(element)
            scope_node = _nearest_scope(element, include_self=True)
            text = _text(element)
            elements.append(
                SemanticElement(
                    engineering_id=engineering_id,
                    svg_id=element.get("id"),
                    bpmn_type=bpmn_type,
                    name=text,
                    text=text,
                    geometry=geom(element),
                    style=_style(element),
                    metadata=_metadata(element),
                    primitives=primitives,
                    source_xpath=xpath,
                    parent_svg_id=(
                        element.getparent().get("id")
                        if element.getparent() is not None
                        else None
                    ),
                    parent_ref=(
                        _engineering_id(parent_node) if parent_node is not None else None
                    ),
                    scope_ref=_engineering_id(scope_node) if scope_node is not None else None,
                )
            )
            engineering_ids[engineering_id].append(("element", xpath))
            semantic_nodes[engineering_id] = element

        for engineering_id, occurrences in engineering_ids.items():
            if len(occurrences) > 1:
                diagnostics.append(
                    Diagnostic(
                        "SEM-ID-002",
                        "ERROR",
                        f"Duplicate engineering id: {engineering_id}",
                        engineering_id,
                        occurrences[0][1],
                    )
                )

        element_index = {element.engineering_id: element for element in elements}
        known_ids = set(engineering_ids)
        references: list[SemanticReference] = []

        for flow in flows:
            for attribute, target_ref, code in (
                ("data-source-ref", flow.source_ref, "SEM-REF-001"),
                ("data-target-ref", flow.target_ref, "SEM-REF-002"),
            ):
                resolved = target_ref in element_index
                references.append(
                    SemanticReference(
                        source_ref=flow.engineering_id,
                        attribute=attribute,
                        target_ref=target_ref,
                        resolved=resolved,
                        source_xpath=flow.source_xpath,
                    )
                )
                if not resolved:
                    diagnostics.append(
                        Diagnostic(
                            code,
                            "ERROR",
                            f"Unresolved {attribute.removeprefix('data-')} {target_ref}",
                            flow.engineering_id,
                            flow.source_xpath,
                        )
                    )

        for source_ref, node in semantic_nodes.items():
            xpath = tree.getpath(node)
            for attribute, value in _metadata(node).items():
                if not (attribute.endswith("-ref") or attribute.endswith("-refs")):
                    continue
                for target_ref in _reference_tokens(value):
                    resolved = target_ref in known_ids
                    references.append(
                        SemanticReference(
                            source_ref=source_ref,
                            attribute=attribute,
                            target_ref=target_ref,
                            resolved=resolved,
                            source_xpath=xpath,
                        )
                    )
                    if not resolved:
                        diagnostics.append(
                            Diagnostic(
                                "SEM-REF-003",
                                "ERROR",
                                f"Unresolved declared reference {target_ref} in {attribute}",
                                source_ref,
                                xpath,
                            )
                        )

        incoming = Counter()
        outgoing = Counter()
        for flow in flows:
            outgoing[flow.source_ref] += 1
            incoming[flow.target_ref] += 1

        child_refs = defaultdict(list)
        for element in elements:
            if element.parent_ref:
                child_refs[element.parent_ref].append(element.engineering_id)

        index = {}
        for element in elements:
            index[element.engineering_id] = {
                "kind": "element",
                "type": element.bpmn_type,
                "incoming": incoming[element.engineering_id],
                "outgoing": outgoing[element.engineering_id],
                "parent": element.parent_ref,
                "scope": element.scope_ref,
                "children": sorted(child_refs[element.engineering_id]),
            }
        for flow in flows:
            index[flow.engineering_id] = {
                "kind": "flow",
                "type": flow.flow_type,
                "source": flow.source_ref,
                "target": flow.target_ref,
                "scope": flow.scope_ref,
            }

        scope_members = defaultdict(list)
        for element in elements:
            if element.scope_ref:
                scope_members[element.scope_ref].append(element.engineering_id)
        for flow in flows:
            if flow.scope_ref:
                scope_members[flow.scope_ref].append(flow.engineering_id)

        scopes = {}
        for element in elements:
            if element.engineering_id != element.scope_ref:
                continue
            parent_scope_ref = None
            if element.parent_ref:
                parent = element_index.get(element.parent_ref)
                if parent is not None:
                    parent_scope_ref = parent.scope_ref
            scopes[element.engineering_id] = SemanticScope(
                scope_ref=element.engineering_id,
                scope_type=element.bpmn_type,
                parent_scope_ref=parent_scope_ref,
                member_refs=sorted(scope_members[element.engineering_id]),
            )

        document_metadata = {
            key: value for key, value in _local_attrs(root).items() if key.startswith("data-")
        }
        title = next(
            (child.text for child in root if etree.QName(child).localname == "title"),
            None,
        )
        description = next(
            (child.text for child in root if etree.QName(child).localname == "desc"),
            None,
        )
        document_metadata.update({"title": title, "description": description})

        type_counts = Counter(element.bpmn_type for element in elements)
        flow_counts = Counter(flow.flow_type for flow in flows)
        severity = Counter(diagnostic.severity for diagnostic in diagnostics)
        statistics = {
            "semanticElementCount": len(elements),
            "flowCount": len(flows),
            "elementTypes": dict(sorted(type_counts.items())),
            "flowTypes": dict(sorted(flow_counts.items())),
            "diagnostics": dict(sorted(severity.items())),
            "svgNodeCount": sum(1 for _ in root.iter()),
            "svgIdCount": len(id_nodes),
            "scopeCount": len(scopes),
            "referenceCount": len(references),
            "unresolvedReferenceCount": sum(not reference.resolved for reference in references),
        }
        source_metadata = {
            "path": str(path),
            "filename": path.name,
            "sha256": _sha256(path),
            "size": path.stat().st_size,
        }
        document = SemanticDocument(
            schema_version=SCHEMA_VERSION,
            source=source_metadata,
            document_metadata=document_metadata,
            elements=elements,
            flows=flows,
            diagnostics=diagnostics,
            index=index,
            statistics=statistics,
            scopes=scopes,
            references=references,
        )
        if self.strict and any(diagnostic.severity == "ERROR" for diagnostic in diagnostics):
            raise ValueError(f"Semantic parsing failed with {severity['ERROR']} error(s)")
        return document


def parse_svg(source: str | Path, strict: bool = False) -> SemanticDocument:
    return SemanticSvgParser(strict=strict).parse(source)
