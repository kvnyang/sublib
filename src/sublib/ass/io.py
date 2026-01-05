# sublib/ass/io.py
"""ASS file I/O operations.

Pure file I/O - delegates to serde for parsing and rendering.
"""
from __future__ import annotations
from pathlib import Path

from sublib.ass.models import AssFile


def load_ass_file(path: str | Path) -> AssFile:
    """Load an ASS file from disk.
    
    Args:
        path: Path to .ass file
        
    Returns:
        Parsed AssFile
    """
    from sublib.ass.serde import parse_ass_string
    
    path = Path(path)
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    return parse_ass_string(content)


def save_ass_file(ass_file: AssFile, path: str | Path) -> None:
    """Save an ASS file to disk.
    
    Args:
        ass_file: AssFile to save
        path: Destination path
    """
    from sublib.ass.serde import render_ass_string
    
    path = Path(path)
    content = render_ass_string(ass_file)
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write(content)
