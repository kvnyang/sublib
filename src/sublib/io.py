"""Generic file I/O utilities.

Provides encoding-aware file read/write operations.
Format-specific logic (parsing, rendering) is handled by the respective model classes.
"""
from __future__ import annotations
from pathlib import Path


def read_text_file(path: Path | str, encoding: str = 'utf-8') -> str:
    """Read text file with specified encoding.
    
    Args:
        path: Path to file
        encoding: File encoding (e.g., 'utf-8', 'utf-8-sig')
        
    Returns:
        File content as string
    """
    path = Path(path)
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def write_text_file(path: Path | str, content: str, encoding: str = 'utf-8') -> None:
    """Write text file with specified encoding.
    
    Args:
        path: Path to file
        content: Content to write
        encoding: File encoding (e.g., 'utf-8', 'utf-8-sig')
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)
