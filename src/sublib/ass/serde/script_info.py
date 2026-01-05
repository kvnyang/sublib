# sublib/ass/serde/script_info.py
"""Parse and render [Script Info] section."""
from __future__ import annotations

from sublib.ass.models import ScriptInfo


# Ordered field definitions: (field_name, ass_key)
_FIELDS: list[tuple[str, str]] = [
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

# Case-insensitive lookup: lowercase key -> field name
_KEY_TO_FIELD: dict[str, str] = {
    ass_key.lower(): field_name for field_name, ass_key in _FIELDS
}


def parse_script_info(lines: list[str]) -> ScriptInfo:
    """Parse [Script Info] section lines into ScriptInfo.
    
    Args:
        lines: Raw lines from [Script Info] section (without section header)
        
    Returns:
        ScriptInfo with populated fields and validation warnings
    """
    info = ScriptInfo()
    
    for line in lines:
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        
        field_name = _KEY_TO_FIELD.get(key.lower())
        
        if field_name is None:
            info.extra[key] = value
            continue
        
        # Parse and validate
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
                info.warnings.append(f"Collisions must be 'Normal' or 'Reverse', got '{value}'")
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
            setattr(info, field_name, value if value else None)
    
    # Validate required fields
    if info.play_res_x is None:
        info.warnings.append("PlayResX is required for correct rendering")
    if info.play_res_y is None:
        info.warnings.append("PlayResY is required for correct rendering")
    
    return info


def render_script_info(info: ScriptInfo) -> list[str]:
    """Render ScriptInfo to [Script Info] section lines.
    
    Args:
        info: ScriptInfo to render
        
    Returns:
        Lines for [Script Info] section (without section header)
    """
    lines = []
    
    for field_name, ass_key in _FIELDS:
        value = getattr(info, field_name)
        
        if value is None:
            continue
        
        if field_name == "timer":
            lines.append(f"{ass_key}: {value:.4f}")
        elif isinstance(value, bool):
            lines.append(f"{ass_key}: {'yes' if value else 'no'}")
        else:
            lines.append(f"{ass_key}: {value}")
    
    for key, value in info.extra.items():
        lines.append(f"{key}: {value}")
    
    return lines
