"""Lyrics functionality for sublib.

Supports parsing and rendering of LRC files.
"""
from sublib.lrc.models import LrcFile, LrcLine, LrcTimestamp
from sublib.lrc.parser import LrcParser
from sublib.lrc.renderer import LrcRenderer
from pathlib import Path


def load(path: str | Path) -> LrcFile:
    """Load an LRC file from path."""
    return LrcFile.load(path)


def loads(content: str) -> LrcFile:
    """Parse LRC content from string."""
    return LrcFile.loads(content)


def dump(lrc_file: LrcFile, path: str | Path) -> None:
    """Save an LRC file to path."""
    lrc_file.save(path)


def dumps(lrc_file: LrcFile) -> str:
    """Render LRC file to string."""
    return lrc_file.dumps()


__all__ = [
    # Facade
    "load",
    "loads",
    "dump",
    "dumps",
    # Models
    "LrcFile",
    "LrcLine",
    "LrcTimestamp",
    "LrcParser",
    "LrcRenderer",
]
