"""Font style tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.core.tags.base import TagCategory, _format_float


def _parse_float(raw: str, *, gt: float | None = None, ge: float | None = None) -> float | None:
    try:
        val = float(raw)
        if gt is not None and val <= gt:
            return None
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


def _parse_bool(raw: str) -> bool | None:
    if raw == "1":
        return True
    elif raw == "0":
        return False
    return None


def _parse_bold(raw: str) -> int | bool | None:
    try:
        val = int(raw)
        if val == 0:
            return False
        if val == 1:
            return True
        if 100 <= val <= 900 and val % 100 == 0:
            return val
    except ValueError:
        pass
    return None


# ============================================================
# Font Tags
# ============================================================

class FnTag:
    """\\fn font name tag definition."""
    name: ClassVar[str] = "fn"
    category: ClassVar[TagCategory] = TagCategory.FONT
    param_pattern: ClassVar[str | None] = r'[^\\]+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> str:
        return raw
    
    @staticmethod
    def format(val: str) -> str:
        return f"\\fn{val}"


class FsTag:
    """\\fs font size tag definition."""
    name: ClassVar[str] = "fs"
    category: ClassVar[TagCategory] = TagCategory.FONT
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, gt=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\fs{_format_float(val)}"


class FscxTag:
    """\\fscx font scale X tag definition."""
    name: ClassVar[str] = "fscx"
    category: ClassVar[TagCategory] = TagCategory.FONT
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, gt=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\fscx{_format_float(val)}"


class FscyTag:
    """\\fscy font scale Y tag definition."""
    name: ClassVar[str] = "fscy"
    category: ClassVar[TagCategory] = TagCategory.FONT
    param_pattern: ClassVar[str | None] = r'\d+(?:\.\d+)?'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw, gt=0)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\fscy{_format_float(val)}"


class FspTag:
    """\\fsp letter spacing tag definition."""
    name: ClassVar[str] = "fsp"
    category: ClassVar[TagCategory] = TagCategory.FONT
    param_pattern: ClassVar[str | None] = r'-?\d+(?:\.\d+)?'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> float | None:
        return _parse_float(raw)
    
    @staticmethod
    def format(val: float) -> str:
        return f"\\fsp{_format_float(val)}"


class FeTag:
    """\\fe font encoding tag definition."""
    name: ClassVar[str] = "fe"
    category: ClassVar[TagCategory] = TagCategory.FONT
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
        return f"\\fe{val}"


# ============================================================
# Text Style Tags
# ============================================================

class BTag:
    """\\b bold tag definition."""
    name: ClassVar[str] = "b"
    category: ClassVar[TagCategory] = TagCategory.TEXT_STYLE
    param_pattern: ClassVar[str | None] = r'(?:[01]|[1-9]00)'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | bool | None:
        return _parse_bold(raw)
    
    @staticmethod
    def format(val: int | bool) -> str:
        if isinstance(val, bool):
            return f"\\b{1 if val else 0}"
        return f"\\b{val}"


class ITag:
    """\\i italic tag definition."""
    name: ClassVar[str] = "i"
    category: ClassVar[TagCategory] = TagCategory.TEXT_STYLE
    param_pattern: ClassVar[str | None] = r'[01]'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> bool | None:
        return _parse_bool(raw)
    
    @staticmethod
    def format(val: bool) -> str:
        return f"\\i{1 if val else 0}"


class UTag:
    """\\u underline tag definition."""
    name: ClassVar[str] = "u"
    category: ClassVar[TagCategory] = TagCategory.TEXT_STYLE
    param_pattern: ClassVar[str | None] = r'[01]'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> bool | None:
        return _parse_bool(raw)
    
    @staticmethod
    def format(val: bool) -> str:
        return f"\\u{1 if val else 0}"


class STag:
    """\\s strikeout tag definition."""
    name: ClassVar[str] = "s"
    category: ClassVar[TagCategory] = TagCategory.TEXT_STYLE
    param_pattern: ClassVar[str | None] = r'[01]'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> bool | None:
        return _parse_bool(raw)
    
    @staticmethod
    def format(val: bool) -> str:
        return f"\\s{1 if val else 0}"


# ============================================================
# Rotation Tags
# ============================================================

class FrxTag:
    """\\frx X-axis rotation tag definition."""
    name: ClassVar[str] = "frx"
    category: ClassVar[TagCategory] = TagCategory.ROTATION
    param_pattern: ClassVar[str | None] = r'-?\d+(?:\.\d+)?'
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
        return f"\\frx{_format_float(val)}"


class FryTag:
    """\\fry Y-axis rotation tag definition."""
    name: ClassVar[str] = "fry"
    category: ClassVar[TagCategory] = TagCategory.ROTATION
    param_pattern: ClassVar[str | None] = r'-?\d+(?:\.\d+)?'
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
        return f"\\fry{_format_float(val)}"


class FrzTag:
    """\\frz Z-axis rotation tag definition."""
    name: ClassVar[str] = "frz"
    category: ClassVar[TagCategory] = TagCategory.ROTATION
    param_pattern: ClassVar[str | None] = r'-?\d+(?:\.\d+)?'
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
        return f"\\frz{_format_float(val)}"


class FrTag:
    """\\fr Z-axis rotation alias tag definition."""
    name: ClassVar[str] = "fr"
    category: ClassVar[TagCategory] = TagCategory.ROTATION
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
        return f"\\fr{_format_float(val)}"


# ============================================================
# Shear Tags
# ============================================================

class FaxTag:
    """\\fax X shear tag definition."""
    name: ClassVar[str] = "fax"
    category: ClassVar[TagCategory] = TagCategory.SHEAR
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
        return f"\\fax{_format_float(val)}"


class FayTag:
    """\\fay Y shear tag definition."""
    name: ClassVar[str] = "fay"
    category: ClassVar[TagCategory] = TagCategory.SHEAR
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
        return f"\\fay{_format_float(val)}"
