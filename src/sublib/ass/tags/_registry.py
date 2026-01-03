# sublib/ass/tags/registry.py
"""Tag registry - unified access interface for all tags.

The registry is built automatically via the @tag decorator.
Each tag module must be imported to trigger registration.
"""
from __future__ import annotations
from typing import Any, Type

# Import base to get the registry
from sublib.ass.tags._base import (
    TagCategory,
    TagDefinition,
    get_registered_tags,
)

# Import all tag modules to trigger @tag decorator registration
# Order doesn't matter - each module registers its own tags
from sublib.ass.tags import position  # noqa: F401
from sublib.ass.tags import clip  # noqa: F401
from sublib.ass.tags import fade  # noqa: F401
from sublib.ass.tags import layout  # noqa: F401
from sublib.ass.tags import drawing  # noqa: F401
from sublib.ass.tags import color  # noqa: F401
from sublib.ass.tags import border  # noqa: F401
from sublib.ass.tags import transform  # noqa: F401
from sublib.ass.tags import font  # noqa: F401


# Get the populated registry
TAGS: dict[str, Type] = get_registered_tags()
"""Tag name -> Tag class mapping."""


# Build mutual exclusives from tag classes
MUTUAL_EXCLUSIVES: dict[str, set[str]] = {
    name: set(cls.exclusives) 
    for name, cls in TAGS.items() 
    if cls.exclusives
}
"""Tag name -> set of mutually exclusive tag names."""


def get_tag(name: str) -> Type | None:
    """Get tag class by name."""
    return TAGS.get(name)


def is_event_tag(name: str) -> bool:
    """Check if tag is event-level."""
    tag = TAGS.get(name)
    return tag.is_event if tag else False


def is_first_wins(name: str) -> bool:
    """Check if first occurrence wins."""
    tag = TAGS.get(name)
    return tag.first_wins if tag else False


def parse_tag(name: str, raw: str) -> Any:
    """Parse a tag value.
    
    Args:
        name: Tag name (without backslash)
        raw: Raw string value
        
    Returns:
        Parsed value, or raw string if tag unknown
    """
    tag = TAGS.get(name)
    if tag:
        return tag.parse(raw)
    return raw


def format_tag(name: str, value: Any) -> str:
    """Format a tag value.
    
    Args:
        name: Tag name (without backslash)
        value: Typed value
        
    Returns:
        Formatted ASS tag string
    """
    tag = TAGS.get(name)
    if tag:
        return tag.format(value)
    return f"\\{name}{value}"
