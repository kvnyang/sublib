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
    
    The text_elements field is the single source of truth.
    Use from_text() to create from ASS text string.
    Use render_text() to render back to ASS text.
    
    For extracting tags or segments, use services directly:
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
    
    @classmethod
    def from_text(
        cls,
        text: str,
        *,
        start_ms: int = 0,
        end_ms: int = 0,
        style: str = "Default",
        layer: int = 0,
        name: str = "",
        margin_l: int = 0,
        margin_r: int = 0,
        margin_v: int = 0,
        effect: str = "",
        strict: bool = True,
    ) -> "AssEvent":
        """Create event from ASS text string.
        
        Args:
            text: ASS text with override tags
            strict: If True, raise error on unrecognized content
            **kwargs: Other AssEvent fields
            
        Returns:
            New AssEvent with parsed text_elements
        """
        from sublib.ass.services import AssTextParser
        elements = AssTextParser(strict=strict).parse(text)
        return cls(
            start_ms=start_ms,
            end_ms=end_ms,
            text_elements=elements,
            style=style,
            layer=layer,
            name=name,
            margin_l=margin_l,
            margin_r=margin_r,
            margin_v=margin_v,
            effect=effect,
        )
    
    def render_text(self) -> str:
        """Render elements back to ASS text format.
        
        Returns:
            The reconstructed ASS text string with override tags.
        """
        from sublib.ass.services import AssTextRenderer
        return AssTextRenderer().render(self.text_elements)


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
    def load(cls, path: Path | str) -> "AssFile":
        """Load ASS file from path."""
        from sublib.ass.io import load_ass_file
        return load_ass_file(Path(path))
    
    def to_string(self) -> str:
        """Render to ASS format string."""
        from sublib.ass.io import save_ass_string
        return save_ass_string(self)
    
    def save(self, path: Path | str) -> None:
        """Save to file."""
        from sublib.ass.io import save_ass_file
        save_ass_file(self, Path(path))
