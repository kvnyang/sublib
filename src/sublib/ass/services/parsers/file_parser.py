# sublib/ass/services/parsers/file_parser.py
"""Parse ASS file content."""
from __future__ import annotations

from sublib.ass.models import AssFile
from .text_parser import AssTextParser
from .style_parser import parse_style_line
from .event_parser import parse_event_line


def parse_ass_string(content: str) -> AssFile:
    """Parse ASS content from string.
    
    Returns an AssFile with all events having their text parsed into elements.
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
            if ':' in line:
                key, _, value = line.partition(':')
                ass_file.script_info[key.strip()] = value.strip()
        
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
    
    return ass_file
