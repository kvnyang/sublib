# sublib/ass/exceptions.py
"""ASS-specific exceptions."""


class SubtitleParseError(Exception):
    """Error during subtitle parsing."""
    def __init__(self, message: str, line_number: int | None = None, position: int | None = None, raw_text: str | None = None):
        super().__init__(message)
        self.line_number = line_number
        self.position = position
        self.raw_text = raw_text


class SubtitleRenderError(Exception):
    """Error during subtitle rendering."""
    pass
