"""Clip value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AssRectClip:
    """Rectangle clip value."""
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class AssVectorClip:
    """Vector drawing clip value."""
    drawing: str
    scale: int = 1


AssClipValue = AssRectClip | AssVectorClip
