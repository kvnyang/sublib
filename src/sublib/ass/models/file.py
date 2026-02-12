"""ASS File model."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
from sublib.ass.parser_layer1 import StructuralParser
from .info import AssScriptInfo
from .style import AssStyles
from .event import AssEvents
from .base import AssSection, AssRawSection
from sublib.ass.naming import normalize_key, get_canonical_name


@dataclass
class AssFile:
    """ASS subtitle file."""
    sections: list[AssSection] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def script_info(self) -> AssScriptInfo:
        for s in self.sections:
            if isinstance(s, AssScriptInfo): return s
        # Fallback to empty if not found
        info = AssScriptInfo()
        self.sections.insert(0, info)
        return info

    @property
    def styles(self) -> AssStyles:
        for s in self.sections:
            if isinstance(s, AssStyles): return s
        # Fallback to empty if not found
        styles = AssStyles()
        # Find index to insert (after script info if possible)
        idx = 0
        for i, s in enumerate(self.sections):
            if isinstance(s, AssScriptInfo): idx = i + 1
        self.sections.insert(idx, styles)
        return styles

    @property
    def events(self) -> AssEvents:
        for s in self.sections:
            if isinstance(s, AssEvents): return s
        # Fallback to empty if not found
        events = AssEvents()
        self.sections.append(events)
        return events

    @property
    def extra_sections(self) -> list[AssRawSection]:
        return [s for s in self.sections if isinstance(s, AssRawSection)]

    def __post_init__(self):
        pass
    
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

    @classmethod
    def loads(cls, content: str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = True) -> "AssFile":
        """Parse ASS content from string using 3-layered architecture.
        
        Args:
            content: The ASS string to parse.
            style_format: Optional format override (filters ingested fields).
            event_format: Optional format override (filters ingested fields).
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
        
        # --- Layer 2: Semantic Parsing (Declarative Dispatch) ---
        script_type = "v4.00+" 
        info_model: AssScriptInfo | None = None
        
        # Pre-pass: We need script_type for some sections context
        raw_info_sec = raw_doc.get_section('script info')
        if raw_info_sec:
            info_model = AssScriptInfo.from_raw(raw_info_sec)
            script_type = info_model.get('scripttype', 'v4.00+')
        
        # Dispatch Mapping
        processed_sections: list[AssSection] = []
        for raw_section in raw_doc.sections:
            section_name = raw_section.name.lower()
            
            if section_name == 'script info':
                section = info_model or AssScriptInfo.from_raw(raw_section)
                info_model = section # ensure reference
            elif section_name in ('v4 styles', 'v4+ styles'):
                # Version Consistency Check
                actual_is_v4plus = section_name == 'v4+ styles'
                defined_is_v4plus = str(script_type) == 'v4.00+'
                if actual_is_v4plus != defined_is_v4plus:
                    expected_h = "[V4+ Styles]" if defined_is_v4plus else "[V4 Styles]"
                    ass_file.diagnostics.append(Diagnostic(
                        DiagnosticLevel.WARNING, 
                        f"ScriptType '{script_type}' mismatch with section header [{raw_section.original_name}] (expected {expected_h})",
                        raw_section.line_number, "VERSION_SECTION_MISMATCH"
                    ))
                section = AssStyles.from_raw(raw_section, script_type=script_type, style_format=style_format, auto_fill=auto_fill)
            elif section_name == 'events':
                section = AssEvents.from_raw(raw_section, script_type=script_type, event_format=event_format, auto_fill=auto_fill)
            else:
                section = AssRawSection(name=section_name, raw_lines=raw_section.raw_lines, original_name=raw_section.original_name)
            
            processed_sections.append(section)
            ass_file.diagnostics.extend(section.diagnostics)

        # Post-pass: Ensure Script Info exists
        if info_model is None:
            info_model = AssScriptInfo()
            info_model.set('scripttype', 'v4.00+')
            processed_sections.insert(0, info_model)
            ass_file.diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING, "Missing [Script Info] section, assuming ScriptType: v4.00+", 0, "MISSING_SCRIPTTYPE"
            ))

        ass_file.sections = processed_sections
        return ass_file

    def dumps(self, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = False) -> str:
        """Serialize the model back to an ASS string using polymorphic rendering."""
        script_type = self.script_info.get('scripttype', 'v4.00+')
        
        section_texts = []
        for section in self.sections:
            if isinstance(section, AssStyles):
                text = section.render(script_type=script_type, auto_fill=auto_fill)
            elif isinstance(section, AssEvents):
                text = section.render(script_type=script_type, auto_fill=auto_fill)
            elif isinstance(section, AssScriptInfo):
                text = section.render()
            else:
                text = section.render()
            
            if text:
                section_texts.append(text)
        
        return "\n\n".join(section_texts)

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
        """Load ASS file from path."""
        from sublib.io import read_text_file
        content = read_text_file(path, encoding='utf-8-sig')
        return cls.loads(content, style_format=style_format, event_format=event_format, auto_fill=auto_fill)
    
    def dump(self, path: Path | str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = False) -> None:
        """Save subtitle model to file."""
        from sublib.io import write_text_file
        content = self.dumps(style_format=style_format, event_format=event_format, auto_fill=auto_fill)
        write_text_file(path, content, encoding='utf-8-sig')
