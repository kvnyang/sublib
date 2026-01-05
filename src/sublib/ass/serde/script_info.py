# sublib/ass/serde/script_info.py
"""Parse and render [Script Info] section."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models import ScriptInfo as ScriptInfoType

from sublib.ass.models import ScriptInfo


# Mapping from ASS key names to ScriptInfo field names
_KEY_TO_FIELD: dict[str, str] = {
    "scripttype": "script_type",
    "script type": "script_type",
    "playresx": "play_res_x",
    "playresy": "play_res_y",
    "wrapstyle": "wrap_style",
    "collisions": "collisions",
    "timer": "timer",
    "ycbcr matrix": "ycbcr_matrix",
    "scaledborderandshadow": "scaled_border_and_shadow",
    "title": "title",
    "original script": "original_script",
    "original translation": "original_translation",
    "original editing": "original_editing",
    "original timing": "original_timing",
    "synch point": "synch_point",
    "script updated by": "script_updated_by",
    "update details": "update_details",
}


# Ordered list of standard fields for consistent output
_STANDARD_FIELDS = [
    ("script_type", "ScriptType"),
    ("title", "Title"),
    ("play_res_x", "PlayResX"),
    ("play_res_y", "PlayResY"),
    ("wrap_style", "WrapStyle"),
    ("scaled_border_and_shadow", "ScaledBorderAndShadow"),
    ("collisions", "Collisions"),
    ("ycbcr_matrix", "YCbCr Matrix"),
    ("timer", "Timer"),
    ("synch_point", "Synch Point"),
    ("original_script", "Original Script"),
    ("original_translation", "Original Translation"),
    ("original_editing", "Original Editing"),
    ("original_timing", "Original Timing"),
    ("script_updated_by", "Script Updated By"),
    ("update_details", "Update Details"),
]


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
        
        else:
            # Optional string fields
            setattr(info, field_name, value if value else None)
    
    # Validate required fields
    if info.play_res_x is None:
        info.warnings.append("PlayResX is required for correct rendering")
    if info.play_res_y is None:
        info.warnings.append("PlayResY is required for correct rendering")
    
    return info


def render_script_info(info: "ScriptInfoType") -> list[str]:
    """Render ScriptInfo to ASS format lines.
    
    Args:
        info: ScriptInfo to render
        
    Returns:
        List of lines (without section header)
    """
    lines = []
    
    for field_name, key_name in _STANDARD_FIELDS:
        value = getattr(info, field_name)
        
        if value is None:
            continue
        
        # Format specific types
        if field_name == "timer":
            lines.append(f"{key_name}: {value:.4f}")
        elif isinstance(value, bool):
            lines.append(f"{key_name}: {'yes' if value else 'no'}")
        else:
            lines.append(f"{key_name}: {value}")
    
    # Add extra (non-standard) fields
    for key, value in info.extra.items():
        lines.append(f"{key}: {value}")
    
    return lines
