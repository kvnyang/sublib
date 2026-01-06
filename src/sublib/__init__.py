# sublib - Subtitle Library
"""
A Python library for parsing and rendering subtitle files.

Supported formats:
- ASS (Advanced SubStation Alpha v4+)
"""

__version__ = "0.2.1"

# ASS format - main exports (Facade API)
from sublib.ass import AssFile, AssEvent, AssStyle

__all__ = [
    "__version__",
    "AssFile",
    "AssEvent",
    "AssStyle",
]
