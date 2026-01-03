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
from sublib.ass.tag_registry import (
    TAG_REGISTRY,
    MUTUAL_EXCLUSIVES,
    get_tag_spec,
)
from sublib.exceptions import SubtitleParseError


class AssTextParser:
    """Parse ASS event text into element sequence.
    
    Handles:
    - Override blocks: {...}
    - Newlines: \\N, \\n
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
            tag_names = sorted(TAG_REGISTRY.keys(), key=len, reverse=True)
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
            
            spec = get_tag_spec(tag_name)
            if spec is None:
                raise SubtitleParseError(
                    f"Unknown override tag: \\{tag_name}",
                    line_number=line_number,
                    position=position,
                    raw_text=block
                )
            
            # Parse the value
            parsed_value = spec.parser(raw_value)
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
    
    def get_event_tags(self, elements: list[AssTextElement]) -> dict[str, Any]:
        """Extract event-level tags from elements.
        
        Applies first-win / last-win and mutual exclusion rules.
        
        Returns:
            Dict mapping tag name to value
        """
        result: dict[str, Any] = {}
        seen_first_win: set[str] = set()
        
        for elem in elements:
            if not isinstance(elem, AssOverrideTag):
                continue
            if not elem.is_event:
                continue
            
            name = elem.name
            
            # First-win: skip if already seen
            if elem.first_wins:
                if name in seen_first_win:
                    continue
                seen_first_win.add(name)
            
            # Apply mutual exclusion
            for excl in MUTUAL_EXCLUSIVES.get(name, set()):
                result.pop(excl, None)
            
            result[name] = elem.value
        
        return result
    
    def get_text_segments(
        self, 
        elements: list[AssTextElement]
    ) -> list[tuple[list[AssOverrideTag], str]]:
        """Get text segments with their preceding inline tags.
        
        Each segment is a tuple of (inline_tags, text) where:
        - inline_tags: list of AssOverrideTag in original order (is_event=False)
        - text: the text content (may include \\N newlines)
        
        Example:
            Input:  "{\\fn思源\\b1}中文{\\fn微软}English"
            Output: [
                ([Tag(fn), Tag(b1)], "中文"),
                ([Tag(fn)], "English"),
            ]
        
        Returns:
            List of (tags, text) tuples
        """
        segments: list[tuple[list[AssOverrideTag], str]] = []
        current_tags: list[AssOverrideTag] = []
        current_text = ""
        
        for elem in elements:
            if isinstance(elem, AssPlainText):
                current_text += elem.content
            elif isinstance(elem, AssNewLine):
                current_text += "\\N" if elem.hard else "\\n"
            elif isinstance(elem, AssOverrideTag):
                if not elem.is_event:
                    # Inline tag: accumulate before text
                    if current_text:
                        # Flush previous segment
                        segments.append((current_tags, current_text))
                        current_tags = []
                        current_text = ""
                    current_tags.append(elem)
        
        # Final segment
        if current_text or current_tags:
            segments.append((current_tags, current_text))
        
        return segments

