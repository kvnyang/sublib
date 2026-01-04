# sublib/ass/services/renderers/style_renderer.py
"""Render Style: lines."""
from __future__ import annotations

from sublib.ass.models import AssStyle


def render_style_line(style: AssStyle) -> str:
    """Render AssStyle to Style: line.
    
    Args:
        style: AssStyle to render
        
    Returns:
        Formatted Style: line
    """
    return (
        f"Style: {style.name},{style.fontname},{style.fontsize},"
        f"{_format_ass_color(style.primary_color)},"
        f"{_format_ass_color(style.secondary_color)},"
        f"{_format_ass_color(style.outline_color)},"
        f"{_format_ass_color(style.back_color)},"
        f"{int(style.bold)},{int(style.italic)},{int(style.underline)},{int(style.strikeout)},"
        f"{style.scale_x},{style.scale_y},{style.spacing},{style.angle},"
        f"{style.border_style},{style.outline},{style.shadow},"
        f"{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},{style.encoding}"
    )


def _format_ass_color(color: int) -> str:
    """Format color int to ASS string."""
    return f"&H{color:08X}&"
