"""Position and movement value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Position:
    """Value for \\pos(x,y) and \\org(x,y) tags."""
    x: float
    y: float


@dataclass
class Move:
    """Value for \\move(x1,y1,x2,y2[,t1,t2]) tag."""
    x1: float
    y1: float
    x2: float
    y2: float
    t1: int | None = None
    t2: int | None = None
