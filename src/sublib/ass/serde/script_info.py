# sublib/ass/serde/script_info.py
"""Parse and render [Script Info] section."""
from __future__ import annotations

from dataclasses import fields
from sublib.ass.models import ScriptInfo


# Field metadata: (field_name, canonical_key, aliases)
# Aliases are alternative ASS key names that map to the same field
_FIELD_METADATA: list[tuple[str, str, tuple[str, ...]]] = [
    ("script_type", "ScriptType", ()),
    ("title", "Title", ()),
    ("play_res_x", "PlayResX", ()),
    ("play_res_y", "PlayResY", ()),
    ("wrap_style", "WrapStyle", ()),
    ("scaled_border_and_shadow", "ScaledBorderAndShadow", ()),
    ("collisions", "Collisions", ()),
    ("ycbcr_matrix", "YCbCr Matrix", ()),
    ("timer", "Timer", ()),
    ("synch_point", "Synch Point", ()),
    ("original_script", "Original Script", ()),
    ("original_translation", "Original Translation", ()),
    ("original_editing", "Original Editing", ()),
    ("original_timing", "Original Timing", ()),
    ("script_updated_by", "Script Updated By", ()),
    ("update_details", "Update Details", ()),
]

# Build lookup table: lowercase ASS key -> field name
_KEY_TO_FIELD: dict[str, str] = {}
for field_name, canonical_key, aliases in _FIELD_METADATA:
    _KEY_TO_FIELD[canonical_key.lower()] = field_name
    for alias in aliases:
        _KEY_TO_FIELD[alias.lower()] = field_name


def parse_script_info_line(line: str) -> tuple[str, str] | None:
    """Parse a single Script Info line to key-value pair.
    
    Args:
        line: A line from [Script Info] section (e.g., "Title: My Script")
        
    Returns:
        Tuple of (key, value) or None if not a valid key-value line
    """
    if ':' not in line:
        return None
    key, _, value = line.partition(':')
    return key.strip(), value.strip()


def parse_script_info(lines: list[tuple[str, str]]) -> ScriptInfo:
    """Parse key-value pairs into ScriptInfo with validation.
    
    Args:
        lines: List of (key, value) tuples from [Script Info] section
        
    Returns:
        ScriptInfo with populated fields and validation warnings
    """
    info = ScriptInfo()
    
    for key, value in lines:
        key_lower = key.lower()
        field_name = _KEY_TO_FIELD.get(key_lower)
        
        if field_name is None:
            # Non-standard field, store in extra
            info.extra[key] = value
            continue
        
        # Parse and validate based on field type
        if field_name == "script_type":
            info.script_type = value
            if value.lower() != "v4.00+":
                info.warnings.append(f"ScriptType '{value}' is not 'v4.00+'")
        
        elif field_name == "play_res_x":
            try:
                val = int(value)
                if val <= 0:
                    info.warnings.append(f"PlayResX must be positive, got {val}")
                else:
                    info.play_res_x = val
            except ValueError:
                info.warnings.append(f"PlayResX must be integer, got '{value}'")
        
        elif field_name == "play_res_y":
            try:
                val = int(value)
                if val <= 0:
                    info.warnings.append(f"PlayResY must be positive, got {val}")
                else:
                    info.play_res_y = val
            except ValueError:
                info.warnings.append(f"PlayResY must be integer, got '{value}'")
        
        elif field_name == "wrap_style":
            try:
                val = int(value)
                if val not in (0, 1, 2, 3):
                    info.warnings.append(f"WrapStyle must be 0-3, got {val}")
                else:
                    info.wrap_style = val
            except ValueError:
                info.warnings.append(f"WrapStyle must be integer, got '{value}'")
        
        elif field_name == "collisions":
            if value not in ("Normal", "Reverse"):
                info.warnings.append(
                    f"Collisions must be 'Normal' or 'Reverse', got '{value}'"
                )
            info.collisions = value
        
        elif field_name == "timer":
            try:
                val = float(value)
                if val <= 0:
                    info.warnings.append(f"Timer must be positive, got {val}")
                else:
                    info.timer = val
            except ValueError:
                info.warnings.append(f"Timer must be number, got '{value}'")
        
        elif field_name == "scaled_border_and_shadow":
            info.scaled_border_and_shadow = value.lower() in ("yes", "1", "true")
        
        elif field_name == "title":
            info.title = value if value else "<untitled>"
        
        elif field_name == "original_script":
            info.original_script = value if value else "<unknown>"
        
        elif field_name == "ycbcr_matrix":
            info.ycbcr_matrix = value if value else None
        
        else:
            # Optional string fields
            setattr(info, field_name, value if value else None)
    
    # Validate required fields
    if info.play_res_x is None:
        info.warnings.append("PlayResX is required for correct rendering")
    if info.play_res_y is None:
        info.warnings.append("PlayResY is required for correct rendering")
    
    return info


def render_script_info(info: ScriptInfo) -> list[str]:
    """Render ScriptInfo to ASS format lines.
    
    Args:
        info: ScriptInfo to render
        
    Returns:
        List of lines (without section header)
    """
    lines = []
    
    for field_name, canonical_key, _ in _FIELD_METADATA:
        value = getattr(info, field_name)
        
        if value is None:
            continue
        
        # Format specific types
        if field_name == "timer":
            lines.append(f"{canonical_key}: {value:.4f}")
        elif isinstance(value, bool):
            lines.append(f"{canonical_key}: {'yes' if value else 'no'}")
        else:
            lines.append(f"{canonical_key}: {value}")
    
    # Add extra (non-standard) fields
    for key, value in info.extra.items():
        lines.append(f"{key}: {value}")
    
    return lines
