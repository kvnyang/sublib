# sublib/ass/tags/border.py
"""Border, shadow, and blur tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags.base import TagCategory


@dataclass
class BorderSize:
    """Border size value."""
    value: float


@dataclass
class ShadowDistance:
    """Shadow distance value."""
    value: float


@dataclass
class BlurEdge:
    """Edge blur strength."""
    strength: int


@dataclass
class BlurGaussian:
    """Gaussian blur strength."""
    strength: float


def _parse_float(raw: str, *, ge: float | None = None) -> float | None:
    try:
        val = float(raw)
        if ge is not None and val < ge:
            return None
        return val
    except ValueError:
        return None


def _parse_int(raw: str, *, ge: int | None = None) -> int | None:
    try:
        val = int(raw)
        if ge is not None and val < ge:
            return None
        return val
    except ValueError:
        return None


def _make_border_tag(tag_name: str):
    """Factory for border tags."""
    _name = tag_name  # Capture for closure
    
    class BorderTag:
        name: ClassVar[str] = _name
        category: ClassVar[TagCategory] = TagCategory.BORDER
        is_event: ClassVar[bool] = False
        is_function: ClassVar[bool] = False
        first_wins: ClassVar[bool] = False
        exclusives: ClassVar[frozenset[str]] = frozenset()
        
        @staticmethod
        def parse(raw: str) -> float | None:
            return _parse_float(raw, ge=0)
        
        @staticmethod
        def format(val: float) -> str:
            return f"\\{_name}{val}"
    
    BorderTag.__name__ = f"{tag_name.capitalize()}Tag"
    return BorderTag


def _make_shadow_tag(tag_name: str, allow_negative: bool = False):
    """Factory for shadow tags."""
    _name = tag_name  # Capture for closure
    
    class ShadowTag:
        name: ClassVar[str] = _name
        category: ClassVar[TagCategory] = TagCategory.SHADOW
        is_event: ClassVar[bool] = False
        is_function: ClassVar[bool] = False
        first_wins: ClassVar[bool] = False
        exclusives: ClassVar[frozenset[str]] = frozenset()
        
        @staticmethod
        def parse(raw: str) -> float | None:
            if allow_negative:
                return _parse_float(raw)
            return _parse_float(raw, ge=0)
        
        @staticmethod
        def format(val: float) -> str:
            return f"\\{_name}{val}"
    
    ShadowTag.__name__ = f"{tag_name.capitalize()}Tag"
    return ShadowTag


# Border tags
BordTag = _make_border_tag("bord")
XbordTag = _make_border_tag("xbord")
YbordTag = _make_border_tag("ybord")

# Shadow tags
ShadTag = _make_shadow_tag("shad")
XshadTag = _make_shadow_tag("xshad", allow_negative=True)
YshadTag = _make_shadow_tag("yshad", allow_negative=True)


class BeTag:
    """\\be edge blur tag definition."""
    name: ClassVar[str] = "be"
    category: ClassVar[TagCategory] = TagCategory.BLUR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_int(raw, ge=0)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\be{val}"


class BlurTag:
    """\\blur gaussian blur tag definition."""
    name: ClassVar[str] = "blur"
    category: ClassVar[TagCategory] = TagCategory.BLUR
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\blur{val}"
