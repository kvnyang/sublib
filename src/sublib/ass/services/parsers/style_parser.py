# sublib/ass/services/parsers/style_parser.py
"""Parse Style: lines."""
from __future__ import annotations

from sublib.ass.models import AssStyle
from sublib.ass.types import Color


def parse_style_line(line: str) -> AssStyle | None:
    """Parse a Style: line to AssStyle.
    
    Args:
        line: Style line (e.g., "Style: Default,Arial,20,...")
        
    Returns:
        AssStyle or None if parsing fails
    """
    if not line.startswith('Style:'):
        return None
    
    parts = line[6:].split(',')
    if len(parts) < 23:
        return None
    
    return AssStyle(
        name=parts[0].strip(),
        fontname=parts[1].strip(),
        fontsize=float(parts[2]),
        primary_color=_parse_style_color(parts[3]),
        secondary_color=_parse_style_color(parts[4]),
        outline_color=_parse_style_color(parts[5]),
        back_color=_parse_style_color(parts[6]),
        bold=parts[7].strip() != '0',
        italic=parts[8].strip() != '0',
        underline=parts[9].strip() != '0',
        strikeout=parts[10].strip() != '0',
        scale_x=float(parts[11]),
        scale_y=float(parts[12]),
        spacing=float(parts[13]),
        angle=float(parts[14]),
        border_style=int(parts[15]),
        outline=float(parts[16]),
        shadow=float(parts[17]),
        alignment=int(parts[18]),
        margin_l=int(parts[19]),
        margin_r=int(parts[20]),
        margin_v=int(parts[21]),
        encoding=int(parts[22]),
    )


def _parse_style_color(color_str: str) -> Color:
    """Parse ASS style color string to Color."""
    color_str = color_str.strip().strip('&H').strip('&')
    try:
        value = int(color_str, 16)
        return Color.from_style_int(value)
    except ValueError:
        return Color(bgr=0, alpha=0)
