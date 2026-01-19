"""Parse and render Dialogue: lines."""
from __future__ import annotations

from sublib.ass.models import AssEvent
from sublib.ass.types import Timestamp
from .text import AssTextParser, AssTextRenderer


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
        start=Timestamp.from_ass_str(parts[1]),
        end=Timestamp.from_ass_str(parts[2]),
        text_elements=text_parser.parse(text, line_number=line_number),
        style=parts[3].strip(),
        layer=int(parts[0]),
        name=parts[4].strip(),
        margin_l=int(parts[5]),
        margin_r=int(parts[6]),
        margin_v=int(parts[7]),
        effect=parts[8].strip(),
    )


def render_event_line(event: AssEvent) -> str:
    """Render AssEvent to Dialogue: line.
    
    Args:
        event: AssEvent to render
        
    Returns:
        Formatted Dialogue: line
    """
    text = AssTextRenderer().render(event.text_elements)
    return (
        f"Dialogue: {event.layer},{event.start.to_ass_str()},"
        f"{event.end.to_ass_str()},{event.style},{event.name},"
        f"{event.margin_l},{event.margin_r},{event.margin_v},{event.effect},{text}"
    )
