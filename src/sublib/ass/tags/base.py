# sublib/ass/tags/base.py
"""Base types for tag definitions.

This module defines core types with no imports from other tag modules,
ensuring a clean dependency graph.
"""
from __future__ import annotations
from typing import Any, ClassVar, Protocol, runtime_checkable
from enum import Enum, auto


def _format_float(val: float) -> str:
    """Format float to string, removing trailing .0 for integers."""
    if val.is_integer():
        return str(int(val))
    return str(val)


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
    param_pattern: ClassVar[str | None]
    is_event_level: ClassVar[bool]
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
