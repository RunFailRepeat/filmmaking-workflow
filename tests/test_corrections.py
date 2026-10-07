"""Regressions reproduced at remote 57723ae; all evidence here is invented."""
import copy
import unittest
from test_continuity import fixture
from validate_continuity import validate


def two_lines():
    d = fixture()
    d["lines"].append(dict(d["lines"][0], line_id="line-02"))
    d["submission"]["ordered_bindings"].append(dict(d["submission"]["ordered_bindings"][0], line_id="line-02"))
    d["review"]["lines"].append(copy.deepcopy(d["review"]["lines"][0]))
    d["review"]["lines"][1]["line_id"] = "line-02"
    return d


class ConfirmedCorrections(unittest.TestCase):
    def test_simultaneous_story_still_has_edited_seam(self):
        d = fixture(); t = d["transition"]
        t["sequential"] = False
        self.assertEqual(validate(d, "release"), [])
        t["normal_speed_reviewed"] = False
        t["checks"] = dict.fromkeys(t["checks"], "unverified")
        self.assertIn("actual seam requires normal-speed review on current export", validate(d, "release"))

    def test_seam_presence_is_explicit_and_standalone_is_allowed(self):
        d = fixture(); del d["transition"]["has_edited_seam"]
        self.assertTrue(validate(d, "release"))
        d = fixture(); d["transition"]["has_edited_seam"] = False
        self.assertTrue(validate(d, "release"))
        d["transition"].update(sequential=False, normal_speed_reviewed=False)
        self.assertEqual(validate(d, "release"), [])

    def test_reversed_starts_rejected_despite_matching_ids(self):
        d = two_lines()
        d["review"]["lines"][1]["export_range"] = dict(start_seconds=0, end_seconds=1)
        self.assertIn("dialogue starts reverse declared playback order", validate(d, "release"))

    def test_overlapping_and_simultaneous_starts_allowed(self):
        d = two_lines()
        for start in (2, 3):
            d["review"]["lines"][1]["export_range"] = dict(start_seconds=start, end_seconds=4)
            self.assertEqual(validate(d, "release"), [])

    def test_placeholder_direct_edit_plan_rejected(self):
        d = fixture(); s = d["submission"]
        s.update(route="direct_edit", bindings_supported=False, ordered_bindings=[])
        s["replacement_plan"]["approved"] = True
        self.assertEqual(validate(d, "preflight"), [])
        for key in ("timeline_ranges", "edit_instructions"):
            for value in ("UNVERIFIED", " pending ", "TBD", "unknown", "N/A", "none"):
                changed = copy.deepcopy(d); changed["submission"]["replacement_plan"][key] = value
                self.assertIn("direct-edit timing and instructions remain unresolved", validate(changed, "preflight"))

    def test_huge_numeric_values_report_errors_without_exception(self):
        d = fixture(); d["review"]["duration_seconds"] = 10**400
        self.assertTrue(validate(d, "release"))
        d = fixture(); d["review"]["listened_ranges"][0]["end_seconds"] = 10**400
        self.assertTrue(validate(d, "release"))
        d = fixture(); d["transition"]["seam_review"]["cut_seconds"] = 10**400
        self.assertTrue(validate(d, "release"))

    def test_seam_provenance_completed_and_current(self):
        for key, value in (("reviewer_id", "UNVERIFIED"), ("reviewed_at", "UNVERIFIED"),
                           ("reviewed_at", "2026-10-07T00:00:00"), ("export_asset_id", "stale"), ("export_version", "stale")):
            d = fixture(); d["transition"]["seam_review"][key] = value
            self.assertTrue(validate(d, "release"), key)
        for key in fixture()["transition"]["seam_review"]:
            d = fixture(); del d["transition"]["seam_review"][key]
            self.assertTrue(validate(d, "release"), key)

    def test_seam_review_straddles_cut_and_sources_are_bounded(self):
        for cut in (0, 1, 3, 5):
            d = fixture(); d["transition"]["seam_review"]["cut_seconds"] = cut
            self.assertTrue(validate(d, "release"))
        for side in ("outgoing_source", "incoming_source"):
            for key, value in (("asset_id", "UNVERIFIED"), ("version", "TBD"), ("duration_seconds", 1)):
                d = fixture(); d["transition"]["seam_review"][side][key] = value
                self.assertTrue(validate(d, "release"))
            d = fixture(); d["transition"]["seam_review"][side]["range"] = dict(start_seconds=4,end_seconds=3)
            self.assertTrue(validate(d, "release"))

    def test_continuous_exception_does_not_waive_approved_voice(self):
        d = fixture(); d["transition"].update(intent="continuous", composition_change="identical", continuous_exception_approved=True)
        self.assertEqual(validate(d, "release"), [])
        for key, value in (("user_heard", False), ("owner_approved", False), ("source_version", "unapproved-take-version")):
            changed = copy.deepcopy(d); changed["voices"][0][key] = value
            self.assertTrue(validate(changed, "release"))
        d["review"]["method"] = "asr"
        self.assertTrue(validate(d, "release"))
