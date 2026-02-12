"""ASS Event models using Eager Sparse Typed Storage."""
from __future__ import annotations
from typing import Any, Iterable, Optional, TYPE_CHECKING, Literal
from sublib.ass.naming import normalize_key, get_canonical_name, AssEventType
from sublib.ass.models.text.elements import AssTextElement
from sublib.ass.types import AssTimestamp

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
    from sublib.ass.diagnostics import Diagnostic


from sublib.ass.naming import EVENT_PROP_TO_KEY as PROPERTY_TO_KEY, EVENT_KEY_TO_PROP as KEY_TO_PROPERTY
from .base import AssFormatSection


class FieldSchema:
    def __init__(self, default: Any, converter: Any, field_name: str = ""):
        self.default = default
        self.converter = converter
        self.field_name = field_name

    def convert(self, value: Any, diagnostics: list[Diagnostic] | None = None, line_number: int = 0) -> Any:
        if isinstance(value, self.converter):
            return value
        raw_str = str(value).strip()
        if not raw_str:
            return self.default
        try:
            if self.converter == AssTimestamp:
                if isinstance(value, int):
                    return AssTimestamp.from_ms(value)
                return AssTimestamp.from_ass_str(raw_str)
            if self.converter == int:
                return int(raw_str)
            if self.converter == str:
                return raw_str
            return self.converter(raw_str)
        except (ValueError, TypeError):
            if diagnostics is not None:
                from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
                diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Invalid value for {self.field_name or 'field'}: '{raw_str}' (expected {self.converter.__name__ if hasattr(self.converter, '__name__') else self.converter}). Falling back to default: {self.default}",
                    line_number, "INVALID_VALUE_TYPE"
                ))
            return self.default

    def format(self, value: Any) -> str:
        if value is None:
            return ""
        if hasattr(value, 'to_ass_str'):
            return value.to_ass_str()
        return str(value)


EVENT_SCHEMA = {
    'layer': FieldSchema(0, int, field_name='Layer'),
    'start': FieldSchema(AssTimestamp(), AssTimestamp, field_name='Start'),
    'end': FieldSchema(AssTimestamp(), AssTimestamp, field_name='End'),
    'style': FieldSchema("Default", str, field_name='Style'),
    'name': FieldSchema("", str, field_name='Name'),
    'margin_l': FieldSchema(0, int, field_name='MarginL'),
    'margin_r': FieldSchema(0, int, field_name='MarginR'),
    'margin_v': FieldSchema(0, int, field_name='MarginV'),
    'effect': FieldSchema("", str, field_name='Effect'),
    'text': FieldSchema("", str, field_name='Text'),
}


