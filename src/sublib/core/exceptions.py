# sublib/core/exceptions.py
"""Subtitle parsing and rendering exceptions."""


class SubtitleParseError(Exception):
    """Subtitle format parsing error.
    
    Provides locatable error information for debugging.
    """
    
    def __init__(
        self,
        message: str,
        line_number: int | None = None,
        position: int | None = None,
        raw_text: str | None = None,
    ):
        self.message = message
        self.line_number = line_number
        self.position = position
        self.raw_text = raw_text
        
        # Build locatable error message
        location = []
        if line_number is not None:
            location.append(f"line {line_number}")
        if position is not None:
            location.append(f"pos {position}")
        
        loc_str = f" ({', '.join(location)})" if location else ""
        full_msg = f"Subtitle Parse Error{loc_str}: {message}"
        if raw_text:
            preview = raw_text[:100] + "..." if len(raw_text) > 100 else raw_text
            full_msg += f"\n  Raw: {preview}"
        
        super().__init__(full_msg)


class SubtitleRenderError(Exception):
    """Subtitle rendering error."""
    pass

