# sublib/ass/models.py
"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from sublib.ass.ast import AssTextElement
from sublib.ass.types import Color, Timestamp


@dataclass
class ScriptInfo:
    """Typed Script Info for ASS V4.00+ format.
    
    Provides typed access to standard fields with validation warnings.
    Non-standard fields are stored in `extra`.
    """
    # Required field
    script_type: str = "v4.00+"
    
    # Functional fields
    play_res_x: int | None = None
    play_res_y: int | None = None
    wrap_style: int = 0  # 0-3
    collisions: str = "Normal"  # Normal/Reverse
    timer: float = 100.0
    ycbcr_matrix: str | None = None  # TV.601, TV.709, PC.601, PC.709, None
    scaled_border_and_shadow: bool = True  # yes/no in ASS format
    
    # Metadata fields
    title: str = "<untitled>"
    original_script: str = "<unknown>"
    original_translation: str | None = None
    original_editing: str | None = None
    original_timing: str | None = None
    synch_point: str | None = None
    script_updated_by: str | None = None
    update_details: str | None = None
    
    # Non-standard fields
    extra: dict[str, str] = field(default_factory=dict)
    
    # Validation warnings (populated during parsing)
    warnings: list[str] = field(default_factory=list)


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
    # Script Info section (typed with validation)
    script_info: ScriptInfo = field(default_factory=ScriptInfo)
    
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
