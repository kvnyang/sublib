"""Layer 1 Structural Parser for ASS files."""
from __future__ import annotations
import re
from typing import Optional

from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
from sublib.ass.models.raw import RawDocument, RawSection, RawRecord
from sublib.ass.descriptors import parse_descriptor_line, CORE_SECTIONS, STYLE_SECTIONS


class StructuralParser:
    """Layer 1 parser: Scans the document structure and basic line types."""

    def __init__(self):
        self.diagnostics: list[Diagnostic] = []
        self._seen_sections: set[str] = set()
        self._has_styles_v4 = False
        self._has_styles_v4plus = False

    def add_diagnostic(self, level: DiagnosticLevel, message: str, line_number: int, code: Optional[str] = None):
        """Record a diagnostic message."""
        self.diagnostics.append(Diagnostic(level, message, line_number, code))

    def parse(self, content: str) -> RawDocument:
        """Parse raw ASS content into a RawDocument structure."""
        doc = RawDocument()
        current_section: Optional[RawSection] = None
        
        non_empty_line_count = 0
        
        for line_number, raw_line in enumerate(content.splitlines(), 1):
            stripped = raw_line.strip()
            
            # 1. Skip strictly empty lines
            if not stripped:
                continue
            
            non_empty_line_count += 1
            
            # 2. Section Headers
            if stripped.startswith('[') and stripped.endswith(']'):
                section_name_raw = stripped[1:-1].strip()
                section_name_norm = section_name_raw.lower()
                
                # Validation: Duplicate Section
                if section_name_norm in self._seen_sections:
                    self.add_diagnostic(
                        DiagnosticLevel.ERROR, 
                        f"Duplicate section header: [{section_name_raw}]", 
                        line_number, "DUPLICATE_SECTION"
                    )
                
                # Validation: Ambiguous Versioning (v4 vs v4+ styles)
                if section_name_norm == 'v4 styles':
                    self._has_styles_v4 = True
                if section_name_norm == 'v4+ styles':
                    self._has_styles_v4plus = True
                
                if self._has_styles_v4 and self._has_styles_v4plus:
                    self.add_diagnostic(
                        DiagnosticLevel.ERROR,
                        "Ambiguous versioning: both [V4 Styles] and [V4+ Styles] present",
                        line_number, "AMBIGUOUS_VERSIONING"
                    )
                
                self._seen_sections.add(section_name_norm)
                current_section = RawSection(
                    name=section_name_norm, 
                    original_name=section_name_raw,
                    line_number=line_number
                )
                doc.sections.append(current_section)
                continue

            if not current_section:
                self.add_diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Content outside of section: {stripped[:50]}",
                    line_number, "ORPHAN_CONTENT"
                )
                continue

            # NEW: If this is a raw passthrough section (e.g., [Fonts], [Graphics], or Custom)
            # We treat EVERYTHING as raw lines.
            if current_section.name not in CORE_SECTIONS:
                current_section.raw_lines.append(raw_line)
                continue

            # 3. Comments (Only for CORE/STYLE sections now)
            if stripped.startswith(';') or stripped.startswith('!:'):
                if current_section.name == 'script info':
                    # Value extraction for comments
                    comment_val = stripped[1:] if stripped.startswith(';') else stripped[2:]
                    current_section.comments.append(comment_val.lstrip())
                continue

            # 4. Descriptor: Value Lines (Use raw_line to preserve trailing spaces via lstrip in helper)
            parsed = parse_descriptor_line(raw_line)
            if not parsed:
                self.add_diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Malformed line (no descriptor): {stripped[:50]}",
                    line_number, "MALFORMED_LINE"
                )
                continue
            
            descriptor, descriptor_content = parsed
            descriptor_norm = descriptor.lower()
            
            # Special case: Format line for Styles/Events
            if descriptor_norm == 'format' and current_section.name in (STYLE_SECTIONS | {'events'}):
                self._handle_format_line(current_section, descriptor_content, line_number)
                continue

            # Standard records
            record = RawRecord(
                descriptor=descriptor, 
                value=descriptor_content, 
                line_number=line_number
            )
            
            # Validation: Missing Format line for Styles/Events
            if current_section.name in (STYLE_SECTIONS | {'events'}) and not current_section.format_fields:
                self.add_diagnostic(
                    DiagnosticLevel.ERROR,
                    f"Data line before Format line in [{current_section.original_name}]",
                    line_number, "MISSING_FORMAT"
                )
            
            # Validation: Comma count for Styles/Events
            if current_section.name in (STYLE_SECTIONS | {'events'}) and current_section.format_fields:
                # Note: We don't perform deep comma count validation in Layer 1 for ALL sections, 
                # but we can check if it looks plausible if we have the format.
                expected_commas = len(current_section.format_fields) - 1
                actual_commas = record.value.count(',')
                if actual_commas < expected_commas:
                     self.add_diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Insufficient fields for {record.descriptor} (expected {len(current_section.format_fields)})",
                        line_number, "INSUFFICIENT_FIELDS"
                    )

            current_section.records.append(record)

        # Post-parse Global Validations
        self._validate_global_structure(doc)
        
        return doc

    def _handle_format_line(self, section: RawSection, content: str, line_number: int):
        """Parse and validate Format lines."""
        if section.format_fields:
            self.add_diagnostic(
                DiagnosticLevel.ERROR,
                f"Multiple Format lines in [{section.original_name}]",
                line_number, "DUPLICATE_FORMAT"
            )
            return

        fields = [f.strip() for f in content.split(',')]
        
        # Validation: Empty fields
        if not fields or (len(fields) == 1 and not fields[0]):
            self.add_diagnostic(DiagnosticLevel.ERROR, "Empty Format line", line_number, "EMPTY_FORMAT")
            return

        # Validation: Duplicate Fields
        seen_fields = set()
        for f in fields:
            f_norm = f.lower()
            if f_norm in seen_fields:
                self.add_diagnostic(
                    DiagnosticLevel.ERROR,
                    f"Duplicate field '{f}' in Format line",
                    line_number, "DUPLICATE_FORMAT_FIELD"
                )
            seen_fields.add(f_norm)

        # Validation: Text must be last for Events
        if section.name == 'events' and fields[-1].lower() != 'text':
             self.add_diagnostic(
                DiagnosticLevel.ERROR,
                "Format line in [Events] must end with 'Text'",
                line_number, "FORMAT_TEXT_NOT_LAST"
            )

        section.format_fields = fields
        section.format_line_number = line_number

    def _validate_global_structure(self, doc: RawDocument):
        """Validate section order and presence of core sections."""
        actual_order = [s.name for s in doc.sections]
        
        # 1. Required Sections
        required = {'script info', 'events'} # Styles is technically optional but highly recommended
        missing = required - set(actual_order)
        for m in missing:
            self.add_diagnostic(DiagnosticLevel.WARNING, f"Missing core section: [{m.upper()}]", 0, "MISSING_SECTION")
        
        # 2. Strict Order for Core Sections
        # Order should be: Script Info -> Styles -> Events -> Fonts -> Graphics -> Custom
        core_rank = {
            'script info': 0,
            'v4 styles': 1,
            'v4+ styles': 1,
            'events': 2,
            'fonts': 3,
            'graphics': 4
        }
        
        current_max_rank = -1
        for s in doc.sections:
            rank = core_rank.get(s.name, 99) # Custom sections get high rank
            if rank < current_max_rank:
                 self.add_diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Section [{s.original_name}] is out of order",
                    s.line_number, "SECTION_OUT_OF_ORDER"
                )
            current_max_rank = max(current_max_rank, rank)
            
            # Custom sections should be at the end
            if rank == 99 and any(core_rank.get(s_next.name, 99) < 99 for s_next in doc.sections[doc.sections.index(s)+1:]):
                 self.add_diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Custom section [{s.original_name}] should appear after standard sections",
                    s.line_number, "CUSTOM_SECTION_PLACEMENT"
                )
