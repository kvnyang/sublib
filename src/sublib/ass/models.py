# sublib/ass/models.py
"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from sublib.ass.ast import AssTextElement
from sublib.ass.types import Color, Timestamp


@dataclass
class AssStyle:
    """ASS style definition.
    
    Represents a style from the [V4+ Styles] section.
    """
    name: str
    fontname: str
    fontsize: float
    primary_color: Color
    secondary_color: Color
    outline_color: Color
    back_color: Color
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
    Pure data class - use services for parsing and rendering:
    
        from sublib.ass.services import AssTextParser, AssTextRenderer
        
        # Parse text to elements
        elements = AssTextParser().parse(text)
        event = AssEvent(text_elements=elements, start=Timestamp(cs=0), end=Timestamp(cs=100))
        
        # Render elements to text
        text = AssTextRenderer().render(event.text_elements)
        
        # Extract tags or segments
        from sublib.ass.services import extract_line_scoped_tags
        tags = extract_line_scoped_tags(event.text_elements)
    """
    # Timing fields
    start: Timestamp = field(default_factory=Timestamp)
    end: Timestamp = field(default_factory=Timestamp)
    
    # ASS-specific fields
    text_elements: list[AssTextElement] = field(default_factory=list)
    style: str = "Default"
    layer: int = 0
    name: str = ""
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0
    effect: str = ""
    
    @property
    def duration(self) -> Timestamp:
        """Get event duration."""
        return self.end - self.start


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    """
    # Script Info: key -> typed value (ordered dict, preserves insertion order)
    script_info: dict[str, Any] = field(default_factory=dict)
    
    # Styles by name
    styles: dict[str, AssStyle] = field(default_factory=dict)
    
    # Dialogue events
    events: list[AssEvent] = field(default_factory=list)
    
    @classmethod
    def from_string(cls, content: str) -> "AssFile":
        """Parse ASS content from string."""
        from sublib.ass.serde import parse_ass_string
        return parse_ass_string(content)
    
    def to_string(self) -> str:
        """Render to ASS format string."""
        from sublib.ass.serde import render_ass_string
        return render_ass_string(self)
    
    @classmethod
    def load(cls, path: Path | str) -> "AssFile":
        """Load ASS file from path."""
        from sublib.io import read_text_file
        from sublib.ass.serde import parse_ass_string
        
        content = read_text_file(path, encoding='utf-8-sig')
        return parse_ass_string(content)
    
    def save(self, path: Path | str) -> None:
        """Save to file."""
        from sublib.io import write_text_file
        from sublib.ass.serde import render_ass_string
        
        content = render_ass_string(self)
        write_text_file(path, content, encoding='utf-8-sig')
