# sublib/ass/services/__init__.py
"""ASS processing services.

Organized by ASS line type hierarchy:
- text: Override tags and special chars within Dialogue text field
- style: Style: lines
- event: Dialogue: lines  
- file: Complete ASS file with sections
"""
from .parsers import (
    AssTextParser,
    parse_style_line,
    parse_event_line,
    parse_ass_string,
)
from .renderers import (
    AssTextRenderer,
    render_style_line,
    render_event_line,
    render_ass_string,
)
from .extractor import (
    extract_line_scoped_tags,
    extract_text_scoped_segments,
)

__all__ = [
    # Text level
    "AssTextParser",
    "AssTextRenderer",
    # Style level
    "parse_style_line",
    "render_style_line",
    # Event level
    "parse_event_line",
    "render_event_line",
    # File level
    "parse_ass_string",
    "render_ass_string",
    # Extractors
    "extract_line_scoped_tags",
    "extract_text_scoped_segments",
]
