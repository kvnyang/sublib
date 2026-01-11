# sublib/ass/extractor.py
"""Extraction utilities for ASS text elements.

These functions extract structured information from parsed AST.
"""
from __future__ import annotations
from typing import Any, NamedTuple

from sublib.ass.ast import (
    AssOverrideBlock, AssOverrideTag,
    AssPlainText, AssSpecialChar, AssTextSegment,
    AssTextElement,
)
from sublib.ass.tags import MUTUAL_EXCLUSIVES


class ExtractionResult(NamedTuple):
    """Result of extracting tags from ASS text elements."""
    event_tags: dict[str, Any]
    """Event-level tags (e.g., pos, an, move) with first-wins/last-wins rules applied."""
    
    segments: list[AssTextSegment]
    """Inline segments with formatting and text content."""


def extract_all(elements: list[AssTextElement]) -> ExtractionResult:
    """Extract both event-level tags and inline segments in one pass.
    
    This is the primary extraction function that combines:
    - Event-level tag extraction (with first-wins/last-wins and mutual exclusion)
    - Inline segment extraction (with formatting tags per segment)
    
    Args:
        elements: Parsed AST elements from parser
        
    Returns:
        ExtractionResult with event_tags dict and segments list.
        
    Example:
        result = extract_all(elements)
        pos = result.event_tags.get("pos")
        for seg in result.segments:
            print(seg.content, seg.block_tags)
    """
    # Event-level tag collection
    event_tags: dict[str, Any] = {}
    seen_first_win: set[str] = set()
    
    # Segment collection
    segments: list[AssTextSegment] = []
    pending_tags: dict[str, Any] = {}
    current_content: list[AssPlainText | AssSpecialChar] = []
    
    def apply_event_level_rules(tag: AssOverrideTag) -> None:
        """Apply first-wins/last-wins and mutual exclusion for event-level tags."""
        name = tag.name
        exclusives = MUTUAL_EXCLUSIVES.get(name, set())
        
        # If a mutually exclusive first-wins tag exists, skip
        if any(ex in seen_first_win for ex in exclusives):
            return
        
        # First-wins: skip if already seen
        if tag.first_wins:
            if name in seen_first_win:
                return
            seen_first_win.add(name)
        
        # Remove mutually exclusive tags (last-wins behavior)
        for excl in exclusives:
            event_tags.pop(excl, None)
        
        event_tags[name] = tag.value
    
    def apply_inline_rules(tag: AssOverrideTag) -> None:
        """Apply last-wins and mutual exclusion for inline tags."""
        name = tag.name
        exclusives = MUTUAL_EXCLUSIVES.get(name, set())
        
        # Remove mutually exclusive tags
        for excl in exclusives:
            pending_tags.pop(excl, None)
        
        # Last-wins: overwrite
        pending_tags[name] = tag.value
    
    # Single pass through elements
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
            
            # Process tags in block
            for item in elem.elements:
                if isinstance(item, AssOverrideTag):
                    if item.is_event_level:
                        apply_event_level_rules(item)
                    else:
                        apply_inline_rules(item)
        
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
    
    return ExtractionResult(event_tags=event_tags, segments=segments)
