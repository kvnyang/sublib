# sublib/ass/types/timestamp.py
"""Timestamp value type for ASS format.

ASS uses H:MM:SS.CC format where CC is centiseconds (hundredths of a second).
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Timestamp:
    """ASS timestamp value.
    
    ASS format: H:MM:SS.CC (centiseconds, i.e. hundredths of a second)
    Internal storage: centiseconds (1/100 second precision)
    
    Attributes:
        cs: Time value in centiseconds
    """
    cs: int = 0
    
    @property
    def hours(self) -> int:
        return self.cs // 360000
    
    @property
    def minutes(self) -> int:
        return (self.cs % 360000) // 6000
    
    @property
    def seconds(self) -> int:
        return (self.cs % 6000) // 100
    
    @property
    def centiseconds(self) -> int:
        return self.cs % 100
    
    @property
    def total_seconds(self) -> float:
        """Get total time in seconds."""
        return self.cs / 100.0
    
    def to_ms(self) -> int:
        """Convert to milliseconds."""
        return self.cs * 10
    
    @classmethod
    def from_ass_str(cls, s: str) -> "Timestamp":
        """Parse from ASS timestamp string (H:MM:SS.CC).
        
        Args:
            s: Timestamp string, e.g. "0:01:30.50"
            
        Returns:
            Timestamp with parsed value
        """
        s = s.strip()
        parts = s.split(':')
        if len(parts) != 3:
            return cls(cs=0)
        
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
            sec_parts = parts[2].split('.')
            seconds = int(sec_parts[0])
            centiseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
            
            total_cs = hours * 360000 + minutes * 6000 + seconds * 100 + centiseconds
            return cls(cs=total_cs)
        except ValueError:
            return cls(cs=0)
    
    @classmethod
    def from_ms(cls, ms: int) -> "Timestamp":
        """Create from milliseconds."""
        return cls(cs=ms // 10)
    
    def to_ass_str(self) -> str:
        """Format as ASS timestamp string (H:MM:SS.CC)."""
        return f"{self.hours}:{self.minutes:02d}:{self.seconds:02d}.{self.centiseconds:02d}"
    
    def __sub__(self, other: "Timestamp") -> "Timestamp":
        """Subtract two timestamps."""
        return Timestamp(cs=self.cs - other.cs)
    
    def __add__(self, other: "Timestamp") -> "Timestamp":
        """Add two timestamps."""
        return Timestamp(cs=self.cs + other.cs)
    
    def __lt__(self, other: "Timestamp") -> bool:
        return self.cs < other.cs
    
    def __le__(self, other: "Timestamp") -> bool:
        return self.cs <= other.cs
    
    def __gt__(self, other: "Timestamp") -> bool:
        return self.cs > other.cs
    
    def __ge__(self, other: "Timestamp") -> bool:
        return self.cs >= other.cs
