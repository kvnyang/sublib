# sublib/ass/tags/color.py
"""Color and alpha tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags.base import TagCategory


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


def _make_color_tag(tag_name: str):
    """Factory for color tag classes."""
    _name = tag_name  # Capture for closure
    
    class ColorTagDef:
        name: ClassVar[str] = _name
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
            return f"\\{_name}&H{val.value:06X}&"
    
    ColorTagDef.__name__ = f"{tag_name.replace('c', 'C')}Tag"
    return ColorTagDef


def _make_alpha_tag(tag_name: str):
    """Factory for alpha tag classes."""
    _name = tag_name  # Capture for closure
    
    class AlphaTagDef:
        name: ClassVar[str] = _name
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
            return f"\\{_name}&H{val.value:02X}&"
    
    AlphaTagDef.__name__ = f"{tag_name.capitalize()}Tag"
    return AlphaTagDef


# Color tags
CTag = _make_color_tag("c")
C1Tag = _make_color_tag("1c")
C2Tag = _make_color_tag("2c")
C3Tag = _make_color_tag("3c")
C4Tag = _make_color_tag("4c")

# Alpha tags
AlphaTag = _make_alpha_tag("alpha")
A1Tag = _make_alpha_tag("1a")
A2Tag = _make_alpha_tag("2a")
A3Tag = _make_alpha_tag("3a")
A4Tag = _make_alpha_tag("4a")
