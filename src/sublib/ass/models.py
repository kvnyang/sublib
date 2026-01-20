"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable, TYPE_CHECKING, Mapping
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from sublib.ass.text import AssTextElement
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

    @classmethod
    def from_ass_line(cls, line: str) -> AssStyle | None:
        """Parse a Style: line to AssStyle.
        
        Args:
            line: Style line (e.g., "Style: Default,Arial,20,...")
            
        Returns:
            AssStyle or None if parsing fails
        """
        if not line.startswith('Style:'):
            return None
        
        parts = line[6:].split(',')
        if len(parts) < 23:
            return None
        
        return cls(
            name=parts[0].strip(),
            fontname=parts[1].strip(),
            fontsize=float(parts[2]),
            primary_color=AssColor.from_style_str(parts[3]),
            secondary_color=AssColor.from_style_str(parts[4]),
            outline_color=AssColor.from_style_str(parts[5]),
            back_color=AssColor.from_style_str(parts[6]),
            bold=parts[7].strip() != '0',
            italic=parts[8].strip() != '0',
            underline=parts[9].strip() != '0',
            strikeout=parts[10].strip() != '0',
            scale_x=float(parts[11]),
            scale_y=float(parts[12]),
            spacing=float(parts[13]),
            angle=float(parts[14]),
            border_style=int(parts[15]),
            outline=float(parts[16]),
            shadow=float(parts[17]),
            alignment=int(parts[18]),
            margin_l=int(parts[19]),
            margin_r=int(parts[20]),
            margin_v=int(parts[21]),
            encoding=int(parts[22]),
        )

    def render(self) -> str:
        """Render AssStyle to Style: line."""
        from sublib.ass.tags.base import _format_float
        return (
            f"Style: {self.name},{self.fontname},{_format_float(self.fontsize)},"
            f"{self.primary_color.to_style_str()},"
            f"{self.secondary_color.to_style_str()},"
            f"{self.outline_color.to_style_str()},"
            f"{self.back_color.to_style_str()},"
            f"{int(self.bold)},{int(self.italic)},{int(self.underline)},{int(self.strikeout)},"
            f"{_format_float(self.scale_x)},{_format_float(self.scale_y)},"
            f"{_format_float(self.spacing)},{_format_float(self.angle)},"
            f"{self.border_style},{_format_float(self.outline)},{_format_float(self.shadow)},"
            f"{self.alignment},{self.margin_l},{self.margin_r},{self.margin_v},{self.encoding}"
        )


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
        if not line.startswith('Dialogue:'):
            return None
        
        # Split into 10 parts (last part is text, may contain commas)
        parts = line[9:].split(',', 9)
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
        )

    def render(self) -> str:
        """Render AssEvent to Dialogue: line."""
        from sublib.ass.text import AssTextRenderer
        text = AssTextRenderer().render(self.text_elements)
        return (
            f"Dialogue: {self.layer},{self.start.to_ass_str()},"
            f"{self.end.to_ass_str()},{self.style},{self.name},"
            f"{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{text}"
        )

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
        from sublib.ass.text import AssTextParser
        
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
        from sublib.ass.text import extract_all
        return extract_all(self.text_elements)

    def compose(self, event_tags=None, segments=None) -> None:
        """Update event text from semantic tags and segments.
        
        Args:
            event_tags: Event-level tags dict
            segments: Inline segments
        """
        from sublib.ass.text import compose_all
        self.text_elements = compose_all(event_tags, segments)

    @staticmethod
    def compose_elements(event_tags=None, segments=None):
        """Build ASS text elements from tags and segments without updating an event."""
        from sublib.ass.text import compose_all
        return compose_all(event_tags, segments)


