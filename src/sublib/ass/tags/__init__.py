# sublib/ass/tags/__init__.py
"""ASS override tag definitions.

This package provides:
- Tag classes with parse/format methods
- Registry for tag lookup

Value types are in sublib.ass.types.
"""

# Base
from sublib.ass.tags._base import TagCategory, TagDefinition

# Re-export value types for convenience (canonical source is types/)
from sublib.ass.types import (
    Color, Alpha,
    Position, Move,
    RectClip, VectorClip, ClipValue,
    Fade, FadeComplex,
    Alignment, WrapStyle, StyleReset,
    Transform, Karaoke,
)

# Registry functions
from sublib.ass.tags._registry import (
    TAGS,
    MUTUAL_EXCLUSIVES,
    get_tag,
    is_line_scoped_tag,
    is_first_wins,
    parse_tag,
    format_tag,
)

__all__ = [
    # Base
    "TagCategory",
    "TagDefinition",
    # Value types (from types/)
    "Color", "Alpha",
    "Position", "Move",
    "RectClip", "VectorClip", "ClipValue",
    "Fade", "FadeComplex",
    "Alignment", "WrapStyle", "StyleReset",
    "Transform", "Karaoke",
    # Registry
    "TAGS",
    "MUTUAL_EXCLUSIVES",
    "get_tag",
    "is_line_scoped_tag",
    "is_first_wins",
    "parse_tag",
    "format_tag",
]
