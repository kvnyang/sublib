# sublib/ass/tags/transform.py
"""Animation and karaoke tag values."""
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
    """Value for \\k, \\K, \\kf, \\ko, \\kt tags."""
    duration: int
    type: Literal["k", "K", "kf", "ko", "kt"] = "k"
