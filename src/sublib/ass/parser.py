# sublib/ass/parser.py
"""Parse ASS event text into structured elements.

DEPRECATED: Import from sublib.ass.services instead.
This module re-exports parser for backward compatibility.
"""
from sublib.ass.services.parser import AssTextParser

__all__ = ["AssTextParser"]
