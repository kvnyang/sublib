# sublib/ass/tags/color.py
"""Color and alpha tag values."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Color:
    """Value for \\c, \\1c, \\2c, \\3c, \\4c tags."""
    value: int  # 0xBBGGRR format
    
    @property
    def blue(self) -> int:
        return (self.value >> 16) & 0xFF
    
    @property
    def green(self) -> int:
        return (self.value >> 8) & 0xFF
    
    @property
    def red(self) -> int:
        return self.value & 0xFF
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        return cls((b << 16) | (g << 8) | r)
    
    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        hex_str = hex_str.strip("&H").strip("&")
        return cls(int(hex_str, 16))


@dataclass
class Alpha:
    """Value for \\alpha, \\1a, \\2a, \\3a, \\4a tags."""
    value: int
    
    @property
    def opacity(self) -> float:
        return 1.0 - (self.value / 255.0)
