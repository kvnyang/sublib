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
    
    _CANONICAL_KEYS = {k.lower(): k for k in KNOWN_FIELDS}

    def __init__(self, data: dict[str, Any] | None = None):
        self._data = data if data is not None else {}

    def _normalize_key(self, key: str) -> str:
        return self._CANONICAL_KEYS.get(key.lower(), key)

    @staticmethod
    def parse_line(line: str) -> tuple[str, str] | None:
        """Parse a single Script Info line into a raw key-value pair."""
        if ':' not in line:
            return None
        key, _, value = line.partition(':')
        return key.strip(), value.strip()

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
        canonical_key = self._normalize_key(key)
        
        # Automatic parsing if value is string (from parser)
        if isinstance(value, str):
            field_type = self.KNOWN_FIELDS.get(canonical_key)
            if field_type:
                value = self._parse_typed_value(canonical_key, value, field_type)
        
        self._data[canonical_key] = value

    def _parse_typed_value(self, key: str, value: str, field_type: str) -> Any:
        try:
            if field_type == "int":
                return int(value)
            elif field_type == "float":
                return float(value)
            elif field_type == "bool":
                return value.lower() in ("yes", "1", "true")
        except ValueError:
            logger.warning(f"Invalid value for {key}: {value} (expected {field_type})")
        return value

    def __getattr__(self, name: str) -> Any:
        # Allow access like file.script_info.Title
        if name.startswith('_'): # Don't interfere with internal attributes
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

    def set(self, key: str, value: Any) -> None:
        self[key] = value

    def set_all(self, info_dict: dict[str, Any]) -> None:
        """Replace all properties."""
        self._data.clear()
        for k, v in info_dict.items():
            self[k] = v

    def add_all(self, info_dict: dict[str, Any]) -> None:
        """Merge/Update properties."""
        for k, v in info_dict.items():
            self[k] = v

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
