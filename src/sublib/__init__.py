# sublib - Subtitle Library
"""
A Python library for parsing and rendering subtitle files.

Supported formats:
- ASS/SSA (Advanced SubStation Alpha)
- SRT (SubRip) - planned
- VTT (WebVTT) - planned
"""

__version__ = "0.1.0"

# Core (format-agnostic)
from sublib.core.models import Cue, SubtitleFile
from sublib.core.exceptions import SubtitleParseError, SubtitleRenderError

# ASS format
from sublib.formats.ass import (
    # Models
    AssFile,
    AssEvent,
    AssStyle,
    # Elements
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
    # Parser/Renderer
    AssTextParser,
    AssTextRenderer,
    # Tag values
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
    # Version
    "__version__",
    # Core
    "SubtitleEvent",
    "SubtitleFile",
    "SubtitleParseError",
    "SubtitleRenderError",
    # ASS Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    # ASS Elements
    "AssTextElement",
    "AssOverrideTag",
    "AssPlainText",
    "AssNewLine",
    "AssHardSpace",
    # ASS Parser/Renderer
    "AssTextParser",
    "AssTextRenderer",
    # ASS Tag Values
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
