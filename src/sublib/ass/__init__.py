"""ASS (Advanced SubStation Alpha v4+) subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle, AssScriptInfo
from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
from sublib.ass.text import AssTextParser, AssTextRenderer, build_text_elements
from sublib.ass.types import AssColor, AssTimestamp
from pathlib import Path


def load(path: str | Path) -> AssFile:
    """Load an ASS file from path."""
    return AssFile.load(path)


def loads(content: str) -> AssFile:
    """Parse ASS content from string."""
    return AssFile.loads(content)


def dump(ass_file: AssFile, path: str | Path) -> None:
    """Save an ASS file to path."""
    ass_file.dump(path)


def dumps(ass_file: AssFile) -> str:
    """Render ASS file to string."""
    return ass_file.dumps()


def extract_event_tags_and_segments(event: AssEvent):
    """Semantic helper to extract tags and segments from an event."""
    return event.extract_event_tags_and_segments()


__all__ = [
    # Facade
    "load",
    "loads",
    "dump",
    "dumps",
    "extract_event_tags_and_segments",
    "build_text_elements",
    # Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    "AssScriptInfo",
    "Diagnostic",
    "DiagnosticLevel",
    # Serde
    "AssTextParser",
    "AssTextRenderer",
    # Types
    "AssColor",
    "AssTimestamp",
]
