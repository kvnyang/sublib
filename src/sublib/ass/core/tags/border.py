"""Border, shadow, and blur tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.core.tags.base import TagCategory, _format_float


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

class BordTag:
    """\\bord tag definition."""
    name: ClassVar[str] = "bord"
    category: ClassVar[TagCategory] = TagCategory.BORDER
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\bord{_format_float(val)}"


class XbordTag:
    """\\xbord tag definition."""
    name: ClassVar[str] = "xbord"
    category: ClassVar[TagCategory] = TagCategory.BORDER
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\xbord{_format_float(val)}"


class YbordTag:
    """\\ybord tag definition."""
    name: ClassVar[str] = "ybord"
    category: ClassVar[TagCategory] = TagCategory.BORDER
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\ybord{_format_float(val)}"


# ============================================================
# Shadow Tags
# ============================================================

class ShadTag:
    """\\shad tag definition."""
    name: ClassVar[str] = "shad"
    category: ClassVar[TagCategory] = TagCategory.SHADOW
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\shad{_format_float(val)}"


class XshadTag:
    """\\xshad tag definition (can be negative)."""
    name: ClassVar[str] = "xshad"
    category: ClassVar[TagCategory] = TagCategory.SHADOW
    param_pattern: ClassVar[str | None] = r'-?\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\xshad{_format_float(val)}"


class YshadTag:
    """\\yshad tag definition (can be negative)."""
    name: ClassVar[str] = "yshad"
    category: ClassVar[TagCategory] = TagCategory.SHADOW
    param_pattern: ClassVar[str | None] = r'-?\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\yshad{_format_float(val)}"


# ============================================================
# Blur Tags
# ============================================================

class BeTag:
    """\\be edge blur tag definition."""
    name: ClassVar[str] = "be"
    category: ClassVar[TagCategory] = TagCategory.BLUR
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
        return f"\\be{val}"


class BlurTag:
    """\\blur gaussian blur tag definition."""
    name: ClassVar[str] = "blur"
    category: ClassVar[TagCategory] = TagCategory.BLUR
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, ge=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\blur{_format_float(val)}"
