from __future__ import annotations
from typing import Any, Iterable, TYPE_CHECKING
from sublib.ass.types import AssColor
from sublib.ass.naming import normalize_key, get_canonical_name
from sublib.ass.tags.base import _format_float

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
    from sublib.ass.diagnostics import Diagnostic


def _format_bool(v: bool) -> str:
    return "1" if v else "0"



from .base import AssFormatSection
from .schema import FieldSchema, AssStructuredRecord

STYLE_SCHEMA = {
    'name': FieldSchema("", str, canonical_name='Name', python_prop='name'),
    'font_name': FieldSchema("Arial", str, canonical_name='Fontname', python_prop='font_name'),
    'font_size': FieldSchema(20.0, float, _format_float, canonical_name='Fontsize', python_prop='font_size'),
    'primary_color': FieldSchema(AssColor.from_style_str('&H00FFFFFF'), AssColor, canonical_name='PrimaryColour', python_prop='primary_color'),
    'secondary_color': FieldSchema(AssColor.from_style_str('&H000000FF'), AssColor, canonical_name='SecondaryColour', python_prop='secondary_color'),
    'outline_color': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor, canonical_name='OutlineColour', python_prop='outline_color'),
    'back_color': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor, canonical_name='BackColour', python_prop='back_color'),
    'bold': FieldSchema(False, bool, _format_bool, canonical_name='Bold', python_prop='bold'),
    'italic': FieldSchema(False, bool, _format_bool, canonical_name='Italic', python_prop='italic'),
    'underline': FieldSchema(False, bool, _format_bool, canonical_name='Underline', python_prop='underline'),
    'strikeout': FieldSchema(False, bool, _format_bool, canonical_name='StrikeOut', python_prop='strikeout'),
    'scale_x': FieldSchema(100.0, float, _format_float, canonical_name='ScaleX', python_prop='scale_x'),
    'scale_y': FieldSchema(100.0, float, _format_float, canonical_name='ScaleY', python_prop='scale_y'),
    'spacing': FieldSchema(0.0, float, _format_float, canonical_name='Spacing', python_prop='spacing'),
    'angle': FieldSchema(0.0, float, _format_float, canonical_name='Angle', python_prop='angle'),
    'border_style': FieldSchema(1, int, canonical_name='BorderStyle', python_prop='border_style'),
    'outline': FieldSchema(2.0, float, _format_float, canonical_name='Outline', python_prop='outline'),
    'shadow': FieldSchema(0.0, float, _format_float, canonical_name='Shadow', python_prop='shadow'),
    'alignment': FieldSchema(2, int, canonical_name='Alignment', python_prop='alignment'),
    'margin_l': FieldSchema(10, int, canonical_name='MarginL', python_prop='margin_l'),
    'margin_r': FieldSchema(10, int, canonical_name='MarginR', python_prop='margin_r'),
    'margin_v': FieldSchema(10, int, canonical_name='MarginV', python_prop='margin_v'),
    'encoding': FieldSchema(1, int, canonical_name='Encoding', python_prop='encoding'),
}

# Identity mapping for Styles (normalized_key -> FieldSchema)
STYLE_IDENTITY_SCHEMA = {s.normalized_key: s for s in STYLE_SCHEMA.values()}
# Support aliases
STYLE_IDENTITY_SCHEMA[normalize_key('PrimaryColor')] = STYLE_SCHEMA['primary_color']
STYLE_IDENTITY_SCHEMA[normalize_key('SecondaryColor')] = STYLE_SCHEMA['secondary_color']
STYLE_IDENTITY_SCHEMA[normalize_key('OutlineColor')] = STYLE_SCHEMA['outline_color']
STYLE_IDENTITY_SCHEMA[normalize_key('BackColor')] = STYLE_SCHEMA['back_color']
STYLE_IDENTITY_SCHEMA[normalize_key('MarginLeft')] = STYLE_SCHEMA['margin_l']
STYLE_IDENTITY_SCHEMA[normalize_key('MarginRight')] = STYLE_SCHEMA['margin_r']
STYLE_IDENTITY_SCHEMA[normalize_key('MarginVertical')] = STYLE_SCHEMA['margin_v']


class AssStyle(AssStructuredRecord):
    """ASS style definition using Schema-Driven Typed Storage."""
    
    def __init__(self, fields: dict[str, Any] | None = None, extra_fields: dict[str, Any] | None = None, **kwargs):
        super().__init__(STYLE_IDENTITY_SCHEMA, fields, extra_fields)
        
        # Apply standard properties via kwargs
        for name, value in kwargs.items():
            self[name] = value

    @property
    def extra_fields(self) -> dict[str, Any]:
        """Custom/non-standard fields."""
        return self._extra




class AssStyles(AssFormatSection):
    """Container for [Styles] section."""
    def __init__(self, data: dict[str, AssStyle] | None = None, original_name: str = "V4+ Styles"):
        # Default name is V4+ Styles for modern files
        super().__init__(normalize_key(original_name), original_name)
        self._data = data if data is not None else {}


    @property
    def section_comments(self) -> list[str]: return self.comments

    @property
    def custom_records(self) -> list[RawRecord]: return self._custom_records


    def __getitem__(self, name: str) -> AssStyle:
        canonical = self._get_canonical_name(name)
        if canonical not in self._data: raise KeyError(name)
        return self._data[canonical]

    def __setitem__(self, name: str, style: AssStyle) -> None:
        if name.lower() != style.name.lower():
            raise ValueError(f"Style name mismatch: {name} != {style.name}")
        self._data[style.name] = style

    def __delitem__(self, name: str) -> None:
        canonical = self._get_canonical_name(name)
        del self._data[canonical]

    def __contains__(self, name: str) -> bool:
        lower_name = name.lower()
        return any(k.lower() == lower_name for k in self._data)

    def get_explicit_format(self, script_type: str | None = None) -> list[str]:
        """Union of all physical keys in standard order."""
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        if is_v4:
            standard = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'TertiaryColour', 'BackColour', 'Bold', 'Italic', 'BorderStyle']
        else:
            standard = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'OutlineColour', 'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut', 'ScaleX', 'ScaleY', 'Spacing', 'Angle', 'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding']
        
        all_physical_keys = set()
        for style in self._data.values():
            for prop_key in style._fields:
                # Resolve prop_key (normalized_key) to canonical name via schema
                if prop_key in STYLE_IDENTITY_SCHEMA:
                    all_physical_keys.add(STYLE_IDENTITY_SCHEMA[prop_key].canonical_name)
                else:
                    all_physical_keys.add(prop_key)
        all_physical_keys.add('Name')
        
        result = []
        for f in standard:
            if normalize_key(f) in all_physical_keys:
                result.append(f)
        
        standard_normalized = {normalize_key(f) for f in standard}
        for field_key in sorted(all_physical_keys - standard_normalized):
             result.append(field_key)
             
        return result

    def __iter__(self): return iter(self._data.values())
    def __len__(self) -> int: return len(self._data)
    def keys(self): return self._data.keys()
    def values(self): return self._data.values()
    def items(self): return self._data.items()
    def get(self, name: str) -> AssStyle | None:
        canonical = self._get_canonical_name(name)
        return self._data.get(canonical)
    def set(self, style: AssStyle) -> None:
        self._data[style.name] = style
    def set_all(self, styles: Iterable[AssStyle]) -> None:
        self._data.clear()
        for s in styles: self.set(s)
