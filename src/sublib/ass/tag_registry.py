# sublib/ass/tag_registry.py
"""ASS override tag registry.

This module provides backward-compatible API for tag specifications.
The actual implementation is in the tags/ subpackage.
"""
from __future__ import annotations

# Re-export from new location
from sublib.ass.tags import (
    TAGS,
    MUTUAL_EXCLUSIVES,
    get_tag,
    is_event_tag,
    is_first_wins,
    parse_tag,
    format_tag,
)

# Legacy aliases
TAG_REGISTRY = TAGS
get_tag_spec = get_tag
get_first_wins = is_first_wins

__all__ = [
    "TAGS",
    "TAG_REGISTRY",
    "MUTUAL_EXCLUSIVES",
    "get_tag",
    "get_tag_spec",
    "is_event_tag",
    "is_first_wins",
    "get_first_wins",
    "parse_tag",
    "format_tag",
]
