# asslib/tag_values.py
"""Strongly-typed value classes for ASS override tags.

These dataclasses provide type-safe representations for tag values,
enabling IDE autocompletion and type checking in downstream projects.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


# ============================================================
# Position and Movement
# ============================================================

@dataclass
class Position:
    """Value for \\pos(x,y) and \\org(x,y) tags.
    
    Coordinates are in script resolution pixels.
    """
    x: float
    y: float


@dataclass
class Move:
    """Value for \\move(x1,y1,x2,y2) or \\move(x1,y1,x2,y2,t1,t2) tag.
    
    Coordinates are in script resolution pixels.
    Times (t1, t2) are in milliseconds relative to event start.
    If t1 and t2 are None, movement spans the entire event duration.
    """
    x1: float
    y1: float
    x2: float
    y2: float
    t1: int | None = None  # start time (ms)
    t2: int | None = None  # end time (ms)


# ============================================================
# Clip
# ============================================================

@dataclass
class RectClip:
    """Value for \\clip(x1,y1,x2,y2) or \\iclip(x1,y1,x2,y2).
    
    Rectangle clip in script resolution pixels.
    """
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class VectorClip:
    """Value for \\clip(drawing) or \\clip(scale,drawing).
    
    Vector drawing clip using ASS drawing commands.
    """
    drawing: str
    scale: int = 1  # Drawing scale (1 = normal, 2 = half resolution, etc.)


# Union type for clip values
ClipValue = RectClip | VectorClip


# ============================================================
# Fade Effects
# ============================================================

@dataclass
class Fade:
    """Value for \\fad(fadein,fadeout) tag.
    
    Times are in milliseconds.
    """
    fadein: int   # fade-in duration (ms)
    fadeout: int  # fade-out duration (ms)


@dataclass
class FadeComplex:
    """Value for \\fade(a1,a2,a3,t1,t2,t3,t4) tag.
    
    Complex fade with three alpha values and four time points.
    Alpha values are 0-255 (0=visible, 255=invisible).
    Times are in milliseconds relative to event start.
    """
    a1: int  # Alpha before t1
    a2: int  # Alpha between t2 and t3
    a3: int  # Alpha after t4
    t1: int  # Start of first transition
    t2: int  # End of first transition
    t3: int  # Start of second transition
    t4: int  # End of second transition


# ============================================================
# Animation
# ============================================================

@dataclass
class Transform:
    """Value for \\t(...) animated transform tag.
    
    Contains timing, acceleration, and nested style modifiers.
    """
    tags: str  # The style modifiers (may contain nested override tags)
    t1: int | None = None    # Start time (ms), None = event start
    t2: int | None = None    # End time (ms), None = event end
    accel: float | None = None  # Acceleration (1=linear, <1=fast start, >1=slow start)


# ============================================================
# Karaoke
# ============================================================

@dataclass
class Karaoke:
    """Value for \\k, \\K, \\kf, \\ko, \\kt tags.
    
    Duration is in centiseconds (1/100 of a second).
    """
    duration: int  # Syllable duration in centiseconds
    type: Literal["k", "K", "kf", "ko", "kt"] = "k"


# ============================================================
# Color and Alpha
# ============================================================

@dataclass
class Color:
    """Value for \\c, \\1c, \\2c, \\3c, \\4c tags.
    
    Color in BGR format (ASS native format).
    """
    value: int  # 0xBBGGRR format
    
    @property
    def blue(self) -> int:
        return (self.value >> 16) & 0xFF
    
    @property
    def green(self) -> int:
        return (self.value >> 8) & 0xFF
    
    @property
    def red(self) -> int:
        return self.value & 0xFF
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        """Create from RGB values (0-255)."""
        return cls((b << 16) | (g << 8) | r)
    
    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create from hex string like 'BBGGRR' or '&HBBGGRR&'."""
        hex_str = hex_str.strip("&H").strip("&")
        return cls(int(hex_str, 16))


@dataclass
class Alpha:
    """Value for \\alpha, \\1a, \\2a, \\3a, \\4a tags.
    
    Alpha value where 0=fully visible, 255=fully transparent.
    """
    value: int  # 0x00-0xFF
    
    @property
    def opacity(self) -> float:
        """Get opacity as 0.0-1.0 (1.0 = fully visible)."""
        return 1.0 - (self.value / 255.0)


# ============================================================
# Font and Text Style
# ============================================================

@dataclass
class FontScale:
    """Value for \\fscx and \\fscy tags.
    
    Scale as percentage (100 = normal size).
    """
    value: float  # percentage, e.g., 100.0 for normal


@dataclass
class Rotation:
    """Value for \\frx, \\fry, \\frz (or \\fr) tags.
    
    Rotation angle in degrees.
    """
    angle: float  # degrees (can be negative or >360)


@dataclass
class Shear:
    """Value for \\fax and \\fay tags.
    
    Shearing factor (typically -2 to 2).
    """
    factor: float


# ============================================================
# Border and Shadow
# ============================================================

@dataclass
class BorderSize:
    """Value for \\bord, \\xbord, \\ybord tags.
    
    Border width in pixels (can be float).
    """
    value: float  # pixels


@dataclass  
class ShadowDistance:
    """Value for \\shad, \\xshad, \\yshad tags.
    
    Shadow offset in pixels (can be negative for xshad/yshad).
    """
    value: float  # pixels


# ============================================================
# Blur
# ============================================================

@dataclass
class BlurEdge:
    """Value for \\be tag.
    
    Edge blur strength (integer repetitions).
    """
    strength: int


@dataclass
class BlurGaussian:
    """Value for \\blur tag.
    
    Gaussian blur strength (can be float).
    """
    strength: float


# ============================================================
# Drawing Mode
# ============================================================

@dataclass
class DrawingMode:
    """Value for \\p tag.
    
    Scale is 2^(value-1). E.g., \\p1 = 1x, \\p2 = 2x, \\p4 = 8x.
    \\p0 disables drawing mode.
    """
    scale: int  # 0 = off, 1+ = on with scale


@dataclass
class BaselineOffset:
    """Value for \\pbo tag.
    
    Y offset for drawing baseline in pixels.
    """
    offset: int  # pixels (can be negative)


# ============================================================
# Alignment
# ============================================================

@dataclass
class Alignment:
    """Value for \\an or \\a (legacy) tags.
    
    Uses numpad-style positions (1-9):
        7 8 9  (top)
        4 5 6  (middle)  
        1 2 3  (bottom)
    """
    value: int  # 1-9 for \\an
    legacy: bool = False  # True if parsed from \\a tag


# ============================================================
# Wrap Style
# ============================================================

@dataclass
class WrapStyle:
    """Value for \\q tag.
    
    0 = Smart wrap (top line wider)
    1 = End-of-line wrap
    2 = No word wrap
    3 = Smart wrap (bottom line wider)
    """
    style: Literal[0, 1, 2, 3]


# ============================================================
# Style Reset
# ============================================================

@dataclass
class StyleReset:
    """Value for \\r or \\r<style> tag.
    
    If style_name is None, resets to the line's default style.
    If style_name is set, resets to that named style.
    """
    style_name: str | None = None
