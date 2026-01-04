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

# Tag value types from tags/
from sublib.ass.tags import (
    Position,
    Move,
    RectClip,
    VectorClip,
    ClipValue,
    Fade,
    FadeComplex,
    Transform,
    Karaoke,
    Color,
    Alpha,
    Alignment,
    WrapStyle,
    StyleReset,
    BorderSize,
    ShadowDistance,
    BlurEdge,
    BlurGaussian,
    FontScale,
    Rotation,
    Shear,
    DrawingMode,
    BaselineOffset,
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
    # Tag Values
    "Position",
    "Move",
    "RectClip",
    "VectorClip",
    "ClipValue",
    "Fade",
    "FadeComplex",
    "Transform",
    "Karaoke",
    "Color",
    "Alpha",
    "Alignment",
    "WrapStyle",
    "StyleReset",
    "BorderSize",
    "ShadowDistance",
    "BlurEdge",
    "BlurGaussian",
    "FontScale",
    "Rotation",
    "Shear",
    "DrawingMode",
    "BaselineOffset",
]
