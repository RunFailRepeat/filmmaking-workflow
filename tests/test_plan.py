import copy
import json
import unittest
from pathlib import Path
from validate_plan import validate, seam_windows


def fixture():
    return json.loads(Path("examples/fictional-plan.json").read_text())


class PlanningChecks(unittest.TestCase):
    def test_fictional_plan_is_not_review_evidence(self):
        self.assertEqual(validate(fixture()), [])
        d = fixture(); d["evidence_kind"] = "media_review_passed"
        self.assertTrue(validate(d))

    def test_user_durations_below_and_above_legacy_range(self):
        def scale(v):
            if isinstance(v, dict): return {k: scale(x) for k, x in v.items()}
            if isinstance(v, list): return [scale(x) for x in v]
            return v * 10 if isinstance(v, (int, float)) else v
        self.assertEqual(validate(fixture()), [])  # Eight seconds, not a fixed minimum.
        self.assertEqual(validate(scale(fixture())), [])  # Eighty seconds, not a fixed maximum.

    def test_user_window_and_beats(self):
        d = fixture(); d["duration"]["maximum"] = 7
        self.assertTrue(validate(d))
        d = fixture(); d["beats"][0]["end"] = 9
        self.assertTrue(validate(d))

    def test_zero_and_nonzero_head_trim_mapping(self):
        d = fixture(); a, b, c = d["clips"]
        self.assertEqual(seam_windows(a, b, 1, 1)["incoming_source_window"], {"start": 3, "end": 4})
        self.assertEqual(seam_windows(b, c, 1, 1)["outgoing_source_window"], {"start": 4, "end": 5})
        self.assertEqual(seam_windows(a, b, 1, 1)["outgoing_source_window"], {"start": 3, "end": 4})
        d["seams"][0]["incoming_source_window"] = {"start": 0, "end": 1}
        self.assertTrue(validate(d))

    def test_source_and_export_coordinates_not_interchangeable(self):
        d = fixture(); d["seams"][1]["outgoing_source_window"] = dict(d["seams"][1]["export_window"])
        self.assertTrue(validate(d))
        d = fixture(); d["dialogue_coverage"][0]["segments"][1]["source_start"] = 0
        self.assertTrue(validate(d))

    def test_invalid_trim_handle_and_retime(self):
        for mutation in (lambda d: d["clips"][1].update(source_out=10),
                         lambda d: d["clips"][1].update(source_in=2),
                         lambda d: d["seams"][0].update(after=3)):
            d = fixture(); mutation(d); self.assertTrue(validate(d))

    def test_dialogue_text_speaker_count_order(self):
        for key in ("text", "speaker", "id"):
            d = fixture(); d["dialogue_coverage"][0][key] = "changed"
            self.assertTrue(validate(d))
        d = fixture(); d["dialogue_coverage"] *= 2
        self.assertTrue(validate(d))
        d = fixture(); d["dialogue_coverage"] = []
        self.assertTrue(validate(d))

    def test_cross_cut_line_cannot_repeat_or_lose_words_timing(self):
        for mutation in (lambda d: d["dialogue_coverage"][0]["segments"].reverse(),
                         lambda d: d["dialogue_coverage"][0]["segments"].pop(),
                         lambda d: d["dialogue_coverage"][0]["segments"].append(copy.deepcopy(d["dialogue_coverage"][0]["segments"][0]))):
            d = fixture(); mutation(d); self.assertTrue(validate(d))

    def test_overlapping_dialogue_allowed_but_reordered_lines_fail(self):
        d = fixture()
        d["approved_dialogue"].append(dict(d["approved_dialogue"][0], id="line-02", speaker="fictional-other"))
        second = copy.deepcopy(d["dialogue_coverage"][0]); second.update(id="line-02", speaker="fictional-other")
        d["dialogue_coverage"].append(second)
        self.assertEqual(validate(d), [])
        d["dialogue_coverage"].reverse()
        self.assertTrue(validate(d))

    def test_silent_plan_still_checks_state_and_seams(self):
        d = fixture(); d["approved_dialogue"] = []; d["dialogue_coverage"] = []
        for clip in d["clips"]: clip["dialogue_mode"] = "silent"
        self.assertEqual(validate(d), [])
        d["clips"][1]["start_state"] = "cup-in-wrong-place"
        self.assertTrue(validate(d))
        d = fixture(); d["clips"][0]["dialogue_mode"] = "silent"
        self.assertTrue(validate(d))

    def test_every_seam_required(self):
        d = fixture(); d["seams"].pop()
        self.assertTrue(validate(d))
        d = fixture(); d["seams"].reverse()
        self.assertTrue(validate(d))

    def test_numeric_and_structure_errors_do_not_crash(self):
        for value in (None, [], "plan"):
            self.assertTrue(validate(value))
        for value in (True, float("nan"), float("inf"), 10**400, -1):
            d = fixture(); d["duration"]["target"] = value
            self.assertTrue(validate(d))
