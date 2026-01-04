# sublib/ass/services/renderers/event_renderer.py
"""Render Dialogue: lines."""
from __future__ import annotations

from sublib.ass.models import AssEvent
from .text_renderer import AssTextRenderer


def render_event_line(event: AssEvent) -> str:
    """Render AssEvent to Dialogue: line.
    
    Args:
        event: AssEvent to render
        
    Returns:
        Formatted Dialogue: line
    """
    text = AssTextRenderer().render(event.text_elements)
    return (
        f"Dialogue: {event.layer},{format_timestamp(event.start_ms)},"
        f"{format_timestamp(event.end_ms)},{event.style},{event.name},"
        f"{event.margin_l},{event.margin_r},{event.margin_v},{event.effect},{text}"
    )


def format_timestamp(ms: int) -> str:
    """Format milliseconds to ASS timestamp.
    
    Format: H:MM:SS.CC (centiseconds)
    """
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    centiseconds = (ms % 1000) // 10
    
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
