"""ASS Style models."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from sublib.ass.types import AssColor


@dataclass
class AssStyle:
    """ASS style definition.
    
    Represents a style from the [V4+ Styles] section.
    """
    name: str
    fontname: str
    fontsize: float
    primary_color: AssColor
    secondary_color: AssColor
    outline_color: AssColor
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
    def from_ass_line(cls, line: str) -> AssStyle | None:
        """Parse a Style: line to AssStyle.
        
        Args:
            line: Style line (e.g., "Style: Default,Arial,20,...")
            
        Returns:
            AssStyle or None if parsing fails
        """
        if not line.startswith('Style:'):
            return None
        
        parts = line[6:].split(',')
        if len(parts) < 23:
            return None
        
        return cls(
            name=parts[0].strip(),
            fontname=parts[1].strip(),
            fontsize=float(parts[2]),
            primary_color=AssColor.from_style_str(parts[3]),
            secondary_color=AssColor.from_style_str(parts[4]),
            outline_color=AssColor.from_style_str(parts[5]),
            back_color=AssColor.from_style_str(parts[6]),
            bold=parts[7].strip() != '0',
            italic=parts[8].strip() != '0',
            underline=parts[9].strip() != '0',
            strikeout=parts[10].strip() != '0',
            scale_x=float(parts[11]),
            scale_y=float(parts[12]),
            spacing=float(parts[13]),
            angle=float(parts[14]),
            border_style=int(parts[15]),
            outline=float(parts[16]),
            shadow=float(parts[17]),
            alignment=int(parts[18]),
            margin_l=int(parts[19]),
            margin_r=int(parts[20]),
            margin_v=int(parts[21]),
            encoding=int(parts[22]),
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

    def _get_canonical_name(self, name: str) -> str:
        # Try exact match first
        if name in self._data:
            return name
        # Case-insensitive lookup
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
        if name != style.name:
            # If name is a case-insensitive match for style.name, it's okay but style.name is the source of truth
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
        """Replace all style definitions."""
        self._data.clear()
        for s in styles:
            self.set(s)

    def add_from_line(self, line: str) -> AssStyle | None:
        """Parse and add a style from an ASS line."""
        style = AssStyle.from_ass_line(line)
        if style:
            self.set(style)
        return style

    def add_all(self, styles: Iterable[AssStyle]) -> None:
        """Merge/Update style definitions."""
        for s in styles:
            self.set(s)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()
