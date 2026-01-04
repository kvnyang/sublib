# sublib/ass/models.py
"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from sublib.ass.ast import AssTextElement


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
    Pure data class - use services for parsing and rendering:
    
        from sublib.ass.services import AssTextParser, AssTextRenderer
        
        # Parse text to elements
        elements = AssTextParser().parse(text)
        event = AssEvent(text_elements=elements, start_ms=0, end_ms=1000)
        
        # Render elements to text
        text = AssTextRenderer().render(event.text_elements)
        
        # Extract tags or segments
        from sublib.ass.services import extract_line_scoped_tags
        tags = extract_line_scoped_tags(event.text_elements)
    """
    # Timing fields
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
    def from_string(cls, content: str) -> "AssFile":
        """Parse ASS content from string."""
        from sublib.ass.services import parse_ass_string
        return parse_ass_string(content)
    
    def to_string(self) -> str:
        """Render to ASS format string."""
        from sublib.ass.services import render_ass_string
        return render_ass_string(self)
    
    @classmethod
    def load(cls, path: Path | str) -> "AssFile":
        """Load ASS file from path."""
        from sublib.ass.io import load_ass_file
        return load_ass_file(Path(path))
    
    def save(self, path: Path | str) -> None:
        """Save to file."""
        from sublib.ass.io import save_ass_file
        save_ass_file(self, Path(path))
