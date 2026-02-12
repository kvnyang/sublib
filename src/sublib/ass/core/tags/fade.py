"""Fade effect tag definitions."""
from __future__ import annotations
from typing import ClassVar

from sublib.ass.core.tags.base import TagCategory
from sublib.ass.types import AssFade, AssFadeComplex


class FadTag:
    """\\fad(fadein,fadeout) tag definition.
    
    Note: Based on Aegisub behavior, fade effects are first-wins.
    If multiple \\fad tags appear (violating the spec), the first one takes precedence.
    """
    name: ClassVar[str] = "fad"
    category: ClassVar[TagCategory] = TagCategory.FADE
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset({"fade"})
    
    @staticmethod
    def parse(raw: str) -> AssFade | None:
        parts = raw.split(",")
        if len(parts) != 2:
            return None
        try:
            return AssFade(fadein=int(parts[0]), fadeout=int(parts[1]))
        except ValueError:
            return None
    
    @staticmethod
    def format(val: AssFade) -> str:
        return f"\\fad({val.fadein},{val.fadeout})"


class FadeTag:
    """\\fade(a1,a2,a3,t1,t2,t3,t4) tag definition.
    
    Note: Based on Aegisub behavior, fade effects are first-wins.
    If multiple \\fade tags appear (violating the spec), the first one takes precedence.
    """
    name: ClassVar[str] = "fade"
    category: ClassVar[TagCategory] = TagCategory.FADE
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = True
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = True
    exclusives: ClassVar[frozenset[str]] = frozenset({"fad"})
    
    @staticmethod
    def parse(raw: str) -> AssFadeComplex | None:
        parts = raw.split(",")
        if len(parts) != 7:
            return None
        try:
            return AssFadeComplex(
                a1=int(parts[0]), a2=int(parts[1]), a3=int(parts[2]),
                t1=int(parts[3]), t2=int(parts[4]), t3=int(parts[5]), t4=int(parts[6])
            )
        except ValueError:
            return None
    
    @staticmethod
    def format(val: AssFadeComplex) -> str:
        return f"\\fade({val.a1},{val.a2},{val.a3},{val.t1},{val.t2},{val.t3},{val.t4})"
