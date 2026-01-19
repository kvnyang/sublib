"""ASS override tag definitions.

This package provides:
- Tag classes with parse/format methods
- Registry for tag lookup

Value types are in sublib.ass.types.
"""

# Base types (no circular dependencies)
from sublib.ass.tags.base import TagCategory, TagDefinition

# Registry data and functions
from sublib.ass.tags.registry import (
    TAGS,
    MUTUAL_EXCLUSIVES,
    get_tag,
    is_event_level_tag,
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
    "is_event_level_tag",
    "is_first_wins",
    "parse_tag",
    "format_tag",
]
