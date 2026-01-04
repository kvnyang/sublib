# sublib/ass/renderer.py
"""Render ASS text from structured elements.

DEPRECATED: Import from sublib.ass.services instead.
This module re-exports renderer for backward compatibility.
"""
from sublib.ass.services.renderer import AssTextRenderer

__all__ = ["AssTextRenderer"]
