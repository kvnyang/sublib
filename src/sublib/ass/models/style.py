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


# Mapping of Python property names to normalized ASS field names
PROPERTY_TO_KEY = {
    'name': 'name',
    'fontname': 'fontname',
    'fontsize': 'fontsize',
    'primary_color': 'primarycolour',
    'secondary_color': 'secondarycolour',
    'outline_color': 'outlinecolour',
    'back_color': 'backcolour',
    'bold': 'bold',
    'italic': 'italic',
    'underline': 'underline',
    'strikeout': 'strikeout',
    'scale_x': 'scalex',
    'scale_y': 'scaley',
    'spacing': 'spacing',
    'angle': 'angle',
    'border_style': 'borderstyle',
    'outline': 'outline',
    'shadow': 'shadow',
    'alignment': 'alignment',
    'margin_l': 'marginl',
    'margin_r': 'marginr',
    'margin_v': 'marginv',
    'encoding': 'encoding'
}


class FieldSchema:
    def __init__(self, default: Any, converter: Any, formatter: Any = str):
        self.default = default
        self.converter = converter
        self.formatter = formatter

    def convert(self, value: Any) -> Any:
        # If it's already the right type, great.
        if isinstance(value, self.converter):
            return value
            
        # If it's empty string or None, we return the default.
        # (Note: In 'Sparse' mode, we won't even call this if the raw string was empty, 
        # but this is here for safety/setter logic).
        raw_str = str(value).strip()
        if not raw_str:
            return self.default
            
        try:
            if self.converter == bool:
                return raw_str not in ('0', 'false', 'False', '')
            if self.converter == int:
                return int(raw_str)
            if self.converter == float:
                return float(raw_str)
            if self.converter == AssColor:
                return AssColor.from_style_str(raw_str)
            if self.converter == str:
                return raw_str
            return self.converter(raw_str)
        except (ValueError, TypeError):
            return self.default

    def format(self, value: Any) -> str:
        if value is None:
            return ""
        if self.formatter == _format_float:
            return _format_float(value)
        if self.formatter == _format_bool:
            return _format_bool(bool(value))
        if hasattr(value, 'to_style_str'):
            return value.to_style_str()
        return str(value)


STYLE_SCHEMA = {
    'name': FieldSchema("", str),
    'fontname': FieldSchema("Arial", str),
    'fontsize': FieldSchema(20.0, float, _format_float),
    'primarycolour': FieldSchema(AssColor.from_style_str('&H00FFFFFF'), AssColor),
    'secondarycolour': FieldSchema(AssColor.from_style_str('&H000000FF'), AssColor),
    'outlinecolour': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor),
    'tertiarycolour': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor),
    'backcolour': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor),
    'bold': FieldSchema(False, bool, _format_bool),
    'italic': FieldSchema(False, bool, _format_bool),
    'underline': FieldSchema(False, bool, _format_bool),
    'strikeout': FieldSchema(False, bool, _format_bool),
    'scalex': FieldSchema(100.0, float, _format_float),
    'scaley': FieldSchema(100.0, float, _format_float),
    'spacing': FieldSchema(0.0, float, _format_float),
    'angle': FieldSchema(0.0, float, _format_float),
    'borderstyle': FieldSchema(1, int),
    'outline': FieldSchema(2.0, float, _format_float),
    'shadow': FieldSchema(0.0, float, _format_float),
    'alignment': FieldSchema(2, int),
    'marginl': FieldSchema(10, int),
    'marginr': FieldSchema(10, int),
    'marginv': FieldSchema(10, int),
    'encoding': FieldSchema(1, int),
}


