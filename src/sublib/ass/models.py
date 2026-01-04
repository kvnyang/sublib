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
    
    def extract_line_scoped_tags(self, strict: bool = False) -> dict[str, Any]:
        """Extract event-level tags with exclusion rules applied.
        
        Args:
            strict: If True, raise SubtitleParseError on duplicate or mutually
                    exclusive tags. If False, apply rules silently (default).
        
        Returns:
            Dict mapping tag name to parsed value.
            
        Raises:
            SubtitleParseError: If strict=True and duplicates/conflicts found.
        """
        from sublib.ass.elements import AssOverrideTag, AssOverrideBlock
        from sublib.ass.tags import MUTUAL_EXCLUSIVES
        from sublib.exceptions import SubtitleParseError
        
        result: dict[str, Any] = {}
        seen_first_win: set[str] = set()
        seen_tags: set[str] = set()  # For strict mode
        
        # Flatten elements to check tags inside blocks
        flat_elements = []
        for elem in self.text_elements:
            if isinstance(elem, AssOverrideBlock):
                flat_elements.extend(item for item in elem.elements if isinstance(item, AssOverrideTag))
        
        for elem in flat_elements:
            if not elem.is_line_scoped:
                continue
            
            name = elem.name
            
            # Check for mutual exclusion
            exclusives = MUTUAL_EXCLUSIVES.get(name, set())
            conflicting_first_wins = [ex for ex in exclusives if ex in seen_first_win]
            has_conflict = any(ex in result for ex in exclusives)
            
            if strict:
                # Strict mode: error on duplicates or mutual exclusion
                if name in seen_tags:
                    raise SubtitleParseError(f"Duplicate event-level tag: \\{name}")
                if has_conflict:
                    conflicting = [ex for ex in exclusives if ex in result]
                    raise SubtitleParseError(
                        f"Mutually exclusive tags: \\{name} conflicts with \\{conflicting[0]}"
                    )
                seen_tags.add(name)
            
            # If a mutually exclusive first-wins tag already exists, skip this tag
            if conflicting_first_wins:
                continue
            
            # First-wins: skip if already seen (self-exclusion)
            if elem.first_wins:
                if name in seen_first_win:
                    continue
                seen_first_win.add(name)
            
            # Remove mutually exclusive tags (for last-wins tags)
            for excl in exclusives:
                result.pop(excl, None)
            
            result[name] = elem.value
        
        return result
    
    def extract_text_scoped_segments(self, strict: bool = False) -> list[AssTextSegment]:
        """Extract text segments with their preceding inline tags.
        
        Each segment contains:
        - tags: list of AssOverrideTag (is_line_scoped=False), with
                first-wins/last-wins and mutual exclusion rules applied
        - text: the text content (may include \\N newlines)
        
        Args:
            strict: If True, raise SubtitleParseError on duplicate or mutually
                    exclusive tags within a segment. If False, apply rules
                    silently (default).
        
        Returns:
            List of AssTextSegment.
            
        Raises:
            SubtitleParseError: If strict=True and duplicates/conflicts found.
        """
        from sublib.ass.elements import AssOverrideBlock, AssOverrideTag, AssPlainText, AssSpecialChar, SpecialCharType, AssTextSegment
        from sublib.ass.tags import MUTUAL_EXCLUSIVES
        from sublib.exceptions import SubtitleParseError
        
        segments: list[AssTextSegment] = []
        current_tags: list[AssOverrideTag] = []
        current_text = ""
        
        def apply_tag_rules(tags: list[AssOverrideTag]) -> list[AssOverrideTag]:
            """Apply first-wins, self-exclusion, and mutual exclusion."""
            result: list[AssOverrideTag] = []
            seen_first_win: set[str] = set()
            seen_tags: set[str] = set()  # For strict mode
            
            for tag in tags:
                name = tag.name
                exclusives = MUTUAL_EXCLUSIVES.get(name, set())
                conflicting_first_wins = [ex for ex in exclusives if ex in seen_first_win]
                has_conflict = any(ex in [t.name for t in result] for ex in exclusives)
                
                if strict:
                    if name in seen_tags and not tag.first_wins:
                        # Last-wins allows duplicates
                        pass
                    elif name in seen_tags and tag.first_wins:
                        raise SubtitleParseError(f"Duplicate inline tag: \\{name}")
                    if has_conflict:
                        conflicting = [ex for ex in exclusives if ex in [t.name for t in result]]
                        raise SubtitleParseError(
                            f"Mutually exclusive tags: \\{name} conflicts with \\{conflicting[0]}"
                        )
                    seen_tags.add(name)
                
                # If a mutually exclusive first-wins tag already exists, skip
                if conflicting_first_wins:
                    continue
                
                # First-wins: skip if already seen (self-exclusion)
                if tag.first_wins and name in seen_first_win:
                    continue
                seen_first_win.add(name)
                
                # Self-exclusion: remove previous same-name tag (last-wins)
                if not tag.first_wins:
                    result = [t for t in result if t.name != name]
                
                # Mutual exclusion: remove conflicting tags (for last-wins)
                result = [t for t in result if t.name not in exclusives]
                
                result.append(tag)
            
            return result
        
        for elem in self.text_elements:
            if isinstance(elem, AssPlainText):
                current_text += elem.content
            elif isinstance(elem, AssSpecialChar):
                if elem.is_newline:
                    current_text += r"\N" if elem.is_hard_newline else r"\n"
                else:  # HARD_SPACE
                    current_text += r"\h"
            elif isinstance(elem, AssOverrideBlock):
                # Process tags inside block
                for item in elem.elements:
                    if isinstance(item, AssOverrideTag):
                        if not item.is_line_scoped:
                            if current_text:
                                # Flush previous segment
                                segments.append(AssTextSegment(tags=apply_tag_rules(current_tags), text=current_text))
                                current_tags = []
                                current_text = ""
                            current_tags.append(item)
        
        # Final segment
        if current_text or current_tags:
            segments.append(AssTextSegment(tags=apply_tag_rules(current_tags), text=current_text))
        
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

