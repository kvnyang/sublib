# sublib/ass/services/parsers/event_parser.py
"""Parse Dialogue: lines."""
from __future__ import annotations

from sublib.ass.models import AssEvent
from .text_parser import AssTextParser


def parse_event_line(
    line: str,
    text_parser: AssTextParser | None = None,
    line_number: int = 0
) -> AssEvent | None:
    """Parse a Dialogue: line to AssEvent.
    
    Args:
        line: Dialogue line (e.g., "Dialogue: 0,0:00:00.00,...")
        text_parser: Parser for text field, creates one if not provided
        line_number: Source line number for error reporting
        
    Returns:
        AssEvent or None if parsing fails
    """
    if not line.startswith('Dialogue:'):
        return None
    
    # Split into 10 parts (last part is text, may contain commas)
    parts = line[9:].split(',', 9)
    if len(parts) < 10:
        return None
    
    if text_parser is None:
        text_parser = AssTextParser()
    
    text = parts[9]
    
    return AssEvent(
        start_ms=parse_timestamp(parts[1]),
        end_ms=parse_timestamp(parts[2]),
        text_elements=text_parser.parse(text, line_number=line_number),
        style=parts[3].strip(),
        layer=int(parts[0]),
        name=parts[4].strip(),
        margin_l=int(parts[5]),
        margin_r=int(parts[6]),
        margin_v=int(parts[7]),
        effect=parts[8].strip(),
    )


def parse_timestamp(ts: str) -> int:
    """Parse ASS timestamp to milliseconds.
    
    Format: H:MM:SS.CC (centiseconds)
    """
    ts = ts.strip()
    parts = ts.split(':')
    if len(parts) != 3:
        return 0
    
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    centiseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + centiseconds * 10
