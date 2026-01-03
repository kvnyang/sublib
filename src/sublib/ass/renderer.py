# sublib/ass/renderer.py
"""Render ASS text from structured elements."""
from __future__ import annotations
from typing import Any

from sublib.ass.elements import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
)
from sublib.ass.tags import get_tag, format_tag


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
                    tag_cls = get_tag(elem.name)
                    if tag_cls:
                        pending_tags.append(tag_cls.format(elem.value))
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
    

