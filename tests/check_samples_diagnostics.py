from sublib import AssFile
from pathlib import Path
import sys

samples = [
    Path('/home/yang/projects/mfgen/Sources/S01/S01E01/Modern.Family.S01E01.Pilot.ass'),
    Path('/home/yang/projects/mfgen/Sources/S01/S01E04/Modern.Family.S01E04.The.Incident.ass')
]

for s in samples:
    if not s.exists():
        print(f"Sample skipped: {s} (not found)")
        continue
        
    print(f"\n--- Analyzing {s.name} ---")
    try:
        ass = AssFile.load(s)
        print(f"Total Errors: {len(ass.errors)}")
        print(f"Total Warnings: {len(ass.warnings)}")
        
        # Group by code to be concise
        from collections import Counter
        codes = Counter(d.code for d in ass.diagnostics)
        for code, count in codes.items():
            print(f"  [{code}]: {count} occurrences")
            
        # Show unique messages briefly
        unique_messages = set(d.message for d in ass.diagnostics)
        for msg in list(unique_messages)[:10]:
            print(f"  Example: {msg}")
        if len(unique_messages) > 10:
            print(f"  ... and {len(unique_messages)-10} more unique message types")
            
    except Exception as e:
        print(f"Failed to analyze {s.name}: {e}")
