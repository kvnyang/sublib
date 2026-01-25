"""ASS Event models using Eager Sparse Typed Storage."""
from __future__ import annotations
from typing import Any, Iterable, Optional, TYPE_CHECKING, Literal
from sublib.ass.naming import normalize_key, get_canonical_name, AssEventType
from sublib.ass.models.text.elements import AssTextElement
from sublib.ass.types import AssTimestamp

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
    from sublib.ass.diagnostics import Diagnostic


# Mapping of Pythonic property names to normalized internal keys
PROPERTY_TO_KEY = {
    'layer': 'layer',
    'start': 'start',
    'end': 'end',
    'style': 'style',
    'name': 'name',
    'margin_l': 'marginl',
    'margin_r': 'marginr',
    'margin_v': 'marginv',
    'effect': 'effect',
    'text': 'text'
}


class FieldSchema:
    def __init__(self, default: Any, converter: Any, formatter: Any = str):
        self.default = default
        self.converter = converter
        self.formatter = formatter

    def convert(self, value: Any) -> Any:
        if isinstance(value, self.converter):
            return value
        raw_str = str(value).strip()
        if not raw_str:
            return self.default
        try:
            if self.converter == AssTimestamp:
                return AssTimestamp.from_ass_str(raw_str)
            if self.converter == int:
                return int(raw_str)
            return self.converter(raw_str)
        except (ValueError, TypeError):
            return self.default

    def format(self, value: Any) -> str:
        if value is None:
            return ""
        if hasattr(value, 'to_ass_str'):
            return value.to_ass_str()
        return str(value)


EVENT_SCHEMA = {
    'layer': FieldSchema(0, int),
    'marked': FieldSchema(0, int), # Alias
    'start': FieldSchema(AssTimestamp(), AssTimestamp),
    'end': FieldSchema(AssTimestamp(), AssTimestamp),
    'style': FieldSchema("Default", str),
    'name': FieldSchema("", str),
    'marginl': FieldSchema(0, int),
    'marginr': FieldSchema(0, int),
    'marginv': FieldSchema(0, int),
    'effect': FieldSchema("", str),
    'text': FieldSchema("", str),
}