class AssScriptInfo:
    """Intelligent container for [Script Info] section with automatic type conversion and validation."""
    
    KNOWN_FIELDS = {
        "ScriptType": "str",
        "Title": "str",
        "PlayResX": "int",
        "PlayResY": "int",
        "WrapStyle": "int",
        "ScaledBorderAndShadow": "bool",
        "Collisions": "str",
        "YCbCr Matrix": "str",
        "Timer": "float",
    }
    
    _CANONICAL_KEYS = {k.lower(): k for k in KNOWN_FIELDS}

    def __init__(self, data: dict[str, Any] | None = None):
        self._data = data if data is not None else {}

    def _normalize_key(self, key: str) -> str:
        return self._CANONICAL_KEYS.get(key.lower(), key)

    @staticmethod
    def parse_line(line: str) -> tuple[str, str] | None:
        """Parse a single Script Info line into a raw key-value pair."""
        if ':' not in line:
            return None
        key, _, value = line.partition(':')
        return key.strip(), value.strip()

    def render_line(self, key: str, value: Any) -> str:
        """Render a single Script Info line."""
        if isinstance(value, bool):
            formatted = "yes" if value else "no"
        elif isinstance(value, float) and key == "Timer":
            formatted = f"{value:.4f}"
        else:
            formatted = str(value)
        return f"{key}: {formatted}"

    def __getitem__(self, key: str) -> Any:
        return self._data[self._normalize_key(key)]

    def __setitem__(self, key: str, value: Any) -> None:
        canonical_key = self._normalize_key(key)
        
        # Automatic parsing if value is string (from parser)
        if isinstance(value, str):
            field_type = self.KNOWN_FIELDS.get(canonical_key)
            if field_type:
                value = self._parse_typed_value(canonical_key, value, field_type)
        
        self._data[canonical_key] = value

    def _parse_typed_value(self, key: str, value: str, field_type: str) -> Any:
        try:
            if field_type == "int":
                return int(value)
            elif field_type == "float":
                return float(value)
            elif field_type == "bool":
                return value.lower() in ("yes", "1", "true")
        except ValueError:
            logger.warning(f"Invalid value for {key}: {value} (expected {field_type})")
        return value

    def __getattr__(self, name: str) -> Any:
        # Allow access like file.script_info.Title
        if name.startswith('_'): # Don't interfere with internal attributes
            raise AttributeError(name)
            
        canonical = self._normalize_key(name)
        if canonical in self._data:
            return self._data[canonical]
            
        raise AttributeError(f"'AssScriptInfo' object has no attribute '{name}'")

    def __delitem__(self, key: str) -> None:
        del self._data[self._normalize_key(key)]

    def __contains__(self, key: str) -> bool:
        return self._normalize_key(key) in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(self._normalize_key(key), default)

    def set(self, key: str, value: Any) -> None:
        self[key] = value

    def set_all(self, info_dict: dict[str, Any]) -> None:
        """Replace all properties."""
        self._data.clear()
        for k, v in info_dict.items():
            self[k] = v

    def add_all(self, info_dict: dict[str, Any]) -> None:
        """Merge/Update properties."""
        for k, v in info_dict.items():
            self[k] = v

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class AssStyles:
    """Intelligent container for [V4+ Styles] section."""
    def __init__(self, data: dict[str, AssStyle] | None = None):
        self._data = data if data is not None else {}

    def _get_canonical_name(self, name: str) -> str:
        # Try exact match first
        if name in self._data:
            return name
        # Case-insensitive lookup
        lower_name = name.lower()
        for k in self._data:
            if k.lower() == lower_name:
                return k
        return name

    def __getitem__(self, name: str) -> AssStyle:
        canonical = self._get_canonical_name(name)
        if canonical not in self._data:
            raise KeyError(name)
        return self._data[canonical]

    def __setitem__(self, name: str, style: AssStyle) -> None:
        if name != style.name:
            # If name is a case-insensitive match for style.name, it's okay but style.name is the source of truth
            if name.lower() != style.name.lower():
                raise ValueError(f"Style name mismatch: {name} != {style.name}")
        self._data[style.name] = style

    def __delitem__(self, name: str) -> None:
        canonical = self._get_canonical_name(name)
        del self._data[canonical]

    def __contains__(self, name: str) -> bool:
        lower_name = name.lower()
        return any(k.lower() == lower_name for k in self._data)

    def __iter__(self):
        return iter(self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def get(self, name: str) -> AssStyle | None:
        canonical = self._get_canonical_name(name)
        return self._data.get(canonical)

    def set(self, style: AssStyle) -> None:
        self._data[style.name] = style

    def set_all(self, styles: Iterable[AssStyle]) -> None:
        """Replace all style definitions."""
        self._data.clear()
        for s in styles:
            self.set(s)

    def add_from_line(self, line: str) -> AssStyle | None:
        """Parse and add a style from an ASS line."""
        style = AssStyle.from_ass_line(line)
        if style:
            self.set(style)
        return style

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

    add = append

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


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    The script_info, styles, and events fields are intelligent containers.
    """
    script_info: AssScriptInfo = field(default_factory=AssScriptInfo)
    styles: AssStyles = field(default_factory=AssStyles)
    events: AssEvents = field(default_factory=AssEvents)

    def __post_init__(self):
        if isinstance(self.script_info, dict):
            self.script_info = AssScriptInfo(self.script_info)
        if isinstance(self.styles, dict):
            self.styles = AssStyles(self.styles)
        if isinstance(self.events, list):
            self.events = AssEvents(self.events)

    @classmethod
    def loads(cls, content: str) -> "AssFile":
        """Parse ASS content from string."""
        from sublib.ass.text import AssTextParser
        text_parser = AssTextParser()
        
        ass_file = cls()
        lines = content.splitlines()
        current_section = None
        line_number = 0
        
        for line in lines:
            line_number += 1
            line = line.strip()
            
            if not line or line.startswith(';'):
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].lower()
                continue
            
            if current_section == 'script info':
                result = AssScriptInfo.parse_line(line)
                if result:
                    key, value = result
                    if key in ass_file.script_info:
                        logger.warning(f"Duplicate Script Info key: {key}")
                    ass_file.script_info[key] = value  # last-wins
            
            elif current_section in ('v4 styles', 'v4+ styles'):
                if line.startswith('Style:'):
                    ass_file.styles.add_from_line(line)
            
            elif current_section == 'events':
                if line.startswith('Dialogue:'):
                    ass_file.events.add_from_line(line, text_parser, line_number)
        
        return ass_file

    def dumps(self, validate: bool = False) -> str:
        """Render to ASS format string.
        
        Args:
            validate: If True, raise ValueError for undefined style references
        """
        if validate:
            errors = self._validate_styles()
            if errors:
                raise ValueError(f"Invalid style references:\n" + "\n".join(errors))
        
        lines = []
        
        # 1. Script Info
        lines.append('[Script Info]')
        for key, value in self.script_info.items():
            lines.append(self.script_info.render_line(key, value))
        lines.append('')
        
        # 2. Styles
        lines.append('[V4+ Styles]')
        lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, '
                     'OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, '
                     'ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, '
                     'Alignment, MarginL, MarginR, MarginV, Encoding')
        for style in self.styles:
            lines.append(style.render())
        lines.append('')
        
        # 3. Events
        lines.append('[Events]')
        lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
        for event in self.events:
            lines.append(event.render())
        
        return '\n'.join(lines)

    @property
    def script_info_keys(self) -> list[str]:
        """Get list of defined script info keys."""
        return list(self.script_info.keys())

    def __iter__(self):
        """Iterate over dialogue events."""
        return iter(self.events)

    def __len__(self) -> int:
        """Get total number of dialogue events."""
        return len(self.events)
    
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
        # Case-insensitive set for quick lookup
        defined_styles = {s.name.lower() for s in self.styles}
        
        for i, event in enumerate(self.events):
            if event.style.lower() not in defined_styles:
                errors.append(f"Event {i+1}: style '{event.style}' not defined")
            
            result = event.extract()
            for seg in result.segments:
                r_style = seg.block_tags.get("r")
                if r_style and r_style.lower() not in defined_styles:
                    errors.append(f"Event {i+1}: \\r style '{r_style}' not defined")
        
        return errors
