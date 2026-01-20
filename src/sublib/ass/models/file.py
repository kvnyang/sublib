"""ASS File model."""
from __future__ import annotations
from dataclasses import dataclass, field
import logging
from pathlib import Path

from .info import AssScriptInfo
from .style import AssStyles
from .event import AssEvents

logger = logging.getLogger(__name__)


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    The script_info, styles, and events fields are intelligent containers.
    """
    script_info: AssScriptInfo = field(default_factory=AssScriptInfo)
    styles: AssStyles = field(default_factory=AssStyles)
    events: AssEvents = field(default_factory=AssEvents)

    def __post_init__(self):
        if isinstance(self.script_info, dict):
            self.script_info = AssScriptInfo(self.script_info)
        if isinstance(self.styles, dict):
            self.styles = AssStyles(self.styles)
        if isinstance(self.events, list):
            self.events = AssEvents(self.events)

    @classmethod
    def loads(cls, content: str) -> "AssFile":
        """Parse ASS content from string."""
        from sublib.ass.text import AssTextParser
        text_parser = AssTextParser()
        
        ass_file = cls()
        lines = content.splitlines()
        current_section = None
        line_number = 0
        
        for line in lines:
            line_number += 1
            line = line.strip()
            
            if not line or line.startswith(';'):
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].lower()
                continue
            
            if current_section == 'script info':
                result = AssScriptInfo.parse_line(line)
                if result:
                    key, value = result
                    if key in ass_file.script_info:
                        logger.warning(f"Duplicate Script Info key: {key}")
                    ass_file.script_info[key] = value  # last-wins
            
            elif current_section in ('v4 styles', 'v4+ styles'):
                if line.startswith('Style:'):
                    ass_file.styles.add_from_line(line)
            
            elif current_section == 'events':
                if line.startswith('Dialogue:'):
                    ass_file.events.add_from_line(line, text_parser, line_number)
        
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
