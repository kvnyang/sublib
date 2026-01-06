# sublib/ass/serde/script_info.py
"""Parse and render Script Info lines."""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


# Known fields with their types: key -> (type, validator)
# type: 'int', 'float', 'bool', 'str'
KNOWN_FIELDS: dict[str, str] = {
    "ScriptType": "str",
    "Title": "str",
    "PlayResX": "int",
    "PlayResY": "int",
    "WrapStyle": "int",
    "ScaledBorderAndShadow": "bool",
    "Collisions": "str",
    "YCbCr Matrix": "str",
    "Timer": "float",
    "Synch Point": "str",
    "Original Script": "str",
    "Original Translation": "str",
    "Original Editing": "str",
    "Original Timing": "str",
    "Script Updated By": "str",
    "Update Details": "str",
}

# Case-insensitive lookup: lowercase key -> canonical key
_CANONICAL_KEY: dict[str, str] = {k.lower(): k for k in KNOWN_FIELDS}


def parse_script_info_line(line: str) -> tuple[str, Any] | None:
    """Parse a single Script Info line.
    
    Args:
        line: Raw line (e.g., "PlayResX: 1920")
        
    Returns:
        (key, typed_value) or None if line is invalid.
        Logs warnings for validation issues.
    """
    if ':' not in line:
        return None
    
    key, _, value = line.partition(':')
    key, value = key.strip(), value.strip()
    
    if not key:
        return None
    
    # Normalize to canonical key if known
    canonical = _CANONICAL_KEY.get(key.lower())
    if canonical:
        key = canonical
        field_type = KNOWN_FIELDS[canonical]
        parsed = _parse_typed_value(key, value, field_type)
        return key, parsed
    else:
        logger.warning(f"Unknown Script Info field: {key}")
        return key, value


def _parse_typed_value(key: str, value: str, field_type: str) -> Any:
    """Parse value according to field type."""
    if field_type == "int":
        try:
            val = int(value)
            if val <= 0 and key in ("PlayResX", "PlayResY"):
                logger.warning(f"{key} must be positive, got {val}")
            return val
        except ValueError:
            logger.warning(f"{key} must be integer, got '{value}'")
            return value  # Keep as string on failure
    
    elif field_type == "float":
        try:
            val = float(value)
            if val <= 0 and key == "Timer":
                logger.warning(f"{key} must be positive, got {val}")
            return val
        except ValueError:
            logger.warning(f"{key} must be number, got '{value}'")
            return value
    
    elif field_type == "bool":
        return value.lower() in ("yes", "1", "true")
    
    else:  # str
        return value


def render_script_info_line(key: str, value: Any) -> str:
    """Render a single Script Info line.
    
    Args:
        key: ASS key name (e.g., "PlayResX")
        value: Typed value
        
    Returns:
        Formatted line (e.g., "PlayResX: 1920")
    """
    formatted = _format_value(key, value)
    return f"{key}: {formatted}"


def _format_value(key: str, value: Any) -> str:
    """Format value for rendering."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    elif isinstance(value, float) and key == "Timer":
        return f"{value:.4f}"
    else:
        return str(value)
