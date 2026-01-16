# ASS Parsing and Rendering Strategy

## Overview

This document outlines the parsing and rendering strategies used in `sublib` for ASS (Advanced SubStation Alpha v4+) implementation.

The architecture follows a strict separation of concerns:
1.  **File Parsing**: Resolves file sections into high-level models (`AssFile`, `AssEvent`, `AssStyle`)
2.  **Text Parsing**: Resolves event text into an Abstract Syntax Tree (AST)

---

## 1. File Structure Parsing

The file parser handles the high-level ASS file structure, which consists of section headers (e.g., `[Events]`) followed by content.

### Strategy: Section-Aware Parsing

| Section | Strategy | Validation Behavior |
|---------|----------|---------------------|
| `[Script Info]` | **Typed + Extensible** | **Warnings only**. Parses all fields. Validates critical fields (e.g., `ScriptType`, `PlayResX`) and collects issues in `script_info.warnings`. |
| `[V4+ Styles]` | **CSV Parsing** | Validates column count and types. Invalid lines are skipped (logged). |
| `[Events]` | **CSV Parsing** | Validates column count. Text field is kept raw until explicitly parsed via `AssTextParser`. |

### Script Info Validation rules

- **ScriptType**: Must be `v4.00+` (case-insensitive).
- **PlayResX/Y**: Must be present and positive integers.
- **Timer**: Must be positive float.
- **WrapStyle**: Must be 0-3.
- **Collisions**: Must be `Normal` or `Reverse`.
- **Unknown Fields**: Preserved in `script_info.extra` for roundtrip fidelity.

---

## 2. Tag Parsing (Event Text)

This implementation follows **Aegisub's actual behavior** (the reference implementation), with precise handling of event-level tags, mutual exclusivity, and multiple occurrence precedence.

### Architecture: Parse-then-Validate

1.  **Parse Phase (Permissive)**:
    - Uses **Regex-Constrained Greedy Matching**.
    - Each tag has a precise parameter pattern (e.g., `\c` matches `&H[0-9A-Fa-f]+&`).
    - Valid tags are resolved to `AssOverrideTag`.
    - **Anything** that doesn't match a known tag pattern is preserved as `AssComment` (unrecognized text).
    - **No data loss**: The AST preserves all characters from the original string.

2.  **Validate Phase (Optional)**:
    - If `strict=True`, validating presence of `AssComment` nodes raises `SubtitleParseError`.
    - If `strict=False`, comments are silently ignored (standard playback behavior).

### Tag Categories & Precedence

#### Event-level Tags (`is_event_level=True`)

Affect the entire event regardless of position.

| Tag | Spec Listed | Precedence | Exclusives | Verified |
|-----|-------------|------------|------------|----------|
| `\pos` | ✓ | **First-wins** | `\move` | ✓ |
| `\move` | ✓ | **First-wins** | `\pos` | ✓ |
| `\org` | ✓ | **First-wins** | - | ✓ |
| `\fad` | ✓ | **First-wins** | `\fade` | ✓ |
| `\fade` | ✓ | **First-wins** | `\fad` | ✓ |
| `\clip` | ✓ | **Last-wins** | `\iclip` | ✓ |
| `\iclip` | ✓ | **Last-wins** | `\clip` | ✓ |
| `\an` | ✓ | **First-wins** | - | ✓ |
| `\a` | ✓ | **First-wins** | - | ✓ |
| `\q` | ✓ | **Last-wins** | - | ✓ |

#### Inline Tags (`is_event_level=False`)

All other tags (e.g., `\b`, `\fs`, `\c`).
- **Precedence**: Last occurrence always wins (`first_wins=False`).
- **Scope**: Affects text following the tag until reset or overridden.

---

## 3. AST Structure

The text parser produces a list of `AssTextElement` nodes.

```python
AssFile
  └── AssEvent
      └── text_elements: list[AssTextElement]
            ├── AssPlainText ("Hello")
            ├── AssSpecialChar ("\N")
            └── AssOverrideBlock ("{\pos(100,100)\b1}")
                  └── elements: list[AssBlockElement]
                        ├── AssOverrideTag (name="pos", value=Position(100,100))
                        ├── AssOverrideTag (name="b", value=True)
                        └── AssComment ("unknowntag")
```

---

## 4. API Usage

### File Loading

```python
from sublib.ass import AssFile

# Load file
ass = AssFile.load("file.ass")

# Check validation warnings
if ass.script_info.warnings:
    print("Script Info issues:", ass.script_info.warnings)
```

### Text Parsing (Manual)

```python
from sublib.ass import AssTextParser

text = "{\\pos(100,100)\\unknown}Hello"

# Strict mode: Raises error on '\unknown'
try:
    AssTextParser(strict=True).parse(text)
except SubtitleParseError as e:
    print(e)

# Permissive mode: Preserves '\unknown' as comment
elements = AssTextParser(strict=False).parse(text)
```

### Text Extraction and Composition

Extract structured data from event text:

```python
# Extract event tags and segments
result = event.extract_all()

# Access event-level tags (pos, an, move, etc.)
pos = result.event_tags.get("pos")
alignment = result.event_tags.get("an")

# Access inline segments with formatting
for seg in result.segments:
    print(seg.get_text())  # Plain text
    print(seg.block_tags)  # {"b": True, "i": False, ...}
```

Compose text elements from structured data:

```python
from sublib.ass import AssEvent
from sublib.ass.ast import AssTextSegment, AssPlainText

# Build segments
segments = [
    AssTextSegment(
        block_tags={"b": True},
        content=[AssPlainText(content="Bold text")]
    ),
    AssTextSegment(
        block_tags={"i": True},
        content=[AssPlainText(content="Italic text")]
    )
]

# Compose into text elements
elements = AssEvent.compose_all(
    event_tags={"pos": Position(100, 200), "an": 8},
    segments=segments
)

# Assign to event
event.text_elements = elements
```

---

## 5. References

- **Implementation**: `src/sublib/ass/`
- **Tag Definitions**: `src/sublib/ass/tags/`
- **Text Transform**: `src/sublib/ass/text_transform.py`

