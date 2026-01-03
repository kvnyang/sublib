# sublib/ass/tags/drawing.py
"""Drawing mode tag values."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DrawingMode:
    """Value for \\p tag."""
    scale: int


@dataclass
class BaselineOffset:
    """Value for \\pbo tag."""
    offset: int
