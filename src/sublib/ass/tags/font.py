# sublib/ass/tags/font.py
"""Font style tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags.base import TagCategory


@dataclass
class FontScale:
    """Font scale value."""
    value: float


@dataclass
class Rotation:
    """Rotation angle value."""
    angle: float


@dataclass
class Shear:
    """Shearing factor value."""
    factor: float


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


def _make_simple_tag(tag_name: str, parser, tag_category: TagCategory = TagCategory.FONT):
    """Factory for simple inline tags."""
    _name = tag_name  # Capture for closure
    _category = tag_category
    
    class SimpleTag:
        name: ClassVar[str] = _name
        category: ClassVar[TagCategory] = _category
        is_event: ClassVar[bool] = False
        is_function: ClassVar[bool] = False
        first_wins: ClassVar[bool] = False
        exclusives: ClassVar[frozenset[str]] = frozenset()
        
        @staticmethod
        def parse(raw: str):
            return parser(raw)
        
        @staticmethod
        def format(val) -> str:
            if isinstance(val, bool):
                return f"\\{_name}{1 if val else 0}"
            return f"\\{_name}{val}"
    
    SimpleTag.__name__ = f"{tag_name.capitalize()}Tag"
    return SimpleTag


# Font tags
FnTag = _make_simple_tag("fn", lambda raw: raw)
FsTag = _make_simple_tag("fs", lambda raw: _parse_float(raw, gt=0))
FscxTag = _make_simple_tag("fscx", lambda raw: _parse_float(raw, gt=0))
FscyTag = _make_simple_tag("fscy", lambda raw: _parse_float(raw, gt=0))
FspTag = _make_simple_tag("fsp", _parse_float)
FeTag = _make_simple_tag("fe", lambda raw: _parse_int(raw, ge=0))

# Text style tags
BTag = _make_simple_tag("b", _parse_bold, TagCategory.TEXT_STYLE)
ITag = _make_simple_tag("i", _parse_bool, TagCategory.TEXT_STYLE)
UTag = _make_simple_tag("u", _parse_bool, TagCategory.TEXT_STYLE)
STag = _make_simple_tag("s", _parse_bool, TagCategory.TEXT_STYLE)

# Rotation tags
FrxTag = _make_simple_tag("frx", _parse_float, TagCategory.ROTATION)
FryTag = _make_simple_tag("fry", _parse_float, TagCategory.ROTATION)
FrzTag = _make_simple_tag("frz", _parse_float, TagCategory.ROTATION)
FrTag = _make_simple_tag("fr", _parse_float, TagCategory.ROTATION)

# Shear tags
FaxTag = _make_simple_tag("fax", _parse_float, TagCategory.SHEAR)
FayTag = _make_simple_tag("fay", _parse_float, TagCategory.SHEAR)
