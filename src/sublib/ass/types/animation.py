# sublib/ass/types/animation.py
"""Animation and karaoke value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass
class Transform:
    """Value for \\t(...) animated transform tag."""
    tags: str
    t1: int | None = None
    t2: int | None = None
    accel: float | None = None


@dataclass
class Karaoke:
    """Value for karaoke tags (\\k, \\K, \\kf, \\ko, \\kt)."""
    duration: int
    type: Literal["k", "K", "kf", "ko", "kt"] = "k"
