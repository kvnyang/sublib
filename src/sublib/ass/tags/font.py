# sublib/ass/tags/font.py
"""Font style tag values."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FontScale:
    """Value for \\fscx and \\fscy tags."""
    value: float


@dataclass
class Rotation:
    """Value for \\frx, \\fry, \\frz tags."""
    angle: float


@dataclass
class Shear:
    """Value for \\fax and \\fay tags."""
    factor: float
