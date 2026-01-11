# sublib/ass/__init__.py
"""ASS (Advanced SubStation Alpha v4+) subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle
from sublib.ass.serde import AssTextParser, AssTextRenderer
from sublib.ass.extractor import extract_all, ExtractionResult
from sublib.ass.types import Color, Timestamp

__all__ = [
    # Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    # Serde
    "AssTextParser",
    "AssTextRenderer",
    # Extractor
    "extract_all",
    "ExtractionResult",
    # Common types
    "Color",
    "Timestamp",
]

