"""LRC lyrics data models."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass(order=True, frozen=True)
class LrcTimestamp:
    """LRC timestamp [mm:ss.xx]."""
    minutes: int
    seconds: int
    centiseconds: int

    def __str__(self) -> str:
        """Format as [mm:ss.xx]."""
        return f"[{self.minutes:02d}:{self.seconds:02d}.{self.centiseconds:02d}]"
    
    @classmethod
    def from_string(cls, text: str) -> LrcTimestamp:
        """Parse from [mm:ss.xx] or [mm:ss.xxx]."""
        # Remove brackets
        content = text.strip("[]")
        parts = content.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid timestamp format: {text}")
            
        minutes = int(parts[0])
        
        sec_parts = parts[1].split(".")
        seconds = int(sec_parts[0])
        
        centiseconds = 0
        if len(sec_parts) > 1:
            cs_str = sec_parts[1]
            if len(cs_str) == 3:
                # Round 3 digits to 2 (ms to cs)
                centiseconds = int(round(int(cs_str) / 10))
            else:
                centiseconds = int(cs_str[:2].ljust(2, '0'))
                
        return cls(minutes, seconds, centiseconds)
        
    @classmethod
    def from_timedelta(cls, td: timedelta) -> LrcTimestamp:
        """Create from timedelta."""
        total_seconds = td.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        centiseconds = int((total_seconds * 100) % 100)
        return cls(minutes, seconds, centiseconds)


@dataclass
class LrcLine:
    """A single line in an LRC file."""
    timestamp: LrcTimestamp
    text: str

    def __str__(self) -> str:
        return f"{self.timestamp}{self.text}"


class LrcMetadata:
    """Intelligent container for LRC metadata."""
    def __init__(self, data: dict[str, str] | None = None):
        self._data = data if data is not None else {}

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __setitem__(self, key: str, value: str) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


class LrcLines:
    """Intelligent container for LRC lines."""
    def __init__(self, data: list[LrcLine] | None = None):
        self._data = data if data is not None else []

    def __getitem__(self, index: int) -> LrcLine:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def add(self, timestamp: str | timedelta | LrcTimestamp, text: str) -> None:
        """Add a lyrics line."""
        if isinstance(timestamp, str):
            ts = LrcTimestamp.from_string(timestamp)
        elif isinstance(timestamp, timedelta):
            ts = LrcTimestamp.from_timedelta(timestamp)
        else:
            ts = timestamp
        self._data.append(LrcLine(ts, text))

    def append(self, line: LrcLine) -> None:
        """Append a pre-constructed LrcLine."""
        self._data.append(line)

    def sort(self, **kwargs):
        self._data.sort(**kwargs)


@dataclass
class LrcFile:
    """Represents a full LRC file with metadata and lines."""
    metadata: LrcMetadata = field(default_factory=LrcMetadata)
    lines: LrcLines = field(default_factory=LrcLines)

    def __post_init__(self):
        if isinstance(self.metadata, dict):
            self.metadata = LrcMetadata(self.metadata)
        if isinstance(self.lines, list):
            self.lines = LrcLines(self.lines)

    @classmethod
    def loads(cls, content: str) -> LrcFile:
        """Parse LRC content from string."""
        from sublib.lrc.parser import LrcParser
        return LrcParser().parse(content)

    def dumps(self) -> str:
        """Render LRC file to string."""
        from sublib.lrc.renderer import LrcRenderer
        return LrcRenderer().render(self)

    @classmethod
    def load(cls, path: Path | str) -> LrcFile:
        """Load LRC file from path."""
        from sublib.io import read_text_file
        content = read_text_file(path, encoding='utf-8-sig')
        return cls.loads(content)

    def dump(self, path: Path | str) -> None:
        """Save to file."""
        from sublib.io import write_text_file
        content = self.dumps()
        write_text_file(path, content, encoding='utf-8-sig')

    @property
    def add_line(self):
        """Legacy helper for addition."""
        return self.lines.add

    def __iter__(self):
        return iter(self.lines)

    def __len__(self) -> int:
        return len(self.lines)
