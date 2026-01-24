"""ASS File model."""
from __future__ import annotations
from dataclasses import dataclass, field
import logging
from pathlib import Path

from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
from sublib.ass.parser_layer1 import StructuralParser
from .info import AssScriptInfo
from .style import AssStyles
from .event import AssEvents

logger = logging.getLogger(__name__)


# Keep for backward compatibility if needed, but prefer sublib.ass.diagnostics.Diagnostic
ParseWarning = Diagnostic
ParseWarningType = DiagnosticLevel


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
    extra_sections: list[RawSection] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def parse_warnings(self) -> list[Diagnostic]:
        """Alias for diagnostics to maintain compatibility."""
        return self.diagnostics

    def __post_init__(self):
        if isinstance(self.script_info, dict):
            self.script_info = AssScriptInfo(self.script_info)
        if isinstance(self.styles, dict):
            self.styles = AssStyles(self.styles)
        if isinstance(self.events, list):
            self.events = AssEvents(self.events)
    
    @property
    def has_warnings(self) -> bool:
        """Check if any parse warnings or errors were collected."""
        return len(self.diagnostics) > 0
    
    @property
    def errors(self) -> list[Diagnostic]:
        """Get diagnostic messages with ERROR level."""
        return [d for d in self.diagnostics if d.level == DiagnosticLevel.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        """Get diagnostic messages with WARNING level."""
        return [d for d in self.diagnostics if d.level == DiagnosticLevel.WARNING]

    @property
    def infos(self) -> list[Diagnostic]:
        """Get diagnostic messages with INFO level."""
        return [d for d in self.diagnostics if d.level == DiagnosticLevel.INFO]

    @classmethod
    def loads(cls, content: str) -> "AssFile":
        """Parse ASS content from string using 3-layered architecture.
        
        Layer 1: Structural Parser (Structure/Sections)
        Layer 2: Semantic Parser (Typing/Logic)
        Layer 3: Content Parser (AST/Tags)
        """
        # --- Layer 1: Structural Parsing ---
        struct_parser = StructuralParser()
        raw_doc = struct_parser.parse(content)
        
        ass_file = cls()
        ass_file.diagnostics.extend(struct_parser.diagnostics)
        
        # --- Layer 2: Semantic Parsing (Dispatch to models) ---
        
        # 1. [Script Info]
        raw_info = raw_doc.get_section('script info')
        if raw_info:
            ass_file.script_info = AssScriptInfo.from_raw(raw_info)
            ass_file.diagnostics.extend(ass_file.script_info.diagnostics)
        else:
            ass_file.diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, "Missing [Script Info] section", 0, "MISSING_SECTION"))

        script_type = ass_file.script_info.get('ScriptType')

        # 2. [Styles]
        raw_styles = raw_doc.get_section('v4+ styles') or raw_doc.get_section('v4 styles')
        if raw_styles:
            ass_file.styles = AssStyles.from_raw(raw_styles, script_type=script_type)
            ass_file.diagnostics.extend(ass_file.styles.diagnostics)
        else:
             ass_file.diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, "Missing Styles section", 0, "MISSING_SECTION"))

        # 3. [Events]
        raw_events = raw_doc.get_section('events')
        if raw_events:
            ass_file.events = AssEvents.from_raw(raw_events, script_type=script_type)
            ass_file.diagnostics.extend(ass_file.events.diagnostics)
        else:
            ass_file.diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, "Missing [Events] section", 0, "MISSING_SECTION"))

        # 4. Custom/Other Sections (Fonts, Graphics, etc.)
        core_sections = {'script info', 'v4 styles', 'v4+ styles', 'events'}
        for section in raw_doc.sections:
            if section.name not in core_sections:
                ass_file.extra_sections.append(section)

        # Post-parse validation: check for missing ScriptType
        if 'ScriptType' not in ass_file.script_info:
            ass_file.diagnostics.append(Diagnostic(DiagnosticLevel.WARNING, 
                       "No ScriptType declaration, assuming v4.00+", 0, "MISSING_SCRIPTTYPE"))
        
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
        # Determine appropriate section name
        style_section = "[V4+ Styles]"
        script_type = self.script_info.get('ScriptType', 'v4.00+')
        if "v4" in script_type.lower() and "+" not in script_type:
             style_section = "[V4 Styles]"
             
        lines.append(style_section)
        # TODO: Dynamic format based on styles present? For now sticks to standard
        if style_section == "[V4 Styles]":
            lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, '
                         'TertiaryColour, BackColour, Bold, Italic, BorderStyle, '
                         'Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding')
        else:
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
        
        # 4. Extra Sections (Fonts, Graphics, etc.)
        for section in self.extra_sections:
            lines.append('')
            lines.append(f'[{section.original_name}]')
            lines.extend(section.raw_lines)
        
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
