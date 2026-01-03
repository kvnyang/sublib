# sublib/ass/tags/registry.py
"""Tag registry built from class-based definitions.

This module collects all tag classes and builds the lookup tables.
"""
from __future__ import annotations
from typing import Any, Type

from sublib.ass.tags.base import TagCategory

# Import all tag classes
from sublib.ass.tags.position import PosTag, MoveTag, OrgTag, Position, Move
from sublib.ass.tags.clip import ClipTag, IClipTag, RectClip, VectorClip, ClipValue
from sublib.ass.tags.fade import FadTag, FadeTag, Fade, FadeComplex
from sublib.ass.tags.color import (
    CTag, C1Tag, C2Tag, C3Tag, C4Tag,
    AlphaTag, A1Tag, A2Tag, A3Tag, A4Tag,
    Color, Alpha,
)
from sublib.ass.tags.layout import AnTag, ATag, QTag, RTag, Alignment, WrapStyle, StyleReset
from sublib.ass.tags.transform import TTag, KTag, KUpperTag, KfTag, KoTag, KtTag, Transform, Karaoke
from sublib.ass.tags.font import (
    FnTag, FsTag, FscxTag, FscyTag, FspTag, FeTag,
    BTag, ITag, UTag, STag,
    FrxTag, FryTag, FrzTag, FrTag,
    FaxTag, FayTag,
    FontScale, Rotation, Shear,
)
from sublib.ass.tags.border import (
    BordTag, XbordTag, YbordTag,
    ShadTag, XshadTag, YshadTag,
    BeTag, BlurTag,
    BorderSize, ShadowDistance, BlurEdge, BlurGaussian,
)
from sublib.ass.tags.drawing import PTag, PboTag, DrawingMode, BaselineOffset


# All tag classes in registration order
_TAG_CLASSES = [
    # Position
    PosTag, MoveTag, OrgTag,
    # Clip
    ClipTag, IClipTag,
    # Fade
    FadTag, FadeTag,
    # Alignment
    AnTag, ATag, QTag,
    # Color
    CTag, C1Tag, C2Tag, C3Tag, C4Tag,
    # Alpha
    AlphaTag, A1Tag, A2Tag, A3Tag, A4Tag,
    # Animation
    TTag,
    # Karaoke
    KTag, KUpperTag, KfTag, KoTag, KtTag,
    # Reset
    RTag,
    # Font
    FnTag, FsTag, FscxTag, FscyTag, FspTag, FeTag,
    # Text style
    BTag, ITag, UTag, STag,
    # Border
    BordTag, XbordTag, YbordTag,
    # Shadow
    ShadTag, XshadTag, YshadTag,
    # Blur
    BeTag, BlurTag,
    # Rotation
    FrxTag, FryTag, FrzTag, FrTag,
    # Shear
    FaxTag, FayTag,
    # Drawing
    PTag, PboTag,
]


# Build registries
TAGS: dict[str, Type] = {cls.name: cls for cls in _TAG_CLASSES}
"""Tag name -> Tag class mapping."""


# Build mutual exclusives from tag classes
MUTUAL_EXCLUSIVES: dict[str, set[str]] = {
    cls.name: set(cls.exclusives) 
    for cls in _TAG_CLASSES 
    if cls.exclusives
}
"""Tag name -> set of mutually exclusive tag names."""


def get_tag(name: str) -> Type | None:
    """Get tag class by name."""
    return TAGS.get(name)


def is_event_tag(name: str) -> bool:
    """Check if tag is event-level."""
    tag = TAGS.get(name)
    return tag.is_event if tag else False


def is_first_wins(name: str) -> bool:
    """Check if first occurrence wins."""
    tag = TAGS.get(name)
    return tag.first_wins if tag else False


def parse_tag(name: str, raw: str) -> Any:
    """Parse a tag value.
    
    Args:
        name: Tag name (without backslash)
        raw: Raw string value
        
    Returns:
        Parsed value, or raw string if tag unknown
    """
    tag = TAGS.get(name)
    if tag:
        return tag.parse(raw)
    return raw


def format_tag(name: str, value: Any) -> str:
    """Format a tag value.
    
    Args:
        name: Tag name (without backslash)
        value: Typed value
        
    Returns:
        Formatted ASS tag string
    """
    tag = TAGS.get(name)
    if tag:
        return tag.format(value)
    return f"\\{name}{value}"
