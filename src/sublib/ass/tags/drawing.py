# sublib/ass/tags/drawing.py
"""Drawing mode tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.tags.base import TagCategory


def _parse_int(raw: str, *, ge: int | None = None) -> int | None:
    try:
        val = int(raw)
        if ge is not None and val < ge:
            return None
        return val
    except ValueError:
        return None


class PTag:
    """\\p drawing mode tag definition."""
    name: ClassVar[str] = "p"
    category: ClassVar[TagCategory] = TagCategory.DRAWING
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_int(raw, ge=0)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\p{val}"


class PboTag:
    """\\pbo baseline offset tag definition."""
    name: ClassVar[str] = "pbo"
    category: ClassVar[TagCategory] = TagCategory.DRAWING
    param_pattern: ClassVar[str | None] = r'-?\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
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
