# sublib/ass/tag_registry.py
"""ASS override tag registry.

This module provides a unified API for tag specifications, parsing, and formatting.
The actual implementations are in the tags/ subpackage.

DEPRECATED: Direct use of this module is deprecated.
Use sublib.ass.tags directly for new code.
"""
from __future__ import annotations
from typing import Any

# Re-export from new locations for backward compatibility
from sublib.ass.tags.spec import (
    TagSpec,
    TagCategory,
    TAGS,
    MUTUAL_EXCLUSIVES,
    get_spec,
    is_event_tag,
    is_first_wins,
    get_exclusives,
)

from sublib.ass.tags.parsers import (
    parse_tag,
    PARSERS,
)

from sublib.ass.tags.formatters import (
    format_tag,
    FORMATTERS,
)


# Legacy names for backward compatibility
TAG_REGISTRY = TAGS


def get_tag_spec(name: str) -> TagSpec | None:
    """Get the spec for a tag by name.
    
    DEPRECATED: Use get_spec() instead.
    """
    return get_spec(name)


def get_first_wins(name: str) -> bool:
    """Check if first occurrence wins for a tag.
    
    DEPRECATED: Use is_first_wins() instead.
    """
    return is_first_wins(name)


__all__ = [
    # Specs
    "TagSpec",
    "TagCategory",
    "TAGS",
    "TAG_REGISTRY",
    "MUTUAL_EXCLUSIVES",
    "get_spec",
    "get_tag_spec",
    "is_event_tag",
    "is_first_wins",
    "get_first_wins",
    "get_exclusives",
    # Parsing
    "parse_tag",
    "PARSERS",
    # Formatting
    "format_tag",
    "FORMATTERS",
]
