"""Parse and render Script Info lines."""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_script_info_line(line: str) -> tuple[str, str] | None:
    """Parse a single Script Info line into a raw key-value pair.
    
    The model (AssScriptInfoView) will handle type conversion and validation.
    """
    if ':' not in line:
        return None
    
    key, _, value = line.partition(':')
    return key.strip(), value.strip()


def render_script_info_line(key: str, value: Any) -> str:
    """Render a single Script Info line."""
    if isinstance(value, bool):
        formatted = "yes" if value else "no"
    elif isinstance(value, float) and key == "Timer":
        formatted = f"{value:.4f}"
    else:
        formatted = str(value)
    return f"{key}: {formatted}"
