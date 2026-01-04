# sublib/ass/tags/base.py
"""Base protocol and utilities for tag definitions."""
from __future__ import annotations
from typing import Any, ClassVar, Protocol, Type, runtime_checkable
from enum import Enum, auto


class TagCategory(Enum):
    """Categories of ASS override tags."""
    POSITION = auto()
    CLIP = auto()
    FADE = auto()
    ALIGNMENT = auto()
    FONT = auto()
    TEXT_STYLE = auto()
    BORDER = auto()
    SHADOW = auto()
    BLUR = auto()
    COLOR = auto()
    ALPHA = auto()
    ROTATION = auto()
    SHEAR = auto()
    KARAOKE = auto()
    DRAWING = auto()
    ANIMATION = auto()
    RESET = auto()


@runtime_checkable
class TagDefinition(Protocol):
    """Protocol for tag definitions.
    
    Each tag class must implement these class variables and methods.
    """
    name: ClassVar[str]
    category: ClassVar[TagCategory]
    param_pattern: ClassVar[str | None]  # NEW: Regex pattern for parameter matching
    is_line_scoped: ClassVar[bool]
    is_function: ClassVar[bool]
    first_wins: ClassVar[bool]
    exclusives: ClassVar[frozenset[str]]
    
    @staticmethod
    def parse(raw: str) -> Any:
        """Parse raw string value to typed value."""
        ...
    
    @staticmethod
    def format(value: Any) -> str:
        """Format typed value to ASS string."""
        ...


# ============================================================
# Auto-Registration
# ============================================================

# Global registry populated by @tag decorator
_TAGS: dict[str, Type] = {}


def tag(cls: Type) -> Type:
    """Decorator to register a tag class.
    
    Usage:
        @tag
        class PosTag:
            name = "pos"
            ...
    """
    if not hasattr(cls, "name"):
        raise ValueError(f"Tag class {cls.__name__} must have 'name' attribute")
    
    tag_name = cls.name
    if tag_name in _TAGS:
        raise ValueError(f"Tag '{tag_name}' already registered by {_TAGS[tag_name].__name__}")
    
    _TAGS[tag_name] = cls
    return cls


def get_registered_tags() -> dict[str, Type]:
    """Get all registered tag classes."""
    return _TAGS.copy()
