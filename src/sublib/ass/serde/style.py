"""Parse and render Style: lines."""
from __future__ import annotations

from sublib.ass.models import AssStyle
from sublib.ass.types import AssColor


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
        primary_color=AssColor.from_style_str(parts[3]),
        secondary_color=AssColor.from_style_str(parts[4]),
        outline_color=AssColor.from_style_str(parts[5]),
        back_color=AssColor.from_style_str(parts[6]),
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
