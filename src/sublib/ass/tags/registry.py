# sublib/ass/tags/registry.py
"""Tag registry - unified access interface for all ASS override tags.

This module:
1. Defines TagCategory and TagDefinition
2. Imports all tag classes from their modules
3. Builds TAGS dict with explicit registration
4. Provides query functions (get_tag, parse_tag, format_tag)
"""
from __future__ import annotations
from typing import Any, Type, ClassVar, Protocol, runtime_checkable
from enum import Enum, auto


class TagCategory(Enum):
    """Categories of ASS override tags."""
    POSITION = auto()
    CLIP = auto()
    FADE = auto()
    ALIGNMENT = auto()
    FONT = auto()
    TEXT_STYLE = auto()
    BORDER = auto()
    SHADOW = auto()
    BLUR = auto()
    COLOR = auto()
    ALPHA = auto()
    ROTATION = auto()
    SHEAR = auto()
    KARAOKE = auto()
    DRAWING = auto()
    ANIMATION = auto()
    RESET = auto()


@runtime_checkable
class TagDefinition(Protocol):
    """Protocol for tag definitions.
    
    Each tag class must implement these class variables and methods.
    """
    name: ClassVar[str]
    category: ClassVar[TagCategory]
    param_pattern: ClassVar[str | None]
    is_line_scoped: ClassVar[bool]
    is_function: ClassVar[bool]
    first_wins: ClassVar[bool]
    exclusives: ClassVar[frozenset[str]]
    
    @staticmethod
    def parse(raw: str) -> Any:
        """Parse raw string value to typed value."""
        ...
    
    @staticmethod
    def format(value: Any) -> str:
        """Format typed value to ASS string."""
        ...


# ============================================================
# Import tag classes from their modules
# ============================================================

from sublib.ass.tags.position import PosTag, MoveTag, OrgTag
from sublib.ass.tags.clip import ClipTag, IClipTag
from sublib.ass.tags.fade import FadTag, FadeTag
from sublib.ass.tags.layout import AnTag, ATag, QTag, RTag
from sublib.ass.tags.drawing import PTag, PboTag
from sublib.ass.tags.color import (
    CTag, C1Tag, C2Tag, C3Tag, C4Tag,
    AlphaTag, A1Tag, A2Tag, A3Tag, A4Tag,
)
from sublib.ass.tags.border import (
    BordTag, XbordTag, YbordTag,
    ShadTag, XshadTag, YshadTag,
    BeTag, BlurTag,
)
from sublib.ass.tags.transform import (
    TTag, KTag, KUpperTag, KfTag, KoTag, KtTag,
)
from sublib.ass.tags.font import (
    FnTag, FsTag, FscxTag, FscyTag, FspTag, FeTag,
    BTag, ITag, UTag, STag,
    FrTag, FrxTag, FryTag, FrzTag,
    FaxTag, FayTag,
)


# ============================================================
# Explicit Tag Registry
# ============================================================

TAGS: dict[str, Type] = {
    # Position
    "pos": PosTag,
    "move": MoveTag,
    "org": OrgTag,
    # Clip
    "clip": ClipTag,
    "iclip": IClipTag,
    # Fade
    "fad": FadTag,
    "fade": FadeTag,
    # Layout
    "an": AnTag,
    "a": ATag,
    "q": QTag,
    "r": RTag,
    # Drawing
    "p": PTag,
    "pbo": PboTag,
    # Color
    "c": CTag,
    "1c": C1Tag,
    "2c": C2Tag,
    "3c": C3Tag,
    "4c": C4Tag,
    # Alpha
    "alpha": AlphaTag,
    "1a": A1Tag,
    "2a": A2Tag,
    "3a": A3Tag,
    "4a": A4Tag,
    # Border
    "bord": BordTag,
    "xbord": XbordTag,
    "ybord": YbordTag,
    # Shadow
    "shad": ShadTag,
    "xshad": XshadTag,
    "yshad": YshadTag,
    # Blur
    "be": BeTag,
    "blur": BlurTag,
    # Font
    "fn": FnTag,
    "fs": FsTag,
    "fscx": FscxTag,
    "fscy": FscyTag,
    "fsp": FspTag,
    "fe": FeTag,
    # Text Style
    "b": BTag,
    "i": ITag,
    "u": UTag,
    "s": STag,
    # Rotation
    "fr": FrTag,
    "frx": FrxTag,
    "fry": FryTag,
    "frz": FrzTag,
    # Shear
    "fax": FaxTag,
    "fay": FayTag,
    # Animation
    "t": TTag,
    # Karaoke
    "k": KTag,
    "K": KUpperTag,
    "kf": KfTag,
    "ko": KoTag,
    "kt": KtTag,
}
"""Tag name -> Tag class mapping."""


# Build mutual exclusives from tag classes
MUTUAL_EXCLUSIVES: dict[str, set[str]] = {
    name: set(cls.exclusives) 
    for name, cls in TAGS.items() 
    if cls.exclusives
}
"""Tag name -> set of mutually exclusive tag names."""


# ============================================================
# Query Functions
# ============================================================

def get_tag(name: str) -> Type | None:
    """Get tag class by name."""
    return TAGS.get(name)


def is_line_scoped_tag(name: str) -> bool:
    """Check if tag is line-scoped (event-level)."""
    tag = TAGS.get(name)
    return tag.is_line_scoped if tag else False


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
