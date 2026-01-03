# sublib/ass/tags/layout.py
"""Layout and style tag values."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass
class Alignment:
    """Value for \\an or \\a (legacy) tags."""
    value: int  # 1-9
    legacy: bool = False


@dataclass
class WrapStyle:
    """Value for \\q tag."""
    style: Literal[0, 1, 2, 3]


@dataclass
class StyleReset:
    """Value for \\r or \\r<style> tag."""
    style_name: str | None = None
