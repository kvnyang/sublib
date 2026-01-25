"""ASS Event models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord

from sublib.ass.naming import normalize_key, get_canonical_name

from sublib.ass.models.text.elements import AssTextElement
from sublib.ass.types import AssTimestamp


# Mapping of Python property names to normalized ASS field names
EVENT_FIELD_MAP = {
    'layer': 'layer',
    'start': 'start',
    'end': 'end',
    'style': 'style',
    'name': 'name',
    'margin_l': 'marginl',
    'margin_r': 'marginr',
    'margin_v': 'marginv',
    'effect': 'effect',
}


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
    # For custom fields preservation: Stores normalized_key -> raw_value
    extra_fields: dict[str, str] = field(default_factory=dict)
    # Track which fields were explicitly provided or set
    _explicit_fields: set[str] = field(default_factory=set, repr=False)

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
        """Create AssEvent from a dictionary of standardized field names."""
        def get_int(names: list[str], default: int = 0) -> int:
            for n in names:
                if n in data:
                    try: return int(data[n])
                    except ValueError: pass
            return default

        # Keys already standardized (normalized) by the parser or caller
        known_standard = {
            'layer', 'marked', 'start', 'end', 'style', 'name',
            'marginl', 'marginr', 'marginv', 'effect', 'text'
        }
        
        extra = {}
        for k, v in data.items():
            if k not in known_standard:
                extra[k] = v

        explicit = {normalize_key(k) for k, v in data.items() if v.strip()}

        return cls(
            start=AssTimestamp.from_ass_str(data.get('start', '0:00:00.00')),
            end=AssTimestamp.from_ass_str(data.get('end', '0:00:00.00')),
            style=data.get('style', 'Default').strip(),
            layer=get_int(['layer', 'marked']),
            name=data.get('name', '').strip(),
            margin_l=get_int(['marginl']),
            margin_r=get_int(['marginr']),
            margin_v=get_int(['marginv']),
            effect=data.get('effect', '').strip(),
            event_type=event_type,
            _raw_text=data.get('text', ''),
            _line_number=line_number,
            extra_fields=extra,
            _explicit_fields=explicit
        )

    def __setattr__(self, name: str, value: Any) -> None:
        # Track manual property changes in _explicit_fields
        if name in EVENT_FIELD_MAP:
             try:
                 expl = self.__dict__.get('_explicit_fields')
                 if expl is not None:
                     expl.add(EVENT_FIELD_MAP[name])
             except Exception:
                 pass
        super().__setattr__(name, value)


    def render(self, format_fields: list[str] | None = None, auto_fill: bool = False) -> str:
        """Render event to ASS line according to requested format fields.
        
        Args:
            format_fields: List of raw field names to output. If None, uses internal defaults.
            auto_fill: If True, fills missing explicit fields with defaults. Default False (Transparent).
        """
        descriptor = get_canonical_name(self.event_type, context="events")
        
        # Mapping of standardized key -> actual value
        vals = {
            'layer': str(self.layer),
            'marked': str(self.layer), # Alias
            'start': self.start.to_ass_str(),
            'end': self.end.to_ass_str(),
            'style': self.style,
            'name': self.name,
            'marginl': str(self.margin_l),
            'marginr': str(self.margin_r),
            'marginv': str(self.margin_v),
            'effect': self.effect,
            'text': self.text
        }
        
        # Add extra fields (mapped by normalized key)
        extra_vals = {normalize_key(k): v for k, v in self.extra_fields.items()}
        
        if format_fields:
            field_values = []
            for f in format_fields:
                key = normalize_key(f)
                
                # Check if field should be rendered (is explicit or auto-fill is on)
                # Note: 'text' is always mandatory for a meaningful event line
                is_explicit = key in self._explicit_fields or key == 'text'
                
                if is_explicit or auto_fill:
                    if key in vals:
                        field_values.append(vals[key])
                    elif key in extra_vals:
                        field_values.append(extra_vals[key])
                    else:
                        field_values.append("") # Unknown field
                else:
                    field_values.append("") # Not explicit, no auto-fill
            return f"{descriptor}: {','.join(field_values)}"

        # Default V4+ render (backward compatibility)
        return (
            f"{descriptor}: {self.layer},{self.start.to_ass_str()},"
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
        self._section_comments: list[str] = []
        self._raw_format_fields: list[str] | None = None

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None, event_format: list[str] | None = None) -> AssEvents:
        """Layer 2: Semantic ingestion from a RawSection.
        
        Args:
            raw: The RawSection containing data.
            script_type: Optional ScriptType hint.
            event_format: Optional format override to filter which fields are ingested as explicit.
        """
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        events = cls()
        events._section_comments = list(raw.comments)
        
        # Determine active format fields for this ingestion
        if event_format:
             events._raw_format_fields = event_format
             parsing_fields = [normalize_key(f) for f in event_format]
        else:
             events._raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
             parsing_fields = raw.format_fields
        
        if not raw.format_fields:
            events._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Events section", raw.line_number, "MISSING_FORMAT"))
            return events

        # 1. Mandatory field verification
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        
        # Determine actual file format for parsing records
        file_format_fields = raw.format_fields # Normalized keys from Layer 1
        
        # User defined mandatory sets for validation
        V4_MANDATORY = {'start', 'end', 'style', 'text'}
        V4PLUS_MANDATORY = {'layer', 'start', 'end', 'style', 'text'}
        
        required = V4_MANDATORY if is_v4 else V4PLUS_MANDATORY
        # We check against parsing_fields (the effective format for this session)
        missing = required - set(parsing_fields)
        if missing:
             events._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                f"Events section missing standard fields: {', '.join(sorted(missing))}",
                raw.format_line_number or raw.line_number, "INCOMPLETE_FORMAT"
            ))

        # 2. Ingest records
        # If event_format was provided, we want to filter the ingestion
        filter_set = set(parsing_fields) if event_format else None
        
        # known_descriptors as standardized from Layer 1
        known_descriptors = {'dialogue', 'comment', 'picture', 'sound', 'movie', 'command'}
        for record in raw.records:
            try:
                # Always split based on the FILE'S actual structure
                parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                full_dict = {name: val for name, val in zip(file_format_fields, parts)}
                
                if filter_set:
                    # Only keep fields requested in the override/filter
                    ingest_dict = {k: v for k, v in full_dict.items() if k in filter_set}
                else:
                    ingest_dict = full_dict
                
                if record.descriptor in known_descriptors:
                    event = AssEvent.from_dict(ingest_dict, event_type=record.descriptor, line_number=record.line_number)
                    events.append(event)
                else:
                    # Custom record preservation: Store raw descriptor for restoration
                    events._custom_records.append(record)
            except Exception as e:
                events._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse {record.raw_descriptor}: {e}", record.line_number, "EVENT_PARSE_ERROR"))

        if not events._data:
            events._diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, "No Events found", raw.line_number, "EMPTY_EVENTS"))

        return events

    @property
    def diagnostics(self) -> list[Diagnostic]:
        return self._diagnostics

    def get_comments(self) -> list[str]:
        """Get all comments."""
        return list(self._section_comments)

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

    def get_explicit_format(self, script_type: str | None = None) -> list[str]:
        """Get the union of all explicit fields across all events in standard order."""
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        
        # Standard Order
        if is_v4:
            standard = ['Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
        else:
            standard = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
            
        all_explicit = set()
        for event in self._data:
            all_explicit.update(event._explicit_fields)
            
        # Text is always mandatory
        all_explicit.add('text')
        
        # Result in standard order
        result = []
        for f in standard:
            if normalize_key(f) in all_explicit:
                result.append(f)
                
        # Any remaining explicit fields that are NOT in standard set (custom fields)
        standard_normalized = {normalize_key(f) for f in standard}
        for field_key in sorted(all_explicit - standard_normalized):
             result.append(field_key)
             
        return result