class AssStyle:
    """ASS style definition using Eager Sparse Typed Storage."""
    
    def __init__(self, fields: dict[str, Any] | None = None):
        # We store normalized keys -> Typed Values
        self._fields = fields if fields is not None else {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
            
        key = PROPERTY_TO_KEY.get(name)
        if key:
            return self[key]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
            
        key = PROPERTY_TO_KEY.get(name)
        if key:
            self[key] = value
        else:
            super().__setattr__(name, value)

    def __getitem__(self, key: str) -> Any:
        norm_key = normalize_key(key)
        
        # 1. Sparse Storage Check (Already Typed)
        if norm_key in self._fields:
            return self._fields[norm_key]
            
        # 2. Schema default
        if norm_key in STYLE_SCHEMA:
            return STYLE_SCHEMA[norm_key].default
            
        # 3. Aliases
        if norm_key == 'tertiarycolour' and 'outlinecolour' in self._fields:
            return self._fields['outlinecolour']
            
        return None

    def __setitem__(self, key: str, value: Any) -> None:
        norm_key = normalize_key(key)
        # Eager parsing on assignment
        if norm_key in STYLE_SCHEMA:
            self._fields[norm_key] = STYLE_SCHEMA[norm_key].convert(value)
        else:
            self._fields[norm_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        val = self[key]
        return val if val is not None else default

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> AssStyle:
        """Create AssStyle with Eager Conversion and Sparse Storage."""
        parsed_fields = {}
        for k, v in data.items():
            norm_k = normalize_key(k)
            v_str = str(v).strip()
            # Sparse: Skip empty physical fields
            if not v_str:
                continue
                
            if norm_k in STYLE_SCHEMA:
                parsed_fields[norm_k] = STYLE_SCHEMA[norm_k].convert(v_str)
            else:
                parsed_fields[norm_k] = v_str
        
        return cls(parsed_fields)

    def render(self, format_fields: list[str] | None = None, auto_fill: bool = False) -> str:
        """Render AssStyle with Sparse Logic."""
        descriptor = get_canonical_name("Style", context="v4+ styles")
        
        if format_fields:
            out_keys = [normalize_key(f) for f in format_fields]
        else:
            # Default V4+ sequence
            out_keys = [
                'name', 'fontname', 'fontsize', 'primarycolour', 'secondarycolour',
                'outlinecolour', 'backcolour', 'bold', 'italic', 'underline', 'strikeout',
                'scalex', 'scaley', 'spacing', 'angle', 'borderstyle', 'outline', 'shadow',
                'alignment', 'marginl', 'marginr', 'marginv', 'encoding'
            ]

        parts = []
        for key in out_keys:
            # 1. If we have it, use it.
            if key in self._fields:
                val = self._fields[key]
                if key in STYLE_SCHEMA:
                    parts.append(STYLE_SCHEMA[key].format(val))
                else:
                    parts.append(str(val))
            # 2. If we don't, check if we should auto-fill
            elif auto_fill or key == 'name' or (format_fields is not None):
                # Using defaults to satisfy the requested format/view
                if key in STYLE_SCHEMA:
                    parts.append(STYLE_SCHEMA[key].format(STYLE_SCHEMA[key].default))
                else:
                    parts.append("")
            # 3. Otherwise, pure sparse blank
            else:
                parts.append("")
                
        return f"{descriptor}: {','.join(parts)}"


class AssStyles:
    """Container for [Styles] section."""
    def __init__(self, data: dict[str, AssStyle] | None = None):
        self._data = data if data is not None else {}
        self._custom_records: list[RawRecord] = []
        self._diagnostics: list[Diagnostic] = []
        self._section_comments: list[str] = []
        self._raw_format_fields: list[str] | None = None

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None) -> AssStyles:
        """Layer 2: Semantic ingestion (Stateless Total Ingestion)."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        styles = cls()
        styles._section_comments = list(raw.comments)
        
        # 1. Physical Reality (Permanent)
        styles._raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
        
        # 2. Ingest ALL physical data
        file_format_fields = raw.format_fields # Normalized
        if not file_format_fields:
            styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Styles section", raw.line_number, "MISSING_FORMAT"))
            return styles

        for record in raw.records:
            if record.descriptor == 'style':
                try:
                    parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                    record_dict = {name: val for name, val in zip(file_format_fields, parts)}
                    style = AssStyle.from_dict(record_dict)
                    if style.name in styles:
                        styles._diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, f"Duplicate style name '{style.name}'", record.line_number, "DUPLICATE_STYLE_NAME"))
                    styles.set(style)
                except Exception as e:
                     styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse style: {e}", record.line_number, "STYLE_PARSE_ERROR"))
            else:
                styles._custom_records.append(record)

        return styles

    @property
    def diagnostics(self) -> list[Diagnostic]: return self._diagnostics

    @property
    def section_comments(self) -> list[str]: return self._section_comments

    @property
    def custom_records(self) -> list[RawRecord]: return self._custom_records

    def _get_canonical_name(self, name: str) -> str:
        if name in self._data: return name
        lower_name = name.lower()
        for k in self._data:
            if k.lower() == lower_name: return k
        return name

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
            all_physical_keys.update(style._fields.keys())
        all_physical_keys.add('name')
        
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
