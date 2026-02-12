"""ASS File model."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
from sublib.ass.structural import StructuralParser
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
        """Parse ASS content from string using the decoupled Parser Engine.
        
        Args:
            content: The ASS string to parse.
            style_format: Optional format override (filters ingested fields).
            event_format: Optional format override (filters ingested fields).
        """
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        from sublib.ass.semantic import SemanticParser
        
        # --- Stage 1: Structural Stage ---
        struct_parser = StructuralParser()
        raw_doc = struct_parser.parse(content)
        
        # Halt if structural errors are fatal
        errors = [d for d in struct_parser.diagnostics if d.level == DiagnosticLevel.ERROR]
        if errors:
            from sublib.ass.diagnostics import AssStructuralError
            raise AssStructuralError(f"Fatal structural errors found in ASS file ({len(errors)})", errors)

        ass_file = cls()
        ass_file.diagnostics.extend(struct_parser.diagnostics)
        
        # --- Stage 2 & 3: Semantic & Orchestration Stage ---
        semantic_parser = SemanticParser()
        script_type = "v4.00+" 
        info_model: AssScriptInfo | None = None
        
        # Pre-pass: Get ScriptType context
        raw_info_sec = raw_doc.get_section('script info')
        if raw_info_sec:
            info_model = semantic_parser.ingest_script_info(raw_info_sec)
            script_type = info_model.get('scripttype', 'v4.00+')
        
        processed_sections: list[AssSection] = []
        for raw_section in raw_doc.sections:
            section_name = raw_section.name.lower()
            
            if section_name == 'script info':
                section = info_model or semantic_parser.ingest_script_info(raw_section)
                info_model = section
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
                section = semantic_parser.ingest_styles(raw_section, style_format=style_format, auto_fill=auto_fill)
            elif section_name == 'events':
                section = semantic_parser.ingest_events(raw_section, script_type=script_type, event_format=event_format, auto_fill=auto_fill)
            else:
                section = AssRawSection(name=section_name, raw_lines=raw_section.raw_lines, original_name=raw_section.original_name)
            
            processed_sections.append(section)
            ass_file.diagnostics.extend(section.diagnostics)

        # Post-pass: Ensure mandated [Script Info] exists
        if info_model is None:
            info_model = AssScriptInfo()
            info_model['scripttype'] = 'v4.00+'
            processed_sections.insert(0, info_model)
            ass_file.diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING, "Missing [Script Info] section, assuming ScriptType: v4.00+", 0, "MISSING_SCRIPTTYPE"
            ))

        ass_file.sections = processed_sections
        return ass_file

    def dumps(self, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = False) -> str:
        """Serialize the model back to an ASS string using the Renderer Engine."""
        from sublib.ass.renderer import AssRenderer
        return AssRenderer().render_file(self, auto_fill=auto_fill)

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
