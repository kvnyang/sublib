# sublib/ass/types/color.py
"""Color and alpha value types for ASS format.

These types are shared between Style definitions and override tags.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Color:
    """ASS color value.
    
    ASS files use BGR format internally, but this class stores
    color channels in the more intuitive r, g, b, a format.
    
    Style format: &HAABBGGRR (8 hex digits, includes alpha)
    Tag format: &HBBGGRR& (6 hex digits, no alpha)
    
    Attributes:
        r: Red channel (0-255)
        g: Green channel (0-255)
        b: Blue channel (0-255)
        a: Alpha value (0=visible, 255=transparent)
    """
    r: int
    g: int
    b: int
    a: int = 0
    
    @classmethod
    def from_style_str(cls, s: str) -> "Color":
        """Parse from style string (&HAABBGGRR).
        
        Args:
            s: Style color string, e.g. "&H00FFFFFF" or "&H80000000"
            
        Returns:
            Color with parsed r, g, b, a
        """
        s = s.strip().lstrip("&H").rstrip("&")
        try:
            value = int(s, 16)
            a = (value >> 24) & 0xFF
            b = (value >> 16) & 0xFF
            g = (value >> 8) & 0xFF
            r = value & 0xFF
            return cls(r=r, g=g, b=b, a=a)
        except ValueError:
            return cls(r=0, g=0, b=0, a=0)
    
    @classmethod
    def from_tag_str(cls, s: str) -> "Color":
        """Parse from tag string (&HBBGGRR&).
        
        Args:
            s: Tag color string, e.g. "&HFFFFFF&"
            
        Returns:
            Color with parsed r, g, b (alpha defaults to 0)
        """
        s = s.strip().lstrip("&H").rstrip("&")
        try:
            value = int(s, 16)
            b = (value >> 16) & 0xFF
            g = (value >> 8) & 0xFF
            r = value & 0xFF
            return cls(r=r, g=g, b=b, a=0)
        except ValueError:
            return cls(r=0, g=0, b=0, a=0)
    
    def to_style_str(self) -> str:
        """Format for style output (e.g., &H00FFFFFF).
        
        Style format has no trailing &, per libass Wiki.
        """
        return f"&H{self.a:02X}{self.b:02X}{self.g:02X}{self.r:02X}"
    
    def to_tag_str(self) -> str:
        """Format for tag output (e.g., &HFFFFFF&)."""
        return f"&H{self.b:02X}{self.g:02X}{self.r:02X}&"


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
