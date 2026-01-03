# sublib/ass/tags/color.py
"""Color and alpha tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags._base import TagCategory, tag


@dataclass
class Color:
    """Color value in BGR format (ASS native)."""
    value: int  # 0xBBGGRR
    
    @property
    def blue(self) -> int:
        return (self.value >> 16) & 0xFF
    
    @property
    def green(self) -> int:
        return (self.value >> 8) & 0xFF
    
    @property
    def red(self) -> int:
        return self.value & 0xFF
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        return cls((b << 16) | (g << 8) | r)


@dataclass
class Alpha:
    """Alpha value (0=visible, 255=transparent)."""
    value: int
    
    @property
    def opacity(self) -> float:
        return 1.0 - (self.value / 255.0)


def _parse_color(raw: str) -> Color | None:
    raw = raw.strip().strip("&H").strip("&")
    try:
        return Color(value=int(raw, 16))
    except ValueError:
        return None


def _parse_alpha(raw: str) -> Alpha | None:
    raw = raw.strip().strip("&H").strip("&")
    try:
        return Alpha(value=int(raw, 16))
    except ValueError:
        return None


# ============================================================
# Color Tags
# ============================================================

@tag
class CTag:
    """\\c (alias for \\1c) tag definition."""
    name: ClassVar[str] = "c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Color | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: Color) -> str:
        return f"\\c&H{val.value:06X}&"


@tag
class C1Tag:
    """\\1c primary color tag definition."""
    name: ClassVar[str] = "1c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Color | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: Color) -> str:
        return f"\\1c&H{val.value:06X}&"


@tag
class C2Tag:
    """\\2c secondary color tag definition."""
    name: ClassVar[str] = "2c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Color | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: Color) -> str:
        return f"\\2c&H{val.value:06X}&"


@tag
class C3Tag:
    """\\3c outline color tag definition."""
    name: ClassVar[str] = "3c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Color | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: Color) -> str:
        return f"\\3c&H{val.value:06X}&"


@tag
class C4Tag:
    """\\4c shadow color tag definition."""
    name: ClassVar[str] = "4c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Color | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: Color) -> str:
        return f"\\4c&H{val.value:06X}&"


# ============================================================
# Alpha Tags
# ============================================================

@tag
class AlphaTag:
    """\\alpha (all colors) tag definition."""
    name: ClassVar[str] = "alpha"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: Alpha) -> str:
        return f"\\alpha&H{val.value:02X}&"


@tag
class A1Tag:
    """\\1a primary alpha tag definition."""
    name: ClassVar[str] = "1a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: Alpha) -> str:
        return f"\\1a&H{val.value:02X}&"


@tag
class A2Tag:
    """\\2a secondary alpha tag definition."""
    name: ClassVar[str] = "2a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: Alpha) -> str:
        return f"\\2a&H{val.value:02X}&"


@tag
class A3Tag:
    """\\3a outline alpha tag definition."""
    name: ClassVar[str] = "3a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: Alpha) -> str:
        return f"\\3a&H{val.value:02X}&"


@tag
class A4Tag:
    """\\4a shadow alpha tag definition."""
    name: ClassVar[str] = "4a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Alpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: Alpha) -> str:
        return f"\\4a&H{val.value:02X}&"
