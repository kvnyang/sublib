# sublib

A Python library for parsing and rendering subtitle files.

## Supported Formats

- **ASS/SSA** - Advanced SubStation Alpha (fully implemented)
- **SRT** - SubRip (planned)
- **VTT** - WebVTT (planned)

## Features

- Format-agnostic core models (`SubtitleEvent`, `SubtitleFile`)
- Full ASS/SSA support:
  - Parse event text into structured elements
  - Render elements back to ASS format
  - Override tags with proper semantics (event-level, inline, first-win, last-win)
  - Mutual exclusion rules
  - Strict validation with detailed error messages

## Installation

```bash
pip install sublib
```

## Usage

### Core (Format-Agnostic)

```python
from sublib import SubtitleEvent, SubtitleFile

# Create a simple subtitle file
event = SubtitleEvent(start_ms=0, end_ms=5000, text="Hello World")
sub_file = SubtitleFile(events=[event])
```

### ASS Format

```python
from sublib import AssFile

# Load an ASS file
ass_file = AssFile.load("subtitles.ass")

# Access events
for event in ass_file.events:
    print(event.start, event.end, event.text)

# Access parsed text elements
for element in event.text_elements:
    print(element)
```

## Project Structure

```
sublib/
├── core/           # Format-agnostic models and exceptions
├── formats/
│   └── ass/        # ASS/SSA implementation
└── utils/          # Shared utilities
```

## License

MIT
