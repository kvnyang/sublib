# sublib - Subtitle Library
"""
A Python library for parsing and rendering subtitle files.

Supported formats:
- ASS/SSA (Advanced SubStation Alpha)
"""

__version__ = "0.1.0"

# ASS format - main exports
from sublib.ass import (
    # File-level
    AssFile,
    AssEvent,
    AssStyle,
    # I/O
    load_ass_file,
    save_ass_file,
)

__all__ = [
    "__version__",
    # ASS
    "AssFile",
    "AssEvent",
    "AssStyle",
    "load_ass_file",
    "save_ass_file",
]
