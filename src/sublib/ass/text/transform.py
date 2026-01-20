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



def extract_event_tags_and_segments(elements: list[AssTextElement]) -> tuple[dict[str, Any], list[AssTextSegment]]:
    """Extract event-level tags and inline segments using a Differential Model.
    
    Rules:
    - Continuous blocks are merged into one set of tags for the next segment.
    - \r clears all previous tags within the current tag collection scope.
    - Segments are emitted only when content (text/special chars) is encountered.
    - Tags are NOT accumulated across segments (Differential).
    """
    event_tags: dict[str, Any] = {}
    seen_first_win: set[str] = set()
    
    segments: list[AssTextSegment] = []
    pending_tags: dict[str, Any] = {}
    current_content: list[AssPlainText | AssSpecialChar] = []

    def apply_event_level_rules(tag: AssOverrideTag) -> None:
        name = tag.name
        # Reset clears event-level tags too if it were present here
        if name == 'r':
            event_tags.clear()
            seen_first_win.clear()
            event_tags[name] = tag.value
            return

        exclusives = MUTUAL_EXCLUSIVES.get(name, set())
        if any(ex in seen_first_win for ex in exclusives):
            return
        if tag.first_wins:
            if name in seen_first_win:
                return
            seen_first_win.add(name)
        for excl in exclusives:
            event_tags.pop(excl, None)
        event_tags[name] = tag.value

    def apply_inline_rules(tag: AssOverrideTag) -> None:
        name = tag.name
        # Intra-block reset: clear all pending tags
        if name == 'r':
            pending_tags.clear()
            pending_tags[name] = tag.value
            return

        exclusives = MUTUAL_EXCLUSIVES.get(name, set())
        for excl in exclusives:
            pending_tags.pop(excl, None)
        pending_tags[name] = tag.value

    # Group continuous blocks and associate with text
    for elem in elements:
        if isinstance(elem, AssOverrideBlock):
            # If we were collecting content, it means a new block group has started
            if current_content:
                segments.append(AssTextSegment(
                    block_tags=pending_tags.copy(),
                    content=current_content.copy()
                ))
                current_content = []
                pending_tags = {} # Clear for differential behavior
            
            for item in elem.elements:
                if isinstance(item, AssOverrideTag):
                    if item.is_event_level:
                        apply_event_level_rules(item)
                    else:
                        apply_inline_rules(item)
        
        elif isinstance(elem, (AssPlainText, AssSpecialChar)):
            current_content.append(elem)

    # Final segment emission
    if current_content:
        segments.append(AssTextSegment(
            block_tags=pending_tags,
            content=current_content
        ))
    
    return event_tags, segments


def build_text_elements(
    event_tags: dict[str, Any] | None = None,
    segments: list[AssTextSegment] | None = None
) -> list[AssTextElement]:
    """Build ASS text elements from event tags and segments.
    
    This is the inverse of extract_event_tags_and_segments(). It constructs
    an AssTextElement list ready for rendering.
    
    Args:
        event_tags: Event-level tags (e.g., {"pos": Position(...), "an": 8})
        segments: Inline segments with formatting and text content
        
    Returns:
        List of AssTextElement (AssOverrideBlock, AssPlainText, AssSpecialChar)
        
    Example:
        elements = build_text_elements(
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
