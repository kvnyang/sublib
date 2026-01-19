"""Clip tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.tags.base import TagCategory
from sublib.ass.types import RectClip, VectorClip, ClipValue


def _parse_clip(raw: str) -> ClipValue | None:
    """Parse clip value (shared by ClipTag and IClipTag)."""
    raw = raw.strip()
    if not raw:
        return None
    
    parts = [x.strip() for x in raw.split(",")]
    
    # Rectangle: 4 integers
    if len(parts) == 4:
        try:
            if all(p.lstrip("-").isdigit() for p in parts):
                return RectClip(
                    x1=int(parts[0]), y1=int(parts[1]),
                    x2=int(parts[2]), y2=int(parts[3])
                )
        except ValueError:
            pass
    
    # Vector with scale
    if len(parts) >= 2 and parts[0].lstrip("-").isdigit():
        try:
            scale = int(parts[0])
            drawing = ",".join(parts[1:]).strip()
            return VectorClip(drawing=drawing, scale=scale)
        except ValueError:
            pass
    
    # Vector without scale
    return VectorClip(drawing=raw, scale=1)


class ClipTag:
    """\\clip(...) tag definition."""
    name: ClassVar[str] = "clip"
    category: ClassVar[TagCategory] = TagCategory.CLIP
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset({"iclip"})
    
    @staticmethod
    def parse(raw: str) -> ClipValue | None:
        return _parse_clip(raw)
    
    @staticmethod
    def format(val: ClipValue) -> str:
        if isinstance(val, RectClip):
            return f"\\clip({val.x1},{val.y1},{val.x2},{val.y2})"
        elif isinstance(val, VectorClip):
            if val.scale != 1:
                return f"\\clip({val.scale},{val.drawing})"
            return f"\\clip({val.drawing})"
        return ""


class IClipTag:
    """\\iclip(...) tag definition."""
    name: ClassVar[str] = "iclip"
    category: ClassVar[TagCategory] = TagCategory.CLIP
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset({"clip"})
    
    @staticmethod
    def parse(raw: str) -> ClipValue | None:
        return _parse_clip(raw)
    
    @staticmethod
    def format(val: ClipValue) -> str:
        if isinstance(val, RectClip):
            return f"\\iclip({val.x1},{val.y1},{val.x2},{val.y2})"
        elif isinstance(val, VectorClip):
            if val.scale != 1:
                return f"\\iclip({val.scale},{val.drawing})"
            return f"\\iclip({val.drawing})"
        return ""
