"""ASS Event models using Eager Sparse Typed Storage."""
from __future__ import annotations
from typing import Any, Iterable, Optional, TYPE_CHECKING, Literal
from sublib.ass.naming import normalize_key, get_canonical_name, AssEventType
from sublib.ass.models.text.elements import AssTextElement
from sublib.ass.types import AssTimestamp

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
    from sublib.ass.diagnostics import Diagnostic



from .base import AssFormatSection
from .schema import FieldSchema, AssStructuredRecord

EVENT_SCHEMA = {
    'layer': FieldSchema(0, int, canonical_name='Layer', python_prop='layer'),
    'start': FieldSchema(AssTimestamp(), AssTimestamp, canonical_name='Start', python_prop='start'),
    'end': FieldSchema(AssTimestamp(), AssTimestamp, canonical_name='End', python_prop='end'),
    'style': FieldSchema("Default", str, canonical_name='Style', python_prop='style'),
    'name': FieldSchema("", str, canonical_name='Name', python_prop='name'),
    'margin_l': FieldSchema(0, int, canonical_name='MarginL', python_prop='margin_l'),
    'margin_r': FieldSchema(0, int, canonical_name='MarginR', python_prop='margin_r'),
    'margin_v': FieldSchema(0, int, canonical_name='MarginV', python_prop='margin_v'),
    'effect': FieldSchema("", str, canonical_name='Effect', python_prop='effect'),
    'text': FieldSchema("", str, canonical_name='Text', python_prop='text'),
}

# Identity mapping for Events (normalized_key -> FieldSchema)
EVENT_IDENTITY_SCHEMA = {s.normalized_key: s for s in EVENT_SCHEMA.values()}
# Support aliases
EVENT_IDENTITY_SCHEMA[normalize_key('MarginLeft')] = EVENT_SCHEMA['margin_l']
EVENT_IDENTITY_SCHEMA[normalize_key('MarginRight')] = EVENT_SCHEMA['margin_r']
EVENT_IDENTITY_SCHEMA[normalize_key('MarginVertical')] = EVENT_SCHEMA['margin_v']


