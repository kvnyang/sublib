"""Unified schema and field management for ASS models."""
from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING, Callable
from sublib.ass.naming import normalize_key

if TYPE_CHECKING:
    from sublib.ass.diagnostics import Diagnostic

class FieldSchema:
    """Definition for a single field in an ASS record."""
    def __init__(
        self, 
        default: Any, 
        converter: Callable,
        formatter: Callable = str, 
        canonical_name: str = "",
        python_prop: str = ""
    ):
        self.default = default
        self.converter = converter
        self.formatter = formatter
        self.canonical_name = canonical_name
        self.python_prop = python_prop
        self.normalized_key = normalize_key(canonical_name)

    def convert(self, value: Any, diagnostics: Optional[list[Diagnostic]] = None, line_number: int = 0) -> Any:
        """Convert raw value to typed value with diagnostic reporting."""
        if isinstance(value, self.converter):
            return value
            
        raw_str = str(value).strip()
        if not raw_str:
            return self.default
            
        try:
            # Special handling for common types
            if self.converter == bool:
                return raw_str not in ('0', 'false', 'False', 'no', 'No', '')
            if self.converter == int:
                return int(raw_str)
            if self.converter == float:
                return float(raw_str)
            if self.converter == str:
                return raw_str
                
            # Fallback to custom converter or type constructor
            if hasattr(self.converter, 'from_style_str'):
                return self.converter.from_style_str(raw_str)
            if hasattr(self.converter, 'from_ass_str'):
                return self.converter.from_ass_str(raw_str)
                
            return self.converter(raw_str)
        except (ValueError, TypeError):
            if diagnostics is not None:
                from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
                diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Invalid value for {self.canonical_name or 'field'}: '{raw_str}' (expected {self.converter.__name__ if hasattr(self.converter, '__name__') else self.converter}). Falling back to default: {self.default}",
                    line_number, "INVALID_VALUE_TYPE"
                ))
            return self.default

    def format(self, value: Any) -> str:
        """Format typed value to ASS string."""
        if value is None:
            return ""
        if hasattr(value, 'to_style_str'):
            return value.to_style_str()
        if hasattr(value, 'to_ass_str'):
            return value.to_ass_str()
        return self.formatter(value)

class AssStructuredRecord:
    """Base class for records with typed fields (Style, Event, etc.)."""
    def __init__(self, schema: dict[str, FieldSchema], fields: dict[str, Any] = None, extra: dict[str, Any] = None):
        # normalized_key -> FieldSchema
        self._schema = schema
        # normalized_key -> typed_value (Standard fields)
        self._fields = fields or {}
        # normalized_key -> raw_str (Custom/Unknown fields)
        self._extra = extra or {}
        
        # reverse map: python_prop -> normalized_key
        self._prop_map = {s.python_prop: k for k, s in schema.items() if s.python_prop}

    def _resolve_key(self, key: str) -> str:
        """Resolve property name or raw key to normalized identity key."""
        if key in self._prop_map:
            return self._prop_map[key]
        return normalize_key(key)

    def __getitem__(self, key: str) -> Any:
        norm_key = self._resolve_key(key)
        if norm_key in self._fields:
            return self._fields[norm_key]
        if norm_key in self._schema:
            return self._schema[norm_key].default
        if norm_key in self._extra:
            return self._extra[norm_key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        norm_key = self._resolve_key(key)
        if norm_key in self._schema:
            self._fields[norm_key] = self._schema[norm_key].convert(value)
        else:
            self._extra[norm_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
        try:
            return self[name]
        except KeyError:
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
            
        # If the attribute already exists as a real instance attribute, don't intercept
        if name in self.__dict__:
            super().__setattr__(name, value)
            return

        # Check if it's a known property or should be a field
        norm_key = self._resolve_key(name)
        if norm_key in self._schema or name in self._prop_map:
            self[name] = value
        else:
            # For non-field attributes, if they are not in __dict__ yet,
            # we must decide if they are new fields or new attributes.
            # In AssStructuredRecord, we default to fields for convenience.
            # But derived classes can use object.__setattr__ to bypass.
            self[name] = value

