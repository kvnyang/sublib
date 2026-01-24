"""ASS parsing diagnostic models."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class DiagnosticLevel(Enum):
    """Severity of a diagnostic message."""
    ERROR = auto()    # Fundamental violation, parsing might be compromised
    WARNING = auto()  # Specification deviation, parsing continues
    INFO = auto()     # Normalization or informational message


@dataclass(frozen=True)
class Diagnostic:
    """A diagnostic message from the parser."""
    level: DiagnosticLevel
    message: str
    line_number: int = 0
    code: Optional[str] = None

    def __str__(self) -> str:
        line_info = f"Line {self.line_number}: " if self.line_number > 0 else ""
        return f"[{self.level.name}] {line_info}{self.message}"
