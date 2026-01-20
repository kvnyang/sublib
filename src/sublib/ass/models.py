"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable, TYPE_CHECKING
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


class AssScriptInfoView:
    """Dict-like view for [Script Info] section."""
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def set_all(self, info_dict: dict[str, Any]) -> None:
        """Replace all properties."""
        self._data.clear()
        self._data.update(info_dict)

    def add_all(self, info_dict: dict[str, Any]) -> None:
        """Merge/Update properties."""
        self._data.update(info_dict)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class AssStylesView:
    """Dict-like view for [V4+ Styles] section."""
    def __init__(self, data: dict[str, AssStyle]):
        self._data = data

    def __getitem__(self, name: str) -> AssStyle:
        return self._data[name]

    def __setitem__(self, name: str, style: AssStyle) -> None:
        if name != style.name:
            raise ValueError(f"Style name mismatch: {name} != {style.name}")
        self._data[name] = style

    def __delitem__(self, name: str) -> None:
        del self._data[name]

    def __contains__(self, name: str) -> bool:
        return name in self._data

    def __iter__(self):
        return iter(self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def get(self, name: str) -> AssStyle | None:
        return self._data.get(name)

    def set(self, style: AssStyle) -> None:
        self._data[style.name] = style

    def set_all(self, styles: Iterable[AssStyle]) -> None:
        """Replace all style definitions."""
        self._data.clear()
        for s in styles:
            self.set(s)

    def add_all(self, styles: Iterable[AssStyle]) -> None:
        """Merge/Update style definitions."""
        for s in styles:
            self.set(s)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


class AssEventsView:
    """List-like view for [Events] section."""
    def __init__(self, data: list[AssEvent]):
        self._data = data

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

    add = append

    def add_all(self, events: Iterable[AssEvent]) -> None:
        self._data.extend(events)

    def set_all(self, events: Iterable[AssEvent]) -> None:
        """Replace all dialogue events."""
        self._data.clear()
        self._data.extend(events)

    def filter(self, style: str | None = None) -> list[AssEvent]:
        """Get events, optionally filtered by style name."""
        if style is None:
            return list(self._data)
        return [e for e in self._data if e.style == style]


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    Validation warnings are logged during parsing.
    """
    # Internal storage
    _script_info: dict[str, Any] = field(default_factory=dict)
    _styles: dict[str, AssStyle] = field(default_factory=dict)
    _events: list[AssEvent] = field(default_factory=list)
    
    @property
    def script_info(self) -> AssScriptInfoView:
        """View into [Script Info] section."""
        return AssScriptInfoView(self._script_info)
    
    @property
    def styles(self) -> AssStylesView:
        """View into [V4+ Styles] section."""
        return AssStylesView(self._styles)
    
    @property
    def events(self) -> AssEventsView:
        """View into [Events] section."""
        return AssEventsView(self._events)

    @classmethod
    def loads(cls, content: str) -> "AssFile":
        """Parse ASS content from string."""
        from sublib.ass.serde import parse_ass_string
        return parse_ass_string(content)
    
    @property
    def script_info_keys(self) -> list[str]:
        """Get list of defined script info keys."""
        return list(self._script_info.keys())

    def __iter__(self):
        """Iterate over dialogue events."""
        return iter(self._events)

    def __len__(self) -> int:
        """Get total number of dialogue events."""
        return len(self._events)
    
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
        defined_styles = set(self._styles.keys())
        
        for i, event in enumerate(self.events):
            if event.style not in defined_styles:
                errors.append(f"Event {i+1}: style '{event.style}' not defined")
            
            result = event.extract_all()
            for seg in result.segments:
                r_style = seg.block_tags.get("r")
                if r_style and r_style not in defined_styles:
                    errors.append(f"Event {i+1}: \\r style '{r_style}' not defined")
        
        return errors
