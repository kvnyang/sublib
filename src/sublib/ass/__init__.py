# sublib/ass/__init__.py
"""ASS (Advanced SubStation Alpha v4+) subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle
from sublib.ass.serde import AssTextParser, AssTextRenderer
from sublib.ass.text_transform import extract_all, ExtractionResult, compose_all
from sublib.ass.types import Color, Timestamp

__all__ = [
    # Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    # Serde
    "AssTextParser",
    "AssTextRenderer",
    # Text transform
    "extract_all",
    "ExtractionResult",
    "compose_all",
    # Common types
    "Color",
    "Timestamp",
]

