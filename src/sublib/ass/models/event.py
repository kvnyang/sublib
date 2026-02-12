"""ASS Event models using Eager Sparse Typed Storage."""
from __future__ import annotations
from typing import Any, Iterable, Optional, TYPE_CHECKING, Literal
from sublib.ass.core.naming import normalize_key, get_canonical_name, AssEventType
from sublib.ass.models.text.elements import AssTextElement
from sublib.ass.types import AssTimestamp

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
    from sublib.ass.core.diagnostics import Diagnostic



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
            from sublib.ass.engines.text import AssTextRenderer
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
            from sublib.ass.engines.text import AssTextParser
            raw = self.get('text', "")
            self._text_elements = AssTextParser().parse(raw, line_number=self._line_number)
            self._ast_synced = True

    @property
    def duration(self) -> AssTimestamp:
        return self.end - self.start

    def extract_event_tags_and_segments(self) -> tuple[dict[str, Any], list[AssTextSegment]]:
        """Extract event-level tags and inline segments using a Differential Model."""
        from sublib.ass.engines.text.text_transform import extract_event_tags_and_segments
        return extract_event_tags_and_segments(self.text_elements)



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

