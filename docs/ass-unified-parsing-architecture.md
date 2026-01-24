# ASS Multi-Layered Parsing Architecture

This document defines the 3-layered parsing architecture for the `sublib` ASS parser. The goal is to separate structural extraction, semantic typing, and content-rich AST parsing while providing a clear diagnostic hierarchy (Error, Warning, Info).

## Core Principles

1.  **Separation of Concerns**: Each layer has a distinct responsibility.
2.  **Diagnostic Hierarchy**:
    *   **Error**: Violates fundamental ASS format or structural constraints. May halt parsing.
    *   **Warning**: Deviates from recommended specs or version inconsistency. Parsing continues.
    *   **Info**: Normalization suggestions or transparent pass-through of unknown data.
3.  **Liberal in, Strict out**: Accept messy inputs (whitespace, case-insensitivity) but normalize on output.
4.  **Passthrough**: Unrecognized data is never discarded; it is kept as raw strings and passed to the caller.

---

## Layer 1: Structural Parser (Document-Level)

The primary goal is to split the raw text into structured but untyped sections.

### 1. Section Constraints

| Level | Condition | Behavior |
| :--- | :--- | :--- |
| **Error** | Duplicate section headers (e.g., two `[Events]`) | Halt/Reject |
| **Error** | Ambiguous versioning (both `[V4+ Styles]` and `[V4 Styles]` present) | Halt/Reject |
| **Warning** | Missing or out-of-order core sections (`Script Info`, `Styles`, `Events`) | Continue |
| **Warning** | `Script Info` is not the first non-empty/non-comment line | Continue |
| **Warning** | Optional/Custom sections appear before core sections | Continue |

### 2. Line-Level Parsing (Core Sections)

Applies to `Script Info`, `Styles`, and `Events`:
*   **Empty Lines**: Ignored.
*   **Comment Lines** (starting with `;` or `!:`):
    *   In `[Script Info]`: Preserved in a list.
    *   In `[Styles]`/`[Events]`: Ignored.
*   **Content Lines** (`Descriptor: Value`):
    *   `Descriptor`: Stripped of whitespace. Case-insensitive matching.
    *   `Value`: Stripped once, then kept as a raw string.

### 3. Section-Specific Logic

*   **[Script Info]**:
    *   Storage: `OrderedDict[str, str]`.
    *   Collision: Duplicate keys result in **Warning** + Last Wins.
*   **[Styles] & [Events]**:
    *   **Format Constraints**:
        *   Exactly one `Format` line per section (**Error** if missing or multiple).
        *   `Format` line must precede all data lines (**Error**).
        *   Duplicate field names in `Format` (**Error**).
        *   `Events` `Format` must end with `Text` (**Error**).
    *   **Data Storage**:
        *   Storage: `list[dict[str, str]]`.
        *   Each record includes `descriptor` (e.g., `Dialogue`) and key-value pairs mapped by `Format`.
        *   Insufficient comma separators compared to `Format` (**Error**).

---

## Layer 2: Semantic Parser (Section/Field-Level)

The primary goal is to convert raw strings from Layer 1 into typed objects and apply version-specific rules.

### 1. Versioning (ScriptType)

1.  Missing or invalid `ScriptType` -> **Warning** + Assume `v4.00+` for logic (do not modify raw value).
2.  Apply `v4` or `v4+` rules based on the `ScriptType` found.

### 2. Field Conversion & Validation

*   **Script Info**: Convert known keys to `int`, `bool`, `float`, or `str` (matrix etc.).
*   **Versioning Checks**: Flag features used in the wrong version (e.g., `WrapStyle` in a `v4` script) as **Warning**.
*   **Field Mapping**: Handle naming differences (e.g., `TertiaryColour` (v4) vs `OutlineColour` (v4+)).

### 3. Styles & Events Minimal Set

*   Validate that mandatory fields exist (e.g., `Start, End, Style, Text` for v4 Events).
*   Missing mandatory fields -> **Warning**.
*   Unknown descriptors (beyond standard set like `Dialogue`, `Comment`, `Style`) are kept as raw string records.

### 4. Fonts, Graphics & Custom Sections

*   These sections are passed through transparently to the caller as raw line lists. No semantic parsing or type conversion is performed.

---

## Layer 3: Content Parser (AST & Transformations)

The deepest level, focusing on the contents of specific fields, primarily `Text`.

### 1. AST Parsing (AssTextParser)

Takes the raw `Text` string from Layer 2 and parses it into an AST (`text_elements`).
*   Handles Override Tags (`{\...}`), Comments, and Plain Text.

### 2. Semantic Transformation (Transform API)

The `extract_event_tags_and_segments` and `build_text_elements` operations act on the Layer 3 AST to provide a "Semantic Model" of the subtitle content.

---

## Conclusion: Unified Flow

`AssFile.loads()`
1.  **Executes Layer 1**: Spits out a `RawDocument` (untyped sections and records).
    *   `Format:` lines are treated as structural headers in `[Styles]` and `[Events]`.
    *   `Format:` lines in `[Script Info]` or custom sections are treated as standard data records.
2.  **Applies Layer 2**: Iterates through `RawDocument`, converting fields and populating `AssFile` models (`AssScriptInfo`, `AssStyles`, `AssEvents`).
3.  **Triggers Layer 3**: For each Event, the `Text` string is passed to `AssTextParser` (either immediately or lazily).

This architecture ensures that fundamental structural errors are caught early, while allowing high flexibility for custom fields and version-mixed files.
