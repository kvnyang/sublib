# sublib/ass/services/renderers/script_info_renderer.py
"""Render [Script Info] section."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models import ScriptInfo


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


def render_script_info(info: "ScriptInfo") -> list[str]:
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
