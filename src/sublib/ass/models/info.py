"""ASS Script Info model."""
from __future__ import annotations
from typing import Any
import logging

logger = logging.getLogger(__name__)


class AssScriptInfo:
    """Intelligent container for [Script Info] section with automatic type conversion and validation."""
    
    KNOWN_FIELDS = {
        "ScriptType": "str",
        "Title": "str",
        "PlayResX": "int",
        "PlayResY": "int",
        "WrapStyle": "int",
        "ScaledBorderAndShadow": "bool",
        "Collisions": "str",
        "YCbCr Matrix": "str",
        "Timer": "float",
    }
    
    # Version-specific fields (field name: min_version)
    VERSION_FIELDS = {
        "WrapStyle": "v4.00+",
        "ScaledBorderAndShadow": "v4.00+",
        "YCbCr Matrix": "v4.00+",
    }
    
    _CANONICAL_KEYS = {k.lower(): k for k in KNOWN_FIELDS}

    def __init__(self, data: dict[str, Any] | None = None):
        self._data = data if data is not None else {}
        self._header_comments: list[str] = []
        self._diagnostics: list[Diagnostic] = []
    
    @classmethod
    def from_raw(cls, raw: RawSection) -> AssScriptInfo:
        """Layer 2: Semantic ingestion from a RawSection."""
        info = cls()
        info.set_comments(raw.comments)
        
        script_type = None
        # First pass: find ScriptType
        for record in raw.records:
            if record.descriptor.lower() == 'scripttype':
                script_type = record.value
                break
        
        # Second pass: ingest values
        for record in raw.records:
            info.set(record.descriptor, record.value, line_number=record.line_number, 
                     script_type=script_type)
            
        return info

    @property
    def header_comments(self) -> list[str]:
        """Comments from [Script Info] section (without leading semicolon)."""
        return self._header_comments
    
    @property
    def diagnostics(self) -> list[Diagnostic]:
        """Diagnostic messages collected during semantic parsing."""
        return self._diagnostics

    def add_comment(self, comment: str) -> None:
        """Add a comment line (without leading semicolon)."""
        self._header_comments.append(comment)
    
    def set_comments(self, comments: list[str]) -> None:
        """Replace all comments."""
        self._header_comments = list(comments)

    def get_comments(self) -> list[str]:
        """Get all comments."""
        return list(self._header_comments)

    def _normalize_key(self, key: str) -> str:
        # Case insensitive, but space sensitive as per requirement
        return self._CANONICAL_KEYS.get(key.lower(), key)

    def render_line(self, key: str, value: Any) -> str:
        """Render a single Script Info line."""
        if isinstance(value, bool):
            formatted = "yes" if value else "no"
        elif isinstance(value, float) and key == "Timer":
            formatted = f"{value:.4f}"
        else:
            formatted = str(value)
        return f"{key}: {formatted}"

    def __getitem__(self, key: str) -> Any:
        return self._data[self._normalize_key(key)]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def set(self, key: str, value: Any, line_number: int = 0, script_type: str | None = None) -> None:
        """Set a property with optional diagnostic reporting."""
        canonical_key = self._normalize_key(key)
        
        # 1. Version Check
        if script_type and canonical_key in self.VERSION_FIELDS:
            min_ver = self.VERSION_FIELDS[canonical_key]
            if min_ver == "v4.00+" and "v4" in script_type.lower() and "+" not in script_type:
                from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
                self._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Field '{key}' is v4.00+ specific but ScriptType is '{script_type}'",
                    line_number, "VERSION_MISMATCH"
                ))

        # 2. Type Conversion
        if isinstance(value, str):
            field_type = self.KNOWN_FIELDS.get(canonical_key)
            if field_type:
                value = self._parse_typed_value(canonical_key, value, field_type, line_number)
        
        # 3. Duplicate Check
        if canonical_key in self._data and line_number > 0:
             from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
             self._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                f"Duplicate key '{key}' in [Script Info]",
                line_number, "DUPLICATE_KEY"
            ))

        self._data[canonical_key] = value

    def _parse_typed_value(self, key: str, value: str, field_type: str, line_number: int = 0) -> Any:
        try:
            if field_type == "int":
                return int(value)
            elif field_type == "float":
                return float(value)
            elif field_type == "bool":
                return value.lower() in ("yes", "1", "true")
        except ValueError:
            from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
            self._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                f"Invalid value for {key}: {value} (expected {field_type})",
                line_number, "INVALID_VALUE_TYPE"
            ))
        return value

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            raise AttributeError(name)
        canonical = self._normalize_key(name)
        if canonical in self._data:
            return self._data[canonical]
        raise AttributeError(f"'AssScriptInfo' object has no attribute '{name}'")

    def __delitem__(self, key: str) -> None:
        del self._data[self._normalize_key(key)]

    def __contains__(self, key: str) -> bool:
        return self._normalize_key(key) in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(self._normalize_key(key), default)

    def set_all(self, info_dict: dict[str, Any]) -> None:
        self._data.clear()
        for k, v in info_dict.items():
            self.set(k, v)

    def add_all(self, info_dict: dict[str, Any]) -> None:
        for k, v in info_dict.items():
            self.set(k, v)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

