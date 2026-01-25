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


from sublib.ass.naming import STYLE_PROP_TO_KEY as PROPERTY_TO_KEY, STYLE_KEY_TO_PROP as KEY_TO_PROPERTY


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
    'font_name': FieldSchema("Arial", str),
    'font_size': FieldSchema(20.0, float, _format_float),
    'primary_color': FieldSchema(AssColor.from_style_str('&H00FFFFFF'), AssColor),
    'secondary_color': FieldSchema(AssColor.from_style_str('&H000000FF'), AssColor),
    'outline_color': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor),
    'back_color': FieldSchema(AssColor.from_style_str('&H00000000'), AssColor),
    'bold': FieldSchema(False, bool, _format_bool),
    'italic': FieldSchema(False, bool, _format_bool),
    'underline': FieldSchema(False, bool, _format_bool),
    'strikeout': FieldSchema(False, bool, _format_bool),
    'scale_x': FieldSchema(100.0, float, _format_float),
    'scale_y': FieldSchema(100.0, float, _format_float),
    'spacing': FieldSchema(0.0, float, _format_float),
    'angle': FieldSchema(0.0, float, _format_float),
    'border_style': FieldSchema(1, int),
    'outline': FieldSchema(2.0, float, _format_float),
    'shadow': FieldSchema(0.0, float, _format_float),
    'alignment': FieldSchema(2, int),
    'margin_l': FieldSchema(10, int),
    'margin_r': FieldSchema(10, int),
    'margin_v': FieldSchema(10, int),
    'encoding': FieldSchema(1, int),
}


class AssStyle:
    """ASS style definition using Eager Sparse Typed Storage."""
    
    def __init__(self, fields: dict[str, Any] | None = None, extra_fields: dict[str, Any] | None = None, **kwargs):
        """Initialize AssStyle.
        
        Args:
            fields: Optional dictionary of snake_case field names -> typed values (Internal use).
            extra_fields: Optional dictionary of custom/non-standard fields.
            **kwargs: Standard fields using snake_case (e.g., primary_color="&H0000FF").
        """
        # Internal fields using snake_case keys for standard fields
        self._fields = fields if fields is not None else {}
        # Separate storage for custom/non-standard fields
        self._extra = extra_fields if extra_fields is not None else {}
        
        # Apply standard properties via kwargs
        for name, value in kwargs.items():
            if name in PROPERTY_TO_KEY:
                setattr(self, name, value)
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
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
            
        if name in PROPERTY_TO_KEY:
            # Standard property - use __setitem__ for conversion
            self[name] = value
        else:
            self._extra[normalize_key(name)] = value

    def __getitem__(self, key: str) -> Any:
        # Enforce Pythonic-only keys for standard fields
        if key in PROPERTY_TO_KEY:
            # Check sparse storage
            if key in self._fields:
                return self._fields[key]
            # Schema default fallback
            schema = STYLE_SCHEMA.get(key)
            return schema.default if schema else None
        
        # Fallback to extra fields
        if key in self._extra:
            return self._extra[key]
            
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        # Enforce Pythonic-only keys for standard fields
        if key in PROPERTY_TO_KEY:
            schema = STYLE_SCHEMA[key]
            self._fields[key] = schema.convert(value)
        else:
            self._extra[normalize_key(key)] = value

    def get(self, key: str, default: Any = None) -> Any:
        val = self[key]
        return val if val is not None else default

    @classmethod
    def from_dict(cls, data: dict[str, str], auto_fill: bool = True) -> AssStyle:
        """Create AssStyle with Eager Conversion and Pythonic storage."""
        from sublib.ass.naming import STYLE_KEY_TO_PROP as KEY_TO_PROPERTY
        parsed_fields = {}
        extra_fields = {}
        
        for k, v in data.items():
            norm_k = normalize_key(k)
            prop = KEY_TO_PROPERTY.get(norm_k)
            v_str = str(v).strip()
            
            if prop:
                parsed_fields[prop] = STYLE_SCHEMA[prop].convert(v_str)
            else:
                extra_fields[norm_k] = v_str
        
        if auto_fill:
            for prop, schema in STYLE_SCHEMA.items():
                if prop not in parsed_fields:
                    parsed_fields[prop] = schema.default
                    
        return cls(parsed_fields, extra_fields=extra_fields)

    def render(self, format_fields: list[str] | None = None, auto_fill: bool = False) -> str:
        """Render AssStyle with Pythonic-to-Canonical mapping."""
        from sublib.ass.naming import STYLE_KEY_TO_PROP as KEY_TO_PROPERTY
        descriptor = get_canonical_name("Style", context="v4+ styles")
        
        if format_fields:
            out_keys = [normalize_key(f) for f in format_fields]
        else:
            # Default V4+ sequence
            out_keys = [PROPERTY_TO_KEY[p] for p in ('name', 'font_name', 'font_size', 'primary_color', 'secondary_color', 'outline_color', 'back_color', 'bold', 'italic', 'underline', 'strikeout', 'scale_x', 'scale_y', 'spacing', 'angle', 'border_style', 'outline', 'shadow', 'alignment', 'margin_l', 'margin_r', 'margin_v', 'encoding')]

        parts = []
        for key in out_keys:
            prop = KEY_TO_PROPERTY.get(key)
            
            val = None
            if prop:
                val = self._fields.get(prop)
                if val is None and auto_fill:
                    val = STYLE_SCHEMA[prop].default
                
                parts.append(STYLE_SCHEMA[prop].format(val) if val is not None else "")
            else:
                # Custom field
                val = self._extra.get(key)
                parts.append(str(val) if val is not None else "")
                
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
    def from_raw(cls, raw: RawSection, script_type: str | None = None, style_format: list[str] | None = [], auto_fill: bool = True) -> AssStyles:
        """Layer 2: Semantic ingestion with Symmetric Slicing and Auto-Fill Control."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        styles = cls()
        styles._section_comments = list(raw.comments)
        
        # 1. Physical Reality
        if style_format:
            styles._raw_format_fields = list(style_format)
        else:
            styles._raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
        
        # 2. Ingest data based on Slicing Policy
        file_format_fields = raw.format_fields # Normalized columns present in file
        if not file_format_fields:
            styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Styles section", raw.line_number, "MISSING_FORMAT"))
            return styles

        # Determine Ingestion Slice
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        if style_format:
            ingest_keys = {normalize_key(f) for f in style_format}
        elif style_format is None:
            ingest_keys = set(file_format_fields) # No filter
        else:
            # Standard Slice
            if is_v4:
                std = {'name', 'fontname', 'fontsize', 'primarycolour', 'secondarycolour', 'tertiarycolour', 'backcolour', 'bold', 'italic', 'borderstyle'}
            else:
                std = {'name', 'fontname', 'fontsize', 'primarycolour', 'secondarycolour', 'outlinecolour', 'backcolour', 'bold', 'italic', 'underline', 'strikeout', 'scalex', 'scaley', 'spacing', 'angle', 'borderstyle', 'outline', 'shadow', 'alignment', 'marginl', 'marginr', 'marginv', 'encoding'}
            ingest_keys = std

        for record in raw.records:
            if record.descriptor == 'style':
                try:
                    parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                    record_dict = {name: val for name, val in zip(file_format_fields, parts)}
                    
                    # Apply Slicing Filter
                    filtered_dict = {k: v for k, v in record_dict.items() if k in ingest_keys}
                    
                    style = AssStyle.from_dict(filtered_dict, auto_fill=auto_fill)
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
            for prop in style._fields:
                all_physical_keys.add(PROPERTY_TO_KEY[prop])
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
