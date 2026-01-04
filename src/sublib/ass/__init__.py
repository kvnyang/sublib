# sublib/ass/__init__.py
"""ASS/SSA subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle
from sublib.ass.ast import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssSpecialChar,
    SpecialCharType,
    AssTextSegment,
    AssOverrideBlock,
    AssComment,
)
from sublib.ass.services import (
    AssTextParser,
    AssTextRenderer,
    extract_line_scoped_tags,
    extract_text_scoped_segments,
)
from sublib.ass.io import load_ass_file, save_ass_file

# Value types (canonical source is types/)
from sublib.ass.types import (
    Color,
    Alpha,
    Position,
    Move,
    RectClip,
    VectorClip,
    ClipValue,
    Fade,
    FadeComplex,
    Alignment,
    WrapStyle,
    StyleReset,
    Transform,
    Karaoke,
)

__all__ = [
    # Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    # I/O
    "load_ass_file",
    "save_ass_file",
    # AST Elements
    "AssTextElement",
    "AssOverrideTag",
    "AssPlainText",
    "AssSpecialChar",
    "SpecialCharType",
    "AssTextSegment",
    "AssOverrideBlock",
    "AssComment",
    # Services
    "AssTextParser",
    "AssTextRenderer",
    "extract_line_scoped_tags",
    "extract_text_scoped_segments",
    # Value Types
    "Color",
    "Alpha",
    "Position",
    "Move",
    "RectClip",
    "VectorClip",
    "ClipValue",
    "Fade",
    "FadeComplex",
    "Alignment",
    "WrapStyle",
    "StyleReset",
    "Transform",
    "Karaoke",
]
