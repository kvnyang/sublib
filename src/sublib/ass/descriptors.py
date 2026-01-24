"""ASS line descriptor and format definitions.

This module defines the allowed descriptors for each section and provides
utilities for parsing Format lines according to ASS specification.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import logging

logger = logging.getLogger(__name__)


# Section -> allowed descriptors (None means any key:value is allowed)
SECTION_DESCRIPTORS: dict[str, set[str] | None] = {
    'script info': None,  # Script Info allows any key:value
    'v4 styles': {'Format', 'Style'},
    'v4+ styles': {'Format', 'Style'},
    'events': {'Format', 'Dialogue', 'Comment', 'Picture', 'Sound', 'Movie', 'Command'},
    'fonts': {'fontname'},
    'graphics': {'filename'},
}

# Event type descriptors
EVENT_TYPES = frozenset({'Dialogue', 'Comment', 'Picture', 'Sound', 'Movie', 'Command'})

# Default field order for Events (v4+ format)
DEFAULT_EVENT_FIELDS = (
    'Layer', 'Start', 'End', 'Style', 'Name',
    'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text'
)

# Default field order for Events (v4/SSA format)
DEFAULT_EVENT_FIELDS_V4 = (
    'Marked', 'Start', 'End', 'Style', 'Name',
    'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text'
)

# Known event fields (for filtering unknown fields)
KNOWN_EVENT_FIELDS = frozenset({
    'Layer', 'Marked', 'Start', 'End', 'Style', 'Name',
    'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text'
})


@dataclass
class FormatSpec:
    """Parsed Format line specification.
    
    Provides field name to index mapping for dynamic event parsing.
    
    Attributes:
        fields: Field names in order as specified in Format line
        field_indices: Map of known field name -> column index
        text_index: Index of Text field (must be last)
    """
    fields: tuple[str, ...]
    field_indices: dict[str, int] = field(default_factory=dict)
    text_index: int = -1
    
    def __post_init__(self):
        # Build index map for known fields only (case-insensitive lookup)
        # Store lowercase keys for unified internal access
        known_lower = {f.lower(): f for f in KNOWN_EVENT_FIELDS}
        for i, f in enumerate(self.fields):
            f_lower = f.lower()
            if f_lower in known_lower:
                canonical = known_lower[f_lower]
                self.field_indices[canonical] = i
        self.text_index = len(self.fields) - 1
    
    @classmethod
    def parse(cls, content: str) -> 'FormatSpec':
        """Parse Format line content.
        
        Args:
            content: The part after 'Format:' in the Format line
            
        Returns:
            FormatSpec instance
            
        Raises:
            ValueError: If Text is not the last field
        """
        fields = tuple(f.strip() for f in content.split(','))
        
        if not fields:
            raise ValueError("Empty Format line")
        
        if fields[-1].lower() != 'text':
            raise ValueError(f"Text must be last field, got '{fields[-1]}'")
        
        return cls(fields=fields)
    
    @classmethod
    def default(cls) -> 'FormatSpec':
        """Get default v4+ format specification."""
        return cls(fields=DEFAULT_EVENT_FIELDS)
    
    @classmethod
    def default_v4(cls) -> 'FormatSpec':
        """Get default v4/SSA format specification."""
        return cls(fields=DEFAULT_EVENT_FIELDS_V4)
    
    def get_index(self, field_name: str) -> int | None:
        """Get column index for a field name.
        
        Returns:
            Column index or None if field not in format
        """
        return self.field_indices.get(field_name)


def parse_descriptor_line(line: str) -> tuple[str, str] | None:
    """Parse a 'Descriptor: content' format line.
    
    Args:
        line: A stripped line from the ASS file
        
    Returns:
        (descriptor, content) tuple, or None if not a descriptor line
    """
    if ':' not in line:
        return None
    descriptor, _, content = line.partition(':')
    return descriptor.strip(), content


def is_descriptor_allowed(section: str, descriptor: str) -> bool:
    """Check if a descriptor is allowed in a section (case-insensitive).
    
    Args:
        section: Section name (lowercase, e.g., 'events')
        descriptor: Descriptor name (e.g., 'Dialogue')
        
    Returns:
        True if allowed, False otherwise
    """
    allowed = SECTION_DESCRIPTORS.get(section)
    if allowed is None:
        return True  # Script Info allows any key
    
    descriptor_lower = descriptor.lower()
    return any(descriptor_lower == a.lower() for a in allowed)


def get_default_format_for_script_type(script_type: str | None) -> FormatSpec:
    """Get default format based on ScriptType.
    
    Args:
        script_type: ScriptType value (e.g., 'v4.00+', 'v4.00')
        
    Returns:
        FormatSpec.default() (v4+/Layer) by default
        FormatSpec.default_v4() (v4/Marked) only when explicitly v4.00 without +
    """
    # Only use v4 format if explicitly specified as v4.00 (without +)
    if script_type and 'v4' in script_type.lower() and '+' not in script_type:
        return FormatSpec.default_v4()
    # Default to v4+ for modern files
    return FormatSpec.default()


def check_format_scripttype_consistency(
    format_spec: FormatSpec, 
    script_type: str | None
) -> str | None:
    """Check if Format fields match ScriptType.
    
    Args:
        format_spec: Parsed format specification
        script_type: ScriptType value (e.g., 'v4.00+')
        
    Returns:
        Warning message if mismatch, None if consistent
    """
    has_layer = 'Layer' in format_spec.field_indices
    has_marked = 'Marked' in format_spec.field_indices
    
    # Treat None or v4+ as modern format (Layer expected)
    # Only explicit v4.00 (without +) is legacy
    is_v4_legacy = script_type and 'v4' in script_type.lower() and '+' not in script_type
    
    if not is_v4_legacy and has_marked and not has_layer:
        return f"Format uses 'Marked' but ScriptType is '{script_type or 'v4.00+'}' (v4+ expects 'Layer')"
    if is_v4_legacy and has_layer and not has_marked:
        return f"Format uses 'Layer' but ScriptType is '{script_type}' (v4 expects 'Marked')"
    return None