class AssEvent:
    """ASS dialogue event using Eager Sparse Typed Storage."""
    
    def __init__(self, fields: dict[str, Any] | None = None, event_type: str = AssEventType.DIALOGUE, line_number: int = 0, extra_fields: dict[str, Any] | None = None, **kwargs):
        """Initialize AssEvent.
        
        Args:
            fields: Optional dictionary of normalized keys -> typed values (Internal use).
            event_type: The type of event (e.g. Dialogue, Comment, Picture). 
                        Accepts raw strings or AssEventType constants.
            line_number: Physical line number in file.
            extra_fields: Optional dictionary of custom/non-standard fields.
            **kwargs: Standard fields using snake_case (e.g., start=1000).
        """
        # We store Typed values for non-empty fields
        self._fields = fields if fields is not None else {}
        self._event_type = get_canonical_name(event_type, context='events')
        self._line_number = line_number
        # AST Sync
        self._text_elements: list[AssTextElement] = []
        self._ast_synced = False
        
        # Apply standard properties via kwargs
        for name, value in kwargs.items():
            if name in PROPERTY_TO_KEY:
                setattr(self, name, value)
            else:
                self[name] = value

        # Apply explicit extra_fields
        if extra_fields:
            for k, v in extra_fields.items():
                self[k] = v

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
            
        key = PROPERTY_TO_KEY.get(name)
        if key:
            return self[key]
            
        if name in self._fields:
            return self._fields[name]
            
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_') or name in ('event_type',):
            super().__setattr__(name, value)
            return
            
        # If it's the text property (or other future explicit properties), let the property setter handle it
        if hasattr(self.__class__, name) and isinstance(getattr(self.__class__, name), property):
            super().__setattr__(name, value)
            return

        key = PROPERTY_TO_KEY.get(name)
        if key:
            self[key] = value
        else:
            self[name] = value

    @property
    def event_type(self) -> str:
        """The canonical type of the event (e.g. 'Dialogue', 'Comment')."""
        return self._event_type
    
    @event_type.setter
    def event_type(self, value: str):
        self._event_type = get_canonical_name(value, context='events')

    @property
    def is_dialogue(self) -> bool:
        """True if the event is a Dialogue entry."""
        return normalize_key(self._event_type) == 'dialogue'

    @property
    def is_comment(self) -> bool:
        """True if the event is a Comment entry."""
        return normalize_key(self._event_type) == 'comment'

    def __getitem__(self, key: str) -> Any:
        norm_key = normalize_key(key)
        
        # 1. Text is special (requires AST sync)
        if norm_key == 'text':
             return self.text
             
        # 2. Sparse Physical Storage (Typed)
        if norm_key in self._fields:
            return self._fields[norm_key]
        
        # 3. Schema Default
        if norm_key in EVENT_SCHEMA:
            return EVENT_SCHEMA[norm_key].default
            
        return None

    def __setitem__(self, key: str, value: Any) -> None:
        norm_key = normalize_key(key)
        if norm_key == 'text':
            self.text = value
        elif norm_key in EVENT_SCHEMA:
            self._fields[norm_key] = EVENT_SCHEMA[norm_key].convert(value)
        else:
            self._fields[norm_key] = value

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

    @classmethod
    def from_dict(cls, data: dict[str, str], event_type: str = "Dialogue", line_number: int = 0, auto_fill: bool = True) -> AssEvent:
        """Create AssEvent with Eager Conversion and Symmetrical Auto-Fill.
        
        If auto_fill=True (Default): Missing standard fields take Schema defaults.
        If auto_fill=False: Missing fields stay out of _fields (results in None).
        """
        parsed_fields = {}
        for k, v in data.items():
            norm_k = normalize_key(k)
            v_str = str(v).strip()
            if norm_k in EVENT_SCHEMA:
                parsed_fields[norm_k] = EVENT_SCHEMA[norm_k].convert(v_str)
            else:
                parsed_fields[norm_k] = v_str
        
        # Handle Gaps
        if auto_fill:
            for k, schema in EVENT_SCHEMA.items():
                if k not in parsed_fields:
                    parsed_fields[k] = schema.default
                    
        return cls(parsed_fields, event_type=event_type, line_number=line_number)

    def render(self, format_fields: list[str] | None = None, auto_fill: bool = False) -> str:
        """Render event with Sparse Logic."""
        descriptor = get_canonical_name(self.event_type, context="events")
        
        if format_fields:
            out_keys = [normalize_key(f) for f in format_fields]
        else:
            # Default V4+ sequence
            out_keys = ['layer', 'start', 'end', 'style', 'name', 'marginl', 'marginr', 'marginv', 'effect', 'text']

        parts = []
        for key in out_keys:
            # Symmetrical Gap Logic (Phase 35):
            # 1. Physical Presence
            if key in self._fields and self._fields[key] is not None:
                val = self[key] # Uses property logic (synced Text)
                if key in EVENT_SCHEMA:
                    parts.append(EVENT_SCHEMA[key].format(val))
                else:
                    parts.append(str(val))
            # 2. Logical Presence (Auto-Fill)
            elif auto_fill:
                if key in EVENT_SCHEMA:
                    parts.append(EVENT_SCHEMA[key].format(EVENT_SCHEMA[key].default))
                else:
                    parts.append("")
            # 3. Gap
            else:
                parts.append("")
                
        return f"{descriptor}: {','.join(parts)}"

    @classmethod
    def create(cls, text: str | list[AssTextElement], start: str | AssTimestamp | int, end: str | AssTimestamp | int, **kwargs) -> AssEvent:
        """Robust factory using Pythonic Names."""
        def _to_timestamp(val: Any) -> AssTimestamp:
            if isinstance(val, AssTimestamp): return val
            if isinstance(val, int): return AssTimestamp.from_ms(val)
            return AssTimestamp.from_ass_str(str(val))

        event = cls(event_type=kwargs.get('event_type', AssEventType.DIALOGUE))
        event.start = _to_timestamp(start)
        event.end = _to_timestamp(end)
        
        if isinstance(text, str):
            event.text = text
        else:
            event._text_elements = text
            event._ast_synced = True
            
        # Add any other fields via kwargs
        for k, v in kwargs.items():
            if k not in ('event_type', 'start', 'end', 'text'):
                setattr(event, k, v)
                
        return event


class AssEvents:
    """Intelligent container for [Events] section."""
    def __init__(self, data: list[AssEvent] | None = None):
        self._data = data if data is not None else []
        self._custom_records: list[RawRecord] = []
        self._diagnostics: list[Diagnostic] = []
        self._section_comments: list[str] = []
        self._raw_format_fields: list[str] | None = None

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None, event_format: list[str] | None = [], auto_fill: bool = True) -> AssEvents:
        """Layer 2: Semantic ingestion with Symmetric Slicing and Auto-Fill Control."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        events = cls()
        events._section_comments = list(raw.comments)
        
        # 1. Physical Reality
        if event_format:
            events._raw_format_fields = list(event_format)
        else:
            events._raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
        
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
                    event = AssEvent.from_dict(filtered_dict, event_type=record.descriptor, line_number=record.line_number, auto_fill=auto_fill)
                    events.append(event)
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

    @property
    def diagnostics(self) -> list[Diagnostic]: return self._diagnostics
    @property
    def section_comments(self) -> list[str]: return self._section_comments
    def get_comments(self) -> list[str]: return list(self._section_comments)
    @property
    def custom_records(self) -> list[RawRecord]: return self._custom_records
