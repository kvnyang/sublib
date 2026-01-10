# sublib/ass/types/animation.py
"""Animation and karaoke value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Transform:
    """Value for \\t(...) animated transform tag.
    
    Attributes:
        tags: Parsed modifier tags as list of (name, value) tuples.
              e.g., [("fs", 40), ("1c", Color(255, 0, 0))]
        t1: Start time in milliseconds (None = line start)
        t2: End time in milliseconds (None = line end)
        accel: Acceleration factor (1.0 = linear)
    """
    tags: list[tuple[str, Any]] = field(default_factory=list)
    t1: int | None = None
    t2: int | None = None
    accel: float | None = None
    
    def to_raw_tags(self) -> str:
        """Render parsed tags back to raw string for ASS output."""
        from sublib.ass.tags.registry import format_tag
        return "".join(format_tag(name, val) for name, val in self.tags)


@dataclass
class Karaoke:
    """Value for karaoke tags (\\k, \\K, \\kf, \\ko, \\kt)."""
    duration: int
    type: Literal["k", "K", "kf", "ko", "kt"] = "k"

