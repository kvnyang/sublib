# sublib/ass/tags/parsers.py
"""Tag value parsers.

Parsing functions that convert raw string values to typed objects.
Separated from specs for single responsibility.
"""
from __future__ import annotations
from typing import Any

from sublib.ass.tags import (
    Position, Move, RectClip, VectorClip, ClipValue,
    Fade, FadeComplex, Transform,
    Color, Alpha, Alignment, WrapStyle, StyleReset,
)


def parse_position(raw: str) -> Position | None:
    """Parse \\pos(x,y) or \\org(x,y)."""
    parts = raw.split(",")
    if len(parts) != 2:
        return None
    try:
        return Position(x=float(parts[0]), y=float(parts[1]))
    except ValueError:
        return None


def parse_move(raw: str) -> Move | None:
    """Parse \\move(x1,y1,x2,y2[,t1,t2])."""
    parts = raw.split(",")
    if len(parts) == 4:
        try:
            return Move(
                x1=float(parts[0]), y1=float(parts[1]),
                x2=float(parts[2]), y2=float(parts[3])
            )
        except ValueError:
            return None
    elif len(parts) == 6:
        try:
            return Move(
                x1=float(parts[0]), y1=float(parts[1]),
                x2=float(parts[2]), y2=float(parts[3]),
                t1=int(parts[4]), t2=int(parts[5])
            )
        except ValueError:
            return None
    return None


def parse_clip(raw: str) -> ClipValue | None:
    """Parse \\clip(...) or \\iclip(...)."""
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
    
    # Vector with scale: scale,drawing
    if len(parts) >= 2 and parts[0].lstrip("-").isdigit():
        try:
            scale = int(parts[0])
            drawing = ",".join(parts[1:]).strip()
            return VectorClip(drawing=drawing, scale=scale)
        except ValueError:
            pass
    
    # Vector without scale
    return VectorClip(drawing=raw, scale=1)


def parse_fade(raw: str) -> Fade | None:
    """Parse \\fad(fadein,fadeout)."""
    parts = raw.split(",")
    if len(parts) != 2:
        return None
    try:
        return Fade(fadein=int(parts[0]), fadeout=int(parts[1]))
    except ValueError:
        return None


def parse_fade_complex(raw: str) -> FadeComplex | None:
    """Parse \\fade(a1,a2,a3,t1,t2,t3,t4)."""
    parts = raw.split(",")
    if len(parts) != 7:
        return None
    try:
        return FadeComplex(
            a1=int(parts[0]), a2=int(parts[1]), a3=int(parts[2]),
            t1=int(parts[3]), t2=int(parts[4]), t3=int(parts[5]), t4=int(parts[6])
        )
    except ValueError:
        return None


def parse_transform(raw: str) -> Transform | None:
    """Parse \\t(...) with various forms."""
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


def parse_color(raw: str) -> Color | None:
    """Parse \\c&HBBGGRR& format."""
    raw = raw.strip().strip("&H").strip("&")
    try:
        value = int(raw, 16)
        return Color(value=value)
    except ValueError:
        return None


def parse_alpha(raw: str) -> Alpha | None:
    """Parse \\alpha&HAA& format."""
    raw = raw.strip().strip("&H").strip("&")
    try:
        value = int(raw, 16)
        return Alpha(value=value)
    except ValueError:
        return None


def parse_alignment(raw: str) -> Alignment | None:
    """Parse \\an<1-9>."""
    try:
        val = int(raw)
        if 1 <= val <= 9:
            return Alignment(value=val)
    except ValueError:
        pass
    return None


def parse_alignment_legacy(raw: str) -> Alignment | None:
    """Parse \\a<pos> (legacy format)."""
    try:
        val = int(raw)
        if val in {1, 2, 3, 5, 6, 7, 9, 10, 11}:
            return Alignment(value=val, legacy=True)
    except ValueError:
        pass
    return None


def parse_wrap_style(raw: str) -> WrapStyle | None:
    """Parse \\q<0-3>."""
    try:
        val = int(raw)
        if val in {0, 1, 2, 3}:
            return WrapStyle(style=val)
    except ValueError:
        pass
    return None


