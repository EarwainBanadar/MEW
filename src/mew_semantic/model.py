from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Geometry:
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    cx: Optional[float] = None
    cy: Optional[float] = None
    radius: Optional[float] = None
    bbox: Optional[Dict[str, float]] = None
    transform: Optional[str] = None
    path_data: Optional[str] = None
    points: List[Point] = field(default_factory=list)

@dataclass(frozen=True)
class GraphicPrimitive:
    svg_id: Optional[str]
    tag: str
    geometry: Geometry
    style: Dict[str, str]
    attributes: Dict[str, str]

@dataclass(frozen=True)
class SemanticElement:
    engineering_id: str
    svg_id: Optional[str]
    bpmn_type: str
    name: Optional[str]
    text: Optional[str]
    geometry: Geometry
    style: Dict[str, str]
    metadata: Dict[str, str]
    primitives: List[GraphicPrimitive]
    source_xpath: str
    parent_svg_id: Optional[str] = None

@dataclass(frozen=True)
class SemanticFlow:
    engineering_id: str
    svg_id: Optional[str]
    flow_type: str
    source_ref: str
    target_ref: str
    name: Optional[str]
    geometry: Geometry
    style: Dict[str, str]
    metadata: Dict[str, str]
    source_xpath: str

@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    element_id: Optional[str] = None
    xpath: Optional[str] = None

@dataclass
class SemanticDocument:
    schema_version: str
    source: Dict[str, Any]
    document_metadata: Dict[str, Any]
    elements: List[SemanticElement]
    flows: List[SemanticFlow]
    diagnostics: List[Diagnostic]
    index: Dict[str, Dict[str, Any]]
    statistics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
