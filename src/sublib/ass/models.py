# sublib/ass/models.py
"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
from pathlib import Path

from sublib.ass.ast import (
    AssTextElement, AssPlainText, AssSpecialChar, 
    SpecialCharType, AssTextSegment
)


@dataclass
class AssStyle:
    """ASS style definition.
    
    Represents a style from the [V4+ Styles] section.
    """
    name: str
    fontname: str
    fontsize: float
    primary_color: int  # 0xAABBGGRR format
    secondary_color: int
    outline_color: int
    back_color: int
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikeout: bool = False
    scale_x: float = 100.0
    scale_y: float = 100.0
    spacing: float = 0.0
    angle: float = 0.0
    border_style: int = 1
    outline: float = 2.0
    shadow: float = 0.0
    alignment: int = 2
    margin_l: int = 10
    margin_r: int = 10
    margin_v: int = 10
    encoding: int = 1


@dataclass
class AssEvent:
    """ASS dialogue event.
    
    Represents a Dialogue line from the [Events] section.
    
    The text_elements field is the single source of truth.
    render_text() renders ASS text from it.
    """
    # Timing fields (inherited from Cue)
    start_ms: int = 0
    end_ms: int = 0
    
    # ASS-specific fields
    text_elements: list[AssTextElement] = field(default_factory=list)
    style: str = "Default"
    layer: int = 0
    name: str = ""
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0
    effect: str = ""
    
    def render_text(self) -> str:
        """Render elements back to ASS text format.
        
        Returns:
            The reconstructed ASS text string with override tags.
        """
        from sublib.ass.services import AssTextRenderer
        return AssTextRenderer().render(self.text_elements)
    
    def extract_line_scoped_tags(self) -> dict[str, Any]:
        """Extract effective line-scoped tags.
        
        Delegates to services.extract_line_scoped_tags().
        
        Returns:
            Dict mapping tag name to effective value.
        """
        from sublib.ass.services import extract_line_scoped_tags
        return extract_line_scoped_tags(self.text_elements)
    
    def extract_text_scoped_segments(self) -> list[AssTextSegment]:
        """Extract text segments with their formatting tags.
        
        Delegates to services.extract_text_scoped_segments().
        
        Returns:
            List of AssTextSegment.
        """
        from sublib.ass.services import extract_text_scoped_segments
        return extract_text_scoped_segments(self.text_elements)


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    """
    # Script Info section (arbitrary key-value pairs)
    script_info: dict[str, str] = field(default_factory=dict)
    
    # Styles by name
    styles: dict[str, AssStyle] = field(default_factory=dict)
    
    # Dialogue events
    events: list[AssEvent] = field(default_factory=list)
    
    @classmethod
    def from_file(cls, path: Path | str) -> "AssFile":
        """Load ASS file from path."""
        from sublib.ass.file_parser import parse_ass_file
        return parse_ass_file(Path(path))
    
    def to_string(self) -> str:
        """Render to ASS format string."""
        from sublib.ass.file_renderer import render_ass_file
        return render_ass_file(self)
    
    def save(self, path: Path | str) -> None:
        """Save to file."""
        Path(path).write_text(self.to_string(), encoding='utf-8-sig')
