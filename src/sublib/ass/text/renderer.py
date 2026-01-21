"""Render ASS text string from elements."""
from __future__ import annotations

from sublib.ass.models.text.elements import (
    AssOverrideBlock, AssOverrideTag,
    AssComment, AssSpecialChar, AssPlainText,
    AssTextElement
)
from sublib.ass.tags import get_tag


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
        
        for elem in elements:
            if isinstance(elem, AssOverrideBlock):
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
            
            elif isinstance(elem, AssSpecialChar):
                result.append(elem.render())
            elif isinstance(elem, AssPlainText):
                result.append(elem.content)
        
        return "".join(result)
