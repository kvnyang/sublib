"""Base classes for ASS sections."""
from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from sublib.ass.core.naming import normalize_key, get_canonical_name

if TYPE_CHECKING:
    from sublib.ass.core.diagnostics import Diagnostic

class AssSection:
    """Base class for all ASS sections."""
    def __init__(self, name: str, original_name: Optional[str] = None):
        self.name = normalize_key(name)
        self.original_name = original_name or name
        self._diagnostics: list[Diagnostic] = []

    @property
    def diagnostics(self) -> list[Diagnostic]:
        """Diagnostic messages collected during parsing."""
        return self._diagnostics

    def render(self) -> str:
        """Polymorphic entry point for serialization."""
        raise NotImplementedError()

class AssRawSection(AssSection):
    """Passthrough for [Fonts], [Graphics], or unknown sections.
    
    Maintains physical fidelity by preserving all lines exactly as read,
    including comments and blank lines within the section.
    """
    def __init__(self, name: str, raw_lines: list[str], original_name: Optional[str] = None):
        super().__init__(name, original_name)
        self.raw_lines = list(raw_lines)

    def render(self) -> str:
        lines = [f"[{self.original_name}]"]
        lines.extend(self.raw_lines)
        return "\n".join(lines)

class AssStructuredSection(AssSection):
    """Base for sections that support metadata like comments."""
    def __init__(self, name: str, original_name: Optional[str] = None):
        super().__init__(name, original_name)
        self.comments: list[str] = []

    def render_header(self) -> list[str]:
        """Render the section header and comments."""
        lines = [f"[{self.original_name}]"]
        for comment in self.comments:
            lines.append(f"; {comment}")
        return lines

class AssCoreSection(AssStructuredSection):
    """Key: Value structure, typically used for [Script Info]."""
    def __init__(self, name: str, original_name: Optional[str] = None):
        super().__init__(name, original_name)
        self._data: dict[str, Any] = {}

class AssFormatSection(AssStructuredSection):
    """Multi-column table structure, used for [Styles] and [Events]."""
    def __init__(self, name: str, original_name: Optional[str] = None):
        super().__init__(name, original_name)
        self._raw_format_fields: list[str] | None = None
        self._custom_records: list[Any] = [] # To be typed in subclasses

    @property
    def raw_format_fields(self) -> list[str] | None:
        return self._raw_format_fields

    @raw_format_fields.setter
    def raw_format_fields(self, value: list[str] | None) -> None:
        self._raw_format_fields = value
