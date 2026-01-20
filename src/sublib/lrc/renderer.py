"""LRC lyrics renderer."""
from __future__ import annotations

from sublib.lrc.models import LrcFile


class LrcRenderer:
    """Renderer for LRC file format."""

    def render(self, lrc_file: LrcFile) -> str:
        """Render LRC file to string."""
        buffer = []
        
        # 1. Render metadata tags
        # Order tags: ti, ar, al, by
        preferred_order = ["ti", "ar", "al", "by", "offset"]
        
        # Render preferred tags first
        for key in preferred_order:
            if key in lrc_file.metadata:
                buffer.append(f"[{key}:{lrc_file.metadata[key]}]")
        
        # Render remaining tags
        for key, value in lrc_file.metadata.items():
            if key not in preferred_order:
                buffer.append(f"[{key}:{value}]")
        
        if buffer:
            buffer.append("")  # Empty line after metadata
            
        # 2. Render lines
        for line in lrc_file.lines:
            buffer.append(str(line))
            
        return "\n".join(buffer)
