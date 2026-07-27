"""Stable public API for semantic SVG parsing."""

from .model import Diagnostic, SemanticDocument, SemanticElement, SemanticFlow
from .parser import SemanticSvgParser, parse_svg

__all__ = [
    "Diagnostic",
    "SemanticDocument",
    "SemanticElement",
    "SemanticFlow",
    "SemanticSvgParser",
    "parse_svg",
]
