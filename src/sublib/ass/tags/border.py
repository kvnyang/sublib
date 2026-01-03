# sublib/ass/tags/border.py
"""Border and shadow tag values."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class BorderSize:
    """Value for \\bord, \\xbord, \\ybord tags."""
    value: float


@dataclass  
class ShadowDistance:
    """Value for \\shad, \\xshad, \\yshad tags."""
    value: float


@dataclass
class BlurEdge:
    """Value for \\be tag."""
    strength: int


@dataclass
class BlurGaussian:
    """Value for \\blur tag."""
    strength: float
