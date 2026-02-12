"""ASS loading and parsing orchestration logic."""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models.file import AssFile

def load_file(path: Path | str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = True) -> "AssFile":
    """Load an ASS file from path."""
    from sublib.io import read_text_file
    content = read_text_file(path, encoding='utf-8-sig')
    return load_string(content, style_format=style_format, event_format=event_format, auto_fill=auto_fill)

def load_string(content: str, style_format: list[str] | None = [], event_format: list[str] | None = [], auto_fill: bool = True) -> "AssFile":
    """Parse ASS content from string using the decoupled Engine architecture.
    
    Stage 1: Structural Stage (Scanning)
    Stage 2: Semantic Stage (Ingestion)
    Stage 3: Orchestration Stage (Model Building)
    """
    from sublib.ass.core.diagnostics import Diagnostic, DiagnosticLevel, AssStructuralError
    from sublib.ass.engines.structural_parser import StructuralParser
    from sublib.ass.engines.semantic_parser import SemanticParser
    from sublib.ass.models.file import AssFile
    from sublib.ass.models.info import AssScriptInfo
    from sublib.ass.models.base import AssSection, AssRawSection
    
    # --- Stage 1: Structural Stage ---
    struct_parser = StructuralParser()
    raw_doc = struct_parser.parse(content)
    
    # Halt if structural errors are fatal
    errors = [d for d in struct_parser.diagnostics if d.level == DiagnosticLevel.ERROR]
    if errors:
        raise AssStructuralError(f"Fatal structural errors found in ASS file ({len(errors)})", errors)

    ass_file = AssFile()
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
