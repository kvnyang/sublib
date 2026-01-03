# sublib/ass/tags/border.py
"""Border, shadow, and blur tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags.base import TagCategory, tag


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


# ============================================================
# Border Tags
# ============================================================

@tag
class BordTag:
    """\\bord tag definition."""
    name: ClassVar[str] = "bord"
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
        return f"\\bord{val}"


@tag
class XbordTag:
    """\\xbord tag definition."""
    name: ClassVar[str] = "xbord"
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
        return f"\\xbord{val}"


@tag
class YbordTag:
    """\\ybord tag definition."""
    name: ClassVar[str] = "ybord"
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
        return f"\\ybord{val}"


# ============================================================
# Shadow Tags
# ============================================================

@tag
class ShadTag:
    """\\shad tag definition."""
    name: ClassVar[str] = "shad"
    category: ClassVar[TagCategory] = TagCategory.SHADOW
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\shad{val}"


@tag
class XshadTag:
    """\\xshad tag definition (can be negative)."""
    name: ClassVar[str] = "xshad"
    category: ClassVar[TagCategory] = TagCategory.SHADOW
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\xshad{val}"


@tag
class YshadTag:
    """\\yshad tag definition (can be negative)."""
    name: ClassVar[str] = "yshad"
    category: ClassVar[TagCategory] = TagCategory.SHADOW
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\yshad{val}"


# ============================================================
# Blur Tags
# ============================================================

@tag
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


@tag
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
