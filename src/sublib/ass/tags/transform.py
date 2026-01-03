# sublib/ass/tags/transform.py
"""Animation and karaoke tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Literal

from sublib.ass.tags.base import TagCategory, tag


@dataclass
class Transform:
    """Value for \\t(...) animated transform tag."""
    tags: str
    t1: int | None = None
    t2: int | None = None
    accel: float | None = None


@dataclass
class Karaoke:
    """Value for karaoke tags."""
    duration: int
    type: Literal["k", "K", "kf", "ko", "kt"] = "k"


@tag
class TTag:
    """\\t(...) animation tag definition."""
    name: ClassVar[str] = "t"
    category: ClassVar[TagCategory] = TagCategory.ANIMATION
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Transform | None:
        raw = raw.strip()
        
        # Form: (tags)
        if not any(c.isdigit() for c in raw.split(",")[0] if c not in "\\"):
            return Transform(tags=raw)
        
        parts = raw.split(",", 3)
        
        # Form: (accel, tags)
        if len(parts) == 2:
            try:
                accel = float(parts[0])
                return Transform(tags=parts[1].strip(), accel=accel)
            except ValueError:
                return Transform(tags=raw)
        
        # Form: (t1, t2, tags)
        if len(parts) == 3:
            try:
                return Transform(
                    t1=int(parts[0]), t2=int(parts[1]),
                    tags=parts[2].strip()
                )
            except ValueError:
                return None
        
        # Form: (t1, t2, accel, tags)
        if len(parts) == 4:
            try:
                return Transform(
                    t1=int(parts[0]), t2=int(parts[1]),
                    accel=float(parts[2]), tags=parts[3].strip()
                )
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def format(val: Transform) -> str:
        if val.t1 is None and val.t2 is None and val.accel is None:
            return f"\\t({val.tags})"
        if val.t1 is None and val.t2 is None and val.accel is not None:
            return f"\\t({val.accel},{val.tags})"
        if val.accel is None:
            return f"\\t({val.t1},{val.t2},{val.tags})"
        return f"\\t({val.t1},{val.t2},{val.accel},{val.tags})"


def _parse_karaoke(raw: str) -> int | None:
    try:
        val = int(raw)
        return val if val >= 0 else None
    except ValueError:
        return None


# ============================================================
# Karaoke Tags
# ============================================================

@tag
class KTag:
    """\\k karaoke tag definition."""
    name: ClassVar[str] = "k"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\k{val}"


@tag
class KUpperTag:
    """\\K karaoke tag definition."""
    name: ClassVar[str] = "K"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\K{val}"


@tag
class KfTag:
    """\\kf karaoke tag definition."""
    name: ClassVar[str] = "kf"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\kf{val}"


@tag
class KoTag:
    """\\ko karaoke tag definition."""
    name: ClassVar[str] = "ko"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\ko{val}"


@tag
class KtTag:
    """\\kt karaoke tag definition."""
    name: ClassVar[str] = "kt"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    is_event: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\kt{val}"
