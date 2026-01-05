# sublib/ass/serde/file.py
"""Parse and render complete ASS files."""
from __future__ import annotations

from sublib.ass.models import AssFile
from .text import AssTextParser
from .style import parse_style_line, render_style_line
from .event import parse_event_line, render_event_line
from .script_info import parse_script_info, render_script_info


def parse_ass_string(content: str) -> AssFile:
    """Parse ASS content from string.
    
    Returns an AssFile with all events having their text parsed into elements.
    """
    text_parser = AssTextParser()
    
    ass_file = AssFile()
    lines = content.splitlines()
    current_section = None
    line_number = 0
    script_info_lines: list[str] = []
    
    for line in lines:
        line_number += 1
        line = line.strip()
        
        if not line or line.startswith(';'):
            continue
        
        # Section header
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            continue
        
        if current_section == 'script info':
            script_info_lines.append(line)
        
        elif current_section in ('v4 styles', 'v4+ styles'):
            if line.startswith('Style:'):
                style = parse_style_line(line)
                if style:
                    ass_file.styles[style.name] = style
        
        elif current_section == 'events':
            if line.startswith('Dialogue:'):
                event = parse_event_line(line, text_parser, line_number)
                if event:
                    ass_file.events.append(event)
    
    ass_file.script_info = parse_script_info(script_info_lines)
    
    return ass_file


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
