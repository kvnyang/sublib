# sublib/ass/tags/transform.py
"""Animation and karaoke tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Literal

from sublib.ass.tags.base import TagCategory


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


def _make_karaoke_tag(tag_name: str):
    """Factory for karaoke tag classes."""
    _name = tag_name  # Capture for closure
    
    class KaraokeTag:
        name: ClassVar[str] = _name
        category: ClassVar[TagCategory] = TagCategory.KARAOKE
        is_event: ClassVar[bool] = False
        is_function: ClassVar[bool] = False
        first_wins: ClassVar[bool] = False
        exclusives: ClassVar[frozenset[str]] = frozenset()
        
        @staticmethod
        def parse(raw: str) -> int | None:
            try:
                val = int(raw)
                return val if val >= 0 else None
            except ValueError:
                return None
        
        @staticmethod
        def format(val: int) -> str:
            return f"\\{_name}{val}"
    
    KaraokeTag.__name__ = f"{tag_name.upper()}Tag"
    return KaraokeTag


KTag = _make_karaoke_tag("k")
KUpperTag = _make_karaoke_tag("K")
KfTag = _make_karaoke_tag("kf")
KoTag = _make_karaoke_tag("ko")
KtTag = _make_karaoke_tag("kt")
