# asslib/elements.py
"""ASS text element types.

These represent the parsed structure of ASS event text.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Union


@dataclass
class AssOverrideTag:
    """Override tag: {\\fn...}, {\\pos(x,y)}, etc.
    
    Attributes:
        name: Tag name without backslash (e.g., "fn", "pos", "1c")
        value: Parsed value (type depends on tag)
        raw: Original string for roundtrip
        is_event: Whether this is an event-level tag
        first_wins: Whether first occurrence wins (vs last)
        is_function: Whether tag uses function syntax with parentheses
    """
    name: str
    value: Any
    raw: str
    is_event: bool = False
    first_wins: bool = False
    is_function: bool = False


@dataclass
class AssPlainText:
    """Plain text segment (no override tags)."""
    content: str


@dataclass
class AssNewLine:
    """Newline marker.
    
    Attributes:
        hard: True for \\N (hard break), False for \\n (soft break)
    """
    hard: bool


@dataclass
class AssHardSpace:
    """Hard space marker (\\h).
    
    A non-breaking space that prevents line wrapping at this position.
    Typically rendered as Unicode U+00A0 (NO-BREAK SPACE).
    """
    pass


@dataclass
class AssTextSegment:
    """A text segment with its preceding inline formatting tags.
    
    Returned by AssEvent.extract_segments() to represent a contiguous
    piece of text with consistent formatting.
    
    Attributes:
        tags: List of inline AssOverrideTag that apply to this segment
        text: The text content (may include \\N, \\n, \\h markers)
    """
    tags: list["AssOverrideTag"]
    text: str


# Union of all text element types
AssTextElement = Union[AssOverrideTag, AssPlainText, AssNewLine, AssHardSpace]

