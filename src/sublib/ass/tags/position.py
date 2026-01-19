"""Position and movement tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.tags.base import TagCategory, _format_float
from sublib.ass.types import Position, Move


class PosTag:
    """\\pos(x,y) tag definition."""
    name: ClassVar[str] = "pos"
    category: ClassVar[TagCategory] = TagCategory.POSITION
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
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
        return f"\\pos({_format_float(val.x)},{_format_float(val.y)})"


class MoveTag:
    """\\move(x1,y1,x2,y2[,t1,t2]) tag definition."""
    name: ClassVar[str] = "move"
    category: ClassVar[TagCategory] = TagCategory.POSITION
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
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
            return f"\\move({_format_float(val.x1)},{_format_float(val.y1)},{_format_float(val.x2)},{_format_float(val.y2)},{val.t1},{val.t2})"
        return f"\\move({_format_float(val.x1)},{_format_float(val.y1)},{_format_float(val.x2)},{_format_float(val.y2)})"


class OrgTag:
    """\\org(x,y) tag definition."""
    name: ClassVar[str] = "org"
    category: ClassVar[TagCategory] = TagCategory.POSITION
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> Position | None:
        return PosTag.parse(raw)
    
    @staticmethod
    def format(val: Position) -> str:
        return f"\\org({_format_float(val.x)},{_format_float(val.y)})"