class AssEvent(AssStructuredRecord):
    """ASS dialogue event using Schema-Driven Typed Storage."""
    
    def __init__(self, fields: dict[str, Any] | None = None, type: str = AssEventType.DIALOGUE, line_number: int = 0, extra_fields: dict[str, Any] | None = None, **kwargs):
        # Use object.__setattr__ for internal housekeeping to avoid trapping in _extra
        object.__setattr__(self, '_type', get_canonical_name(type, context='events'))
        object.__setattr__(self, '_line_number', line_number)
        object.__setattr__(self, '_text_elements', [])
        object.__setattr__(self, '_ast_synced', False)
        
        super().__init__(EVENT_IDENTITY_SCHEMA, fields, extra_fields)
        
        # Apply standard properties via kwargs (uses base __setattr__ -> __setitem__ -> schema.convert)
        for name, value in kwargs.items():
            self[name] = value

    @property
    def extra_fields(self) -> dict[str, Any]:
        """Custom/non-standard fields."""
        return self._extra

    @property
    def type(self) -> str:
        """The canonical type of the event (e.g. 'Dialogue', 'Comment')."""
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = get_canonical_name(value, context='events')

    @property
    def is_dialogue(self) -> bool:
        """True if the event is a Dialogue entry."""
        return normalize_key(self._type) == 'dialogue'

    @property
    def is_comment(self) -> bool:
        """True if the event is a Comment entry."""
        return normalize_key(self._type) == 'comment'

    @property
    def line_number(self) -> int:
        return self._line_number

    @property
    def text(self) -> str:
        """The text content of the entry, synchronized with AST elements."""
        if self._ast_synced:
            from sublib.ass.text import AssTextRenderer
            return AssTextRenderer().render(self._text_elements)
        # Access via base __getitem__ which looks at _fields
        return self.get('text', "")

    @text.setter
    def text(self, value: str) -> None:
        self['text'] = value  # This will store in _fields via __setitem__
        self._ast_synced = False

    @property
    def text_elements(self) -> list[AssTextElement]:
        self._ensure_ast()
        return self._text_elements

    @text_elements.setter
    def text_elements(self, value: list[AssTextElement]) -> None:
        self._text_elements = value
        self._ast_synced = True

    def _ensure_ast(self):
        if not self._ast_synced:
            from sublib.ass.text import AssTextParser
            raw = self.get('text', "")
            self._text_elements = AssTextParser().parse(raw, line_number=self._line_number)
            self._ast_synced = True

    @property
    def duration(self) -> AssTimestamp:
        return self.end - self.start

    def extract_event_tags_and_segments(self) -> tuple[dict[str, Any], list[AssTextSegment]]:
        """Extract event-level tags and inline segments using a Differential Model."""
        from sublib.ass.text.transform import extract_event_tags_and_segments
        return extract_event_tags_and_segments(self.text_elements)

    @classmethod
    def from_dict(cls, data: dict[str, str], event_type: str = "Dialogue", line_number: int = 0, auto_fill: bool = True, diagnostics: list[Diagnostic] | None = None) -> AssEvent:
        """Create AssEvent with Eager Conversion and Identity mapping."""
        parsed_fields = {}
        extra_fields = {}
        
        for k, v in data.items():
            norm_k = normalize_key(k)
            v_str = str(v).strip()
            
            if norm_k in EVENT_IDENTITY_SCHEMA:
                schema = EVENT_IDENTITY_SCHEMA[norm_k]
                parsed_fields[schema.normalized_key] = schema.convert(v_str, diagnostics=diagnostics, line_number=line_number)
            else:
                extra_fields[norm_k] = v_str
        
        if auto_fill:
            for norm_key, schema in EVENT_IDENTITY_SCHEMA.items():
                if norm_key == schema.normalized_key and norm_key not in parsed_fields:
                    parsed_fields[norm_key] = schema.default
                    
        return cls(parsed_fields, type=event_type, line_number=line_number, extra_fields=extra_fields)

    def render_row(self, format_fields: list[str], auto_fill: bool = False) -> str:
        """Render AssEvent with standardized format support."""
        descriptor = self._type
        
        parts = []
        for raw_f in format_fields:
            norm_f = normalize_key(raw_f)
            
            if norm_f in EVENT_IDENTITY_SCHEMA:
                schema = EVENT_IDENTITY_SCHEMA[norm_f]
                val = self._fields.get(schema.normalized_key)
                if val is None and auto_fill:
                    val = schema.default
                parts.append(schema.format(val) if val is not None else "")
            else:
                # Custom/Extra field
                val = self._extra.get(norm_f, "")
                parts.append(str(val))
                
        return f"{descriptor}: {','.join(parts)}"

    @classmethod
    def create(cls, text: str | list[AssTextElement], start: str | AssTimestamp | int, end: str | AssTimestamp | int, **kwargs) -> AssEvent:
        """Robust factory using Pythonic Names."""
        def _to_timestamp(val: Any) -> AssTimestamp:
            if isinstance(val, AssTimestamp): return val
            if isinstance(val, int): return AssTimestamp.from_ms(val)
            return AssTimestamp.from_ass_str(str(val))

        event = cls(type=kwargs.get('type', AssEventType.DIALOGUE))
        event.start = _to_timestamp(start)
        event.end = _to_timestamp(end)
        
        if isinstance(text, str):
            event.text = text
        else:
            event._text_elements = text
            event._ast_synced = True
            
        # Add any other fields via kwargs
        for k, v in kwargs.items():
            if k not in ('type', 'start', 'end', 'text'):
                setattr(event, k, v)
                
        return event


