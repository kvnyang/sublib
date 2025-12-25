# asslib/text_renderer.py
"""Render ASS text from structured elements."""
from __future__ import annotations
from typing import Any

from sublib.formats.ass.elements import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
)
from sublib.formats.ass.tag_registry import get_tag_spec


class AssTextRenderer:
    """Render ASS text string from elements.
    
    Converts parsed elements back to ASS text format.
    """
    
    def render(self, elements: list[AssTextElement]) -> str:
        """Render elements to ASS text string.
        
        If tag has 'raw' field, uses it for exact roundtrip.
        Otherwise, uses the tag's formatter to render from value.
        """
        result = []
        pending_tags: list[str] = []
        
        for elem in elements:
            if isinstance(elem, AssOverrideTag):
                # Use raw if available, otherwise render from value
                if elem.raw:
                    pending_tags.append(elem.raw)
                else:
                    spec = get_tag_spec(elem.name)
                    if spec:
                        pending_tags.append(spec.formatter(elem.value))
            elif isinstance(elem, AssNewLine):
                # Flush pending tags first
                if pending_tags:
                    result.append("{" + "".join(pending_tags) + "}")
                    pending_tags = []
                result.append("\\N" if elem.hard else "\\n")
            elif isinstance(elem, AssHardSpace):
                # Flush pending tags first
                if pending_tags:
                    result.append("{" + "".join(pending_tags) + "}")
                    pending_tags = []
                result.append("\\h")
            elif isinstance(elem, AssPlainText):
                # Flush pending tags first
                if pending_tags:
                    result.append("{" + "".join(pending_tags) + "}")
                    pending_tags = []
                result.append(elem.content)
        
        # Flush any remaining tags
        if pending_tags:
            result.append("{" + "".join(pending_tags) + "}")
        
        return "".join(result)
    
    def render_from_segments(
        self,
        segments: list[tuple[list[AssOverrideTag], str]],
        event_tags: dict[str, Any] | None = None,
    ) -> str:
        """Render text from segments (tags + text pairs).
        
        Args:
            segments: List of (tags, text) tuples from get_text_segments()
            event_tags: Optional event-level tags dict to prepend
            
        Returns:
            ASS text string
        """
        result = []
        
        # Event-level tags at the start
        if event_tags:
            tag_strs = []
            for name, value in event_tags.items():
                spec = get_tag_spec(name)
                if spec:
                    tag_strs.append(spec.formatter(value))
            if tag_strs:
                result.append("{" + "".join(tag_strs) + "}")
        
        # Segments with inline tags
        for tags, text in segments:
            if tags:
                tag_strs = []
                for tag in tags:
                    if tag.raw:
                        tag_strs.append(tag.raw)
                    else:
                        spec = get_tag_spec(tag.name)
                        if spec:
                            tag_strs.append(spec.formatter(tag.value))
                if tag_strs:
                    result.append("{" + "".join(tag_strs) + "}")
            result.append(text)
        
        return "".join(result)

