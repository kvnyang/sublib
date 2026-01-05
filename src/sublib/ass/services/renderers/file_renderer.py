# sublib/ass/services/renderers/file_renderer.py
"""Render ASS file content."""
from __future__ import annotations

from sublib.ass.models import AssFile
from .style_renderer import render_style_line
from .event_renderer import render_event_line
from .script_info_renderer import render_script_info


def render_ass_string(ass_file: AssFile) -> str:
    """Render AssFile to ASS format string.
    
    Args:
        ass_file: AssFile to render
        
    Returns:
        Complete ASS file content as string
    """
    lines = []
    
    # Script Info
    lines.append('[Script Info]')
    lines.extend(render_script_info(ass_file.script_info))
    lines.append('')
    
    # Styles
    lines.append('[V4+ Styles]')
    lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, '
                 'OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, '
                 'ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, '
                 'Alignment, MarginL, MarginR, MarginV, Encoding')
    for style in ass_file.styles.values():
        lines.append(render_style_line(style))
    lines.append('')
    
    # Events
    lines.append('[Events]')
    lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
    for event in ass_file.events:
        lines.append(render_event_line(event))
    
    return '\n'.join(lines)
