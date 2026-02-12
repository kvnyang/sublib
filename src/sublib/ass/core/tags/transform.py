"""Animation and karaoke tag definitions."""
from __future__ import annotations
import re
from typing import Any, ClassVar, Literal

from sublib.ass.core.tags.base import TagCategory
from sublib.ass.types import AssTransform, AssKaraoke


def _find_matching_paren(text: str, start: int) -> int:
    """Find the position of the closing parenthesis matching the one at 'start'."""
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


def parse_tags_string(tags_str: str) -> list[tuple[str, Any]]:
    """Parse a tags string into list of (name, value) tuples.
    
    Uses manual scanning with bracket counting to handle nested parentheses
    in function tags like \\clip(...).
    
    Args:
        tags_str: Raw tags string like "\\fs40\\1c&HFF0000&"
        
    Returns:
        List of (tag_name, parsed_value) tuples
    """
    from sublib.ass.core.tags.registry import TAGS, parse_tag
    
    result: list[tuple[str, Any]] = []
    tags_str = tags_str.strip()
    
    if not tags_str:
        return result
    
    i = 0
    while i < len(tags_str):
        if tags_str[i] == '\\':
            tag_start = i + 1
            
            # Find matching tag name (longest first)
            for tag_name in sorted(TAGS.keys(), key=len, reverse=True):
                if tags_str[tag_start:].startswith(tag_name):
                    tag_cls = TAGS[tag_name]
                    value_start = tag_start + len(tag_name)
                    
                    if tag_cls.is_function:
                        # Function tag: find matching parenthesis
                        if value_start < len(tags_str) and tags_str[value_start] == '(':
                            close_pos = _find_matching_paren(tags_str, value_start)
                            if close_pos > 0:
                                raw_value = tags_str[value_start + 1:close_pos]
                                parsed = parse_tag(tag_name, raw_value)
                                if parsed is not None:
                                    result.append((tag_name, parsed))
                                i = close_pos + 1
                                break
                        # No valid function tag, skip
                        i = value_start
                        break
                    else:
                        # Non-function tag: read until next backslash
                        end_pos = value_start
                        while end_pos < len(tags_str) and tags_str[end_pos] != '\\':
                            end_pos += 1
                        
                        raw_value = tags_str[value_start:end_pos].strip()
                        
                        # Validate with param_pattern if available
                        if tag_cls.param_pattern:
                            pattern = re.compile(f'^{tag_cls.param_pattern}')
                            match = pattern.match(raw_value)
                            if match:
                                raw_value = match.group(0)
                                end_pos = value_start + len(raw_value)
                        
                        parsed = parse_tag(tag_name, raw_value)
                        if parsed is not None:
                            result.append((tag_name, parsed))
                        i = end_pos
                        break
            else:
                # No tag matched, skip this backslash
                i += 1
        else:
            i += 1
    
    return result


class TTag:
    """\\t(...) animation tag definition."""
    name: ClassVar[str] = "t"
    category: ClassVar[TagCategory] = TagCategory.ANIMATION
    param_pattern: ClassVar[str | None] = None
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = True
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def _split_toplevel_commas(s: str, max_splits: int = -1) -> list[str]:
        """Split string on commas that are not inside parentheses.
        
        Args:
            s: String to split
            max_splits: Maximum number of splits (-1 for unlimited)
            
        Returns:
            List of substrings
        """
        result = []
        current = []
        depth = 0
        splits = 0
        
        for char in s:
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0 and (max_splits < 0 or splits < max_splits):
                result.append(''.join(current))
                current = []
                splits += 1
            else:
                current.append(char)
        
        result.append(''.join(current))
        return result
    
    @staticmethod
    def parse(raw: str) -> AssTransform | None:
        raw = raw.strip()
        
        t1: int | None = None
        t2: int | None = None
        accel: float | None = None
        tags_str: str = ""
        
        # Form: (tags) - no leading numeric parameter
        if not any(c.isdigit() for c in TTag._split_toplevel_commas(raw, 1)[0] if c not in "\\"):
            tags_str = raw
        else:
            # Split on top-level commas only (respecting nested parens)
            parts = TTag._split_toplevel_commas(raw, 3)
            
            # Form: (accel, tags)
            if len(parts) == 2:
                try:
                    accel = float(parts[0])
                    tags_str = parts[1].strip()
                except ValueError:
                    tags_str = raw
            
            # Form: (t1, t2, tags)
            elif len(parts) == 3:
                try:
                    t1 = int(parts[0])
                    t2 = int(parts[1])
                    tags_str = parts[2].strip()
                except ValueError:
                    return None
            
            # Form: (t1, t2, accel, tags)
            elif len(parts) == 4:
                try:
                    t1 = int(parts[0])
                    t2 = int(parts[1])
                    accel = float(parts[2])
                    tags_str = parts[3].strip()
                except ValueError:
                    return None
        
        # Parse the tags string
        parsed_tags = parse_tags_string(tags_str)
        
        return AssTransform(tags=parsed_tags, t1=t1, t2=t2, accel=accel)
    
    @staticmethod
    def format(val: AssTransform) -> str:
        from sublib.ass.core.tags.base import _format_float
        raw_tags = val.to_raw_tags()
        if val.t1 is None and val.t2 is None and val.accel is None:
            return f"\\t({raw_tags})"
        if val.t1 is None and val.t2 is None and val.accel is not None:
            return f"\\t({_format_float(val.accel)},{raw_tags})"
        if val.accel is None:
            return f"\\t({val.t1},{val.t2},{raw_tags})"
        return f"\\t({val.t1},{val.t2},{_format_float(val.accel)},{raw_tags})"


def _parse_karaoke(raw: str) -> int | None:
    try:
        val = int(raw)
        return val if val >= 0 else None
    except ValueError:
        return None


# ============================================================
# Karaoke Tags
# ============================================================

class KTag:
    """\\k karaoke tag definition."""
    name: ClassVar[str] = "k"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\k{val}"


class KUpperTag:
    """\\K karaoke tag definition."""
    name: ClassVar[str] = "K"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\K{val}"


class KfTag:
    """\\kf karaoke tag definition."""
    name: ClassVar[str] = "kf"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\kf{val}"


class KoTag:
    """\\ko karaoke tag definition."""
    name: ClassVar[str] = "ko"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\ko{val}"


class KtTag:
    """\\kt karaoke tag definition."""
    name: ClassVar[str] = "kt"
    category: ClassVar[TagCategory] = TagCategory.KARAOKE
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    param_pattern: ClassVar[str | None] = r'\d+'
    is_event_level: ClassVar[bool] = False
    is_function: ClassVar[bool] = False
    first_wins: ClassVar[bool] = False
    exclusives: ClassVar[frozenset[str]] = frozenset()
    
    @staticmethod
    def parse(raw: str) -> int | None:
        return _parse_karaoke(raw)
    
    @staticmethod
    def format(val: int) -> str:
        return f"\\kt{val}"
