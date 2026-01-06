# sublib/ass/tags/__init__.py
"""ASS override tag definitions.

This package provides:
- Tag classes with parse/format methods
- Registry for tag lookup

Value types are in sublib.ass.types.
"""

from sublib.ass.tags.registry import (
    TagCategory,
    TagDefinition,
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
