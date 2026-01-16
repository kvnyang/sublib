# sublib/ass/serde/file.py
"""Parse and render complete ASS files."""
from __future__ import annotations
import logging
from typing import Any

from sublib.ass.models import AssFile
from .text import AssTextParser
from .style import parse_style_line, render_style_line
from .event import parse_event_line, render_event_line
from .script_info import parse_script_info_line, render_script_info_line

logger = logging.getLogger(__name__)


def parse_ass_string(content: str) -> AssFile:
    """Parse ASS content from string.
    
    Returns an AssFile with all events having their text parsed into elements.
    Script info fields are stored in insertion order with typed values.
    """
    text_parser = AssTextParser()
    
    ass_file = AssFile()
    lines = content.splitlines()
    current_section = None
    line_number = 0
    
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
            result = parse_script_info_line(line)
            if result:
                key, value = result
                if key in ass_file.script_info:
                    logger.warning(f"Duplicate Script Info key: {key}")
                ass_file.script_info[key] = value  # last-wins, preserves first occurrence order
        
        elif current_section in ('v4 styles', 'v4+ styles'):
            if line.startswith('Style:'):
                style = parse_style_line(line)
                if style:
                    if style.name in ass_file.styles:
                        logger.warning(f"Duplicate style name: {style.name}")
                    ass_file.styles[style.name] = style
        
        elif current_section == 'events':
            if line.startswith('Dialogue:'):
                event = parse_event_line(line, text_parser, line_number)
                if event:
                    ass_file.events.append(event)
    
    # Validate style references
    _validate_style_references(ass_file)
    
    return ass_file


def _validate_style_references(ass_file: AssFile) -> None:
    """Check that all style references are defined."""
    defined_styles = set(ass_file.styles.keys())
    
    for i, event in enumerate(ass_file.events):
        # Check event.style
        if event.style not in defined_styles:
            ass_file.warnings.append(
                f"Line {i+1}: event style '{event.style}' not defined"
            )
        
        # Check \r references in segments
        result = event.extract_all()
        for seg in result.segments:
            r_style = seg.block_tags.get("r")
            if r_style and r_style not in defined_styles:
                ass_file.warnings.append(
                    f"Line {i+1}: \\r style '{r_style}' not defined"
                )


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
    for key, value in ass_file.script_info.items():
        lines.append(render_script_info_line(key, value))
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
