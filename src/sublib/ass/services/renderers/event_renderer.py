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
        f"Dialogue: {event.layer},{event.start.to_ass_str()},"
        f"{event.end.to_ass_str()},{event.style},{event.name},"
        f"{event.margin_l},{event.margin_r},{event.margin_v},{event.effect},{text}"
    )
