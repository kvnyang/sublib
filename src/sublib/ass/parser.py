# asslib/text_parser.py
"""Parse ASS event text into structured elements."""
from __future__ import annotations
import re
from typing import Any, Union

from sublib.ass.elements import (
    AssTextElement,
    AssOverrideTag,
    AssPlainText,
    AssNewLine,
    AssHardSpace,
    AssBlock,
    AssComment,
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
        
        # Phase 2: Validate (if strict mode)
        if self.strict:
            self._validate_strict(elements, line_number)
        
        return elements
    
    def _parse_override_block(
        self, 
        block_text: str, 
        line_number: int | None = None,
        position: int | None = None
    ) -> AssBlock:
        """Parse a single override block {...} content (always permissive)."""
        block_elements: list[Union[AssOverrideTag, AssComment]] = []
        last_end = 0
        
        # Use smart pattern with regex-constrained matching
        pattern = self._build_smart_pattern()
        
        for match in pattern.finditer(block_text):
            # Content before this tag is comment
            if match.start() > last_end:
                comment_text = block_text[last_end:match.start()]
                if comment_text:
                    block_elements.append(AssComment(content=comment_text))
            
            # Extract tag name and value from match groups
            # The pattern creates nested groups, need to find which one matched
            tag_name, raw_value, is_function = self._extract_tag_from_match(match)
            
            # Special case: \c is alias for \1c
            if tag_name == 'c' and tag_name != '1c':
                tag_name = '1c'
            
            spec = get_tag(tag_name)
            if spec:
                # Try to parse the value
                parsed_value = parse_tag(tag_name, raw_value)
                if parsed_value is not None or not raw_value:
                    # Successfully parsed
                    raw = f"\\{tag_name}({raw_value})" if is_function else f"\\{tag_name}{raw_value}"
                    block_elements.append(AssOverrideTag(
                        name=tag_name,
                        value=parsed_value,
                        raw=raw,
                        is_line_scoped=spec.is_line_scoped,
                        first_wins=spec.first_wins,
                        is_function=is_function,
                    ))
                    last_end = match.end()
                    continue
            
            # Failed to parse or unknown tag → treat as comment
            block_elements.append(AssComment(content=match.group(0)))
            last_end = match.end()
        
        # Remaining text is comment
        if last_end < len(block_text):
            comment_text = block_text[last_end:]
            if comment_text:
                block_elements.append(AssComment(content=comment_text))
        
        return AssBlock(elements=block_elements)
    
    def _extract_tag_from_match(self, match: re.Match) -> tuple[str, str, bool]:
        """Extract tag name, value, and is_function from regex match groups."""
        # Pattern creates groups like: (\tag(value)|(\tag)(value))
        # Need to iterate to find which one matched
        groups = match.groups()
        
        # Find the first non-None group (the outer group)
        for i, group in enumerate(groups):
            if group is not None and group.startswith('\\'):
                # This is the matched tag
                tag_str = group
                
                # Check if it's a function tag
                if '(' in tag_str:
                    # Function tag: \tag(value)
                    tag_name = tag_str[1:tag_str.index('(')]
                    raw_value = tag_str[tag_str.index('(')+1:tag_str.rindex(')')]
                    return tag_name, raw_value.strip(), True
                else:
                    # Non-function tag: \tagvalue
                    # Extract tag name from TAGS keys
                    for possible_tag in sorted(TAGS.keys(), key=len, reverse=True):
                        if tag_str.startswith(f'\\{possible_tag}'):
                            tag_name = possible_tag
                            raw_value = tag_str[len(possible_tag)+1:]
                            return tag_name, raw_value.strip(), False
        
        # Fallback (should not reach here)
        return "", "", False
    
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
            if isinstance(elem, AssBlock):
                for item in elem.elements:
                    if isinstance(item, AssComment):
                        comments.append(item)
        return comments
