"""LRC lyrics parser."""
from __future__ import annotations
import re

from sublib.lyrics.models import LrcFile, LrcLine, LrcTimestamp


class LrcParser:
    """Parser for LRC file format."""
    
    # Matches [mm:ss.xx] or [mm:ss.xxx]
    TIMESTAMP_REGEX = re.compile(r"\[(\d{2}:\d{2}\.\d{2,3})\]")
    
    # Matches [key:value]
    TAG_REGEX = re.compile(r"\[([a-zA-Z]+):(.+)\]")

    def parse(self, content: str) -> LrcFile:
        """Parse LRC string content."""
        lrc_file = LrcFile()
        lines = content.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for ID tags [ti:Title]
            tag_match = self.TAG_REGEX.match(line)
            if tag_match:
                key, value = tag_match.groups()
                # If the value contains timestamps, it's not a metadata tag (e.g. line with prefix)
                # But standard LRC tags are usually at the start.
                # A robust check is if the key is standard metadata.
                # For simplicity, we assume if it parses as tag and key is alpha, it's metadata, 
                # UNLESS it also contains timestamps later?
                # Actually, standard LRC format is strict.
                # Let's check for timestamps first because lines can have logic.
                pass

            # Find all timestamps in the line
            timestamps = self.TIMESTAMP_REGEX.findall(line)
            
            if timestamps:
                # Iterate and create lines for each timestamp
                # The text is whatever remains after removing all timestamps? 
                # Or usually timestamps are at the beginning.
                # " [00:12.00][00:15.30] Text content "
                
                # Remove all timestamps to get text
                clean_text = self.TIMESTAMP_REGEX.sub("", line).strip()
                
                for ts_str in timestamps:
                    try:
                        ts = LrcTimestamp.from_string(f"[{ts_str}]")
                        lrc_file.lines.append(LrcLine(timestamp=ts, text=clean_text))
                    except ValueError:
                        continue
            else:
                # Try parsing as metadata tag
                tag_match = self.TAG_REGEX.match(line)
                if tag_match:
                    key, value = tag_match.groups()
                    lrc_file.metadata[key.strip()] = value.strip()
        
        # Sort lines by timestamp
        lrc_file.lines.sort(key=lambda x: x.timestamp)
        
        return lrc_file
