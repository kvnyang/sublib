# sublib

A Python library for parsing and rendering subtitle files.

## Supported Formats

- **ASS** - Advanced SubStation Alpha v4+ (fully implemented)
- **SRT** - SubRip (planned)
- **VTT** - WebVTT (planned)

## Features

- Full ASS (v4+) support:
  - Strongly typed models (`AssFile`, `AssEvent`, `AssStyle`, `ScriptInfo`)
  - Semantic parsing of event text into AST elements (`AssOverrideTag`, `AssTextSegment`, etc.)
  - Full support for `[Script Info]` with validation warnings
  - Override tag handling with proper semantics (collision resolution, nesting)
  - Strict validation modes

## Installation

```bash
pip install sublib
```

## Usage

### ASS Format

#### Loading and Saving

```python
from sublib.ass import AssFile

# Load an ASS file
ass_file = AssFile.load("subtitles.ass")

# Or parse from string
ass_file = AssFile.from_string(content)

# Save back to file
ass_file.save("output.ass")
```

#### Accessing Script Info

The `[Script Info]` section is fully typed accessible via `ass_file.script_info`:

```python
info = ass_file.script_info

# Access standard fields directly
print(f"Title: {info.title}")
print(f"Resolution: {info.play_res_x}x{info.play_res_y}")
print(f"Color Matrix: {info.ycbcr_matrix}")  # e.g., "TV.709"

# Check validation warnings (e.g., missing resolution or wrong format)
for warning in info.warnings:
    print(f"Warning: {warning}")
```

#### Working with Events and Text

Event text is parsed into a structured AST (Abstract Syntax Tree), allowing precise manipulation of tags and text.

```python
from sublib.ass import AssTextParser, AssTextRenderer

# Access events
for event in ass_file.events:
    print(f"Timing: {event.start} -> {event.end}")
    
    # event.text_elements contains the parsed AST
    # Example text: "{\\pos(100,200)\\fnArial}Hello"
    for element in event.text_elements:
        print(element) 
        # Output: 
        # AssOverrideBlock(elements=[AssOverrideTag(name='pos', ...), AssOverrideTag(name='fn', ...)])
        # AssPlainText(content='Hello')

# Extract effective tags for a line (resolving collisions)
from sublib.ass import extract_line_scoped_tags
tags = extract_line_scoped_tags(event.text_elements)

# Render back to string
renderer = AssTextRenderer()
raw_text = renderer.render(event.text_elements)
```

## Project Structure

```
sublib/
├── ass/                # ASS v4+ implementation
│   ├── ast/            # Abstract Syntax Tree nodes
│   ├── models.py       # Data models (AssFile, AssEvent, ScriptInfo)
│   ├── services/       # Parsers and Renderers
│   └── types/          # Value types (Color, Timestamp, etc.)
└── exceptions.py       # Shared exceptions
```

## License

MIT
