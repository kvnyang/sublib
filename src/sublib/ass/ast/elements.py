# sublib/ass/ast/elements.py
"""ASS text element types.

These represent the parsed structure of ASS event text,
aligned with official ASS specification terminology.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Union


# ===== Override System (inside {...}) =====

@dataclass
class AssOverrideTag:
    """Override tag within override blocks.
    
    Examples: \\b1, \\i1, \\pos(100,100)
    
    Per ASS spec: "Override tags modify text styling and must appear 
    within override blocks {...}."
    
    Attributes:
        name: Tag name without backslash (e.g., "b", "pos", "1c")
        value: Parsed value (type depends on tag)
        raw: Original string for roundtrip
        is_event_level: Whether this affects the entire line
        first_wins: Whether first occurrence wins (vs last)
        is_function: Whether tag uses function syntax with parentheses
    """
    name: str
    value: Any
    raw: str
    is_event_level: bool = False
    first_wins: bool = False
    is_function: bool = False


@dataclass
class AssComment:
    """Comment/unrecognized text inside an override block."""
    content: str


@dataclass
class AssOverrideBlock:
    """Override block: {...}
    
    Per ASS spec: "Override tags must appear within override blocks, 
    which begin with { and end with }."
    
    Contains override tags and optionally comments (unrecognized text).
    """
    elements: list[Union[AssOverrideTag, AssComment]]


# ===== Text System (outside {...}) =====

class SpecialCharType(Enum):
    """Types of special characters.
    
    Per ASS spec: "Special characters are written in the middle of 
    the text, and not inside override blocks."
    """
    HARD_NEWLINE = 'N'   # \\N - Always creates new line
    SOFT_NEWLINE = 'n'   # \\n - New line only in wrap mode 2
    HARD_SPACE = 'h'     # \\h - Non-breaking space


@dataclass
class AssSpecialChar:
    """Special character (\\N, \\n, \\h).
    
    Per ASS spec: "The following tags are written in the middle of 
    the text, and not inside override blocks."
    
    These are written directly in text flow, not in {...} blocks.
    
    Attributes:
        type: Which special character this represents
    """
    type: SpecialCharType
    
    @property
    def is_newline(self) -> bool:
        """Check if this is any kind of newline."""
        return self.type in (
            SpecialCharType.HARD_NEWLINE,
            SpecialCharType.SOFT_NEWLINE
        )
    
    @property
    def is_hard_newline(self) -> bool:
        """Check if this is a hard newline (\\N)."""
        return self.type == SpecialCharType.HARD_NEWLINE
    
    def render(self) -> str:
        """Render to ASS text."""
        return f'\\{self.type.value}'


@dataclass
class AssPlainText:
    """Plain text content.
    
    Regular text without special meaning.
    """
    content: str


# ===== Element Union =====

# All text element types that can appear in ASS event text
AssTextElement = Union[AssOverrideBlock, AssSpecialChar, AssPlainText]

# Block element types that can appear inside override blocks
AssBlockElement = Union[AssOverrideTag, AssComment]
