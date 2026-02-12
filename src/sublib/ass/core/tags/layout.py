"""Alignment, wrap style, and reset tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.core.tags.base import TagCategory
from sublib.ass.types import AssAlignment, AssWrapStyle


class AnTag:
    """\\an<1-9> tag definition."""
    name: ClassVar[str] = "an"
    category: ClassVar[TagCategory] = TagCategory.ALIGNMENT
    # param_pattern: ClassVar[str | None] = r'(?:[1-3]|[5-7]|9|1[01])'  # Old incorrect pattern?
    param_pattern: ClassVar[str | None] = r'[1-9]'
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlignment | None:
        try:
            val = int(raw)
            if 1 <= val <= 9:
                return AssAlignment(value=val)
        except ValueError:
            pass
        return None
    
    @staticmethod
    def format(val: AssAlignment) -> str:
        return f"\\an{val.value}"


class ATag:
    """\\a<pos> legacy alignment tag definition."""
    name: ClassVar[str] = "a"
    category: ClassVar[TagCategory] = TagCategory.ALIGNMENT
    param_pattern: ClassVar[str | None] = r'(?:[1-3]|[5-7]|9|1[01])'
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlignment | None:
        try:
            val = int(raw)
            if val in {1, 2, 3, 5, 6, 7, 9, 10, 11}:
                return AssAlignment(value=val, legacy=True)
        except ValueError:
            pass
        return None
    
    @staticmethod
    def format(val: AssAlignment) -> str:
        return f"\\a{val.value}"


class QTag:
    """\\q<0-3> wrap style tag definition."""
    name: ClassVar[str] = "q"
    category: ClassVar[TagCategory] = TagCategory.ALIGNMENT
    param_pattern: ClassVar[str | None] = r'[0-3]'
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssWrapStyle | None:
        try:
            val = int(raw)
            if val in {0, 1, 2, 3}:
                return AssWrapStyle(style=val)
        except ValueError:
            pass
        return None
    
    @staticmethod
    def format(val: AssWrapStyle) -> str:
        return f"\\q{val.style}"


class RTag:
    """\\r or \\r<style> style reset tag definition.
    
    Returns:
        str | None: style name to reset to, or None for default reset
    """
    name: ClassVar[str] = "r"
    category: ClassVar[TagCategory] = TagCategory.RESET
    param_pattern: ClassVar[str | None] = r'[^\\]*'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> str | None:
        raw = raw.strip()
        return raw if raw else None
    
    @staticmethod
    def format(val: str | None) -> str:
        if val:
            return f"\\r{val}"
        return "\\r"

