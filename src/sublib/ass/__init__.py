# sublib/ass/__init__.py
"""ASS/SSA subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle
from sublib.ass.elements import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
    AssTextSegment,
)
from sublib.ass.parser import AssTextParser
from sublib.ass.renderer import AssTextRenderer
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
    # Elements
    "AssTextElement",
    "AssOverrideTag",
    "AssPlainText",
    "AssNewLine",
    "AssHardSpace",
    "AssTextSegment",
    # Parser/Renderer
    "AssTextParser",
    "AssTextRenderer",
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
