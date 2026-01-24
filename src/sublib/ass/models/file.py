"""ASS File model."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
from typing import NamedTuple

from .info import AssScriptInfo
from .style import AssStyles
from .event import AssEvents

logger = logging.getLogger(__name__)


class ParseWarningType(Enum):
    """Types of parse warnings."""
    MALFORMED_LINE = 'malformed_line'           # Line has no descriptor
    INVALID_DESCRIPTOR = 'invalid_descriptor'   # Descriptor not allowed in section
    DUPLICATE_KEY = 'duplicate_key'             # Duplicate Script Info key
    MISSING_FORMAT = 'missing_format'           # Event before Format line
    INVALID_FORMAT = 'invalid_format'           # Format line parsing error
    FORMAT_SCRIPTTYPE_MISMATCH = 'format_scripttype_mismatch'  # Format vs ScriptType inconsistency
    MISSING_SCRIPTTYPE = 'missing_scripttype'   # No ScriptType declaration


class ParseWarning(NamedTuple):
    """A parse warning with context."""
    type: ParseWarningType
    line_number: int
    message: str


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    The script_info, styles, and events fields are intelligent containers.
    
    Attributes:
        script_info: Script metadata and comments
        styles: Style definitions
        events: Dialogue and other events
        parse_warnings: Warnings collected during parsing (by category)
    """
    script_info: AssScriptInfo = field(default_factory=AssScriptInfo)
    styles: AssStyles = field(default_factory=AssStyles)
    events: AssEvents = field(default_factory=AssEvents)
    parse_warnings: list[ParseWarning] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.script_info, dict):
            self.script_info = AssScriptInfo(self.script_info)
        if isinstance(self.styles, dict):
            self.styles = AssStyles(self.styles)
        if isinstance(self.events, list):
            self.events = AssEvents(self.events)
    
    @property
    def has_warnings(self) -> bool:
        """Check if any parse warnings were collected."""
        return len(self.parse_warnings) > 0
    
    @property
    def warnings_by_type(self) -> dict[ParseWarningType, list[ParseWarning]]:
        """Get parse warnings grouped by type."""
        result: dict[ParseWarningType, list[ParseWarning]] = {}
        for w in self.parse_warnings:
            result.setdefault(w.type, []).append(w)
        return result

    @classmethod
    def loads(cls, content: str) -> "AssFile":
        """Parse ASS content from string.
        
        Uses unified descriptor-based parsing with section-specific routing.
        Follows Postel's Law: be liberal in what you accept.
        
        Parse warnings are collected in ass_file.parse_warnings for inspection.
        """
        from sublib.ass.text import AssTextParser
        from sublib.ass.descriptors import (
            parse_descriptor_line, is_descriptor_allowed,
            EVENT_TYPES, FormatSpec,
            get_default_format_for_script_type, check_format_scripttype_consistency
        )
        
        def add_warning(wtype: ParseWarningType, line_num: int, msg: str):
            """Helper to add warning and log it."""
            ass_file.parse_warnings.append(ParseWarning(wtype, line_num, msg))
            logger.warning(f"Line {line_num}: {msg}")
        
        text_parser = AssTextParser()
        ass_file = cls()
        
        current_section: str | None = None
        current_format: FormatSpec | None = None
        
        for line_number, raw_line in enumerate(content.splitlines(), 1):
            line = raw_line.strip()
            
            if not line:
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip().lower()
                current_format = None  # Reset format for new section
                continue
            
            # Handle comments (both modern ';' and legacy '!:')
            if line.startswith(';'):
                if current_section == 'script info':
                    ass_file.script_info.add_comment(line[1:].lstrip())
                continue
            if line.startswith('!:'):
                if current_section == 'script info':
                    ass_file.script_info.add_comment(line[2:].lstrip())
                continue
            
            # Parse descriptor line
            parsed = parse_descriptor_line(line)
            if not parsed:
                add_warning(ParseWarningType.MALFORMED_LINE, line_number, 
                           f"Malformed line (no descriptor): {line[:50]}")
                continue
            
            descriptor, descriptor_content = parsed
            descriptor_lower = descriptor.lower()
            
            # Check if descriptor is allowed in this section
            if current_section and not is_descriptor_allowed(current_section, descriptor):
                add_warning(ParseWarningType.INVALID_DESCRIPTOR, line_number,
                           f"'{descriptor}' not allowed in [{current_section}]")
                continue
            
            # Route to section-specific handler
            if current_section == 'script info':
                # Script Info: any key allowed
                if descriptor in ass_file.script_info:
                    add_warning(ParseWarningType.DUPLICATE_KEY, line_number,
                               f"Duplicate key '{descriptor}'")
                ass_file.script_info[descriptor] = descriptor_content.strip()
            
            elif current_section in ('v4 styles', 'v4+ styles'):
                if descriptor_lower == 'format':
                    pass  # Styles use fixed format, ignore Format line content
                elif descriptor_lower == 'style':
                    ass_file.styles.add_from_line(raw_line)
            
            elif current_section == 'events':
                if descriptor_lower == 'format':
                    try:
                        current_format = FormatSpec.parse(descriptor_content)
                        # Check consistency with ScriptType
                        script_type = ass_file.script_info.get('ScriptType')
                        mismatch_msg = check_format_scripttype_consistency(current_format, script_type)
                        if mismatch_msg:
                            add_warning(ParseWarningType.FORMAT_SCRIPTTYPE_MISMATCH, line_number, mismatch_msg)
                    except ValueError as e:
                        add_warning(ParseWarningType.INVALID_FORMAT, line_number,
                                   f"Invalid Format: {e}")
                        current_format = None
                elif any(descriptor_lower == et.lower() for et in EVENT_TYPES):
                    if current_format is None:
                        script_type = ass_file.script_info.get('ScriptType')
                        current_format = get_default_format_for_script_type(script_type)
                        add_warning(ParseWarningType.MISSING_FORMAT, line_number,
                                   f"Event before Format line, using default for {script_type or 'v4.00+'}")
                    ass_file.events.add_from_line(raw_line, text_parser, line_number, format_spec=current_format)
        
        # Post-parse validation: check for missing ScriptType
        if 'ScriptType' not in ass_file.script_info:
            add_warning(ParseWarningType.MISSING_SCRIPTTYPE, 0,
                       "No ScriptType declaration, assuming v4.00+")
        
        return ass_file

    def dumps(self, validate: bool = False) -> str:
        """Render to ASS format string.
        
        Args:
            validate: If True, raise ValueError for undefined style references
        """
        if validate:
            errors = self._validate_styles()
            if errors:
                raise ValueError(f"Invalid style references:\n" + "\n".join(errors))
        
        lines = []
        
        # 1. Script Info
        lines.append('[Script Info]')
        # Output preserved comments first
        for comment in self.script_info.header_comments:
            lines.append(f'; {comment}')
        for key, value in self.script_info.items():
            lines.append(self.script_info.render_line(key, value))
        lines.append('')
        
        # 2. Styles
        lines.append('[V4+ Styles]')
        lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, '
                     'OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, '
                     'ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, '
                     'Alignment, MarginL, MarginR, MarginV, Encoding')
        for style in self.styles:
            lines.append(style.render())
        lines.append('')
        
        # 3. Events
        lines.append('[Events]')
        lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
        for event in self.events:
            lines.append(event.render())
        
        return '\n'.join(lines)

    @property
    def script_info_keys(self) -> list[str]:
        """Get list of defined script info keys."""
        return list(self.script_info.keys())

    def __iter__(self):
        """Iterate over dialogue events."""
        return iter(self.events)

    def __len__(self) -> int:
        """Get total number of dialogue events."""
        return len(self.events)
    
    @classmethod
    def load(cls, path: Path | str) -> "AssFile":
        """Load ASS file from path.
        
        Validation warnings are logged at WARNING level.
        """
        from sublib.io import read_text_file
        content = read_text_file(path, encoding='utf-8-sig')
        return cls.loads(content)
    
    def dump(self, path: Path | str, validate: bool = False) -> None:
        """Save to file.
        
        Args:
            path: Output file path
            validate: If True, raise ValueError for undefined style references
        """
        from sublib.io import write_text_file
        content = self.dumps(validate=validate)
        write_text_file(path, content, encoding='utf-8-sig')
    
    def _validate_styles(self) -> list[str]:
        """Validate that all style references are defined.
        
        Returns:
            List of error messages (empty = valid)
        """
        errors = []
        # Case-insensitive set for quick lookup
        defined_styles = {s.name.lower() for s in self.styles}
        
        for i, event in enumerate(self.events):
            if event.style.lower() not in defined_styles:
                errors.append(f"Event {i+1}: style '{event.style}' not defined")
            
            result = event.extract()
            for seg in result.segments:
                r_style = seg.block_tags.get("r")
                if r_style and r_style.lower() not in defined_styles:
                    errors.append(f"Event {i+1}: \\r style '{r_style}' not defined")
        
        return errors
