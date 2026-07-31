"""Stable public API for semantic SVG parsing, graph analysis, and quality gates."""

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
from .quality import (
    CrossScopeFlowRule,
    EngineeringQualityValidator,
    MissingNameRule,
    OrphanElementRule,
    QualityFinding,
    QualityProfile,
    QualityResult,
    QualitySeverity,
    UnresolvedReferenceRule,
    validate_quality,
)
from .query import ImpactResult, SemanticQueryService

__all__ = [
    "CrossScopeFlowRule",
    "Diagnostic",
    "EngineeringQualityValidator",
    "GraphEdge",
    "ImpactResult",
    "MissingNameRule",
    "OrphanElementRule",
    "QualityFinding",
    "QualityProfile",
    "QualityResult",
    "QualitySeverity",
    "SemanticDocument",
    "SemanticElement",
    "SemanticFlow",
    "SemanticGraph",
    "SemanticQueryService",
    "SemanticReference",
    "SemanticScope",
    "SemanticSvgParser",
    "UnresolvedReferenceRule",
    "build_dependency_graph",
    "build_model_graph",
    "parse_svg",
    "validate_quality",
]
