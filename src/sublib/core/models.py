# sublib/core/models.py
"""Format-agnostic subtitle models."""
from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Cue:
    """Base class for all subtitle cues.
    
    Contains only universally shared attributes across all subtitle formats.
    Format-specific attributes should be defined in subclasses.
    
    The term "cue" is industry standard (WebVTT, TTML, W3C).
    
    Attributes:
        start_ms: Start time in milliseconds
        end_ms: End time in milliseconds
    """
    start_ms: int
    end_ms: int
    
    @property
    def duration_ms(self) -> int:
        """Duration in milliseconds."""
        return self.end_ms - self.start_ms
    
    @property
    @abstractmethod
    def plain_text(self) -> str:
        """Text content without formatting tags.
        
        Subclasses must implement this to extract plain text
        from their format-specific text representation.
        """
        ...


@dataclass
class SubtitleFile:
    """Format-agnostic subtitle file container.
    
    Attributes:
        events: List of subtitle cues
        metadata: File-level metadata (title, author, etc.)
    """
    events: list[Cue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def sort_by_time(self) -> None:
        """Sort events by start time in place."""
        self.events.sort(key=lambda e: e.start_ms)
    
    def sorted_events(self) -> list[Cue]:
        """Return events sorted by start time."""
        return sorted(self.events, key=lambda e: e.start_ms)

