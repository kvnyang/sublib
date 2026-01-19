"""Fade effect value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Fade:
    """Value for \\fad(fadein,fadeout) tag."""
    fadein: int
    fadeout: int


@dataclass
class FadeComplex:
    """Value for \\fade(a1,a2,a3,t1,t2,t3,t4) tag."""
    a1: int
    a2: int
    a3: int
    t1: int
    t2: int
    t3: int
    t4: int
