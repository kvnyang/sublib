"""ASS Event models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable

from sublib.ass.models.text.elements import AssTextElement
from sublib.ass.types import AssTimestamp


@dataclass
class AssEvent:
    """ASS dialogue event.
    
    Represents a Dialogue line from the [Events] section.
    
    Text extraction/composition (Semantic):
        event.extract_event_tags_and_segments() -> (event_tags, segments)
        event.build_text_elements(event_tags, segments) -> None
    
    Low-level structure (AST):
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
    event_type: str = "Dialogue"

    @classmethod
    def from_ass_line(
        cls,
        line: str,
        text_parser: Any | None = None,
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
        if line.startswith('Dialogue:'):
            header = 'Dialogue:'
        elif line.startswith('Comment:'):
            header = 'Comment:'
        else:
            return None
        
        # Split into 10 parts (last part is text, may contain commas)
        parts = line[len(header):].split(',', 9)
        if len(parts) < 10:
            return None
        
        if text_parser is None:
            from sublib.ass.text import AssTextParser
            text_parser = AssTextParser()
        
        text = parts[9]
        
        return cls(
            start=AssTimestamp.from_ass_str(parts[1]),
            end=AssTimestamp.from_ass_str(parts[2]),
            text_elements=text_parser.parse(text, line_number=line_number),
            style=parts[3].strip(),
            layer=int(parts[0]),
            name=parts[4].strip(),
            margin_l=int(parts[5]),
            margin_r=int(parts[6]),
            margin_v=int(parts[7]),
            effect=parts[8].strip(),
            event_type=header[:-1],
        )

    def render(self) -> str:
        """Render event to ASS line (Dialogue: or Comment:)."""
        from sublib.ass.text import AssTextRenderer
        text = AssTextRenderer().render(self.text_elements)
        return (
            f"{self.event_type}: {self.layer},{self.start.to_ass_str()},"
            f"{self.end.to_ass_str()},{self.style},{self.name},"
            f"{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{text}"
        )

    @classmethod
    def create(
        cls,
        text: str | list[AssTextElement],
        start: str | AssTimestamp | int,
        end: str | AssTimestamp | int,
        style: str = "Default",
        layer: int = 0,
        name: str = "",
        margin_l: int = 0,
        margin_r: int = 0,
        margin_v: int = 0,
        effect: str = "",
        event_type: str = "Dialogue"
    ) -> AssEvent:
        """Robust factory to create an event with explicit ASS fields.
        
        Mandatory args: text, start, end.
        
        Args:
            text: Raw ASS text (parsed) or pre-built AssTextElement list
            start: Start time (string, AssTimestamp, or integer ms)
            end: End time (string, AssTimestamp, or integer ms)
            style: Style name (defaults to "Default")
            layer: Layer level (0-based)
            name: Actor/Speaker name field
            margin_l/r/v: Margin overrides
            effect: Transition/Karaoke effect field
        """
        # Handle Timing
        def _to_timestamp(val: Any) -> AssTimestamp:
            if isinstance(val, AssTimestamp):
                return val
            if isinstance(val, int):
                return AssTimestamp.from_ms(val)
            return AssTimestamp.from_ass_str(str(val))

        # Handle Text
        if isinstance(text, str):
            from sublib.ass.text import AssTextParser
            elements = AssTextParser().parse(text)
        else:
            elements = text
        
        return cls(
            start=_to_timestamp(start),
            end=_to_timestamp(end),
            text_elements=elements,
            style=style,
            layer=layer,
            name=name,
            margin_l=margin_l,
            margin_r=margin_r,
            margin_v=margin_v,
            effect=effect,
            event_type=event_type,
        )
    
    @property
    def duration(self) -> AssTimestamp:
        """Get event duration."""
        return self.end - self.start
    
    @property
    def text(self) -> str:
        """Get or set the raw text string (Convenience/String access).
        
        This property provides a high-level string view of the event.
        - Getter: Renders the underlying AST to a string.
        - Setter: Parses the string into a new AST, replacing content.
        
        For precise structural manipulation, use `text_elements` (AST).
        For semantic content extraction, use `extract()`.
        """
        from sublib.ass.text import AssTextRenderer
        return AssTextRenderer().render(self.text_elements)

    @text.setter
    def text(self, value: str) -> None:
        from sublib.ass.text import AssTextParser
        self.text_elements = AssTextParser().parse(value)

    def extract_event_tags_and_segments(self):
        """Extract event-level tags and inline segments from text.
        
        Returns:
            tuple of (event_tags dict, segments list).
        """
        from sublib.ass.text import extract_event_tags_and_segments
        return extract_event_tags_and_segments(self.text_elements)

    def build_text_elements(self, event_tags=None, segments=None) -> None:
        """Update event text from semantic tags and segments.
        
        Args:
            event_tags: Event-level tags dict
            segments: Inline segments
        """
        from sublib.ass.text import build_text_elements
        self.text_elements = build_text_elements(event_tags, segments)



class AssEvents:
    """Intelligent container for [Events] section."""
    def __init__(self, data: list[AssEvent] | None = None):
        self._data = data if data is not None else []

    def __getitem__(self, index: int) -> AssEvent:
        return self._data[index]

    def __setitem__(self, index: int, event: AssEvent) -> None:
        self._data[index] = event

    def __delitem__(self, index: int) -> None:
        del self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def append(self, event: AssEvent) -> None:
        self._data.append(event)

    def add_all(self, events: Iterable[AssEvent]) -> None:
        self._data.extend(events)

    def set_all(self, events: Iterable[AssEvent]) -> None:
        """Replace all dialogue events."""
        self._data.clear()
        self._data.extend(events)

    def add_from_line(self, line: str, text_parser: Any | None = None, line_number: int = 0) -> AssEvent | None:
        """Parse and add an event from an ASS line."""
        event = AssEvent.from_ass_line(line, text_parser=text_parser, line_number=line_number)
        if event:
            self.append(event)
        return event

    def filter(self, style: str | None = None) -> list[AssEvent]:
        """Get events, optionally filtered by style name."""
        if style is None:
            return list(self._data)
        target = style.lower()
        return [e for e in self._data if e.style.lower() == target]
