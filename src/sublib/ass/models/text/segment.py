"""Text segment type for extract results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models.text.elements import AssPlainText, AssSpecialChar


@dataclass
class AssTextSegment:
    """A text segment with its formatting tags.
    
    Returned by extract_inline_segments() to represent 
    a contiguous piece of text with consistent formatting.
    
    Attributes:
        block_tags: Dict of effective text-scoped tag values.
              Represents the incremental tags from preceding block(s).
              Conflicts are resolved (last-wins), so dict is appropriate.
        content: List of content elements, preserving type info.
                 Allows distinct handling of plain text vs special chars.
    """
    block_tags: dict[str, Any]
    content: list["AssPlainText | AssSpecialChar"]
    
    def get_text(self) -> str:
        """Get combined text as string.
        
        Convenience method for simple use cases.
        Special chars rendered as escape sequences (\\N, \\n, \\h).
        """
        from sublib.ass.models.text.elements import AssPlainText, AssSpecialChar
        
        result = []
        for item in self.content:
            if isinstance(item, AssPlainText):
                result.append(item.content)
            elif isinstance(item, AssSpecialChar):
                result.append(item.render())
        return "".join(result)
    
    def __len__(self) -> int:
        """Return total character length of text content."""
        return len(self.get_text())
    
    def __bool__(self) -> bool:
        """Return True if segment has content."""
        return bool(self.content)
