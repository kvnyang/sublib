# sublib/ass/elements.py
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
        is_line_scoped: Whether this affects the entire line
        first_wins: Whether first occurrence wins (vs last)
        is_function: Whether tag uses function syntax with parentheses
    """
    name: str
    value: Any
    raw: str
    is_line_scoped: bool = False
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


# ===== Helper Types =====

@dataclass
class AssTextSegment:
    """A text segment with its formatting tags.
    
    Returned by AssEvent.extract_text_scoped_segments() to represent 
    a contiguous piece of text with consistent formatting.
    
    Attributes:
        tags: Dict of effective text-scoped tag values.
              Conflicts are resolved (last-wins), so dict is appropriate.
        content: List of content elements, preserving type info.
                 Allows distinct handling of plain text vs special chars.
    """
    block_tags: dict[str, Any]
    content: list["AssPlainText | AssSpecialChar"]
    
    def get_text(self) -> str:
        """Get combined text as string.
        
        Convenience method for simple use cases.
        Special chars rendered as escape sequences (\\N, \\n, \\h).
        """
        result = []
        for item in self.content:
            if isinstance(item, AssPlainText):
                result.append(item.content)
            elif isinstance(item, AssSpecialChar):
                result.append(item.render())
        return "".join(result)
    
    def __len__(self) -> int:
        """Return total character length of text content."""
        return len(self.get_text())
    
    def __bool__(self) -> bool:
        """Return True if segment has content."""
        return bool(self.content)


# ===== Element Union =====

# All text element types that can appear in ASS event text
AssTextElement = Union[AssOverrideBlock, AssSpecialChar, AssPlainText]
