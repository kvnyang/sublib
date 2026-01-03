# sublib/ass/tags/spec.py
"""Tag specification and registry.

This module defines tag specifications in a declarative manner.
All tag metadata is centralized here for easy reference.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Literal
from enum import Enum, auto


class TagCategory(Enum):
    """Categories of ASS override tags."""
    POSITION = auto()    # pos, move, org
    CLIP = auto()        # clip, iclip
    FADE = auto()        # fad, fade
    ALIGNMENT = auto()   # an, a, q
    FONT = auto()        # fn, fs, fscx, fscy, fsp, fe
    TEXT_STYLE = auto()  # b, i, u, s
    BORDER = auto()      # bord, xbord, ybord
    SHADOW = auto()      # shad, xshad, yshad
    BLUR = auto()        # be, blur
    COLOR = auto()       # c, 1c, 2c, 3c, 4c
    ALPHA = auto()       # alpha, 1a, 2a, 3a, 4a
    ROTATION = auto()    # frx, fry, frz, fr
    SHEAR = auto()       # fax, fay
    KARAOKE = auto()     # k, K, kf, ko, kt
    DRAWING = auto()     # p, pbo
    ANIMATION = auto()   # t
    RESET = auto()       # r


@dataclass(frozen=True)
class TagSpec:
    """Specification for an ASS override tag.
    
    All fields are immutable to prevent accidental modification.
    
    Attributes:
        name: Tag name without backslash (e.g., "pos", "1c")
        category: Tag category for grouping
        is_event: True if event-level (applies to whole line)
        is_function: True if uses function syntax \\tag(...)
        first_wins: True if first occurrence wins (else last wins)
        exclusives: Tags that are mutually exclusive with this one
        value_type: Expected Python type of parsed value
    """
    name: str
    category: TagCategory
    is_event: bool = False
    is_function: bool = False
    first_wins: bool = False
    exclusives: frozenset[str] = field(default_factory=frozenset)
    value_type: type | None = None


# ============================================================
# Tag Specifications (Declarative Registry)
# ============================================================

TAGS: dict[str, TagSpec] = {
    # --------------------------------------------------------
    # Position & Movement (event-level, first-wins)
    # --------------------------------------------------------
    "pos": TagSpec(
        name="pos",
        category=TagCategory.POSITION,
        is_event=True,
        is_function=True,
        first_wins=True,
        exclusives=frozenset({"move"}),
    ),
    "move": TagSpec(
        name="move",
        category=TagCategory.POSITION,
        is_event=True,
        is_function=True,
        first_wins=True,
        exclusives=frozenset({"pos"}),
    ),
    "org": TagSpec(
        name="org",
        category=TagCategory.POSITION,
        is_event=True,
        is_function=True,
        first_wins=True,
    ),
    
    # --------------------------------------------------------
    # Clip (event-level)
    # --------------------------------------------------------
    "clip": TagSpec(
        name="clip",
        category=TagCategory.CLIP,
        is_event=True,
        is_function=True,
        exclusives=frozenset({"iclip"}),
    ),
    "iclip": TagSpec(
        name="iclip",
        category=TagCategory.CLIP,
        is_event=True,
        is_function=True,
        exclusives=frozenset({"clip"}),
    ),
    
    # --------------------------------------------------------
    # Fade (event-level)
    # --------------------------------------------------------
    "fad": TagSpec(
        name="fad",
        category=TagCategory.FADE,
        is_event=True,
        is_function=True,
        exclusives=frozenset({"fade"}),
    ),
    "fade": TagSpec(
        name="fade",
        category=TagCategory.FADE,
        is_event=True,
        is_function=True,
        exclusives=frozenset({"fad"}),
    ),
    
    # --------------------------------------------------------
    # Alignment (event-level, first-wins)
    # --------------------------------------------------------
    "an": TagSpec(
        name="an",
        category=TagCategory.ALIGNMENT,
        is_event=True,
        first_wins=True,
    ),
    "a": TagSpec(
        name="a",
        category=TagCategory.ALIGNMENT,
        is_event=True,
        first_wins=True,
    ),
    "q": TagSpec(
        name="q",
        category=TagCategory.ALIGNMENT,
        is_event=True,
    ),
    
    # --------------------------------------------------------
    # Font (inline)
    # --------------------------------------------------------
    "fn": TagSpec(name="fn", category=TagCategory.FONT),
    "fs": TagSpec(name="fs", category=TagCategory.FONT),
    "fscx": TagSpec(name="fscx", category=TagCategory.FONT),
    "fscy": TagSpec(name="fscy", category=TagCategory.FONT),
    "fsp": TagSpec(name="fsp", category=TagCategory.FONT),
    "fe": TagSpec(name="fe", category=TagCategory.FONT),
    
    # --------------------------------------------------------
    # Text Style (inline)
    # --------------------------------------------------------
    "b": TagSpec(name="b", category=TagCategory.TEXT_STYLE),
    "i": TagSpec(name="i", category=TagCategory.TEXT_STYLE),
    "u": TagSpec(name="u", category=TagCategory.TEXT_STYLE),
    "s": TagSpec(name="s", category=TagCategory.TEXT_STYLE),
    
    # --------------------------------------------------------
    # Border (inline)
    # --------------------------------------------------------
    "bord": TagSpec(name="bord", category=TagCategory.BORDER),
    "xbord": TagSpec(name="xbord", category=TagCategory.BORDER),
    "ybord": TagSpec(name="ybord", category=TagCategory.BORDER),
    
    # --------------------------------------------------------
    # Shadow (inline)
    # --------------------------------------------------------
    "shad": TagSpec(name="shad", category=TagCategory.SHADOW),
    "xshad": TagSpec(name="xshad", category=TagCategory.SHADOW),
    "yshad": TagSpec(name="yshad", category=TagCategory.SHADOW),
    
    # --------------------------------------------------------
    # Blur (inline)
    # --------------------------------------------------------
    "be": TagSpec(name="be", category=TagCategory.BLUR),
    "blur": TagSpec(name="blur", category=TagCategory.BLUR),
    
    # --------------------------------------------------------
    # Color (inline)
    # --------------------------------------------------------
    "c": TagSpec(name="c", category=TagCategory.COLOR),
    "1c": TagSpec(name="1c", category=TagCategory.COLOR),
    "2c": TagSpec(name="2c", category=TagCategory.COLOR),
    "3c": TagSpec(name="3c", category=TagCategory.COLOR),
    "4c": TagSpec(name="4c", category=TagCategory.COLOR),
    
    # --------------------------------------------------------
    # Alpha (inline)
    # --------------------------------------------------------
    "alpha": TagSpec(name="alpha", category=TagCategory.ALPHA),
    "1a": TagSpec(name="1a", category=TagCategory.ALPHA),
    "2a": TagSpec(name="2a", category=TagCategory.ALPHA),
    "3a": TagSpec(name="3a", category=TagCategory.ALPHA),
    "4a": TagSpec(name="4a", category=TagCategory.ALPHA),
    
    # --------------------------------------------------------
    # Rotation (inline)
    # --------------------------------------------------------
    "frx": TagSpec(name="frx", category=TagCategory.ROTATION),
    "fry": TagSpec(name="fry", category=TagCategory.ROTATION),
    "frz": TagSpec(name="frz", category=TagCategory.ROTATION),
    "fr": TagSpec(name="fr", category=TagCategory.ROTATION),
    
    # --------------------------------------------------------
    # Shear (inline)
    # --------------------------------------------------------
    "fax": TagSpec(name="fax", category=TagCategory.SHEAR),
    "fay": TagSpec(name="fay", category=TagCategory.SHEAR),
    
    # --------------------------------------------------------
    # Karaoke (inline)
    # --------------------------------------------------------
    "k": TagSpec(name="k", category=TagCategory.KARAOKE),
    "K": TagSpec(name="K", category=TagCategory.KARAOKE),
    "kf": TagSpec(name="kf", category=TagCategory.KARAOKE),
    "ko": TagSpec(name="ko", category=TagCategory.KARAOKE),
    "kt": TagSpec(name="kt", category=TagCategory.KARAOKE),
    
    # --------------------------------------------------------
    # Drawing Mode (inline)
    # --------------------------------------------------------
    "p": TagSpec(name="p", category=TagCategory.DRAWING),
    "pbo": TagSpec(name="pbo", category=TagCategory.DRAWING),
    
    # --------------------------------------------------------
    # Animation (inline, function)
    # --------------------------------------------------------
    "t": TagSpec(
        name="t",
        category=TagCategory.ANIMATION,
        is_function=True,
    ),
    
    # --------------------------------------------------------
    # Style Reset (inline)
    # --------------------------------------------------------
    "r": TagSpec(name="r", category=TagCategory.RESET),
}


# ============================================================
# Computed Views (derived from TAGS)
# ============================================================

def get_spec(name: str) -> TagSpec | None:
    """Get tag specification by name."""
    return TAGS.get(name)


def is_event_tag(name: str) -> bool:
    """Check if tag is event-level."""
    spec = TAGS.get(name)
    return spec.is_event if spec else False


def is_first_wins(name: str) -> bool:
    """Check if first occurrence wins for tag."""
    spec = TAGS.get(name)
    return spec.first_wins if spec else False


def get_exclusives(name: str) -> frozenset[str]:
    """Get mutually exclusive tags for a tag."""
    spec = TAGS.get(name)
    return spec.exclusives if spec else frozenset()


# Backward compatibility: build MUTUAL_EXCLUSIVES from specs
MUTUAL_EXCLUSIVES: dict[str, set[str]] = {
    name: set(spec.exclusives) for name, spec in TAGS.items() if spec.exclusives
}
