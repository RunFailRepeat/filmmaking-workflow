"""Normal-speed hard-cut planning checks only; never evidence of media review."""
import json
import math
import sys
from pathlib import Path
from validate_continuity import shape

SCHEMA = Path(__file__).parent / "schemas/plan.schema.json"


def same(a, b):
    return math.isclose(a, b, rel_tol=0, abs_tol=1e-7)


def source_time(clip, export_time):
    """Map normal-speed export seconds to the clip's original source seconds."""
    return clip["source_in"] + export_time - clip["export_start"]


def seam_windows(outgoing, incoming, before, after):
    """Caller validates clips/handles; output is a proposed review window only."""
    cut = outgoing["export_end"]
    return {"export_window": {"start": cut - before, "end": cut + after},
            "outgoing_source_window": {"start": source_time(outgoing, cut - before), "end": outgoing["source_out"]},
            "incoming_source_window": {"start": incoming["source_in"], "end": source_time(incoming, cut + after)}}


def validate(d):
    errors = shape(d, json.loads(SCHEMA.read_text(encoding="utf-8")))
    if errors:
        return errors

    def require(ok, message):
        if not ok:
            errors.append(message)

    duration = d["duration"]
    target = duration["target"]
    require(duration["minimum"] <= target <= duration["maximum"], "target outside user duration window")
    beats = d["beats"]
    require(len({b["id"] for b in beats}) == len(beats), "duplicate beat id")
    for beat in beats:
        require(beat["start"] < beat["end"] <= target, "beat outside user-defined export duration")
    clips = d["clips"]
    by_id = {c["id"]: c for c in clips}
    require(len(by_id) == len(clips), "duplicate clip id")
    endpoint = 0
    for clip in clips:
        require(clip["source_in"] < clip["source_out"] <= clip["source_duration"], "invalid source trim")
        require(clip["export_start"] < clip["export_end"] <= target, "invalid export clip range")
        require(same(clip["source_out"] - clip["source_in"], clip["export_end"] - clip["export_start"]), "source/export duration mismatch (retiming unsupported)")
        require(same(clip["export_start"], endpoint), "hard-cut timeline has gap/overlap or reordered clips")
        endpoint = clip["export_end"]
    require(same(endpoint, target), "edit does not fill user target duration")
    require(len(d["seams"]) == len(clips) - 1, "one planned seam required per adjacent clip pair")
    for seam, outgoing, incoming in zip(d["seams"], clips, clips[1:]):
        require(seam["outgoing"] == outgoing["id"] and seam["incoming"] == incoming["id"], "seam clip order mismatch")
        require(outgoing["end_state"] == incoming["start_state"], "seam state discontinuity (including silent shots)")
        before, after = seam["before"], seam["after"]
        require(before <= outgoing["export_end"] - outgoing["export_start"] and after <= incoming["export_end"] - incoming["export_start"], "seam handles exceed retained clips")
        expected = seam_windows(outgoing, incoming, before, after)
        for key, span in expected.items():
            require(all(same(seam[key][k], span[k]) for k in ("start", "end")), key + " mapping mismatch; include source head trims")
    lines = d["approved_dialogue"]
    ids = [line["id"] for line in lines]
    require(len(set(ids)) == len(ids), "duplicate approved line id")
    require([x["id"] for x in d["dialogue_coverage"]] == ids, "dialogue order/count changed across coverage")
    previous_start = -1
    spoken_clips = set()
    for approved, actual in zip(lines, d["dialogue_coverage"]):
        require(actual["speaker"] == approved["speaker"] and actual["text"] == approved["text"], "exact dialogue or speaker changed")
        require(previous_start <= approved["start"] < approved["end"] <= target, "approved dialogue timing/order invalid")
        previous_start = approved["start"]
        cursor = approved["start"]
        for segment in actual["segments"]:
            clip = by_id.get(segment["clip"])
            if clip is None:
                errors.append("dialogue references missing clip")
                continue
            spoken_clips.add(clip["id"])
            start, end = segment["export_start"], segment["export_end"]
            require(same(start, cursor) and start < end <= approved["end"], "dialogue clipped/duplicated or coverage gap")
            require(clip["export_start"] <= start < end <= clip["export_end"], "dialogue segment outside clip")
            require(same(segment["source_start"], source_time(clip, start)) and same(segment["source_end"], source_time(clip, end)), "dialogue source mapping omits trim or uses wrong coordinates")
            cursor = end
        require(same(cursor, approved["end"]), "dialogue coverage incomplete")
    for clip in clips:
        require((clip["dialogue_mode"] == "spoken") == (clip["id"] in spoken_clips), "silent/spoken clip disagrees with planned dialogue")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python validate_plan.py PLAN.json")
    try:
        errors = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
    print("\n".join(errors) if errors else "Planning metadata consistent; no actual media reviewed or execution authorized.")
    raise SystemExit(bool(errors))
