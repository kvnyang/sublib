"""ASS rendering and writing orchestration logic."""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models.file import AssFile

def render_string(ass_file: AssFile, auto_fill: bool = False) -> str:
    """Render ASS file model to string."""
    from sublib.ass.engines.doc_renderer import AssRenderer
    return AssRenderer().render_file(ass_file, auto_fill=auto_fill)

def write_file(ass_file: AssFile, path: Path | str, auto_fill: bool = False) -> None:
    """Save ASS file model to path."""
    from sublib.io import write_text_file
    content = render_string(ass_file, auto_fill=auto_fill)
    write_text_file(path, content, encoding='utf-8-sig')
