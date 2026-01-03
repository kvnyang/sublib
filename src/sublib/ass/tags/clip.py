# sublib/ass/tags/clip.py
"""Clip tag values."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RectClip:
    """Value for \\clip(x1,y1,x2,y2) or \\iclip(x1,y1,x2,y2)."""
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class VectorClip:
    """Value for \\clip(drawing) or \\clip(scale,drawing)."""
    drawing: str
    scale: int = 1


ClipValue = RectClip | VectorClip
