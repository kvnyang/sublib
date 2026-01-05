# sublib/ass/tags/__init__.py
"""ASS override tag definitions.

This package provides:
- Tag classes with parse/format methods
- Registry for tag lookup

Value types are in sublib.ass.types.
"""

# Base
from sublib.ass.tags._base import TagCategory, TagDefinition

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
    # Registry
    "TAGS",
    "MUTUAL_EXCLUSIVES",
    "get_tag",
    "is_line_scoped_tag",
    "is_first_wins",
    "parse_tag",
    "format_tag",
]
