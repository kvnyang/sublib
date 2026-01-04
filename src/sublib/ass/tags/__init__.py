# sublib/ass/tags/__init__.py
"""ASS override tag definitions.

This package provides:
- Tag value types (Position, Move, Color, etc.)
- Tag classes with parse/format methods
- Registry for tag lookup
"""

# Base
from sublib.ass.tags._base import TagCategory, TagDefinition

# Value types (multi-field dataclasses only - single values use primitives)
from sublib.ass.tags.position import Position, Move
from sublib.ass.tags.clip import RectClip, VectorClip, ClipValue
from sublib.ass.tags.fade import Fade, FadeComplex
from sublib.ass.tags.color import Color, Alpha
from sublib.ass.tags.layout import Alignment, WrapStyle, StyleReset
from sublib.ass.tags.transform import Transform, Karaoke

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
    # Value types
    "Position", "Move",
    "RectClip", "VectorClip", "ClipValue",
    "Fade", "FadeComplex",
    "Color", "Alpha",
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
