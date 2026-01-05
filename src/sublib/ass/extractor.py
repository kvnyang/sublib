# sublib/ass/extractor.py
"""Extraction utilities for ASS text elements.

These functions extract structured information from parsed AST.
"""
from __future__ import annotations
from typing import Any

from sublib.ass.ast import (
    AssOverrideBlock, AssOverrideTag,
    AssPlainText, AssSpecialChar, AssTextSegment,
    AssTextElement,
)
from sublib.ass.tags import MUTUAL_EXCLUSIVES


def extract_line_scoped_tags(elements: list[AssTextElement]) -> dict[str, Any]:
    """Extract effective line-scoped tags from AST.
    
    Applies first-wins/last-wins and mutual exclusion rules.
    Comments are automatically ignored (type filtering).
    
    Args:
        elements: Parsed AST elements from parser
        
    Returns:
        Dict mapping tag name to effective value.
    """
    result: dict[str, Any] = {}
    seen_first_win: set[str] = set()
    
    # Collect all line-scoped tags from all blocks
    for elem in elements:
        if isinstance(elem, AssOverrideBlock):
            for item in elem.elements:
                if isinstance(item, AssOverrideTag) and item.is_line_scoped:
                    name = item.name
                    exclusives = MUTUAL_EXCLUSIVES.get(name, set())
                    
                    # If a mutually exclusive first-wins tag exists, skip
                    if any(ex in seen_first_win for ex in exclusives):
                        continue
                    
                    # First-wins: skip if already seen
                    if item.first_wins:
                        if name in seen_first_win:
                            continue
                        seen_first_win.add(name)
                    
                    # Remove mutually exclusive tags (last-wins behavior)
                    for excl in exclusives:
                        result.pop(excl, None)
                    
                    result[name] = item.value
    
    return result


def extract_text_scoped_segments(elements: list[AssTextElement]) -> list[AssTextSegment]:
    """Extract text segments with their formatting tags.
    
    Behavior:
    - Adjacent override blocks are merged
    - Tag conflicts resolved with last-wins
    - Comments are ignored (type filtering)
    - Tags reset after each text segment (no accumulation)
    
    Args:
        elements: Parsed AST elements from parser
        
    Returns:
        List of AssTextSegment, each with:
        - block_tags: dict of effective text-scoped tag values
        - content: list of text content elements
    """
    segments: list[AssTextSegment] = []
    pending_tags: dict[str, Any] = {}
    current_content: list[AssPlainText | AssSpecialChar] = []
    
    def apply_tag_rules(tags: dict[str, Any], new_tag: AssOverrideTag) -> dict[str, Any]:
        """Apply last-wins and mutual exclusion rules."""
        name = new_tag.name
        exclusives = MUTUAL_EXCLUSIVES.get(name, set())
        
        # Remove mutually exclusive tags
        for excl in exclusives:
            tags.pop(excl, None)
        
        # Last-wins: overwrite
        tags[name] = new_tag.value
        return tags
    
    for elem in elements:
        if isinstance(elem, AssOverrideBlock):
            # New block after content = new segment
            if current_content:
                segments.append(AssTextSegment(
                    block_tags=pending_tags.copy(),
                    content=current_content.copy()
                ))
                pending_tags = {}
                current_content = []
            
            # Collect text-scoped tags (last-wins)
            for item in elem.elements:
                if isinstance(item, AssOverrideTag) and not item.is_line_scoped:
                    apply_tag_rules(pending_tags, item)
        
        elif isinstance(elem, AssPlainText):
            current_content.append(elem)
        
        elif isinstance(elem, AssSpecialChar):
            current_content.append(elem)
    
    # Final segment
    if current_content:
        segments.append(AssTextSegment(
            block_tags=pending_tags,
            content=current_content
        ))
    
    return segments
