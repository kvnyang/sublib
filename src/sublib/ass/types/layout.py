"""Layout-related value types for ASS format."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass
class Alignment:
    """Alignment value (numpad style 1-9).
    
    Attributes:
        value: Alignment position (1-9, numpad layout)
        legacy: True if from legacy \\a tag
    """
    value: int
    legacy: bool = False


@dataclass
class WrapStyle:
    """Wrap style value (0-3)."""
    style: Literal[0, 1, 2, 3]

