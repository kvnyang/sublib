# sublib/ass/tags/transform.py
"""Animation and karaoke tag definitions."""
from __future__ import annotations
import re
from typing import Any, ClassVar, Literal

from sublib.ass.tags.base import TagCategory
from sublib.ass.types import Transform, Karaoke


def parse_tags_string(tags_str: str) -> list[tuple[str, Any]]:
    """Parse a tags string into list of (name, value) tuples.
    
    Args:
        tags_str: Raw tags string like "\\fs40\\1c&HFF0000&"
        
    Returns:
        List of (tag_name, parsed_value) tuples
    """
    from sublib.ass.tags.registry import TAGS, parse_tag
    
    result: list[tuple[str, Any]] = []
    tags_str = tags_str.strip()
    
    if not tags_str:
        return result
    
    # Pattern to match tag names and their values
    # Handles both function tags like \t(...) and simple tags like \fs40
    # Sort by length descending to match longer names first (e.g., "fscx" before "fs")
    tag_names = sorted(TAGS.keys(), key=len, reverse=True)
    tag_pattern = "|".join(re.escape(name) for name in tag_names)
    
    # Pattern: \tagname followed by either (...) for function or value until next \ or end
    pattern = re.compile(
        rf'\\({tag_pattern})(?:\(([^)]*)\)|([^\\]*))',
        re.IGNORECASE
    )
    
    for match in pattern.finditer(tags_str):
        tag_name = match.group(1)
        func_value = match.group(2)  # Value inside parentheses
        simple_value = match.group(3)  # Value after tag name
        
        raw_value = func_value if func_value is not None else (simple_value or "")
        raw_value = raw_value.strip()
        
        # Parse the value
        parsed = parse_tag(tag_name, raw_value)
        if parsed is not None:
            result.append((tag_name, parsed))
    
    return result


class TTag:
    """\\t(...) animation tag definition."""
    name: ClassVar[str] = "t"
    category: ClassVar[TagCategory] = TagCategory.ANIMATION
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Transform | None:
        raw = raw.strip()
        
        t1: int | None = None
        t2: int | None = None
        accel: float | None = None
        tags_str: str = ""
        
        # Form: (tags)
        if not any(c.isdigit() for c in raw.split(",")[0] if c not in "\\"):
            tags_str = raw
        else:
            parts = raw.split(",", 3)
            
            # Form: (accel, tags)
            if len(parts) == 2:
                try:
                    accel = float(parts[0])
                    tags_str = parts[1].strip()
                except ValueError:
                    tags_str = raw
            
            # Form: (t1, t2, tags)
            elif len(parts) == 3:
                try:
                    t1 = int(parts[0])
                    t2 = int(parts[1])
                    tags_str = parts[2].strip()
                except ValueError:
                    return None
            
            # Form: (t1, t2, accel, tags)
            elif len(parts) == 4:
                try:
                    t1 = int(parts[0])
                    t2 = int(parts[1])
                    accel = float(parts[2])
                    tags_str = parts[3].strip()
                except ValueError:
                    return None
        
        # Parse the tags string
        parsed_tags = parse_tags_string(tags_str)
        
        return Transform(tags=parsed_tags, t1=t1, t2=t2, accel=accel)
    
    @staticmethod
    def format(val: Transform) -> str:
        raw_tags = val.to_raw_tags()
        if val.t1 is None and val.t2 is None and val.accel is None:
            return f"\\t({raw_tags})"
        if val.t1 is None and val.t2 is None and val.accel is not None:
            return f"\\t({val.accel},{raw_tags})"
        if val.accel is None:
            return f"\\t({val.t1},{val.t2},{raw_tags})"
        return f"\\t({val.t1},{val.t2},{val.accel},{raw_tags})"


def _parse_karaoke(raw: str) -> int | None:
    try:
        val = int(raw)
        return val if val >= 0 else None
    except ValueError:
        return None


# ============================================================
# Karaoke Tags
# ============================================================

class KTag:
    """\\k karaoke tag definition."""
    name: ClassVar[str] = "k"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\k{val}"


class KUpperTag:
    """\\K karaoke tag definition."""
    name: ClassVar[str] = "K"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\K{val}"


class KfTag:
    """\\kf karaoke tag definition."""
    name: ClassVar[str] = "kf"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\kf{val}"


class KoTag:
    """\\ko karaoke tag definition."""
    name: ClassVar[str] = "ko"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\ko{val}"


class KtTag:
    """\\kt karaoke tag definition."""
    name: ClassVar[str] = "kt"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\kt{val}"
