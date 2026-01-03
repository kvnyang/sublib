# sublib/ass/exceptions.py
"""ASS-specific exceptions."""


class SubtitleParseError(Exception):
    """Error during subtitle parsing."""
    pass


class SubtitleRenderError(Exception):
    """Error during subtitle rendering."""
    pass
