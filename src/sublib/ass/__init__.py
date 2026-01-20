"""ASS (Advanced SubStation Alpha v4+) subtitle format support."""

from sublib.ass.models import AssFile, AssEvent, AssStyle
from sublib.ass.text import AssTextParser, AssTextRenderer, ExtractionResult
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


def extract(event: AssEvent):
    """Semantic helper to extract tags and segments from an event."""
    return event.extract()


def compose(event_tags=None, segments=None) -> list:
    """Semantic helper to build ASS text elements."""
    return AssEvent.compose_elements(event_tags, segments)


__all__ = [
    # Facade
    "load",
    "loads",
    "dump",
    "dumps",
    "extract",
    "compose",
    # Models
    "AssFile",
    "AssEvent",
    "AssStyle",
    # Serde
    "AssTextParser",
    "AssTextRenderer",
    # Types
    "ExtractionResult",
    "AssColor",
    "AssTimestamp",
]
