# sublib/ass/renderer.py
"""Render ASS text from structured elements."""
from __future__ import annotations
from typing import Any

from sublib.ass.elements import (
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
    AssBlock,
    AssComment,
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
            if isinstance(elem, AssBlock):
                result.append("{")
                for item in elem.elements:
                    if isinstance(item, AssOverrideTag):
                        # Use raw if available, otherwise render from value
                        if item.raw:
                            result.append(item.raw)
                        else:
                            tag_cls = get_tag(item.name)
                            if tag_cls:
                                result.append(tag_cls.format(item.value))
                    elif isinstance(item, AssComment):
                        result.append(item.content)
                result.append("}")
            
            elif isinstance(elem, AssNewLine):
                result.append("\\N" if elem.hard else "\\n")
            elif isinstance(elem, AssHardSpace):
                result.append("\\h")
            elif isinstance(elem, AssPlainText):
                result.append(elem.content)
        

        
        return "".join(result)
    

