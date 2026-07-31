"""Stable public API for semantic SVG parsing and graph analysis."""

from .graph import GraphEdge, SemanticGraph, build_dependency_graph, build_model_graph
from .model import (
    Diagnostic,
    SemanticDocument,
    SemanticElement,
    SemanticFlow,
    SemanticReference,
    SemanticScope,
)
from .parser import SemanticSvgParser, parse_svg
from .query import ImpactResult, SemanticQueryService

__all__ = [
    "Diagnostic",
    "GraphEdge",
    "ImpactResult",
    "SemanticDocument",
    "SemanticElement",
    "SemanticFlow",
    "SemanticGraph",
    "SemanticQueryService",
    "SemanticReference",
    "SemanticScope",
    "SemanticSvgParser",
    "build_dependency_graph",
    "build_model_graph",
    "parse_svg",
]
