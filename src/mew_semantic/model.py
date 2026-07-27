from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Geometry:
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    cx: float | None = None
    cy: float | None = None
    radius: float | None = None
    bbox: dict[str, float] | None = None
    transform: str | None = None
    path_data: str | None = None
    points: list[Point] = field(default_factory=list)

@dataclass(frozen=True)
class GraphicPrimitive:
    svg_id: str | None
    tag: str
    geometry: Geometry
    style: dict[str, str]
    attributes: dict[str, str]

@dataclass(frozen=True)
class SemanticElement:
    engineering_id: str
    svg_id: str | None
    bpmn_type: str
    name: str | None
    text: str | None
    geometry: Geometry
    style: dict[str, str]
    metadata: dict[str, str]
    primitives: list[GraphicPrimitive]
    source_xpath: str
    parent_svg_id: str | None = None

@dataclass(frozen=True)
class SemanticFlow:
    engineering_id: str
    svg_id: str | None
    flow_type: str
    source_ref: str
    target_ref: str
    name: str | None
    geometry: Geometry
    style: dict[str, str]
    metadata: dict[str, str]
    source_xpath: str

@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    element_id: str | None = None
    xpath: str | None = None

@dataclass
class SemanticDocument:
    schema_version: str
    source: dict[str, Any]
    document_metadata: dict[str, Any]
    elements: list[SemanticElement]
    flows: list[SemanticFlow]
    diagnostics: list[Diagnostic]
    index: dict[str, dict[str, Any]]
    statistics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
