# asslib/tag_registry.py
"""ASS override tag registry.

Defines specifications for all supported ASS override tags including:
- Parsing and formatting functions
- Event-level vs inline classification
- First-win vs last-win behavior
- Mutual exclusion rules
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from functools import partial
import re

from sublib.ass.tag_values import (
    Position, Move, RectClip, VectorClip, ClipValue,
    Fade, FadeComplex, Transform,
    Color, Alpha, Alignment, WrapStyle, StyleReset,
    BorderSize, ShadowDistance, BlurEdge, BlurGaussian,
    FontScale, Rotation, Shear, DrawingMode, BaselineOffset,
)


@dataclass
class TagSpec:
    """Specification for an ASS override tag.
    
    Attributes:
        name: Tag name without backslash
        parser: Function to parse tag value string -> typed value
        formatter: Function to format typed value -> string
        is_event: True if this is an event-level tag
        is_function: True if tag uses function syntax: \\tag(args)
        first_wins: True if first occurrence wins, False if last wins
    """
    name: str
    parser: Callable[[str], Any]
    formatter: Callable[[Any], str]
    is_event: bool = False
    is_function: bool = False
    first_wins: bool = False


# Mutual exclusion rules: if tag A is present, tag B is removed
MUTUAL_EXCLUSIVES: dict[str, set[str]] = {
    "pos": {"move"},
    "move": {"pos"},
    "clip": {"iclip"},
    "iclip": {"clip"},
    "fad": {"fade"},
    "fade": {"fad"},
}


# The global tag registry
TAG_REGISTRY: dict[str, TagSpec] = {}


def get_tag_spec(name: str) -> TagSpec | None:
    """Get the spec for a tag by name."""
    return TAG_REGISTRY.get(name)


def is_event_tag(name: str) -> bool:
    """Check if a tag is event-level."""
    spec = get_tag_spec(name)
    return spec.is_event if spec else False


def get_first_wins(name: str) -> bool:
    """Check if first occurrence wins for a tag."""
    spec = get_tag_spec(name)
    return spec.first_wins if spec else False


# ============================================================
# Parsers
# ============================================================

def _parse_position(raw: str) -> Position | None:
    """Parse \\pos(x,y) or \\org(x,y)."""
    parts = raw.split(",")
    if len(parts) != 2:
        return None
    try:
        return Position(x=float(parts[0]), y=float(parts[1]))
    except ValueError:
        return None


def _parse_move(raw: str) -> Move | None:
    """Parse \\move(x1,y1,x2,y2) or \\move(x1,y1,x2,y2,t1,t2)."""
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


def _parse_clip(raw: str) -> ClipValue | None:
    """Parse \\clip(...) or \\iclip(...) - rectangle or vector."""
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


def _parse_fade(raw: str) -> Fade | None:
    """Parse \\fad(fadein,fadeout)."""
    parts = raw.split(",")
    if len(parts) != 2:
        return None
    try:
        return Fade(fadein=int(parts[0]), fadeout=int(parts[1]))
    except ValueError:
        return None


def _parse_fade_complex(raw: str) -> FadeComplex | None:
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


def _parse_transform(raw: str) -> Transform | None:
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


def _parse_color(raw: str) -> Color | None:
    """Parse \\c&HBBGGRR& format."""
    raw = raw.strip().strip("&H").strip("&")
    try:
        value = int(raw, 16)
        return Color(value=value)
    except ValueError:
        return None


def _parse_alpha(raw: str) -> Alpha | None:
    """Parse \\alpha&HAA& format."""
    raw = raw.strip().strip("&H").strip("&")
    try:
        value = int(raw, 16)
        return Alpha(value=value)
    except ValueError:
        return None


def _parse_alignment(raw: str) -> Alignment | None:
    """Parse \\an<1-9>."""
    try:
        val = int(raw)
        if 1 <= val <= 9:
            return Alignment(value=val)
    except ValueError:
        pass
    return None


def _parse_alignment_legacy(raw: str) -> Alignment | None:
    """Parse \\a<pos> (legacy format)."""
    try:
        val = int(raw)
        # Legacy values: 1,2,3 (bottom), 5,6,7 (top), 9,10,11 (middle)
        if val in {1, 2, 3, 5, 6, 7, 9, 10, 11}:
            return Alignment(value=val, legacy=True)
    except ValueError:
        pass
    return None


def _parse_wrap_style(raw: str) -> WrapStyle | None:
    """Parse \\q<0-3>."""
    try:
        val = int(raw)
        if val in {0, 1, 2, 3}:
            return WrapStyle(style=val)
    except ValueError:
        pass
    return None


def _parse_style_reset(raw: str) -> StyleReset:
    """Parse \\r or \\r<style>."""
    raw = raw.strip()
    if raw:
        return StyleReset(style_name=raw)
    return StyleReset(style_name=None)


def _parse_plain(raw: str, allow_empty: bool = False) -> str | None:
    """Parse plain string value."""
    if not raw and not allow_empty:
        return None
    return raw


def _parse_number(raw: str, typ=int, ge=None, gt=None, le=None, lt=None) -> int | float | None:
    """Parse numeric value with optional constraints."""
    try:
        val = typ(raw)
        if ge is not None and val < ge:
            return None
        if gt is not None and val <= gt:
            return None
        if le is not None and val > le:
            return None
        if lt is not None and val >= lt:
            return None
        return val
    except (ValueError, TypeError):
        return None


def _parse_bool(raw: str) -> bool | None:
    """Parse boolean (0/1)."""
    if raw == "1":
        return True
    elif raw == "0":
        return False
    return None


def _parse_bold(raw: str) -> int | bool | None:
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
# Formatters
# ============================================================

def _format_position(val: Position, tag_name: str) -> str:
    return f"\\{tag_name}({val.x},{val.y})"


def _format_move(val: Move, tag_name: str = "move") -> str:
    if val.t1 is not None and val.t2 is not None:
        return f"\\{tag_name}({val.x1},{val.y1},{val.x2},{val.y2},{val.t1},{val.t2})"
    return f"\\{tag_name}({val.x1},{val.y1},{val.x2},{val.y2})"


def _format_clip(val: ClipValue, tag_name: str) -> str:
    if isinstance(val, RectClip):
        return f"\\{tag_name}({val.x1},{val.y1},{val.x2},{val.y2})"
    elif isinstance(val, VectorClip):
        if val.scale != 1:
            return f"\\{tag_name}({val.scale},{val.drawing})"
        return f"\\{tag_name}({val.drawing})"
    return ""


def _format_fade(val: Fade, tag_name: str = "fad") -> str:
    return f"\\{tag_name}({val.fadein},{val.fadeout})"


def _format_fade_complex(val: FadeComplex, tag_name: str = "fade") -> str:
    return f"\\{tag_name}({val.a1},{val.a2},{val.a3},{val.t1},{val.t2},{val.t3},{val.t4})"


def _format_transform(val: Transform, tag_name: str = "t") -> str:
    if val.t1 is None and val.t2 is None and val.accel is None:
        return f"\\{tag_name}({val.tags})"
    if val.t1 is None and val.t2 is None and val.accel is not None:
        return f"\\{tag_name}({val.accel},{val.tags})"
    if val.accel is None:
        return f"\\{tag_name}({val.t1},{val.t2},{val.tags})"
    return f"\\{tag_name}({val.t1},{val.t2},{val.accel},{val.tags})"


def _format_color(val: Color, tag_name: str) -> str:
    return f"\\{tag_name}&H{val.value:06X}&"


def _format_alpha(val: Alpha, tag_name: str) -> str:
    return f"\\{tag_name}&H{val.value:02X}&"


def _format_alignment(val: Alignment, tag_name: str) -> str:
    return f"\\{tag_name}{val.value}"


def _format_wrap_style(val: WrapStyle, tag_name: str) -> str:
    return f"\\{tag_name}{val.style}"


def _format_style_reset(val: StyleReset, tag_name: str = "r") -> str:
    if val.style_name:
        return f"\\{tag_name}{val.style_name}"
    return f"\\{tag_name}"


def _format_simple(val: Any, tag_name: str) -> str:
    if isinstance(val, bool):
        return f"\\{tag_name}{1 if val else 0}"
    return f"\\{tag_name}{val}"


# ============================================================
# Registration
# ============================================================

def _reg(
    name: str,
    parser: Callable,
    formatter: Callable,
    is_event: bool = False,
    is_function: bool = False,
    first_wins: bool = False,
) -> None:
    """Register a tag in the registry."""
    TAG_REGISTRY[name] = TagSpec(
        name=name,
        parser=parser,
        formatter=partial(formatter, tag_name=name),
        is_event=is_event,
        is_function=is_function,
        first_wins=first_wins,
    )


# ============================================================
# Register all tags
# ============================================================

# Positioning (event-level, first-wins per ASS spec)
_reg("pos", _parse_position, _format_position, is_event=True, is_function=True, first_wins=True)
_reg("move", _parse_move, _format_move, is_event=True, is_function=True, first_wins=True)
_reg("org", _parse_position, _format_position, is_event=True, is_function=True, first_wins=True)

# Clip (event-level)
_reg("clip", _parse_clip, _format_clip, is_event=True, is_function=True)
_reg("iclip", _parse_clip, _format_clip, is_event=True, is_function=True)

# Fade (event-level)
_reg("fad", _parse_fade, _format_fade, is_event=True, is_function=True)
_reg("fade", _parse_fade_complex, _format_fade_complex, is_event=True, is_function=True)

# Alignment (event-level, first-wins)
_reg("an", _parse_alignment, _format_alignment, is_event=True, first_wins=True)
_reg("a", _parse_alignment_legacy, _format_alignment, is_event=True, first_wins=True)

# Wrap style (event-level)
_reg("q", _parse_wrap_style, _format_wrap_style, is_event=True)

# Font and text style (inline)
_reg("fn", _parse_plain, _format_simple)  # font name
_reg("fs", partial(_parse_number, typ=float, gt=0), _format_simple)  # font size
_reg("fscx", partial(_parse_number, typ=float, gt=0), _format_simple)  # scale X
_reg("fscy", partial(_parse_number, typ=float, gt=0), _format_simple)  # scale Y
_reg("fsp", partial(_parse_number, typ=float), _format_simple)  # letter spacing
_reg("fe", partial(_parse_number, typ=int, ge=0), _format_simple)  # font encoding

# Bold/Italic/Underline/Strikeout (inline)
_reg("b", _parse_bold, _format_simple)  # bold (0, 1, or weight)
_reg("i", _parse_bool, _format_simple)  # italic
_reg("u", _parse_bool, _format_simple)  # underline
_reg("s", _parse_bool, _format_simple)  # strikeout

# Border and shadow (inline)
_reg("bord", partial(_parse_number, typ=float, ge=0), _format_simple)
_reg("xbord", partial(_parse_number, typ=float, ge=0), _format_simple)
_reg("ybord", partial(_parse_number, typ=float, ge=0), _format_simple)
_reg("shad", partial(_parse_number, typ=float, ge=0), _format_simple)
_reg("xshad", partial(_parse_number, typ=float), _format_simple)  # can be negative
_reg("yshad", partial(_parse_number, typ=float), _format_simple)  # can be negative

# Blur (inline)
_reg("be", partial(_parse_number, typ=int, ge=0), _format_simple)  # edge blur
_reg("blur", partial(_parse_number, typ=float, ge=0), _format_simple)  # gaussian blur

# Colors (inline)
_reg("c", _parse_color, _format_color)  # alias for \1c
_reg("1c", _parse_color, _format_color)  # primary
_reg("2c", _parse_color, _format_color)  # secondary
_reg("3c", _parse_color, _format_color)  # outline
_reg("4c", _parse_color, _format_color)  # shadow

# Alpha (inline)
_reg("alpha", _parse_alpha, _format_alpha)  # all
_reg("1a", _parse_alpha, _format_alpha)  # primary
_reg("2a", _parse_alpha, _format_alpha)  # secondary
_reg("3a", _parse_alpha, _format_alpha)  # outline
_reg("4a", _parse_alpha, _format_alpha)  # shadow

# Rotation (inline)
_reg("frx", partial(_parse_number, typ=float), _format_simple)  # X axis
_reg("fry", partial(_parse_number, typ=float), _format_simple)  # Y axis
_reg("frz", partial(_parse_number, typ=float), _format_simple)  # Z axis
_reg("fr", partial(_parse_number, typ=float), _format_simple)  # Z axis (alias)

# Shearing (inline)
_reg("fax", partial(_parse_number, typ=float), _format_simple)
_reg("fay", partial(_parse_number, typ=float), _format_simple)

# Karaoke (inline)
_reg("k", partial(_parse_number, typ=int, ge=0), _format_simple)
_reg("K", partial(_parse_number, typ=int, ge=0), _format_simple)
_reg("kf", partial(_parse_number, typ=int, ge=0), _format_simple)
_reg("ko", partial(_parse_number, typ=int, ge=0), _format_simple)
_reg("kt", partial(_parse_number, typ=int, ge=0), _format_simple)

# Drawing mode (inline)
_reg("p", partial(_parse_number, typ=int, ge=0), _format_simple)
_reg("pbo", partial(_parse_number, typ=int), _format_simple)

# Animation
_reg("t", _parse_transform, _format_transform, is_function=True)

# Style reset (inline)
_reg("r", _parse_style_reset, _format_style_reset)
