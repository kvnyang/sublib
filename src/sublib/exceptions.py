"""Subtitle processing exceptions."""


class SubtitleError(Exception):
    """Base class for all subtitle errors."""


class ParseError(SubtitleError):
    """Base class for parsing errors."""
    
    def __init__(
        self,
        message: str,
        line_number: int | None = None,
        position: int | None = None,
        raw_text: str | None = None
    ):
        super().__init__(message)
        self.line_number = line_number
        self.position = position
        self.raw_text = raw_text


class TextParseError(ParseError):
    """Error parsing event text (tag syntax, etc.)."""


class FileParseError(ParseError):
    """Error parsing file structure (encoding, missing sections, etc.)."""


class RenderError(SubtitleError):
    """Error during subtitle rendering."""


# Backward compatibility aliases
SubtitleParseError = ParseError
SubtitleRenderError = RenderError
