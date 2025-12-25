# sublib/formats/ass/__init__.py
"""ASS/SSA subtitle format support."""

from sublib.formats.ass.models import AssFile, AssEvent, AssStyle
from sublib.formats.ass.elements import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
)
from sublib.formats.ass.text_parser import AssTextParser
from sublib.formats.ass.text_renderer import AssTextRenderer

# Tag value types
from sublib.formats.ass.tag_values import (
    Position,
    Move,
    RectClip,
    VectorClip,
    ClipValue,
    Fade,
    FadeComplex,
    Transform,
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
    # Elements
    "AssTextElement",
    "AssOverrideTag",
    "AssPlainText",
    "AssNewLine",
    "AssHardSpace",
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
