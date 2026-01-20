"""ASS text processing system.

This package unifies the AST (Abstract Syntax Tree), Parsing, Rendering,
and Transformation logic for ASS event text.
"""
from .elements import (
    AssOverrideTag,
    AssComment,
    AssOverrideBlock,
    SpecialCharType,
    AssSpecialChar,
    AssPlainText,
    AssTextElement,
    AssBlockElement,
)
from .segment import AssTextSegment
from .parser import AssTextParser, AssTextRenderer
from .transform import ExtractionResult, extract_all, compose_all

__all__ = [
    # AST Elements
    "AssOverrideTag",
    "AssComment",
    "AssOverrideBlock",
    "SpecialCharType",
    "AssSpecialChar",
    "AssPlainText",
    "AssTextElement",
    "AssBlockElement",
    "AssTextSegment",
    # Parser & Renderer
    "AssTextParser",
    "AssTextRenderer",
    # Transformations
    "ExtractionResult",
    "extract_all",
    "compose_all",
]
