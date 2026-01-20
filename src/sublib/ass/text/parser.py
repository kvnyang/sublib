"""Parse and render ASS event text."""
from __future__ import annotations
import re
from typing import Any, Union

from .elements import (
    AssOverrideTag, AssComment, AssOverrideBlock,
    SpecialCharType, AssSpecialChar, AssPlainText,
    AssTextElement, AssBlockElement
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
    - Comments (unrecognized text)
    - Mutual exclusion rules
    - First-win / last-win semantics
    
    Args:
        strict: If True, raise error when comments found. If False, silently preserve.
    """
    
    def __init__(self, strict: bool = True):
        self.strict = strict
    
    # Pattern to match override blocks, newlines, and hard spaces
    _BLOCK_PATTERN = re.compile(r'\{([^}]*)\}|\\([Nnh])')
    
    # Cache for smart pattern (built on first use)
    _SMART_PATTERN = None
    
    @classmethod
    def _build_smart_pattern(cls):
        """Build smart regex pattern using param_pattern from each tag."""
        if cls._SMART_PATTERN is not None:
            return cls._SMART_PATTERN
        
        patterns = []
        # Sort by tag name length (longest first) to avoid short tags matching prematurely
        for tag_name in sorted(TAGS.keys(), key=len, reverse=True):
            tag_cls = TAGS[tag_name]
            
            if tag_cls.is_function:
                # Function tags: \tag(...)
                pat = rf'\\{re.escape(tag_name)}\(([^)]*)\)'
            elif tag_cls.param_pattern:
                # Non-function tags with pattern: use regex-constrained matching
                pat = rf'\\{re.escape(tag_name)}({tag_cls.param_pattern})'
            else:
                # Fallback: match non-backslash characters
                pat = rf'\\{re.escape(tag_name)}([^\\]*)'
            
            patterns.append(f'({pat})')
        
        # Combine all patterns with alternation
        cls._SMART_PATTERN = re.compile('|'.join(patterns))
        return cls._SMART_PATTERN
    
    def parse(self, text: str, line_number: int | None = None) -> list[AssTextElement]:
        """Parse text to elements.
        
        Args:
            text: The ASS event text string
            line_number: Optional line number for error messages
            
        Returns:
            List of parsed elements
            
        Raises:
            SubtitleParseError: If text format is invalid (or if strict=True and comments found)
        """
        if not text:
            return []
        
        # Phase 1: Parse (always permissive)
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
                block = self._parse_override_block(
                    block_content, 
                    line_number=line_number,
                    position=match.start()
                )
                elements.append(block)
            else:
                # Special characters \N, \n, \h
                char = match.group(2)
                if char == 'h':
                    elements.append(AssSpecialChar(type=SpecialCharType.HARD_SPACE))
                else:
                    if char == 'N':
                        elements.append(AssSpecialChar(type=SpecialCharType.HARD_NEWLINE))
                    else:  # 'n'
                        elements.append(AssSpecialChar(type=SpecialCharType.SOFT_NEWLINE))
            
            last_end = match.end()
        
        # Add remaining plain text
        if last_end < len(text):
            plain = text[last_end:]
            if plain:
                elements.append(AssPlainText(content=plain))
        
        # Phase 2: Validate (if strict mode)
        if self.strict:
            self._validate_strict(elements, line_number)
        
        return elements
    
    def _parse_override_block(
        self, 
        block_text: str, 
        line_number: int | None = None,
        position: int | None = None
    ) -> AssOverrideBlock:
        """Parse a single override block {...} content (always permissive).
        
        Uses manual scanning with bracket counting to correctly handle nested
        parentheses in function tags like \t(\clip(...)).
        """
        block_text = block_text.strip()
        if not block_text:
            return AssOverrideBlock(elements=[])
        
        block_elements: list[Union[AssOverrideTag, AssComment]] = []
        i = 0
        comment_start = 0
        
        while i < len(block_text):
            # Look for backslash (tag start)
            if block_text[i] == '\\':
                # Add any comment text before this tag
                if i > comment_start:
                    comment_text = block_text[comment_start:i].strip()
                    if comment_text:
                        block_elements.append(AssComment(content=comment_text))
                
                # Parse tag starting at position i
                tag_result = self._parse_single_tag(block_text, i)
                if tag_result:
                    tag_elem, end_pos = tag_result
                    block_elements.append(tag_elem)
                    i = end_pos
                    comment_start = i
                else:
                    # Failed to parse, move to next character
                    i += 1
            else:
                i += 1
        
        # Add any remaining comment text
        if comment_start < len(block_text):
            comment_text = block_text[comment_start:].strip()
            if comment_text:
                block_elements.append(AssComment(content=comment_text))
        
        return AssOverrideBlock(elements=block_elements)
    
    def _parse_single_tag(self, text: str, start: int) -> tuple[AssOverrideTag | AssComment, int] | None:
        """Parse a single tag starting at position 'start'.
        
        Returns (element, end_position) or None if not a valid tag.
        """
        if start >= len(text) or text[start] != '\\':
            return None
        
        # Find tag name - match longest known tag name first
        tag_start = start + 1
        
        for tag_name in sorted(TAGS.keys(), key=len, reverse=True):
            if text[tag_start:].startswith(tag_name):
                tag_cls = TAGS[tag_name]
                value_start = tag_start + len(tag_name)
                
                if tag_cls.is_function:
                    # Function tag: need to find matching closing parenthesis
                    if value_start < len(text) and text[value_start] == '(':
                        close_pos = self._find_matching_paren(text, value_start)
                        if close_pos > 0:
                            raw_value = text[value_start + 1:close_pos]
                            end_pos = close_pos + 1
                            raw = text[start:end_pos]
                            
                            parsed_value = parse_tag(tag_name, raw_value)
                            return (AssOverrideTag(
                                name=tag_name,
                                value=parsed_value,
                                raw=raw,
                                is_event_level=tag_cls.is_event_level,
                                first_wins=tag_cls.first_wins,
                                is_function=True,
                            ), end_pos)
                    # No opening paren or no matching close - skip this tag
                    return None
                else:
                    # Non-function tag: read value until next backslash or end
                    end_pos = value_start
                    while end_pos < len(text) and text[end_pos] != '\\':
                        end_pos += 1
                    
                    raw_value = text[value_start:end_pos].strip()
                    raw = text[start:end_pos]
                    
                    # Validate with param_pattern if available
                    if tag_cls.param_pattern:
                        pattern = re.compile(f'^{tag_cls.param_pattern}')
                        match = pattern.match(raw_value)
                        if match:
                            raw_value = match.group(0)
                            end_pos = value_start + len(raw_value)
                            raw = text[start:end_pos]
                    
                    parsed_value = parse_tag(tag_name, raw_value)
                    if parsed_value is not None or not raw_value:
                        return (AssOverrideTag(
                            name=tag_name,
                            value=parsed_value,
                            raw=raw,
                            is_event_level=tag_cls.is_event_level,
                            first_wins=tag_cls.first_wins,
                            is_function=False,
                        ), end_pos)
        
        return None
    
    def _find_matching_paren(self, text: str, start: int) -> int:
        """Find the position of the closing parenthesis matching the one at 'start'.
        
        Uses bracket counting to handle nested parentheses.
        Returns position of closing ')', or -1 if not found.
        """
        if start >= len(text) or text[start] != '(':
            return -1
        
        depth = 1
        i = start + 1
        while i < len(text) and depth > 0:
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
            i += 1
        
        return i - 1 if depth == 0 else -1
    
    def _validate_strict(self, elements: list[AssTextElement], line_number: int | None):
        """Validate elements in strict mode - raise error if comments found."""
        comments = self._collect_comments(elements)
        
        if comments:
            comment_texts = ', '.join(repr(c.content) for c in comments)
            message = f"Strict mode: found {len(comments)} unrecognized text(s): {comment_texts}"
            raise SubtitleParseError(
                message,
                line_number=line_number
            )
    
    def _collect_comments(self, elements: list[AssTextElement]) -> list[AssComment]:
        """Collect all comments from elements."""
        comments = []
        for elem in elements:
            if isinstance(elem, AssOverrideBlock):
                for item in elem.elements:
                    if isinstance(item, AssComment):
                        comments.append(item)
        return comments


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
