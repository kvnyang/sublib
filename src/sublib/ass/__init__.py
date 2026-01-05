# sublib/ass/__init__.py
"""ASS (Advanced SubStation Alpha v4+) subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle, ScriptInfo
from sublib.ass.serde import AssTextParser, AssTextRenderer
from sublib.ass.extractor import extract_line_scoped_tags, extract_text_scoped_segments
from sublib.ass.types import Color, Timestamp

__all__ = [
    # Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    "ScriptInfo",
    # Serde
    "AssTextParser",
    "AssTextRenderer",
    # Extractor
    "extract_line_scoped_tags",
    "extract_text_scoped_segments",
    # Common types
    "Color",
    "Timestamp",
]
