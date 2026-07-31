"""Stable public API for semantic SVG parsing."""

from .model import (
    Diagnostic,
    SemanticDocument,
    SemanticElement,
    SemanticFlow,
    SemanticReference,
    SemanticScope,
)
from .parser import SemanticSvgParser, parse_svg

__all__ = [
    "Diagnostic",
    "SemanticDocument",
    "SemanticElement",
    "SemanticFlow",
    "SemanticReference",
    "SemanticScope",
    "SemanticSvgParser",
    "parse_svg",
]
