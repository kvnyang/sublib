# sublib/ass/types/clip.py
"""Clip value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RectClip:
    """Rectangle clip value."""
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class VectorClip:
    """Vector drawing clip value."""
    drawing: str
    scale: int = 1


ClipValue = RectClip | VectorClip
