# asslib/text_parser.py
"""Parse ASS event text into structured elements."""
from __future__ import annotations
import re
from typing import Any

from sublib.ass.elements import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
)
from sublib.ass.tags import (
    TAGS,
    MUTUAL_EXCLUSIVES,
    get_tag,
    parse_tag,
)
from sublib.exceptions import SubtitleParseError


class AssTextParser:
    """Parse ASS event text into element sequence.
    
    Handles:
    - Override blocks: {...}
    - Newlines: \\\\N, \\\\n
    - Plain text
    - Mutual exclusion rules
    - First-win / last-win semantics
    """
    
    # Pattern to match override blocks, newlines, and hard spaces
    _BLOCK_PATTERN = re.compile(r'\{([^}]*)\}|\\([Nnh])')
    
    # Pattern to match individual tags within a block
    # Handles:
    # - \tag(args) - function style
    # - \tagValue - simple style
    # - \1c, \2c, etc. - digit-prefixed tags
    _TAG_PATTERN = re.compile(
        r'\\([0-9]?[a-zA-Z]+)'  # Tag name: optional digit prefix + letters (e.g., "fn", "1c", "an")
        r'(?:\(([^)]*)\)|([^\\]*))'  # Function args or simple value (including digits like "8" for \an8)
    )
    
    # Cache for registry-based pattern (built on first use)
    _KNOWN_TAGS_PATTERN = None
    
    @classmethod
    def _get_known_tags_pattern(cls):
        """Build regex pattern that matches known tags (longest first)."""
        if cls._KNOWN_TAGS_PATTERN is None:
            # Sort by length descending so longer matches are tried first
            tag_names = sorted(TAGS.keys(), key=len, reverse=True)
            escaped = [re.escape(t) for t in tag_names]
            # Pattern: \tagname followed by either (args) or value until next \ or end
            pattern = r'\\(' + '|'.join(escaped) + r')(?:\(([^)]*)\)|([^\\]*))'
            cls._KNOWN_TAGS_PATTERN = re.compile(pattern)
        return cls._KNOWN_TAGS_PATTERN
    
    def parse(self, text: str, line_number: int | None = None) -> list[AssTextElement]:
        """Parse text to elements.
        
        Args:
            text: The ASS event text string
            line_number: Optional line number for error messages
            
        Returns:
            List of parsed elements
            
        Raises:
            SubtitleParseError: If text format is invalid
        """
        if not text:
            return []
        
        elements: list[AssTextElement] = []
        last_end = 0
        
        for match in self._BLOCK_PATTERN.finditer(text):
            # Add plain text before this match
            if match.start() > last_end:
                plain = text[last_end:match.start()]
                if plain:
                    elements.append(AssPlainText(content=plain))
            
            if match.group(1) is not None:
                # Override block {...}
                block_content = match.group(1)
                block_elements = self._parse_override_block(
                    block_content, 
                    line_number=line_number,
                    position=match.start()
                )
                elements.extend(block_elements)
            else:
                # Newline \N, \n or hard space \h
                char = match.group(2)
                if char == 'h':
                    elements.append(AssHardSpace())
                else:
                    hard = char == 'N'
                    elements.append(AssNewLine(hard=hard))
            
            last_end = match.end()
        
        # Add remaining plain text
        if last_end < len(text):
            plain = text[last_end:]
            if plain:
                elements.append(AssPlainText(content=plain))
        
        return elements
    
    def _parse_override_block(
        self, 
        block: str, 
        line_number: int | None = None,
        position: int | None = None
    ) -> list[AssOverrideTag]:
        """Parse a single override block {...} content."""
        tags: list[AssOverrideTag] = []
        
        # Use registry-based pattern for correct tag matching
        pattern = self._get_known_tags_pattern()
        for match in pattern.finditer(block):
            tag_name = match.group(1)
            # Function args or simple value
            raw_value = match.group(2) if match.group(2) is not None else (match.group(3) or "")
            raw_value = raw_value.strip()
            is_function = match.group(2) is not None
            
            # Special case: \c is alias for \1c
            if tag_name == 'c':
                tag_name = '1c'
            
            spec = get_tag(tag_name)
            if spec is None:
                raise SubtitleParseError(
                    f"Unknown override tag: \\{tag_name}",
                    line_number=line_number,
                    position=position,
                    raw_text=block
                )
            
            # Parse the value using dispatch table
            parsed_value = parse_tag(tag_name, raw_value)
            if parsed_value is None and raw_value:
                raise SubtitleParseError(
                    f"Invalid value for \\{tag_name}: {raw_value}",
                    line_number=line_number,
                    position=position,
                    raw_text=block
                )
            
            # Build raw representation for roundtrip
            if is_function:
                raw = f"\\{tag_name}({raw_value})"
            else:
                raw = f"\\{tag_name}{raw_value}"
            
            tags.append(AssOverrideTag(
                name=tag_name,
                value=parsed_value,
                raw=raw,
                is_event=spec.is_event,
                first_wins=spec.first_wins,
                is_function=is_function,
            ))
        
        return tags
    


