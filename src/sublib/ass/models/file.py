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
    def loads(cls, content: str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = True) -> "AssFile":
        """Parse ASS content from string using 3-layered architecture.
        
        Args:
            content: The ASS string to parse.
            style_format: Optional format override (filters ingested fields).
            event_format: Optional format override (filters ingested fields).
            
        Layer 1: Structural Parser (Structure/Sections)
        Layer 2: Semantic Parser (Typing/Logic)
        Layer 3: Content Parser (AST/Tags)
        """
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
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
            # Create default Script Info if missing.
            # StructuralParser already added a MISSING_SECTION warning.
            ass_file.script_info = AssScriptInfo()
            ass_file.script_info.set('scripttype', 'v4.00+')
            
            ass_file.diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                "Missing [Script Info] section, assuming ScriptType: v4.00+",
                0, "MISSING_SCRIPTTYPE"
            ))

        script_type = ass_file.script_info.get('scripttype')

        # 2. [Styles]
        raw_styles_v4plus = raw_doc.get_section('v4+ styles')
        raw_styles_v4 = raw_doc.get_section('v4 styles')
        raw_styles = raw_styles_v4plus or raw_styles_v4
        
        if raw_styles:
            from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
            # Version Consistency Check
            actual_is_v4plus = raw_styles.name == 'v4+ styles'
            defined_is_v4plus = script_type == 'v4.00+'
            
            if actual_is_v4plus != defined_is_v4plus:
                expected_header = "[V4+ Styles]" if defined_is_v4plus else "[V4 Styles]"
                actual_header = f"[{raw_styles.original_name}]"
                ass_file.diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"ScriptType '{script_type}' mismatch with section header {actual_header} (expected {expected_header})",
                    raw_styles.line_number, "VERSION_SECTION_MISMATCH"
                ))

            ass_file.styles = AssStyles.from_raw(raw_styles, script_type=script_type, style_format=style_format, auto_fill=auto_fill)
            ass_file.diagnostics.extend(ass_file.styles.diagnostics)
        else:
            # StructuralParser already warned if Styles are missing
            ass_file.styles = AssStyles()

        # 3. [Events]
        raw_events = raw_doc.get_section('events')
        if raw_events:
            ass_file.events = AssEvents.from_raw(raw_events, script_type=script_type, event_format=event_format, auto_fill=auto_fill)
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

    def dumps(self, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = False, validate: bool = False) -> str:
        """Serialize the model back to an ASS string.
        
        Args:
            style_format: Optional format override for Styles section.
            event_format: Optional format override for Events section.
            auto_fill: If True, fills missing fields with defaults.
            validate: If True, validates style references before dumping.
        """
        if validate:
            errors = self._validate_styles()
            if errors:
                raise ValueError(f"Style validation failed: {'; '.join(errors)}")

        lines = []
        script_type = self.script_info.get('scripttype', 'v4.00+')
        
        # 1. Script Info
        lines.append(f'[{get_canonical_name("script info", context="SECTION")}]')
        for comment in self.script_info.header_comments:
            lines.append(f'; {comment}')
        
        standard_keys = [
            'scripttype', 'title', 'original script', 'original translation', 
            'original editing', 'original timing', 'synch point', 'script updated by', 
            'update details', 'playresx', 'playresy', 'playdepth', 'timer', 
            'wrapstyle'
        ]
        written_keys = set()
        for key in standard_keys:
            if key in self.script_info:
                lines.append(self.script_info.render_line(key, self.script_info[key]))
                written_keys.add(key)
        for key in self.script_info.keys():
            if normalize_key(key) not in written_keys:
                lines.append(self.script_info.render_line(key, self.script_info[key]))
        lines.append('')
        
        # 2. Styles
        is_v4 = "v4" in script_type.lower() and "+" not in script_type
        style_section_key = normalize_key("v4 styles") if is_v4 else normalize_key("v4+ styles")
        lines.append(f'[{get_canonical_name(style_section_key, context="SECTION")}]')
        for comment in self.styles.section_comments:
            lines.append(f'; {comment}')
            
        # Format Priority (Phase 33 - Stateless):
        # 1. Parameter List (Non-empty): Specific Intent
        # 2. Parameter None: Fidelity/Minimalist
        # 3. Parameter Empty List []: Standard View
        if style_format:
            out_style_format = style_format
        elif style_format is None:
            out_style_format = self.styles._raw_format_fields or self.styles.get_explicit_format(script_type)
        else:
            # Default ([]) -> Standard Mode
            if is_v4:
                out_style_format = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'TertiaryColour', 'BackColour', 'Bold', 'Italic', 'BorderStyle']
            else:
                out_style_format = ['Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'OutlineColour', 'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut', 'ScaleX', 'ScaleY', 'Spacing', 'Angle', 'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding']
            
        lines.append(f"Format: {', '.join(out_style_format)}")

        for style in self.styles:
            lines.append(style.render(format_fields=out_style_format, auto_fill=auto_fill))
        for record in self.styles.custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
        lines.append('')
        
        # 3. Events
        lines.append(f'[{get_canonical_name("events", context="SECTION")}]')
        for comment in self.events.get_comments():
            lines.append(f'; {comment}')
            
        # Format Priority (Phase 33 - Stateless):
        # 1. Parameter List (Non-empty): Specific Intent
        # 2. Parameter None: Fidelity/Minimalist
        # 3. Parameter Empty List []: Standard View
        if event_format:
            out_event_format = event_format
        elif event_format is None:
            out_event_format = self.events._raw_format_fields or self.events.get_explicit_format(script_type)
        else:
            # Default ([]) -> Standard Mode
            if is_v4:
                out_event_format = ['Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
            else:
                out_event_format = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
            
        lines.append(f"Format: {', '.join(out_event_format)}")
        for event in self.events:
            lines.append(event.render(format_fields=out_event_format, auto_fill=auto_fill))
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
    def load(cls, path: Path | str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = True) -> "AssFile":
        """Load ASS file from path.
        
        Args:
            path: Target file path.
            style_format: Optional format override for Styles section.
            event_format: Optional format override for Events section.
            auto_fill: Whether to fill missing standard fields with defaults.
        """
        from sublib.io import read_text_file
        content = read_text_file(path, encoding='utf-8-sig')
        return cls.loads(content, style_format=style_format, event_format=event_format, auto_fill=auto_fill)
    
    def dump(self, path: Path | str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = False, validate: bool = False) -> None:
        """Save subtitle model to file.
        
        Args:
            path: Output file path.
            style_format: Optional format override for Styles section.
            event_format: Optional format override for Events section.
            auto_fill: Whether to fill missing fields with defaults.
            validate: If True, raise ValueError for undefined style references.
        """
        from sublib.io import write_text_file
        content = self.dumps(style_format=style_format, event_format=event_format, auto_fill=auto_fill, validate=validate)
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
