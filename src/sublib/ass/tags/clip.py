# sublib/ass/tags/clip.py
"""Clip tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags.base import TagCategory, tag


@dataclass
class RectClip:
    """Rectangle clip value."""
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class VectorClip:
    """Vector drawing clip value."""
    drawing: str
    scale: int = 1


ClipValue = RectClip | VectorClip


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


@tag
class ClipTag:
    """\\clip(...) tag definition."""
    name: ClassVar[str] = "clip"
    category: ClassVar[TagCategory] = TagCategory.CLIP
    is_event: ClassVar[bool] = True
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


@tag
class IClipTag:
    """\\iclip(...) tag definition."""
    name: ClassVar[str] = "iclip"
    category: ClassVar[TagCategory] = TagCategory.CLIP
    is_event: ClassVar[bool] = True
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
