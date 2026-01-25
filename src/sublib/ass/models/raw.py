"""Raw structure models for Layer 1 parsing."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawRecord:
    """A raw key-value pair from a descriptor line."""
    descriptor: str  # Standardized name if known
    raw_descriptor: str # Original name from file
    value: str
    line_number: int


@dataclass
class RawSection:
    """A raw section containing comments and records."""
    name: str  # Standardized name (e.g., 'Script Info')
    original_name: str # Original section name from file
    line_number: int = 0
    raw_lines: list[str] = field(default_factory=list)

    comments: list[str] = field(default_factory=list)
    records: list[RawRecord] = field(default_factory=list)
    
    # For Format-based sections (Styles, Events)
    format_fields: Optional[list[str]] = None      # Standardized fields
    raw_format_fields: Optional[list[str]] = None  # Original fields
    format_line_number: Optional[int] = None


@dataclass
class RawDocument:
    """A collection of raw sections."""
    sections: list[RawSection] = field(default_factory=list)
    
    def get_section(self, name: str) -> Optional[RawSection]:
        """Get the first section with the given normalized name."""
        name_lower = name.lower()
        for section in self.sections:
            if section.name.lower() == name_lower:
                return section
        return None
