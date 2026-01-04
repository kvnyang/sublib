# sublib/ass/models.py
"""ASS file, event, and style models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
from pathlib import Path

from sublib.ass.elements import AssTextElement, AssPlainText, AssSpecialChar, SpecialCharType, AssTextSegment


@dataclass
class AssStyle:
    """ASS style definition.
    
    Represents a style from the [V4+ Styles] section.
    """
    name: str
    fontname: str
    fontsize: float
    primary_color: int  # 0xAABBGGRR format
    secondary_color: int
    outline_color: int
    back_color: int
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikeout: bool = False
    scale_x: float = 100.0
    scale_y: float = 100.0
    spacing: float = 0.0
    angle: float = 0.0
    border_style: int = 1
    outline: float = 2.0
    shadow: float = 0.0
    alignment: int = 2
    margin_l: int = 10
    margin_r: int = 10
    margin_v: int = 10
    encoding: int = 1


@dataclass
class AssEvent:
    """ASS dialogue event.
    
    Represents a Dialogue line from the [Events] section.
    
    The text_elements field is the single source of truth.
    render_text() renders ASS text from it.
    """
    # Timing fields (inherited from Cue)
    start_ms: int = 0
    end_ms: int = 0
    
    # ASS-specific fields
    text_elements: list[AssTextElement] = field(default_factory=list)
    style: str = "Default"
    layer: int = 0
    name: str = ""
    margin_l: int = 0
    margin_r: int = 0
    margin_v: int = 0
    effect: str = ""
    
    def render_text(self) -> str:
        """Render elements back to ASS text format.
        
        Returns:
            The reconstructed ASS text string with override tags.
        """
        from sublib.ass.renderer import AssTextRenderer
        return AssTextRenderer().render(self.text_elements)
    
    def extract_line_scoped_tags(self) -> dict[str, Any]:
        """Extract effective line-scoped tags.
        
        Applies first-wins/last-wins and mutual exclusion rules.
        Comments are automatically ignored (type filtering).
        
        Returns:
            Dict mapping tag name to effective value.
        """
        from sublib.ass.elements import AssOverrideTag, AssOverrideBlock
        from sublib.ass.tags import MUTUAL_EXCLUSIVES
        
        result: dict[str, Any] = {}
        seen_first_win: set[str] = set()
        
        # Collect all line-scoped tags from all blocks
        for elem in self.text_elements:
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
    
    def extract_text_scoped_segments(self) -> list[AssTextSegment]:
        """Extract text segments with their formatting tags.
        
        Behavior:
        - Adjacent override blocks are merged
        - Tag conflicts resolved with last-wins
        - Comments are ignored (type filtering)
        - Tags reset after each text segment (no accumulation)
        
        Returns:
            List of AssTextSegment, each with:
            - tags: dict of effective text-scoped tag values
            - content: list of text content elements
        """
        from sublib.ass.elements import (
            AssOverrideBlock, AssOverrideTag, 
            AssPlainText, AssSpecialChar, AssTextSegment
        )
        from sublib.ass.tags import MUTUAL_EXCLUSIVES
        
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
        
        for elem in self.text_elements:
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


@dataclass
class AssFile:
    """ASS subtitle file.
    
    Contains script info, styles, and events.
    """
    script_info: dict[str, Any] = field(default_factory=dict)
    styles: dict[str, AssStyle] = field(default_factory=dict)
    events: list[AssEvent] = field(default_factory=list)
    
    @classmethod
    def load(cls, path: str | Path) -> "AssFile":
        """Load an ASS file from disk."""
        from sublib.ass.io import load_ass_file
        return load_ass_file(path)
    
    def save(self, path: str | Path) -> None:
        """Save the ASS file to disk."""
        from sublib.ass.io import save_ass_file
        save_ass_file(self, path)
    
    def sort_events(
        self,
        by: Literal["start", "end", "layer"] = "start",
        reverse: bool = False,
    ) -> None:
        """Sort events in place.
        
        Args:
            by: Sort key - "start" (default), "end", or "layer"
            reverse: Reverse sort order (default False)
        
        The secondary sort key is always layer for time-based sorts,
        or start time for layer-based sorts.
        """
        key_funcs = {
            "start": lambda e: (e.start_ms, e.layer, e.end_ms),
            "end": lambda e: (e.end, e.layer, e.start),
            "layer": lambda e: (e.layer, e.start_ms, e.end_ms),
        }
        self.events.sort(key=key_funcs[by], reverse=reverse)
    
    def sorted_events(
        self,
        by: Literal["start", "end", "layer"] = "start",
        reverse: bool = False,
    ) -> list[AssEvent]:
        """Return a sorted copy of events.
        
        Args:
            by: Sort key - "start" (default), "end", or "layer"
            reverse: Reverse sort order (default False)
        
        Returns:
            New list of events, sorted. Original list is unchanged.
        """
        key_funcs = {
            "start": lambda e: (e.start_ms, e.layer, e.end_ms),
            "end": lambda e: (e.end, e.layer, e.start),
            "layer": lambda e: (e.layer, e.start_ms, e.end_ms),
        }
        return sorted(self.events, key=key_funcs[by], reverse=reverse)