def parse_style_reset(raw: str) -> StyleReset:
    """Parse \\r or \\r<style>."""
    raw = raw.strip()
    return StyleReset(style_name=raw if raw else None)


def parse_int(raw: str, *, ge: int | None = None, gt: int | None = None) -> int | None:
    """Parse integer with optional constraints."""
    try:
        val = int(raw)
        if ge is not None and val < ge:
            return None
        if gt is not None and val <= gt:
            return None
        return val
    except ValueError:
        return None


def parse_float(raw: str, *, ge: float | None = None, gt: float | None = None) -> float | None:
    """Parse float with optional constraints."""
    try:
        val = float(raw)
        if ge is not None and val < ge:
            return None
        if gt is not None and val <= gt:
            return None
        return val
    except ValueError:
        return None


def parse_bool(raw: str) -> bool | None:
    """Parse boolean (0/1)."""
    if raw == "1":
        return True
    elif raw == "0":
        return False
    return None


def parse_bold(raw: str) -> int | bool | None:
    """Parse \\b - can be 0, 1, or weight (100-900)."""
    try:
        val = int(raw)
        if val == 0:
            return False
        if val == 1:
            return True
        if 100 <= val <= 900 and val % 100 == 0:
            return val
    except ValueError:
        pass
    return None


# ============================================================
# Parser Dispatch Table
# ============================================================

PARSERS: dict[str, callable] = {
    # Position
    "pos": parse_position,
    "org": parse_position,
    "move": parse_move,
    
    # Clip
    "clip": parse_clip,
    "iclip": parse_clip,
    
    # Fade
    "fad": parse_fade,
    "fade": parse_fade_complex,
    
    # Alignment
    "an": parse_alignment,
    "a": parse_alignment_legacy,
    "q": parse_wrap_style,
    
    # Color
    "c": parse_color,
    "1c": parse_color,
    "2c": parse_color,
    "3c": parse_color,
    "4c": parse_color,
    
    # Alpha
    "alpha": parse_alpha,
    "1a": parse_alpha,
    "2a": parse_alpha,
    "3a": parse_alpha,
    "4a": parse_alpha,
    
    # Transform
    "t": parse_transform,
    
    # Reset
    "r": parse_style_reset,
    
    # Text style
    "b": parse_bold,
    "i": parse_bool,
    "u": parse_bool,
    "s": parse_bool,
    
    # Font
    "fn": lambda raw: raw,
    "fs": lambda raw: parse_float(raw, gt=0),
    "fscx": lambda raw: parse_float(raw, gt=0),
    "fscy": lambda raw: parse_float(raw, gt=0),
    "fsp": parse_float,
    "fe": lambda raw: parse_int(raw, ge=0),
    
    # Border
    "bord": lambda raw: parse_float(raw, ge=0),
    "xbord": lambda raw: parse_float(raw, ge=0),
    "ybord": lambda raw: parse_float(raw, ge=0),
    
    # Shadow
    "shad": lambda raw: parse_float(raw, ge=0),
    "xshad": parse_float,
    "yshad": parse_float,
    
    # Blur
    "be": lambda raw: parse_int(raw, ge=0),
    "blur": lambda raw: parse_float(raw, ge=0),
    
    # Rotation
    "frx": parse_float,
    "fry": parse_float,
    "frz": parse_float,
    "fr": parse_float,
    
    # Shear
    "fax": parse_float,
    "fay": parse_float,
    
    # Karaoke
    "k": lambda raw: parse_int(raw, ge=0),
    "K": lambda raw: parse_int(raw, ge=0),
    "kf": lambda raw: parse_int(raw, ge=0),
    "ko": lambda raw: parse_int(raw, ge=0),
    "kt": lambda raw: parse_int(raw, ge=0),
    
    # Drawing
    "p": lambda raw: parse_int(raw, ge=0),
    "pbo": parse_int,
}


def parse_tag(name: str, raw: str) -> Any:
    """Parse a tag value using the appropriate parser.
    
    Args:
        name: Tag name (without backslash)
        raw: Raw string value (without tag name)
        
    Returns:
        Parsed value, or None if parsing failed
    """
    parser = PARSERS.get(name)
    if parser:
        return parser(raw)
    return raw  # Return raw for unknown tags
