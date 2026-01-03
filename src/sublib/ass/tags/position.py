# sublib/ass/tags/position.py
"""Position and movement tag definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

from sublib.ass.tags.base import TagCategory


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


class PosTag:
    """\\pos(x,y) tag definition."""
    name: ClassVar[str] = "pos"
    category: ClassVar[TagCategory] = TagCategory.POSITION
    is_event: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset({"move"})
    
    @staticmethod
    def parse(raw: str) -> Position | None:
        parts = raw.split(",")
        if len(parts) != 2:
            return None
        try:
            return Position(x=float(parts[0]), y=float(parts[1]))
        except ValueError:
            return None
    
    @staticmethod
    def format(val: Position) -> str:
        return f"\\pos({val.x},{val.y})"


class MoveTag:
    """\\move(x1,y1,x2,y2[,t1,t2]) tag definition."""
    name: ClassVar[str] = "move"
    category: ClassVar[TagCategory] = TagCategory.POSITION
    is_event: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset({"pos"})
    
    @staticmethod
    def parse(raw: str) -> Move | None:
        parts = raw.split(",")
        if len(parts) == 4:
            try:
                return Move(
                    x1=float(parts[0]), y1=float(parts[1]),
                    x2=float(parts[2]), y2=float(parts[3])
                )
            except ValueError:
                return None
        elif len(parts) == 6:
            try:
                return Move(
                    x1=float(parts[0]), y1=float(parts[1]),
                    x2=float(parts[2]), y2=float(parts[3]),
                    t1=int(parts[4]), t2=int(parts[5])
                )
            except ValueError:
                return None
        return None
    
    @staticmethod
    def format(val: Move) -> str:
        if val.t1 is not None and val.t2 is not None:
            return f"\\move({val.x1},{val.y1},{val.x2},{val.y2},{val.t1},{val.t2})"
        return f"\\move({val.x1},{val.y1},{val.x2},{val.y2})"


class OrgTag:
    """\\org(x,y) tag definition."""
    name: ClassVar[str] = "org"
    category: ClassVar[TagCategory] = TagCategory.POSITION
    is_event: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Position | None:
        return PosTag.parse(raw)
    
    @staticmethod
    def format(val: Position) -> str:
        return f"\\org({val.x},{val.y})"