class AssEvent:
    """ASS dialogue event using Eager Sparse Typed Storage."""
    
    def __init__(self, fields: dict[str, Any] | None = None, type: str = AssEventType.DIALOGUE, line_number: int = 0, extra_fields: dict[str, Any] | None = None, **kwargs):
        """Initialize AssEvent.
        
        Args:
            fields: Optional dictionary of snake_case field names -> typed values (Internal use).
            type: The type of event (e.g. Dialogue, Comment, Picture). 
                  Accepts raw strings or AssEventType constants.
            line_number: Physical line number in file.
            extra_fields: Optional dictionary of custom/non-standard fields.
            **kwargs: Standard fields using snake_case (e.g., start=1000).
        """
        # Internal fields using snake_case keys for standard fields
        self._fields = fields if fields is not None else {}
        # Separate storage for custom/non-standard fields
        self._extra = extra_fields if extra_fields is not None else {}
        
        self._type = get_canonical_name(type, context='events')
        self._line_number = line_number
        # AST Sync
        self._text_elements: list[AssTextElement] = []
        self._ast_synced = False
        
        # Apply standard properties via kwargs
        for name, value in kwargs.items():
            if name in PROPERTY_TO_KEY:
                self[name] = value
            else:
                self._extra[normalize_key(name)] = value

    @property
    def extra_fields(self) -> dict[str, Any]:
        """Custom/non-standard fields."""
        return self._extra

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
            
        if name in PROPERTY_TO_KEY:
            return self[name]
            
        norm_name = normalize_key(name)
        if norm_name in self._extra:
            return self._extra[norm_name]
            
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_') or name in ('_type',):
            super().__setattr__(name, value)
            return
            
        if name in PROPERTY_TO_KEY:
            # Standard property - use __setitem__ for conversion
            self[name] = value
        else:
            self._extra[normalize_key(name)] = value

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

    def __getitem__(self, key: str) -> Any:
        # Enforce Pythonic-only keys for standard fields
        if key in PROPERTY_TO_KEY:
            # Text is special (requires AST sync)
            if key == 'text':
                 return self.text
                 
            # Check sparse storage
            if key in self._fields:
                return self._fields[key]
            
            # Schema default fallback
            schema = EVENT_SCHEMA.get(key)
            return schema.default if schema else None
        
        # Fallback to extra fields
        if key in self._extra:
            return self._extra[key]
            
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        # Enforce Pythonic-only keys for standard fields
        if key in PROPERTY_TO_KEY:
            if key == 'text':
                self.text = value
            else:
                schema = EVENT_SCHEMA[key]
                self._fields[key] = schema.convert(value)
        else:
            self._extra[normalize_key(key)] = value

    def __delitem__(self, key: str) -> None:
        if key in self._fields:
            del self._fields[key]
        elif key in self._extra:
            del self._extra[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self._fields or key in self._extra

    @property
    def text(self) -> str:
        if self._ast_synced:
            from sublib.ass.text import AssTextRenderer
            return AssTextRenderer().render(self._text_elements)
        return self._fields.get('text', "")

    @text.setter
    def text(self, value: str) -> None:
        self._fields['text'] = value
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
            raw = self._fields.get('text', "")
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
        """Create AssEvent with Eager Conversion and Pythonic storage."""
        from sublib.ass.naming import EVENT_KEY_TO_PROP as KEY_TO_PROPERTY
        parsed_fields = {}
        extra_fields = {}
        
        for k, v in data.items():
            norm_k = normalize_key(k)
            prop = KEY_TO_PROPERTY.get(norm_k)
            v_str = str(v).strip()
            
            if prop:
                parsed_fields[prop] = EVENT_SCHEMA[prop].convert(v_str, diagnostics=diagnostics, line_number=line_number)
            else:
                extra_fields[norm_k] = v_str
        
        # Handle Gaps
        if auto_fill:
            for prop, schema in EVENT_SCHEMA.items():
                if prop not in parsed_fields:
                    parsed_fields[prop] = schema.default
                    
        return cls(parsed_fields, type=event_type, line_number=line_number, extra_fields=extra_fields)

    def render_row(self, format_fields: list[str], auto_fill: bool = False) -> str:
        """Render AssEvent with Pythonic-to-Canonical mapping."""
        from sublib.ass.naming import EVENT_KEY_TO_PROP as KEY_TO_PROPERTY
        descriptor = self._type
        
        out_keys = [normalize_key(f) for f in format_fields]
        parts = []
        for key in out_keys:
            prop = KEY_TO_PROPERTY.get(key)
            
            val = None
            if prop:
                val = self[prop]
                if val is None and auto_fill:
                    val = EVENT_SCHEMA[prop].default
                
                parts.append(EVENT_SCHEMA[prop].format(val) if val is not None else "")
            else:
                # Custom field
                val = self[key]
                parts.append(str(val) if val is not None else "")
                
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
            all_physical_keys.update(event._fields.keys())
        all_physical_keys.add('text')
        
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
            out_format = self.raw_format_fields
        else:
            out_format = self.get_explicit_format(script_type)
            
        lines.append(f"Format: {', '.join(out_format)}")
        
        for event in self:
            lines.append(event.render_row(format_fields=out_format, auto_fill=auto_fill))
            
        for record in self._custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
            
        return "\n".join(lines)
