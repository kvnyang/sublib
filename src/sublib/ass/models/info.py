"""ASS Script Info model."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection

from sublib.ass.naming import normalize_key, get_canonical_name

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

    def __init__(self, data: dict[str, Any] | None = None):
        self._data: dict[str, Any] = {}
        self._display_names: dict[str, str] = {}
        self._header_comments: list[str] = []
        self._diagnostics: list[Diagnostic] = []
        if data:
            self.set_all(data)
    
    @classmethod
    def from_raw(cls, raw: RawSection) -> AssScriptInfo:
        """Layer 2: Semantic ingestion from a RawSection."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        info = cls()
        info.set_comments(raw.comments)
        
        # Pass 1: Aggregate records (Last-one-wins)
        # record.descriptor is already standardized (or lowercase unknown) by Layer 1
        aggregated: dict[str, tuple[str, str, int]] = {}
        for record in raw.records:
            if record.descriptor in aggregated:
                info._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Duplicate key '{record.raw_descriptor}' in [Script Info]",
                    record.line_number, "DUPLICATE_KEY"
                ))
            # Store (raw_descriptor, value, line_number)
            aggregated[record.descriptor] = (record.raw_descriptor, record.value, record.line_number)

        # Pass 2: Detect Version (scripttype)
        script_type = 'v4.00+'  # Default
        if 'scripttype' in aggregated:
            raw_st, val, ln = aggregated['scripttype']
            if val in ('v4.00', 'v4.00+'):
                script_type = val
            else:
                info._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Invalid ScriptType '{val}', defaulting to 'v4.00+'",
                    ln, "INVALID_SCRIPTTYPE"
                ))
            # Update values
            aggregated['scripttype'] = (raw_st, script_type, ln)
        else:
            info._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                "Missing 'ScriptType' in [Script Info], defaulting to 'v4.00+'",
                raw.line_number, "MISSING_SCRIPTTYPE"
            ))
            info.set('scripttype', script_type)
        
        # Pass 3: Semantic Validation and Type Conversion
        for std_key, (raw_key, value, line_number) in aggregated.items():
            # Pass raw_key for display/diagnostic fidelity
            info.set(std_key, value, raw_key=raw_key, line_number=line_number, script_type=script_type)
            
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
        return normalize_key(key)

    def render_line(self, key: str, value: Any) -> str:
        """Render a single Script Info line."""
        canonical_key = get_canonical_name(key, context='script info')
        if isinstance(value, bool):
            formatted = "yes" if value else "no"
        elif isinstance(value, float) and canonical_key == "Timer":
            formatted = f"{value:.4f}"
        else:
            formatted = str(value)
        return f"{canonical_key}: {formatted}"

    def __getitem__(self, key: str) -> Any:
        return self._data[self._normalize_key(key)]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def set(self, key: str, value: Any, raw_key: str | None = None, line_number: int = 0, script_type: str | None = None) -> None:
        """Set a property with optional diagnostic reporting."""
        canonical_key = self._normalize_key(key)
        
        # Update display name
        display_name = get_canonical_name(raw_key or key, context='script info')
        self._display_names[canonical_key] = display_name

        # 1. Version Check
        if script_type and canonical_key in self.VERSION_FIELDS:
            min_ver = self.VERSION_FIELDS[canonical_key]
            if min_ver == "v4.00+" and "v4" in script_type.lower() and "+" not in script_type:
                from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
                self._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Field '{raw_key or key}' is v4.00+ specific but ScriptType is '{script_type}'",
                    line_number, "VERSION_MISMATCH"
                ))

        # 2. Type Conversion
        if isinstance(value, str):
            field_type = self.KNOWN_FIELDS.get(canonical_key)
            if field_type:
                value = self._parse_typed_value(raw_key or key, value, field_type, line_number)
        
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
        return iter(self.keys())

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
        return [self._display_names.get(k, k) for k in self._data.keys()]

    def values(self):
        return self._data.values()

    def items(self):
        for k, v in self._data.items():
            yield self._display_names.get(k, get_canonical_name(k, context='script info')), v

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