class AssEvents(AssFormatSection):
    """Intelligent container for [Events] section."""
    def __init__(self, data: list[AssEvent] | None = None, original_name: str = "Events"):
        super().__init__("events", original_name)
        self._data = data if data is not None else []

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None, event_format: list[str] | None = [], auto_fill: bool = True) -> AssEvents:
        """Layer 2: Semantic ingestion with Symmetric Slicing and Auto-Fill Control."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        events = cls(original_name=raw.original_name)
        events.comments = list(raw.comments)
        
        # 1. Physical Reality
        if event_format:
            events.raw_format_fields = list(event_format)
        else:
            events.raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
        
        # 2. Ingest data based on Slicing Policy
        file_format_fields = raw.format_fields
        if not file_format_fields:
            events._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Events section", raw.line_number, "MISSING_FORMAT"))
            return events

        # Determine Ingestion Slice
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        if event_format:
            ingest_keys = {normalize_key(f) for f in event_format}
        elif event_format is None:
            ingest_keys = set(file_format_fields)
        else:
            if is_v4:
                ingest_keys = {'layer', 'start', 'end', 'style', 'name', 'marginl', 'marginr', 'marginv', 'effect', 'text', 'marked'}
            else:
                ingest_keys = {'layer', 'start', 'end', 'style', 'name', 'marginl', 'marginr', 'marginv', 'effect', 'text'}

        # Ingest records
        standard_descriptors = {normalize_key(t) for t in AssEventType.get_standard_types()}
        for record in raw.records:
            try:
                parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                record_dict = {name: val for name, val in zip(file_format_fields, parts)}
                
                # Apply Slicing Filter
                filtered_dict = {k: v for k, v in record_dict.items() if k in ingest_keys}
                
                if record.descriptor in standard_descriptors:
                    event = AssEvent.from_dict(filtered_dict, event_type=record.descriptor, line_number=record.line_number, auto_fill=auto_fill, diagnostics=events._diagnostics)
                    events.append(event)
                    
                    # 3. Field count check
                    actual_count = len(record.value.split(','))
                    expected_count = len(file_format_fields)
                    if actual_count < expected_count:
                        events._diagnostics.append(Diagnostic(
                            DiagnosticLevel.WARNING,
                            f"Field count mismatch in event at line {record.line_number}: found {actual_count}, expected {expected_count}",
                            record.line_number, "FIELD_COUNT_MISMATCH"
                        ))
                else:
                    events._custom_records.append(record)
            except Exception as e:
                events._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse event: {e}", record.line_number, "EVENT_PARSE_ERROR"))

        return events

    def __getitem__(self, index: int) -> AssEvent: return self._data[index]
    def __setitem__(self, index: int, event: AssEvent) -> None: self._data[index] = event
    def __delitem__(self, index: int) -> None: del self._data[index]
    def __len__(self) -> int: return len(self._data)
    def __iter__(self): return iter(self._data)
    def append(self, event: AssEvent) -> None: self._data.append(event)
    def add_all(self, events: Iterable[AssEvent]) -> None: self._data.extend(events)
    def set_all(self, events: Iterable[AssEvent]) -> None:
        self._data.clear()
        self._data.extend(events)

    def filter(self, style: str | None = None) -> list[AssEvent]:
        if style is None: return list(self._data)
        target = style.lower()
        return [e for e in self._data if e.style.lower() == target]

    def get_explicit_format(self, script_type: str | None = None) -> list[str]:
        """Union of all physical keys."""
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        if is_v4:
            standard = ['Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
        else:
            standard = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
            
        all_physical_keys = set()
        for event in self._data:
            for prop_key in event._fields:
                if prop_key in EVENT_IDENTITY_SCHEMA:
                    all_physical_keys.add(EVENT_IDENTITY_SCHEMA[prop_key].canonical_name)
                else:
                    all_physical_keys.add(prop_key)
        all_physical_keys.add('Text')
        
        result = []
        for f in standard:
            if normalize_key(f) in all_physical_keys:
                result.append(f)
                
        standard_normalized = {normalize_key(f) for f in standard}
        for field_key in sorted(all_physical_keys - standard_normalized):
             result.append(field_key)
             
        return result

    def render(self, script_type: str | None = None, auto_fill: bool = False) -> str:
        """Polymorphic render for Events section."""
        lines = self.render_header()
        
        # Format resolution logic
        is_v4 = script_type and "v4" in script_type.lower() and "+" not in script_type
        
        if self.raw_format_fields:
            # Normalize standard field names in the format header (Normalization over Fidelity)
            out_format = [
                EVENT_IDENTITY_SCHEMA[normalize_key(f)].canonical_name 
                if normalize_key(f) in EVENT_IDENTITY_SCHEMA else f 
                for f in self.raw_format_fields
            ]
        else:
            out_format = self.get_explicit_format(script_type)
            
        lines.append(f"Format: {', '.join(out_format)}")
        
        for event in self:
            lines.append(event.render_row(format_fields=out_format, auto_fill=auto_fill))
            
        for record in self._custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
            
        return "\n".join(lines)
