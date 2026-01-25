from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
from sublib.ass.types import AssColor
from sublib.ass.naming import normalize_key, get_canonical_name


# Mapping of Python property names to normalized ASS field names
STYLE_FIELD_MAP = {
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


@dataclass
class AssStyle:
    """ASS style definition.
    
    Represents a style from the [V4+ Styles] or [V4 Styles] section.
    """
    name: str
    fontname: str
    fontsize: float
    primary_color: AssColor
    secondary_color: AssColor
    outline_color: AssColor  # Maps to TertiaryColour in v4
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
    # For custom fields preservation: Stores normalized_key -> raw_value
    extra_fields: dict[str, str] = field(default_factory=dict)
    # Track which fields were explicitly provided or set
    _explicit_fields: set[str] = field(default_factory=set, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> AssStyle:
        """Create AssStyle from a dictionary of standardized field names."""
        def get_field(names: list[str], default: str = "") -> str:
            for n in names:
                if n in data: return data[n]
            return default

        # Keys already standardized (normalized) by the parser or caller
        known_standard = {
            'name', 'fontname', 'fontsize', 'primarycolour', 'secondarycolour',
            'outlinecolour', 'tertiarycolour', 'backcolour', 'bold', 'italic',
            'underline', 'strikeout', 'scalex', 'scaley', 'spacing', 'angle',
            'borderstyle', 'outline', 'shadow', 'alignment', 'marginl', 'marginr',
            'marginv', 'encoding'
        }
        
        extra = {}
        for k, v in data.items():
            if k not in known_standard:
                extra[k] = v

        explicit = {normalize_key(k) for k, v in data.items() if v.strip()}

        return cls(
            name=get_field(['name']).strip(),
            fontname=get_field(['fontname']).strip(),
            fontsize=float(get_field(['fontsize'], '0')),
            primary_color=AssColor.from_style_str(get_field(['primarycolour'])),
            secondary_color=AssColor.from_style_str(get_field(['secondarycolour'])),
            outline_color=AssColor.from_style_str(get_field(['outlinecolour', 'tertiarycolour'])),
            back_color=AssColor.from_style_str(get_field(['backcolour'])),
            bold=get_field(['bold'], '0').strip() != '0',
            italic=get_field(['italic'], '0').strip() != '0',
            underline=get_field(['underline'], '0').strip() != '0',
            strikeout=get_field(['strikeout'], '0').strip() != '0',
            scale_x=float(get_field(['scalex'], '100')),
            scale_y=float(get_field(['scaley'], '100')),
            spacing=float(get_field(['spacing'], '0')),
            angle=float(get_field(['angle'], '0')),
            border_style=int(get_field(['borderstyle'], '1')),
            outline=float(get_field(['outline'], '2')),
            shadow=float(get_field(['shadow'], '0')),
            alignment=int(get_field(['alignment'], '2')),
            margin_l=int(get_field(['marginl'], '10')),
            margin_r=int(get_field(['marginr'], '10')),
            margin_v=int(get_field(['marginv'], '10')),
            encoding=int(get_field(['encoding'], '1')),
            extra_fields=extra,
            _explicit_fields=explicit
        )

    def __setattr__(self, name: str, value: Any) -> None:
        # Track manual property changes in _explicit_fields
        # We only track if _explicit_fields already exists (not during early __init__)
        # and if the field is one of the mapped ones.
        if name in STYLE_FIELD_MAP:
             try:
                 expl = self.__dict__.get('_explicit_fields')
                 if expl is not None:
                     expl.add(STYLE_FIELD_MAP[name])
             except Exception:
                 pass
        super().__setattr__(name, value)


    def render(self, format_fields: list[str] | None = None, auto_fill: bool = False) -> str:
        """Render AssStyle to Style: line according to requested format fields.
        
        Args:
            format_fields: List of raw field names to output. If None, uses internal defaults.
            auto_fill: If True, fills missing explicit fields with defaults. Default False (Transparent).
        """
        from sublib.ass.tags.base import _format_float
        descriptor = get_canonical_name("Style", context="v4+ styles")
        
        # Mapping of standardized key -> actual value
        vals = {
            'name': self.name,
            'fontname': self.fontname,
            'fontsize': _format_float(self.fontsize),
            'primarycolour': self.primary_color.to_style_str(),
            'secondarycolour': self.secondary_color.to_style_str(),
            'tertiarycolour': self.outline_color.to_style_str(), # Alias for outline in V4
            'outlinecolour': self.outline_color.to_style_str(),
            'backcolour': self.back_color.to_style_str(),
            'bold': str(int(self.bold)),
            'italic': str(int(self.italic)),
            'underline': str(int(self.underline)),
            'strikeout': str(int(self.strikeout)),
            'scalex': _format_float(self.scale_x),
            'scaley': _format_float(self.scale_y),
            'spacing': _format_float(self.spacing),
            'angle': _format_float(self.angle),
            'borderstyle': str(self.border_style),
            'outline': _format_float(self.outline),
            'shadow': _format_float(self.shadow),
            'alignment': str(self.alignment),
            'marginl': str(self.margin_l),
            'marginr': str(self.margin_r),
            'marginv': str(self.margin_v),
            'encoding': str(self.encoding)
        }
        
        # Add extra fields (mapped by normalized key)
        extra_vals = {normalize_key(k): v for k, v in self.extra_fields.items()}
        
        if format_fields:
            field_values = []
            for f in format_fields:
                key = normalize_key(f)
                
                # Check if field should be rendered (is explicit or auto-fill is on)
                # Note: 'name' is always mandatory for a meaningful Style line
                is_explicit = key in self._explicit_fields or key == 'name'
                
                if is_explicit or auto_fill:
                    # Priority: extra_vals (preserved raw data) > vals (properties)
                    if key in extra_vals:
                        field_values.append(extra_vals[key])
                    elif key in vals:
                        field_values.append(vals[key])
                    else:
                        field_values.append("") # Unknown field
                else:
                    field_values.append("") # Not explicit, no auto-fill
            return f"{descriptor}: {','.join(field_values)}"

        # Default V4+ render (backward compatibility)
        return (
            f"{descriptor}: {self.name},{self.fontname},{vals['fontsize']},"
            f"{vals['primarycolour']},{vals['secondarycolour']},"
            f"{vals['outlinecolour']},{vals['backcolour']},"
            f"{vals['bold']},{vals['italic']},{vals['underline']},{vals['strikeout']},"
            f"{vals['scalex']},{vals['scaley']},"
            f"{vals['spacing']},{vals['angle']},"
            f"{vals['borderstyle']},{vals['outline']},{vals['shadow']},"
            f"{vals['alignment']},{vals['marginl']},{vals['marginr']},{vals['marginv']},{vals['encoding']}"
        )


class AssStyles:
    """Intelligent container for [V4+ Styles] section."""
    def __init__(self, data: dict[str, AssStyle] | None = None):
        self._data = data if data is not None else {}
        self._custom_records: list[RawRecord] = []
        self._diagnostics: list[Diagnostic] = []
        self._section_comments: list[str] = []
        self._raw_format_fields: list[str] | None = None

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None, style_format: list[str] | None = None) -> AssStyles:
        """Layer 2: Semantic ingestion from a RawSection.
        
        Args:
            raw: The RawSection containing data.
            script_type: Optional ScriptType hint.
            style_format: Optional format override to filter which fields are ingested as explicit.
        """
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        styles = cls()
        styles._section_comments = list(raw.comments)
        
        # Determine active format fields for this ingestion
        if style_format:
             styles._raw_format_fields = style_format
             parsing_fields = [normalize_key(f) for f in style_format]
        else:
             styles._raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
             parsing_fields = raw.format_fields
        
        if not raw.format_fields:
            # StructParser should have caught this, but safety first
            styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Styles section", raw.line_number, "MISSING_FORMAT"))
            return styles

        # 1. Mandatory field verification
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        
        # Determine actual file format for parsing records
        file_format_fields = raw.format_fields # Normalized keys from Layer 1
        
        # User defined mandatory sets for validation
        V4_MANDATORY = {'name', 'fontname', 'fontsize', 'primarycolour', 'secondarycolour', 
                        'tertiarycolour', 'backcolour', 'bold', 'italic', 'borderstyle'}
        V4PLUS_MANDATORY = {'name', 'fontname', 'fontsize', 'primarycolour', 'secondarycolour', 
                            'outlinecolour', 'backcolour', 'bold', 'italic', 'underline', 
                            'strikeout', 'scalex', 'scaley', 'spacing', 'angle', 
                            'borderstyle', 'outline', 'shadow', 'alignment', 'marginl', 
                            'marginr', 'marginv', 'encoding'}
        
        required = V4_MANDATORY if is_v4 else V4PLUS_MANDATORY
        # We check against parsing_fields (the effective format for this session)
        missing = required - set(parsing_fields)
        if missing:
             styles._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                f"Styles section missing standard fields: {', '.join(sorted(missing))}",
                raw.format_line_number or raw.line_number, "INCOMPLETE_FORMAT"
            ))

        # 2. Ingest records
        for record in raw.records:
            if record.descriptor == 'style':
                try:
                    # Always split based on the FILE'S actual structure to ensure type accuracy
                    parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                    record_dict = {name: val for name, val in zip(file_format_fields, parts)}
                    
                    style = AssStyle.from_dict(record_dict)
                    
                    # Warn on duplicate style names (Last-one-wins)
                    if style.name in styles:
                        styles._diagnostics.append(Diagnostic(
                            DiagnosticLevel.WARNING,
                            f"Duplicate style name '{style.name}' found. The last definition will take precedence.",
                            record.line_number, "DUPLICATE_STYLE_NAME"
                        ))
                    
                    styles.set(style)
                except Exception as e:
                     styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse {record.raw_descriptor}: {e}", record.line_number, "STYLE_PARSE_ERROR"))
            else:
                # Custom record preservation: Store raw descriptor for restoration
                styles._custom_records.append(record)

        if not styles._data:
            styles._diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, "No Style definitions found", raw.line_number, "EMPTY_STYLES"))

        return styles

    @property
    def diagnostics(self) -> list[Diagnostic]:
        return self._diagnostics

    @property
    def section_comments(self) -> list[str]:
        return self._section_comments

    def get_comments(self) -> list[str]:
        """Get all comments."""
        return list(self._section_comments)

    @property
    def custom_records(self) -> list[RawRecord]:
        return self._custom_records

    def _get_canonical_name(self, name: str) -> str:
        if name in self._data:
            return name
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
        """Get the union of all explicit fields across all styles in standard order."""
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        
        # Standard Order
        if is_v4:
            standard = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'TertiaryColour', 'BackColour', 'Bold', 'Italic', 'BorderStyle']
        else:
            standard = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'OutlineColour', 'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut', 'ScaleX', 'ScaleY', 'Spacing', 'Angle', 'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding']
        
        all_explicit = set()
        for style in self._data.values():
            all_explicit.update(style._explicit_fields)
            
        # Name is always mandatory
        all_explicit.add('name')
        
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
        self._data.clear()
        for s in styles:
            self.set(s)


    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

