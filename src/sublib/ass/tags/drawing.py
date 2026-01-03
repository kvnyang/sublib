# sublib/ass/tags/drawing.py
"""Drawing mode tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags._base import TagCategory, tag


@dataclass
class DrawingMode:
    """Value for \\p tag."""
    scale: int


@dataclass
class BaselineOffset:
    """Value for \\pbo tag."""
    offset: int


def _parse_int(raw: str, *, ge: int | None = None) -> int | None:
    try:
        val = int(raw)
        if ge is not None and val < ge:
            return None
        return val
    except ValueError:
        return None


@tag
class PTag:
    """\\p drawing mode tag definition."""
    name: ClassVar[str] = "p"
    category: ClassVar[TagCategory] = TagCategory.DRAWING
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_int(raw, ge=0)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\p{val}"


@tag
class PboTag:
    """\\pbo baseline offset tag definition."""
    name: ClassVar[str] = "pbo"
    category: ClassVar[TagCategory] = TagCategory.DRAWING
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        try:
            return int(raw)
        except ValueError:
            return None
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\pbo{val}"
