"""Raw structure models for Layer 1 parsing."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawRecord:
    """A raw key-value pair from a descriptor line."""
    descriptor: str
    value: str
    line_number: int


@dataclass
class RawSection:
    """A raw section containing comments and records."""
    name: str  # Normalized lowercase name
    original_name: str
    raw_lines: list[str] = field(default_factory=list)
    line_number: int = 0

    comments: list[str] = field(default_factory=list)
    records: list[RawRecord] = field(default_factory=list)
    
    # For Format-based sections (Styles, Events)
    format_fields: Optional[list[str]] = None
    format_line_number: Optional[int] = None


@dataclass
class RawDocument:
    """A collection of raw sections."""
    sections: list[RawSection] = field(default_factory=list)
    
    def get_section(self, name: str) -> Optional[RawSection]:
        """Get the first section with the given normalized name."""
        name_lower = name.lower()
        for section in self.sections:
            if section.name == name_lower:
                return section
        return None
