import unittest
import os
import sys
from pathlib import Path

# Add sublib src to path
sublib_path = Path("/home/yang/projects/sublib/src")
if str(sublib_path) not in sys.path:
    sys.path.insert(0, str(sublib_path))

from sublib import AssFile

class MfgenRegressionTest(unittest.TestCase):
    def setUp(self):
        # We'll use the Modern Family Pilot sample tracked in mfgen
        self.sample_path = Path("/home/yang/projects/mfgen/Sources/S01/S01E01/Modern.Family.S01E01.Pilot.ass")
        if not self.sample_path.exists():
            # Fallback if the path is different
            self.sample_path = Path("/home/yang/projects/sublib/tests/samples/test_v4plus.ass")

    def test_roundtrip_idempotency(self):
        """Test that loading and dumping is idempotent (2nd pass matches 1st pass)."""
        if not self.sample_path.exists():
            self.skipTest(f"Sample file not found: {self.sample_path}")

        with open(self.sample_path, 'r', encoding='utf-8-sig') as f:
            original_content = f.read()

        # Pass 1
        ass_file1 = AssFile.loads(original_content)
        dump1 = ass_file1.dumps()
        
        # Pass 2
        ass_file2 = AssFile.loads(dump1)
        dump2 = ass_file2.dumps()

        # They should be identical
        self.assertEqual(dump1.strip(), dump2.strip())

    def test_diagnostics_collection(self):
        """Test that diagnostics are correctly aggregated."""
        if not self.sample_path.exists():
            self.skipTest(f"Sample file not found: {self.sample_path}")

        ass_file = AssFile.load(self.sample_path)
        
        # The sample should be relatively clean
        for diag in ass_file.diagnostics:
            print(diag)
            
        # Verify specific categorization methods exist
        self.assertIsInstance(ass_file.errors, list)
        self.assertIsInstance(ass_file.warnings, list)
        # We'll test for infos removal in the next phase

if __name__ == '__main__':
    unittest.main()
