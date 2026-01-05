# sublib/ass/services/renderers/style_renderer.py
"""Render Style: lines."""
from __future__ import annotations

from sublib.ass.models import AssStyle
from sublib.ass.types import Color


def render_style_line(style: AssStyle) -> str:
    """Render AssStyle to Style: line.
    
    Args:
        style: AssStyle to render
        
    Returns:
        Formatted Style: line
    """
    return (
        f"Style: {style.name},{style.fontname},{style.fontsize},"
        f"{style.primary_color.to_style_str()},"
        f"{style.secondary_color.to_style_str()},"
        f"{style.outline_color.to_style_str()},"
        f"{style.back_color.to_style_str()},"
        f"{int(style.bold)},{int(style.italic)},{int(style.underline)},{int(style.strikeout)},"
        f"{style.scale_x},{style.scale_y},{style.spacing},{style.angle},"
        f"{style.border_style},{style.outline},{style.shadow},"
        f"{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},{style.encoding}"
    )
