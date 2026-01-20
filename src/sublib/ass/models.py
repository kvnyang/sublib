"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from sublib.ass.ast import AssTextElement
from sublib.ass.types import AssColor, AssTimestamp


@dataclass
class AssStyle:
    """ASS style definition.
    
    Represents a style from the [V4+ Styles] section.
    """
    name: str
    fontname: str
    fontsize: float
    primary_color: AssColor
    secondary_color: AssColor
    outline_color: AssColor
    back_color: AssColor
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
    
    Text extraction/composition:
        event.extract_all() -> ExtractionResult(event_tags, segments)
        AssEvent.compose_all(event_tags, segments) -> list[AssTextElement]
    
    Low-level access:
        event.text_elements -> list[AssTextElement]
    """
    # Timing fields
    start: AssTimestamp = field(default_factory=AssTimestamp)
    end: AssTimestamp = field(default_factory=AssTimestamp)
    
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
    def create(
        cls,
        text: str,
        start: str | AssTimestamp = "0:00:00.00",
        end: str | AssTimestamp = "0:00:05.00",
        style: str = "Default",
        **kwargs
    ) -> AssEvent:
        """Convenience factory to create an event from raw text.
        
        Args:
            text: Raw ASS text (may contain tags like {\\b1}Hello)
            start: Start time (string or AssTimestamp)
            end: End time (string or AssTimestamp)
            style: Style name
            **kwargs: Other AssEvent fields (layer, name, etc.)
        """
        from sublib.ass.serde import AssTextParser
        
        start_ts = AssTimestamp.from_ass_str(start) if isinstance(start, str) else start
        end_ts = AssTimestamp.from_ass_str(end) if isinstance(end, str) else end
        
        return cls(
            start=start_ts,
            end=end_ts,
            text_elements=AssTextParser().parse(text),
            style=style,
            **kwargs
        )
    
    @property
    def duration(self) -> AssTimestamp:
        """Get event duration."""
        return self.end - self.start
    
    def extract(self):
        """Extract event-level tags and inline segments from text.
        
        Returns:
            ExtractionResult with event_tags dict and segments list.
        """
        from sublib.ass.text_transform import extract_all
        return extract_all(self.text_elements)

    def compose(self, event_tags=None, segments=None) -> None:
        """Update event text from semantic tags and segments.
        
        Args:
            event_tags: Event-level tags dict
            segments: Inline segments
        """
        from sublib.ass.text_transform import compose_all
        self.text_elements = compose_all(event_tags, segments)

    @staticmethod
    def compose_elements(event_tags=None, segments=None):
        """Build ASS text elements from tags and segments without updating an event."""
        from sublib.ass.text_transform import compose_all
        return compose_all(event_tags, segments)


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    Validation warnings are logged during parsing.
    """
    # Script Info: key -> typed value (ordered dict, preserves insertion order)
    script_info: dict[str, Any] = field(default_factory=dict)
    
    # Styles by name
    styles: dict[str, AssStyle] = field(default_factory=dict)
    
    # Dialogue events
    events: list[AssEvent] = field(default_factory=list)
    
    @classmethod
    def loads(cls, content: str) -> "AssFile":
        """Parse ASS content from string."""
        from sublib.ass.serde import parse_ass_string
        return parse_ass_string(content)
    
    def get_info(self, key: str, default: Any = None) -> Any:
        """Get a value from [Script Info] section."""
        return self.script_info.get(key, default)
        
    def set_info(self, key: str, value: Any) -> None:
        """Set a value in [Script Info] section."""
        self.script_info[key] = value

    def set_style(self, style: AssStyle) -> None:
        """Add or update a style definition."""
        self.styles[style.name] = style
        
    def get_style(self, name: str) -> AssStyle | None:
        """Get style by name."""
        return self.styles.get(name)
        
    def add_event(self, event: AssEvent) -> None:
        """Add a dialogue event."""
        self.events.append(event)

    def get_event(self, index: int) -> AssEvent:
        """Get event by index."""
        return self.events[index]
    
    def dumps(self, validate: bool = False) -> str:
        """Render to ASS format string.
        
        Args:
            validate: If True, raise ValueError for undefined style references
        """
        from sublib.ass.serde import render_ass_string
        
        if validate:
            errors = self._validate_styles()
            if errors:
                raise ValueError(f"Invalid style references:\n" + "\n".join(errors))
        return render_ass_string(self)
    
    @classmethod
    def load(cls, path: Path | str) -> "AssFile":
        """Load ASS file from path.
        
        Validation warnings are logged at WARNING level.
        """
        from sublib.io import read_text_file
        content = read_text_file(path, encoding='utf-8-sig')
        return cls.loads(content)
    
    def dump(self, path: Path | str, validate: bool = False) -> None:
        """Save to file.
        
        Args:
            path: Output file path
            validate: If True, raise ValueError for undefined style references
        """
        from sublib.io import write_text_file
        content = self.dumps(validate=validate)
        write_text_file(path, content, encoding='utf-8-sig')
    
    def _validate_styles(self) -> list[str]:
        """Validate that all style references are defined.
        
        Returns:
            List of error messages (empty = valid)
        """
        errors = []
        defined_styles = set(self.styles.keys())
        
        for i, event in enumerate(self.events):
            if event.style not in defined_styles:
                errors.append(f"Event {i+1}: style '{event.style}' not defined")
            
            result = event.extract_all()
            for seg in result.segments:
                r_style = seg.block_tags.get("r")
                if r_style and r_style not in defined_styles:
                    errors.append(f"Event {i+1}: \\r style '{r_style}' not defined")
        
        return errors
