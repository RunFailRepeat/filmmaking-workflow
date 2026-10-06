import json
import re
import unittest
from pathlib import Path
from validate_shot import validate

class ShotChecks(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(Path("examples/fictional-shot.json").read_text())
    def test_fictional_metadata(self): self.assertEqual(validate(self.d), [])
    def test_schema_text_patterns(self):
        schema = json.loads(Path("schemas/shot.schema.json").read_text())
        for key, prop in schema["properties"].items():
            if "pattern" in prop:
                with self.subTest(field=key):
                    self.assertIsNotNone(re.search(prop["pattern"], self.d[key]))
                    self.assertIsNone(re.search(prop["pattern"], " \t\n"))
    def test_edit_overrun(self):
        self.d["edit_seconds"] = 100
        self.assertIn("edit_seconds exceeds source_seconds", validate(self.d))
    def test_missing_camera(self):
        del self.d["camera"]
        self.assertIn("camera must be nonempty text", validate(self.d))
    def test_frames_are_not_full_review(self):
        self.d["review_coverage"] = "looks-good"
        self.assertIn("review_coverage invalid", validate(self.d))
