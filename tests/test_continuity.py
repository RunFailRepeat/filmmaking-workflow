"""Synthetic declarations only: no actual voice, footage, or approvals exist."""
import copy
import json
import unittest
from pathlib import Path
from validate_continuity import validate, shape, SCHEMA


def fixture():
    d = json.loads(Path("examples/fictional-continuity.json").read_text())
    d["voices"][0].update(owner_approved=True, user_heard=True)
    d["submission"]["actual_payload_reviewed"] = True
    d["review"].update(method="direct_listen", actual_export_listened=True, owner_review_pending=False)
    d["review"].update(listener_id="synthetic-reviewer", listened_at="2026-10-06T20:00:00Z",
                        listened_ranges=[{"start_seconds": 0, "end_seconds": 4}])
    heard = d["review"]["lines"][0]
    heard.update(heard_accent=d["voices"][0]["accent"], heard_words=d["lines"][0]["exact_dialogue"])
    heard["checks"] = dict.fromkeys(heard["checks"], "pass")
    d["enhancement"].update(original_retained=True, editable_retained=True)
    d["release"]["owner_approved"] = True
    d["transition"]["normal_speed_reviewed"] = True
    d["transition"]["checks"] = dict.fromkeys(d["transition"]["checks"], "pass")
    return d


class ContinuityChecks(unittest.TestCase):
    def test_example_is_valid_shape_but_not_approved(self):
        d = json.loads(Path("examples/fictional-continuity.json").read_text())
        self.assertEqual(shape(d, json.loads(SCHEMA.read_text())), [])
        self.assertTrue(validate(d))
        self.assertTrue(validate(d, "release"))

    def test_consistent_synthetic_record(self):
        self.assertEqual(validate(fixture(), "preflight"), [])
        self.assertEqual(validate(fixture(), "release"), [])

    def test_missing_voice_or_audio_data(self):
        for key in ("voices", "audio", "submission"):
            d = fixture(); del d[key]
            self.assertTrue(validate(d))

    def test_exact_heard_take_and_new_film(self):
        for key, value in (("user_heard", False), ("owner_approved", False),
                           ("take_id", "different-take"), ("source_version", "different-version"),
                           ("voice_type", "converted-preset"), ("audition_project_id", "previous-film")):
            d = fixture(); d["voices"][0][key] = value
            self.assertTrue(validate(d), key)

    def test_ordered_bindings_and_dialogue(self):
        d = fixture(); d["lines"].append(dict(d["lines"][0], line_id="line-02"))
        d["submission"]["ordered_bindings"].append(dict(d["submission"]["ordered_bindings"][0], line_id="line-02"))
        self.assertEqual(validate(d), [])
        d["submission"]["ordered_bindings"].reverse()
        self.assertTrue(validate(d))
        d = fixture(); d["submission"]["ordered_bindings"][0]["exact_dialogue"] = "Changed words."
        self.assertTrue(validate(d))

    def test_missing_payload_or_unsupported_binding(self):
        for key in ("actual_payload_reviewed", "bindings_supported"):
            d = fixture(); d["submission"][key] = False
            self.assertTrue(validate(d))
        d = fixture(); d["submission"]["ordered_bindings"] = []
        self.assertTrue(validate(d))

    def test_direct_edit_plan_and_completed_replacement(self):
        d = fixture(); s = d["submission"]
        s.update(route="direct_edit", bindings_supported=False, ordered_bindings=[])
        self.assertTrue(validate(d))
        s["replacement_plan"]["approved"] = True
        self.assertEqual(validate(d), [])
        self.assertTrue(validate(d, "release"))
        d["audio"].update(state="replaced", replacement_approved=True)
        self.assertEqual(validate(d, "release"), [])
        s["replacement_plan"]["payload_version"] = "stale"
        self.assertTrue(validate(d))

    def test_removed_changed_or_unapproved_replacement(self):
        for state in ("removed", "changed", "replaced"):
            d = fixture(); d["audio"]["state"] = state
            self.assertTrue(validate(d), state)

    def test_camera_change_requires_explicit_approval(self):
        for key in fixture()["camera"]["submitted"]:
            d = fixture(); d["camera"]["submitted"][key] = "different visual intent"
            self.assertTrue(validate(d), key)
            d["camera"]["change_approved"] = True
            self.assertEqual(validate(d), [])

    def test_accent_words_and_voice_reference(self):
        for key in ("heard_accent", "heard_words", "take_id", "source_version", "character_id"):
            d = fixture(); d["review"]["lines"][0][key] = "mismatch"
            self.assertTrue(validate(d, "release"), key)

    def test_asr_or_unavailable_is_never_listening(self):
        for method in ("asr", "unavailable"):
            d = fixture(); d["review"]["method"] = method
            self.assertTrue(validate(d, "release"))
        for key, value in (("actual_export_listened", False), ("owner_review_pending", True)):
            d = fixture(); d["review"][key] = value
            self.assertTrue(validate(d, "release"))

    def test_every_line_and_every_audio_check(self):
        d = fixture(); d["review"]["lines"] = []
        self.assertTrue(validate(d, "release"))
        for key in fixture()["review"]["lines"][0]["checks"]:
            for status in ("fail", "unverified"):
                d = fixture(); d["review"]["lines"][0]["checks"][key] = status
                self.assertTrue(validate(d, "release"), key)

    def test_stale_export_listening_and_release_approval(self):
        d = fixture(); d["audio"]["export_version"] = "new-export"
        self.assertTrue(validate(d, "release"))
        d = fixture(); d["release"]["export_version"] = "old-export"
        self.assertTrue(validate(d, "release"))
        d = fixture(); d["release"]["owner_approved"] = False
        self.assertTrue(validate(d, "release"))

    def test_enhancement_planning_and_paid_approval(self):
        d = fixture(); e = d["enhancement"]; e["requested"] = True
        self.assertTrue(validate(d, "enhancement"))
        e.update(picture_edit_approved=True, operation_approved=True)
        self.assertEqual(validate(d, "enhancement"), [])
        e["paid"] = True
        self.assertTrue(validate(d, "enhancement"))
        e["fresh_spend_approved"] = True
        self.assertEqual(validate(d, "enhancement"), [])
        e["source_version"] = "unapproved-edit"
        self.assertTrue(validate(d, "enhancement"))

    def test_enhanced_export_requires_new_actual_review(self):
        d = fixture(); e = d["enhancement"]
        e.update(requested=True, picture_edit_approved=True, operation_approved=True,
                 actual_export_compared=True, comparison_approved=True)
        e["checks"] = dict.fromkeys(e["checks"], "pass")
        self.assertTrue(validate(d, "release"))
        for key in ("audio", "review", "release"):
            d[key]["export_version"] = e["output_version"]
        d["transition"]["seam_export_version"] = e["output_version"]
        self.assertEqual(validate(d, "release"), [])
        for key in e["checks"]:
            changed = copy.deepcopy(d); changed["enhancement"]["checks"][key] = "unverified"
            self.assertTrue(validate(changed, "release"), key)
        for key in ("actual_export_compared", "comparison_approved", "original_retained", "editable_retained"):
            changed = copy.deepcopy(d); changed["enhancement"][key] = False
            self.assertTrue(validate(changed, "release"), key)

    def test_malformed_input_fails_without_truthy_approvals(self):
        for value in (None, [], "approved"):
            self.assertTrue(validate(value))
        d = fixture(); d["voices"][0]["owner_approved"] = "true"
        self.assertTrue(validate(d))
        d = fixture(); d["voices"][0]["take_id"] = "   "
        self.assertTrue(validate(d))

    def test_transition_defaults_to_distinct_coverage(self):
        for composition in ("tiny", "identical"):
            d = fixture(); d["transition"]["composition_change"] = composition
            self.assertTrue(validate(d))
        d["transition"].update(intent="continuous", continuous_exception_approved=True)
        self.assertEqual(validate(d), [])
        d["transition"]["continuous_exception_approved"] = False
        self.assertTrue(validate(d))

    def test_fixed_frame_is_not_arbitrary_angle_control(self):
        d = fixture(); t = d["transition"]; t["reference_mode"] = "fixed_start_frame"
        self.assertTrue(validate(d))
        t.update(fixed_frame_plan="supported_alternative", provider_alternative_supported=True)
        self.assertEqual(validate(d), [])
        t.update(fixed_frame_plan="verified_trim_handles", provider_alternative_supported=False)
        self.assertTrue(validate(d))
        t["trim_handles_verified"] = True
        self.assertEqual(validate(d), [])

    def test_actual_seam_review_and_no_repeated_or_frozen_action(self):
        for key in fixture()["transition"]["checks"]:
            d = fixture(); d["transition"]["checks"][key] = "unverified"
            self.assertTrue(validate(d, "release"), key)
        d = fixture(); d["transition"]["normal_speed_reviewed"] = False
        self.assertTrue(validate(d, "release"))
        d = fixture(); d["transition"]["seam_export_version"] = "stale"
        self.assertTrue(validate(d, "release"))

    def test_actual_spatial_seam_checks_required(self):
        for key in ("incoming_angle_shot_size", "axis_180", "screen_direction", "eyelines", "props_environment", "sound_effects"):
            for value in ("fail", "unverified", None):
                d = fixture()
                if value is None:
                    del d["transition"]["checks"][key]
                else:
                    d["transition"]["checks"][key] = value
                self.assertTrue(validate(d, "release"), (key, value))

    def test_continuous_exception_still_requires_actual_seam_review(self):
        d = fixture(); t = d["transition"]
        t.update(intent="continuous", composition_change="identical", continuous_exception_approved=True)
        self.assertEqual(validate(d, "release"), [])
        t["checks"]["incoming_angle_shot_size"] = "unverified"
        self.assertTrue(validate(d, "release"))

    def test_listener_source_and_timestamp_provenance(self):
        for key, value in (("listener_id", "UNVERIFIED"), ("listener_id", "  "),
                           ("listened_at", "not-a-date"), ("listened_at", "2026-10-06T20:00:00"),
                           ("listened_source_id", "old-export-asset")):
            d = fixture(); d["review"][key] = value
            self.assertTrue(validate(d, "release"), (key, value))
        for key in ("listener_id", "listened_at", "listened_source_id", "listened_ranges", "duration_seconds"):
            d = fixture(); del d["review"][key]
            self.assertTrue(validate(d, "release"), key)

    def test_listened_ranges_cover_actual_export(self):
        d = fixture()
        d["review"]["listened_ranges"] = [{"start_seconds": 0, "end_seconds": 2}, {"start_seconds": 2, "end_seconds": 4}]
        self.assertEqual(validate(d, "release"), [])
        for ranges in ([], [(2, 4)], [(0, 2), (3, 4)], [(0, 5)], [(2, 1)], [(0, 0)],
                       [(-1, 4)], [(False, 4)], [(0, float("inf"))], [(0, float("nan"))]):
            d = fixture(); d["review"]["listened_ranges"] = [{"start_seconds": a, "end_seconds": b} for a, b in ranges]
            self.assertTrue(validate(d, "release"), ranges)

    def test_dialogue_ranges_and_export_duration(self):
        for span in ({"start_seconds": 2, "end_seconds": 5}, {"start_seconds": 3, "end_seconds": 2}):
            d = fixture(); d["review"]["lines"][0]["export_range"] = span
            self.assertTrue(validate(d, "release"))
        d = fixture(); del d["review"]["lines"][0]["export_range"]
        self.assertTrue(validate(d, "release"))
        for duration in (0, -1, True, float("nan"), float("inf")):
            d = fixture(); d["review"]["duration_seconds"] = duration
            self.assertTrue(validate(d, "release"), duration)

    def test_sound_effects_are_distinct_from_ambience(self):
        for value in ("fail", "unverified", None):
            d = fixture()
            if value is None:
                del d["review"]["lines"][0]["checks"]["sound_effects"]
            else:
                d["review"]["lines"][0]["checks"]["sound_effects"] = value
            self.assertEqual(d["review"]["lines"][0]["checks"]["ambience"], "pass")
            self.assertTrue(validate(d, "release"))
