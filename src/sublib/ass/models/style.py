"""ASS Style models."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from sublib.ass.types import AssColor


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

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> AssStyle:
        """Create AssStyle from a dictionary of raw strings (mapped by Format)."""
        # Mapping for v4 compatibility
        def get_field(names: list[str], default: str = "") -> str:
            for n in names:
                if n in data: return data[n]
            return default

        return cls(
            name=get_field(['Name']).strip(),
            fontname=get_field(['Fontname']).strip(),
            fontsize=float(get_field(['Fontsize'], '0')),
            primary_color=AssColor.from_style_str(get_field(['PrimaryColour'])),
            secondary_color=AssColor.from_style_str(get_field(['SecondaryColour'])),
            outline_color=AssColor.from_style_str(get_field(['OutlineColour', 'TertiaryColour'])),
            back_color=AssColor.from_style_str(get_field(['BackColour'])),
            bold=get_field(['Bold'], '0').strip() != '0',
            italic=get_field(['Italic'], '0').strip() != '0',
            underline=get_field(['Underline'], '0').strip() != '0',
            strikeout=get_field(['StrikeOut'], '0').strip() != '0',
            scale_x=float(get_field(['ScaleX'], '100')),
            scale_y=float(get_field(['ScaleY'], '100')),
            spacing=float(get_field(['Spacing'], '0')),
            angle=float(get_field(['Angle'], '0')),
            border_style=int(get_field(['BorderStyle'], '1')),
            outline=float(get_field(['Outline'], '2')),
            shadow=float(get_field(['Shadow'], '0')),
            alignment=int(get_field(['Alignment'], '2')),
            margin_l=int(get_field(['MarginL', 'MarginLeft'], '10')),
            margin_r=int(get_field(['MarginR', 'MarginRight'], '10')),
            margin_v=int(get_field(['MarginV', 'MarginVertical'], '10')),
            encoding=int(get_field(['Encoding'], '1')),
        )


    def render(self) -> str:
        """Render AssStyle to Style: line."""
        from sublib.ass.tags.base import _format_float
        return (
            f"Style: {self.name},{self.fontname},{_format_float(self.fontsize)},"
            f"{self.primary_color.to_style_str()},"
            f"{self.secondary_color.to_style_str()},"
            f"{self.outline_color.to_style_str()},"
            f"{self.back_color.to_style_str()},"
            f"{int(self.bold)},{int(self.italic)},{int(self.underline)},{int(self.strikeout)},"
            f"{_format_float(self.scale_x)},{_format_float(self.scale_y)},"
            f"{_format_float(self.spacing)},{_format_float(self.angle)},"
            f"{self.border_style},{_format_float(self.outline)},{_format_float(self.shadow)},"
            f"{self.alignment},{self.margin_l},{self.margin_r},{self.margin_v},{self.encoding}"
        )


class AssStyles:
    """Intelligent container for [V4+ Styles] section."""
    def __init__(self, data: dict[str, AssStyle] | None = None):
        self._data = data if data is not None else {}
        self._custom_records: list[RawRecord] = []
        self._diagnostics: list[Diagnostic] = []
        self._section_comments: list[str] = []

    @classmethod
    def from_raw(cls, raw: RawSection, script_type: str | None = None) -> AssStyles:
        """Layer 2: Semantic ingestion from a RawSection."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        styles = cls()
        styles._section_comments = list(raw.comments)
        
        if not raw.format_fields:
            # StructParser should have caught this, but safety first
            styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Styles section", raw.line_number, "MISSING_FORMAT"))
            return styles

        # 1. Minimum field verification
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        expected_min = 10 if is_v4 else 23
        if len(raw.format_fields) < expected_min:
             styles._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                f"Styles section has fewer fields ({len(raw.format_fields)}) than standard ({expected_min}) for {script_type or 'v4.00+'}",
                raw.format_line_number or raw.line_number, "INCOMPLETE_FORMAT"
            ))

        # 2. Ingest records
        for record in raw.records:
            if record.descriptor.lower() == 'style':
                try:
                    # Map fields using format
                    record_data = {}
                    for i, field_name in enumerate(raw.format_fields):
                        # Split the value by commas (limited to Format length)
                        # Actually RAW data already has values in records in StructuralParser? 
                        # No, records have the WHOLE value string.
                        pass
                    
                    # Wait, StructuralParser just strip() values. 
                    # We need to split the value string by commas based on Format.
                    parts = [p.strip() for p in record.value.split(',', len(raw.format_fields)-1)]
                    record_dict = {name: val for name, val in zip(raw.format_fields, parts)}
                    
                    style = AssStyle.from_dict(record_dict)
                    styles.set(style)
                except Exception as e:
                     styles._diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse Style: {e}", record.line_number, "STYLE_PARSE_ERROR"))
            else:
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

