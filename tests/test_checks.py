import unittest
from check_packet import check, FIELDS, APPROVALS

def packet():
    d = dict.fromkeys(FIELDS, "synthetic-value")
    d.update(dict.fromkeys(APPROVALS, "APPROVED"))
    d.update(edit_duration_seconds="4", source_duration_seconds="6")
    return "\n".join(k + ": " + v for k, v in d.items())

class PacketChecks(unittest.TestCase):
    def test_complete_synthetic_packet(self):
        self.assertEqual(check(packet()), [])
    def test_missing_approval(self):
        self.assertIn("approval not recorded: execution_approval",
                      check(packet().replace("execution_approval: APPROVED", "execution_approval: PENDING")))
    def test_duplicate_cannot_hide_pending(self):
        self.assertIn("duplicate field: story_approval", check(packet() + "\nstory_approval: APPROVED"))
    def test_nonfinite_duration(self):
        self.assertIn("invalid positive duration: edit_duration_seconds",
                      check(packet().replace("edit_duration_seconds: 4", "edit_duration_seconds: nan")))
    def test_placeholder_is_not_ready(self):
        self.assertIn("unresolved field: ending", check(packet().replace("ending: synthetic-value", "ending: TBD")))
