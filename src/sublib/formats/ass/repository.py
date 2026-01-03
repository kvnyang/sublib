# asslib/repository.py
"""ASS file I/O operations."""
from __future__ import annotations
from pathlib import Path

from sublib.formats.ass.models import AssFile, AssEvent, AssStyle
from sublib.formats.ass.text_parser import AssTextParser
from sublib.core.exceptions import SubtitleParseError


def load_ass_file(path: str | Path) -> AssFile:
    """Load an ASS file from disk.
    
    Parses the file and returns an AssFile with all events
    having their text parsed into elements.
    """
    path = Path(path)
    parser = AssTextParser()
    
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    ass_file = AssFile()
    lines = content.splitlines()
    current_section = None
    line_number = 0
    
    for line in lines:
        line_number += 1
        line = line.strip()
        
        if not line or line.startswith(';'):
            continue
        
        # Section header
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            continue
        
        if current_section == 'script info':
            if ':' in line:
                key, _, value = line.partition(':')
                ass_file.script_info[key.strip()] = value.strip()
        
        elif current_section in ('v4 styles', 'v4+ styles'):
            if line.startswith('Style:'):
                style = _parse_style_line(line)
                if style:
                    ass_file.styles[style.name] = style
        
        elif current_section == 'events':
            if line.startswith('Dialogue:'):
                event = _parse_dialogue_line(line, parser, line_number)
                if event:
                    ass_file.events.append(event)
    
    return ass_file


def save_ass_file(ass_file: AssFile, path: str | Path) -> None:
    """Save an ASS file to disk."""
    path = Path(path)
    lines = []
    
    # Script Info
    lines.append('[Script Info]')
    for key, value in ass_file.script_info.items():
        lines.append(f'{key}: {value}')
    lines.append('')
    
    # Styles
    lines.append('[V4+ Styles]')
    lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, '
                 'OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, '
                 'ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, '
                 'Alignment, MarginL, MarginR, MarginV, Encoding')
    for style in ass_file.styles.values():
        lines.append(_format_style_line(style))
    lines.append('')
    
    # Events
    lines.append('[Events]')
    lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
    for event in ass_file.events:
        lines.append(_format_dialogue_line(event))
    
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines))


def _parse_style_line(line: str) -> AssStyle | None:
    """Parse a Style: line."""
    if not line.startswith('Style:'):
        return None
    
    parts = line[6:].split(',')
    if len(parts) < 23:
        return None
    
    return AssStyle(
        name=parts[0].strip(),
        fontname=parts[1].strip(),
        fontsize=float(parts[2]),
        primary_color=_parse_ass_color(parts[3]),
        secondary_color=_parse_ass_color(parts[4]),
        outline_color=_parse_ass_color(parts[5]),
        back_color=_parse_ass_color(parts[6]),
        bold=parts[7].strip() != '0',
        italic=parts[8].strip() != '0',
        underline=parts[9].strip() != '0',
        strikeout=parts[10].strip() != '0',
        scale_x=float(parts[11]),
        scale_y=float(parts[12]),
        spacing=float(parts[13]),
        angle=float(parts[14]),
        border_style=int(parts[15]),
        outline=float(parts[16]),
        shadow=float(parts[17]),
        alignment=int(parts[18]),
        margin_l=int(parts[19]),
        margin_r=int(parts[20]),
        margin_v=int(parts[21]),
        encoding=int(parts[22]),
    )


def _parse_dialogue_line(
    line: str, 
    parser: AssTextParser, 
    line_number: int
) -> AssEvent | None:
    """Parse a Dialogue: line."""
    if not line.startswith('Dialogue:'):
        return None
    
    # Split into 10 parts (last part is text, may contain commas)
    parts = line[9:].split(',', 9)
    if len(parts) < 10:
        return None
    
    text = parts[9]
    
    return AssEvent(
        start_ms=_parse_timestamp(parts[1]),
        end_ms=_parse_timestamp(parts[2]),
        text_elements=parser.parse(text, line_number=line_number),
        style=parts[3].strip(),
        layer=int(parts[0]),
        name=parts[4].strip(),
        margin_l=int(parts[5]),
        margin_r=int(parts[6]),
        margin_v=int(parts[7]),
        effect=parts[8].strip(),
    )


def _parse_timestamp(ts: str) -> int:
    """Parse ASS timestamp to milliseconds."""
    ts = ts.strip()
    parts = ts.split(':')
    if len(parts) != 3:
        return 0
    
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    centiseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + centiseconds * 10


def _format_timestamp(ms: int) -> str:
    """Format milliseconds to ASS timestamp."""
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    centiseconds = (ms % 1000) // 10
    
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def _parse_ass_color(color_str: str) -> int:
    """Parse ASS color string to int."""
    color_str = color_str.strip().strip('&H').strip('&')
    try:
        return int(color_str, 16)
    except ValueError:
        return 0


def _format_ass_color(color: int) -> str:
    """Format color int to ASS string."""
    return f"&H{color:08X}&"


def _format_style_line(style: AssStyle) -> str:
    """Format a Style: line."""
    return (
        f"Style: {style.name},{style.fontname},{style.fontsize},"
        f"{_format_ass_color(style.primary_color)},"
        f"{_format_ass_color(style.secondary_color)},"
        f"{_format_ass_color(style.outline_color)},"
        f"{_format_ass_color(style.back_color)},"
        f"{int(style.bold)},{int(style.italic)},{int(style.underline)},{int(style.strikeout)},"
        f"{style.scale_x},{style.scale_y},{style.spacing},{style.angle},"
        f"{style.border_style},{style.outline},{style.shadow},"
        f"{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},{style.encoding}"
    )


def _format_dialogue_line(event: AssEvent) -> str:
    """Format a Dialogue: line."""
    return (
        f"Dialogue: {event.layer},{_format_timestamp(event.start_ms)},"
        f"{_format_timestamp(event.end_ms)},{event.style},{event.name},"
        f"{event.margin_l},{event.margin_r},{event.margin_v},{event.effect},{event.render_text()}"
    )
