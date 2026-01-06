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


def extract_event_level_tags(elements: list[AssTextElement]) -> dict[str, Any]:
    """Extract effective event-level tags from AST.
    
    Applies first-wins/last-wins and mutual exclusion rules.
    Comments are automatically ignored (type filtering).
    
    Args:
        elements: Parsed AST elements from parser
        
    Returns:
        Dict mapping tag name to effective value.
    """
    result: dict[str, Any] = {}
    seen_first_win: set[str] = set()
    
    # Collect all event-level tags from all blocks
    for elem in elements:
        if isinstance(elem, AssOverrideBlock):
            for item in elem.elements:
                if isinstance(item, AssOverrideTag) and item.is_event_level:
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


def extract_inline_segments(elements: list[AssTextElement]) -> list[AssTextSegment]:
    """Extract text segments with their formatting tags.
    
    Behavior:
    - Each override block boundary creates a new segment (including empty blocks)
    - Adjacent blocks (without intervening text) are merged into one segment
    - Within a segment, tags are processed in order with last-wins and mutual exclusion
    - Comments are ignored (type filtering)
    - Tag accumulation is NOT handled here (renderer's responsibility)
    
    Edge cases:
    - Leading text without block: creates segment with empty tags
    - Trailing blocks without text: ignored (no segment created)
    - Blocks only (no text): returns empty list
    
    Args:
        elements: Parsed AST elements from parser
        
    Returns:
        List of AssTextSegment, each with:
        - block_tags: dict of effective inline tag values for this segment
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
                if isinstance(item, AssOverrideTag) and not item.is_event_level:
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
