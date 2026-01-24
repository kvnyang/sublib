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
    """
    # Timing fields
    start: AssTimestamp = field(default_factory=AssTimestamp)
    end: AssTimestamp = field(default_factory=AssTimestamp)
    
    # ASS-specific fields
    style: str = "Default"
    layer: int = 0
    name: str = ""
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0
    effect: str = ""
    event_type: str = "Dialogue"
    
    # Internal storage for AST and Lazy Parsing (Layer 3)
    _text_elements: list[AssTextElement] = field(default_factory=list, repr=False)
    _raw_text: Optional[str] = field(default=None, repr=False)
    _line_number: int = 0

    @property
    def text_elements(self) -> list[AssTextElement]:
        """Low-level AST elements. Triggers lazy parsing if needed."""
        self._ensure_ast()
        return self._text_elements

    @text_elements.setter
    def text_elements(self, value: list[AssTextElement]) -> None:
        self._text_elements = value
        self._raw_text = None

    @classmethod
    def from_dict(cls, data: dict[str, str], event_type: str = "Dialogue", line_number: int = 0) -> AssEvent:
        """Create AssEvent from a dictionary of raw strings (mapped by Format)."""
        def get_int(names: list[str], default: int = 0) -> int:
            for n in names:
                if n in data:
                    try: return int(data[n])
                    except ValueError: pass
            return default

        return cls(
            start=AssTimestamp.from_ass_str(data.get('Start', '0:00:00.00')),
            end=AssTimestamp.from_ass_str(data.get('End', '0:00:00.00')),
            style=data.get('Style', 'Default').strip(),
            layer=get_int(['Layer', 'Marked']),
            name=data.get('Name', '').strip(),
            margin_l=get_int(['MarginL']),
            margin_r=get_int(['MarginR']),
            margin_v=get_int(['MarginV']),
            effect=data.get('Effect', '').strip(),
            event_type=event_type,
            _raw_text=data.get('Text', ''),
            _line_number=line_number
        )


    def render(self) -> str:
        """Render event to ASS line (Dialogue: or Comment:)."""
        return (
            f"{self.event_type}: {self.layer},{self.start.to_ass_str()},"
            f"{self.end.to_ass_str()},{self.style},{self.name},"
            f"{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{self.text}"
        )

    @classmethod
    def create(cls, text: str | list[AssTextElement], start: str | AssTimestamp | int, end: str | AssTimestamp | int, **kwargs) -> AssEvent:
        """Robust factory (remains similar but uses unified field mapping)."""
        def _to_timestamp(val: Any) -> AssTimestamp:
            if isinstance(val, AssTimestamp): return val
            if isinstance(val, int): return AssTimestamp.from_ms(val)
            return AssTimestamp.from_ass_str(str(val))

        if isinstance(text, str):
            from sublib.ass.text import AssTextParser
            elements = AssTextParser().parse(text)
        else:
            elements = text
        
        return cls(
            start=_to_timestamp(start),
            end=_to_timestamp(end),
            _text_elements=elements,
            style=kwargs.get('style', "Default"),
            layer=kwargs.get('layer', 0),
            name=kwargs.get('name', ""),
            margin_l=kwargs.get('margin_l', 0),
            margin_r=kwargs.get('margin_r', 0),
            margin_v=kwargs.get('margin_v', 0),
            effect=kwargs.get('effect', ""),
            event_type=kwargs.get('event_type', "Dialogue"),
        )
    
    @property
    def duration(self) -> AssTimestamp:
        return self.end - self.start
    
    @property
    def text(self) -> str:
        """Get or set the raw text string. Correctly handles lazy AST (Layer 3)."""
        if self._raw_text is not None:
             return self._raw_text
        from sublib.ass.text import AssTextRenderer
        return AssTextRenderer().render(self.text_elements)

    @text.setter
    def text(self, value: str) -> None:
        from sublib.ass.text import AssTextParser
        self.text_elements = AssTextParser().parse(value)
        self._raw_text = None

    def _ensure_ast(self):
        """Internal: Trigger Layer 3 parsing if needed."""
        if self._raw_text is not None:
            from sublib.ass.text import AssTextParser
            self.text_elements = AssTextParser().parse(self._raw_text, line_number=self._line_number)
            self._raw_text = None

    def extract_event_tags_and_segments(self):
        self._ensure_ast()
        from sublib.ass.text import extract_event_tags_and_segments
        return extract_event_tags_and_segments(self.text_elements)

    def build_text_elements(self, event_tags=None, segments=None) -> None:
        from sublib.ass.text import build_text_elements
        self.text_elements = build_text_elements(event_tags, segments)
        self._raw_text = None


class AssEvents:
    """Intelligent container for [Events] section."""
    def __init__(self, data: list[AssEvent] | None = None):
        self._data = data if data is not None else []
        self._custom_records: list[RawRecord] = []
        self._diagnostics: list[Diagnostic] = []

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None) -> AssEvents:
        """Layer 2: Semantic ingestion from a RawSection."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        events = cls()
        
        if not raw.format_fields:
            events._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Events section", raw.line_number, "MISSING_FORMAT"))
            return events

        # 1. Minimum field verification
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        # v4: Start, End, Style, Text (4)
        # v4+: Layer, Start, End, Style, Text (5)
        required = {'Start', 'End', 'Style', 'Text'}
        if not is_v4: required.add('Layer')
        
        missing = required - set(raw.format_fields)
        if missing:
             events._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                f"Events section missing mandatory fields: {', '.join(missing)}",
                raw.format_line_number or raw.line_number, "INCOMPLETE_FORMAT"
            ))

        # 2. Ingest records
        known_descriptors = {'dialogue', 'comment', 'picture', 'sound', 'movie', 'command'}
        for record in raw.records:
            desc_lower = record.descriptor.lower()
            if desc_lower in known_descriptors:
                try:
                    parts = [p.strip() for p in record.value.split(',', len(raw.format_fields)-1)]
                    record_dict = {name: val for name, val in zip(raw.format_fields, parts)}
                    
                    event = AssEvent.from_dict(record_dict, event_type=record.descriptor, line_number=record.line_number)
                    events.append(event)
                except Exception as e:
                     events._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse Event: {e}", record.line_number, "EVENT_PARSE_ERROR"))
            else:
                events._custom_records.append(record)

        if not events._data:
            events._diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, "No Events found", raw.line_number, "EMPTY_EVENTS"))

        return events

    @property
    def diagnostics(self) -> list[Diagnostic]:
        return self._diagnostics

    @property
    def custom_records(self) -> list[RawRecord]:
        return self._custom_records

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
        self._data.clear()
        self._data.extend(events)


    def filter(self, style: str | None = None) -> list[AssEvent]:
        if style is None: return list(self._data)
        target = style.lower()
        return [e for e in self._data if e.style.lower() == target]
