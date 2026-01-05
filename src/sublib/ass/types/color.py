# sublib/ass/types/color.py
"""Color and alpha value types for ASS format.

These types are shared between Style definitions and override tags.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Color:
    """ASS color value.
    
    ASS colors are in BGR format (Blue-Green-Red).
    
    Style format: &HAABBGGRR& (8 hex digits, includes alpha)
    Tag format: &HBBGGRR& (6 hex digits, no alpha)
    
    Attributes:
        bgr: Color value in 0xBBGGRR format
        alpha: Alpha value (0=visible, 255=transparent)
    """
    bgr: int
    alpha: int = 0
    
    @property
    def blue(self) -> int:
        return (self.bgr >> 16) & 0xFF
    
    @property
    def green(self) -> int:
        return (self.bgr >> 8) & 0xFF
    
    @property
    def red(self) -> int:
        return self.bgr & 0xFF
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, alpha: int = 0) -> "Color":
        """Create from RGB values."""
        return cls(bgr=(b << 16) | (g << 8) | r, alpha=alpha)
    
    @classmethod
    def from_style_int(cls, value: int) -> "Color":
        """Parse from Style format integer (0xAABBGGRR)."""
        alpha = (value >> 24) & 0xFF
        bgr = value & 0xFFFFFF
        return cls(bgr=bgr, alpha=alpha)
    
    def to_style_int(self) -> int:
        """Convert to Style format integer (0xAABBGGRR)."""
        return (self.alpha << 24) | self.bgr
    
    def to_tag_str(self) -> str:
        """Format for tag output (e.g., &HFFFFFF&)."""
        return f"&H{self.bgr:06X}&"
    
    def to_style_str(self) -> str:
        """Format for style output (e.g., &H00FFFFFF).
        
        Style format has no trailing &, per libass Wiki.
        """
        return f"&H{self.alpha:02X}{self.bgr:06X}"


@dataclass
class Alpha:
    """ASS alpha value.
    
    0 = fully visible, 255 = fully transparent
    """
    value: int
    
    @property
    def opacity(self) -> float:
        """Get opacity as 0.0-1.0 value."""
        return 1.0 - (self.value / 255.0)
    
    def to_tag_str(self) -> str:
        """Format for tag output (e.g., &HFF&)."""
        return f"&H{self.value:02X}&"
