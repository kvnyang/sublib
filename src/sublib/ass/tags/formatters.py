# sublib/ass/tags/formatters.py
"""Tag value formatters.

Formatting functions that convert typed objects back to ASS string format.
"""
from __future__ import annotations
from typing import Any

from sublib.ass.tags import (
    Position, Move, RectClip, VectorClip, ClipValue,
    Fade, FadeComplex, Transform,
    Color, Alpha, Alignment, WrapStyle, StyleReset,
)


def format_position(val: Position, tag: str) -> str:
    """Format \\pos(x,y) or \\org(x,y)."""
    return f"\\{tag}({val.x},{val.y})"


def format_move(val: Move) -> str:
    """Format \\move(...)."""
    if val.t1 is not None and val.t2 is not None:
        return f"\\move({val.x1},{val.y1},{val.x2},{val.y2},{val.t1},{val.t2})"
    return f"\\move({val.x1},{val.y1},{val.x2},{val.y2})"


def format_clip(val: ClipValue, tag: str) -> str:
    """Format \\clip(...) or \\iclip(...)."""
    if isinstance(val, RectClip):
        return f"\\{tag}({val.x1},{val.y1},{val.x2},{val.y2})"
    elif isinstance(val, VectorClip):
        if val.scale != 1:
            return f"\\{tag}({val.scale},{val.drawing})"
        return f"\\{tag}({val.drawing})"
    return ""


def format_fade(val: Fade) -> str:
    """Format \\fad(fadein,fadeout)."""
    return f"\\fad({val.fadein},{val.fadeout})"


def format_fade_complex(val: FadeComplex) -> str:
    """Format \\fade(...)."""
    return f"\\fade({val.a1},{val.a2},{val.a3},{val.t1},{val.t2},{val.t3},{val.t4})"


def format_transform(val: Transform) -> str:
    """Format \\t(...)."""
    if val.t1 is None and val.t2 is None and val.accel is None:
        return f"\\t({val.tags})"
    if val.t1 is None and val.t2 is None and val.accel is not None:
        return f"\\t({val.accel},{val.tags})"
    if val.accel is None:
        return f"\\t({val.t1},{val.t2},{val.tags})"
    return f"\\t({val.t1},{val.t2},{val.accel},{val.tags})"


def format_color(val: Color, tag: str) -> str:
    """Format color tag."""
    return f"\\{tag}&H{val.value:06X}&"


def format_alpha(val: Alpha, tag: str) -> str:
    """Format alpha tag."""
    return f"\\{tag}&H{val.value:02X}&"


def format_alignment(val: Alignment, tag: str) -> str:
    """Format alignment tag."""
    return f"\\{tag}{val.value}"


def format_wrap_style(val: WrapStyle) -> str:
    """Format \\q tag."""
    return f"\\q{val.style}"


def format_style_reset(val: StyleReset) -> str:
    """Format \\r or \\r<style>."""
    if val.style_name:
        return f"\\r{val.style_name}"
    return "\\r"


def format_simple(val: Any, tag: str) -> str:
    """Format simple value tags."""
    if isinstance(val, bool):
        return f"\\{tag}{1 if val else 0}"
    return f"\\{tag}{val}"


# ============================================================
# Formatter Dispatch Table
# ============================================================

def _make_pos_formatter(tag: str):
    return lambda val: format_position(val, tag)


def _make_clip_formatter(tag: str):
    return lambda val: format_clip(val, tag)


def _make_color_formatter(tag: str):
    return lambda val: format_color(val, tag)


def _make_alpha_formatter(tag: str):
    return lambda val: format_alpha(val, tag)


def _make_simple_formatter(tag: str):
    return lambda val: format_simple(val, tag)


FORMATTERS: dict[str, callable] = {
    # Position
    "pos": _make_pos_formatter("pos"),
    "org": _make_pos_formatter("org"),
    "move": format_move,
    
    # Clip
    "clip": _make_clip_formatter("clip"),
    "iclip": _make_clip_formatter("iclip"),
    
    # Fade
    "fad": format_fade,
    "fade": format_fade_complex,
    
    # Alignment
    "an": lambda val: format_alignment(val, "an"),
    "a": lambda val: format_alignment(val, "a"),
    "q": format_wrap_style,
    
    # Color
    "c": _make_color_formatter("c"),
    "1c": _make_color_formatter("1c"),
    "2c": _make_color_formatter("2c"),
    "3c": _make_color_formatter("3c"),
    "4c": _make_color_formatter("4c"),
    
    # Alpha
    "alpha": _make_alpha_formatter("alpha"),
    "1a": _make_alpha_formatter("1a"),
    "2a": _make_alpha_formatter("2a"),
    "3a": _make_alpha_formatter("3a"),
    "4a": _make_alpha_formatter("4a"),
    
    # Transform
    "t": format_transform,
    
    # Reset
    "r": format_style_reset,
}

# Add simple formatters for remaining tags
_SIMPLE_TAGS = [
    "fn", "fs", "fscx", "fscy", "fsp", "fe",
    "b", "i", "u", "s",
    "bord", "xbord", "ybord",
    "shad", "xshad", "yshad",
    "be", "blur",
    "frx", "fry", "frz", "fr",
    "fax", "fay",
    "k", "K", "kf", "ko", "kt",
    "p", "pbo",
]

for _tag in _SIMPLE_TAGS:
    if _tag not in FORMATTERS:
        FORMATTERS[_tag] = _make_simple_formatter(_tag)


def format_tag(name: str, value: Any) -> str:
    """Format a tag value using the appropriate formatter.
    
    Args:
        name: Tag name (without backslash)
        value: Typed value to format
        
    Returns:
        Formatted ASS tag string
    """
    formatter = FORMATTERS.get(name)
    if formatter:
        return formatter(value)
    return f"\\{name}{value}"
