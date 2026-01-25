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
from sublib.ass.naming import normalize_key, get_canonical_name

logger = logging.getLogger(__name__)



@dataclass
class AssFile:
    """ASS subtitle file.
    
    Represents a complete .ass file with styles and events.
    The script_info, styles, and events fields are intelligent containers.
    
    Attributes:
        script_info: Script metadata and comments
        styles: Style definitions
        events: Dialogue and other events
        diagnostics: Structured diagnostics (Error, Warning, Info)
    """
    script_info: AssScriptInfo = field(default_factory=AssScriptInfo)
    styles: AssStyles = field(default_factory=AssStyles)
    events: AssEvents = field(default_factory=AssEvents)
    extra_sections: list[RawSection] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)

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
        
        # Mandatory: Halt if Layer 1 found fatal structural errors
        errors = [d for d in struct_parser.diagnostics if d.level == DiagnosticLevel.ERROR]
        if errors:
            from sublib.ass.diagnostics import AssStructuralError
            raise AssStructuralError(f"Fatal structural errors found in ASS file ({len(errors)})", errors)

        ass_file = cls()
        ass_file.diagnostics.extend(struct_parser.diagnostics)
        
        # --- Layer 2: Semantic Parsing (Dispatch to models) ---
        
        # 1. [Script Info]
        raw_info = raw_doc.get_section('script info')
        if raw_info:
            ass_file.script_info = AssScriptInfo.from_raw(raw_info)
            ass_file.diagnostics.extend(ass_file.script_info.diagnostics)
        else:
            # Fallback: Create default Script Info if missing.
            # StructuralParser already added a MISSING_SECTION warning.
            ass_file.script_info = AssScriptInfo()
            ass_file.script_info.set('ScriptType', 'v4.00+')

        script_type = ass_file.script_info.get('ScriptType')

        # 2. [Styles]
        raw_styles = raw_doc.get_section('v4+ styles') or raw_doc.get_section('v4 styles')
        if raw_styles:
            ass_file.styles = AssStyles.from_raw(raw_styles, script_type=script_type)
            ass_file.diagnostics.extend(ass_file.styles.diagnostics)
        else:
            # StructuralParser already warned if Styles are missing
            ass_file.styles = AssStyles()

        # 3. [Events]
        raw_events = raw_doc.get_section('events')
        if raw_events:
            ass_file.events = AssEvents.from_raw(raw_events, script_type=script_type)
            ass_file.diagnostics.extend(ass_file.events.diagnostics)
        else:
            # StructuralParser already warned if Events are missing
            ass_file.events = AssEvents()

        # 4. Custom/Other Sections (Fonts, Graphics, etc.)
        core_sections = {'script info', 'v4 styles', 'v4+ styles', 'events'}
        for section in raw_doc.sections:
            if section.name.lower() not in core_sections:
                ass_file.extra_sections.append(section)

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
        lines.append(f'[{get_canonical_name("script info", context="SECTION")}]')
        # Output preserved comments first
        for comment in self.script_info.header_comments:
            lines.append(f'; {comment}')
        for key, value in self.script_info.items():
            lines.append(self.script_info.render_line(key, value))
        lines.append('')
        
        # 2. Styles
        # Determine appropriate section name
        script_type = self.script_info.get('ScriptType', 'v4.00+')
        if "v4" in script_type.lower() and "+" not in script_type:
             style_section_key = normalize_key("v4 styles")
        else:
             style_section_key = normalize_key("v4+ styles")
             
        lines.append(f'[{get_canonical_name(style_section_key, context="SECTION")}]')
        # Output preserved comments
        for comment in self.styles.get_comments():
            lines.append(f'; {comment}')
            
        # Use raw format if available, else standard
        if self.styles._raw_format_fields:
            out_fields = self.styles._raw_format_fields
        elif "v4 styles" == style_section_key:
            out_fields = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour',
                        'TertiaryColour', 'BackColour', 'Bold', 'Italic', 'BorderStyle',
                        'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding']
        else:
            out_fields = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour',
                        'OutlineColour', 'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut',
                        'ScaleX', 'ScaleY', 'Spacing', 'Angle', 'BorderStyle', 'Outline', 'Shadow',
                        'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding']
        
        lines.append(f"Format: {', '.join(out_fields)}")
        
        for style in self.styles:
            lines.append(style.render(format_fields=out_fields))
            
        # Render custom records (unknown descriptors)
        for record in self.styles.custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
            
        lines.append('')
        
        # 3. Events
        lines.append(f'[{get_canonical_name("events", context="SECTION")}]')
        # Output preserved comments
        for comment in self.events.get_comments():
            lines.append(f'; {comment}')
            
        # Use raw format if available, else standard
        if self.events._raw_format_fields:
            out_fields = self.events._raw_format_fields
        else:
            out_fields = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
            
        lines.append(f"Format: {', '.join(out_fields)}")
        for event in self.events:
            lines.append(event.render(format_fields=out_fields))
            
        # Render custom records (unknown descriptors)
        for record in self.events.custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
        
        # 4. Extra Sections (Fonts, Graphics, etc.)
        # Sort to ensure standard order: Fonts -> Graphics -> Others (stable sort)
        sorted_extras = sorted(
            self.extra_sections,
            key=lambda s: 0 if s.name == 'fonts' else 1 if s.name == 'graphics' else 2
        )
        for section in sorted_extras:
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
