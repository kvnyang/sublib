"""ASS File model."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from sublib.ass.core.diagnostics import Diagnostic, DiagnosticLevel
from .info import AssScriptInfo
from .style import AssStyles
from .event import AssEvents
from .base import AssSection, AssRawSection


@dataclass
class AssFile:
    """ASS subtitle file.
    
    A container for ASS sections and diagnostics. 
    Functionality is delegated to specialized engines via the io package.
    """
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
        """Parse ASS content from string."""
        from sublib.ass.io.loader import load_string
        return load_string(content, style_format=style_format, event_format=event_format, auto_fill=auto_fill)

    def dumps(self, auto_fill: bool = False) -> str:
        """Serialize the model back to an ASS string."""
        from sublib.ass.io.writer import render_string
        return render_string(self, auto_fill=auto_fill)

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
        from sublib.ass.io.loader import load_file
        return load_file(path, style_format=style_format, event_format=event_format, auto_fill=auto_fill)
    
    def dump(self, path: Path | str, auto_fill: bool = False) -> None:
        """Save subtitle model to file."""
        from sublib.ass.io.writer import write_file
        write_file(self, path, auto_fill=auto_fill)
