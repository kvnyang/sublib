"""Extraction utilities for ASS text elements.

These functions extract structured information from parsed AST.
"""
from __future__ import annotations
from typing import Any, NamedTuple

from .elements import (
    AssOverrideBlock, AssOverrideTag,
    AssPlainText, AssSpecialChar,
    AssTextElement,
)
from .segment import AssTextSegment
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


def compose_all(
    event_tags: dict[str, Any] | None = None,
    segments: list[AssTextSegment] | None = None
) -> list[AssTextElement]:
    """Compose ASS text elements from event tags and segments.
    
    This is the inverse of extract_all(). It builds AssTextElement list
    that can be rendered to ASS text using AssTextRenderer.
    
    Args:
        event_tags: Event-level tags (e.g., {"pos": Position(...), "an": 8})
        segments: Inline segments with formatting and text content
        
    Returns:
        List of AssTextElement (AssOverrideBlock, AssPlainText, AssSpecialChar)
        
    Example:
        elements = compose_all(
            event_tags={"pos": Position(100, 200), "an": 8},
            segments=[AssTextSegment(block_tags={"b": True}, content=[...])]
        )
        text = AssTextRenderer().render(elements)
    """
    from sublib.ass.tags import get_tag, format_tag
    
    elements: list[AssTextElement] = []
    
    # Build event-level tags block (always at the start)
    event_block_tags: list[AssOverrideTag] = []
    if event_tags:
        for name, value in event_tags.items():
            tag_cls = get_tag(name)
            if tag_cls:
                event_block_tags.append(AssOverrideTag(
                    name=name,
                    value=value,
                    raw=format_tag(name, value),
                    is_event_level=tag_cls.is_event_level,
                    first_wins=tag_cls.first_wins,
                    is_function=tag_cls.is_function,
                ))
    
    # Process segments
    if segments:
        for i, seg in enumerate(segments):
            # Build block tags for this segment
            block_tags: list[AssOverrideTag] = []
            
            # First segment includes event-level tags
            if i == 0:
                block_tags.extend(event_block_tags)
            
            # Add segment's inline tags
            if seg.block_tags:
                for name, value in seg.block_tags.items():
                    tag_cls = get_tag(name)
                    if tag_cls:
                        block_tags.append(AssOverrideTag(
                            name=name,
                            value=value,
                            raw=format_tag(name, value),
                            is_event_level=tag_cls.is_event_level,
                            first_wins=tag_cls.first_wins,
                            is_function=tag_cls.is_function,
                        ))
            
            # Add override block if there are tags
            if block_tags:
                elements.append(AssOverrideBlock(elements=block_tags))
            
            # Add content
            elements.extend(seg.content)
    
    elif event_block_tags:
        # No segments but have event tags - create a single empty block
        elements.append(AssOverrideBlock(elements=event_block_tags))
    
    return elements
