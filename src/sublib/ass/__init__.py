# sublib/ass/__init__.py
"""ASS (Advanced SubStation Alpha v4+) subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle
from sublib.ass.serde import AssTextParser, AssTextRenderer
from sublib.ass.extractor import extract_event_level_tags, extract_inline_segments
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
    "extract_event_level_tags",
    "extract_inline_segments",
    # Common types
    "Color",
    "Timestamp",
]
