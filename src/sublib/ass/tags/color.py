"""Color and alpha tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.tags.base import TagCategory
from sublib.ass.types import AssColor, AssAlpha


def _parse_color(raw: str) -> AssColor | None:
    """Parse color tag value to AssColor."""
    try:
        return AssColor.from_tag_str(raw)
    except ValueError:
        return None


def _parse_alpha(raw: str) -> AssAlpha | None:
    raw = raw.strip().strip("&H").strip("&")
    try:
        return AssAlpha(value=int(raw, 16))
    except ValueError:
        return None


# ============================================================
# Color Tags
# ============================================================

class CTag:
    """\\c (alias for \\1c) tag definition."""
    name: ClassVar[str] = "c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssColor | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: AssColor) -> str:
        return f"\\c{val.to_tag_str()}"


class C1Tag:
    """\\1c primary color tag definition."""
    name: ClassVar[str] = "1c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssColor | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: AssColor) -> str:
        return f"\\1c{val.to_tag_str()}"


class C2Tag:
    """\\2c secondary color tag definition."""
    name: ClassVar[str] = "2c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssColor | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: AssColor) -> str:
        return f"\\2c{val.to_tag_str()}"


class C3Tag:
    """\\3c outline color tag definition."""
    name: ClassVar[str] = "3c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssColor | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: AssColor) -> str:
        return f"\\3c{val.to_tag_str()}"


class C4Tag:
    """\\4c shadow color tag definition."""
    name: ClassVar[str] = "4c"
    category: ClassVar[TagCategory] = TagCategory.COLOR
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssColor | None:
        return _parse_color(raw)
    
    @staticmethod
    def format(val: AssColor) -> str:
        return f"\\4c{val.to_tag_str()}"


# ============================================================
# Alpha Tags
# ============================================================

class AlphaTag:
    """\\alpha (all colors) tag definition."""
    name: ClassVar[str] = "alpha"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: AssAlpha) -> str:
        return f"\\alpha&H{val.value:02X}&"


class A1Tag:
    """\\1a primary alpha tag definition."""
    name: ClassVar[str] = "1a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: AssAlpha) -> str:
        return f"\\1a&H{val.value:02X}&"


class A2Tag:
    """\\2a secondary alpha tag definition."""
    name: ClassVar[str] = "2a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: AssAlpha) -> str:
        return f"\\2a&H{val.value:02X}&"


class A3Tag:
    """\\3a border alpha tag definition."""
    name: ClassVar[str] = "3a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: AssAlpha) -> str:
        return f"\\3a&H{val.value:02X}&"


class A4Tag:
    """\\4a shadow alpha tag definition."""
    name: ClassVar[str] = "4a"
    category: ClassVar[TagCategory] = TagCategory.ALPHA
    param_pattern: ClassVar[str | None] = r'&H[0-9A-Fa-f]+&'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> AssAlpha | None:
        return _parse_alpha(raw)
    
    @staticmethod
    def format(val: AssAlpha) -> str:
        return f"\\4a&H{val.value:02X}&"
