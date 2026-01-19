"""Lyrics functionality for sublib.

Supports parsing and rendering of LRC files.
"""
from sublib.lyrics.models import LrcFile, LrcLine, LrcTimestamp
from sublib.lyrics.parser import LrcParser
from sublib.lyrics.renderer import LrcRenderer

__all__ = [
    "LrcFile",
    "LrcLine",
    "LrcTimestamp",
    "LrcParser",
    "LrcRenderer",
]
