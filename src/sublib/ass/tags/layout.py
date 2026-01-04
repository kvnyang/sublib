# sublib/ass/tags/layout.py
"""Alignment, wrap style, and reset tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Literal

from sublib.ass.tags._base import TagCategory, tag


@dataclass
class Alignment:
    """Alignment value (numpad style 1-9)."""
    value: int
    legacy: bool = False


@dataclass
class WrapStyle:
    """Wrap style value (0-3)."""
    style: Literal[0, 1, 2, 3]


@dataclass
class StyleReset:
    """Style reset value."""
    style_name: str | None = None


@tag
class AnTag:
    """\\an<1-9> tag definition."""
    name: ClassVar[str] = "an"
    category: ClassVar[TagCategory] = TagCategory.ALIGNMENT
    param_pattern: ClassVar[str | None] = r'(?:[1-3]|[5-7]|9|1[01])'
    param_pattern: ClassVar[str | None] = r'[1-9]'
    is_line_scoped: ClassVar[bool] = True
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alignment | None:
        try:
            val = int(raw)
            if 1 <= val <= 9:
                return Alignment(value=val)
        except ValueError:
            pass
        return None
    
    @staticmethod
    def format(val: Alignment) -> str:
        return f"\\an{val.value}"


@tag
class ATag:
    """\\a<pos> legacy alignment tag definition."""
    name: ClassVar[str] = "a"
    category: ClassVar[TagCategory] = TagCategory.ALIGNMENT
    param_pattern: ClassVar[str | None] = r'(?:[1-3]|[5-7]|9|1[01])'
    is_line_scoped: ClassVar[bool] = True
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alignment | None:
        try:
            val = int(raw)
            if val in {1, 2, 3, 5, 6, 7, 9, 10, 11}:
                return Alignment(value=val, legacy=True)
        except ValueError:
            pass
        return None
    
    @staticmethod
    def format(val: Alignment) -> str:
        return f"\\a{val.value}"


@tag
class QTag:
    """\\q<0-3> wrap style tag definition."""
    name: ClassVar[str] = "q"
    category: ClassVar[TagCategory] = TagCategory.ALIGNMENT
    param_pattern: ClassVar[str | None] = r'[0-3]'
    is_line_scoped: ClassVar[bool] = True
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> WrapStyle | None:
        try:
            val = int(raw)
            if val in {0, 1, 2, 3}:
                return WrapStyle(style=val)
        except ValueError:
            pass
        return None
    
    @staticmethod
    def format(val: WrapStyle) -> str:
        return f"\\q{val.style}"


@tag
class RTag:
    """\\r or \\r<style> style reset tag definition."""
    name: ClassVar[str] = "r"
    category: ClassVar[TagCategory] = TagCategory.RESET
    param_pattern: ClassVar[str | None] = r'[^\\]*'
    is_line_scoped: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> StyleReset:
        raw = raw.strip()
        return StyleReset(style_name=raw if raw else None)
    
    @staticmethod
    def format(val: StyleReset) -> str:
        if val.style_name:
            return f"\\r{val.style_name}"
        return "\\r"
