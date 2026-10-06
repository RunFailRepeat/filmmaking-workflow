"""Offline checks of recorded evidence, never a media listener or approval authority."""
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

SCHEMA = Path(__file__).parent / "schemas/continuity.schema.json"
AUDIO_CHECKS = ("voice", "accent", "words", "pronunciation", "delivery", "unclipped_timing", "sync", "other_speakers", "ambience", "sound_effects")
ENHANCEMENT_CHECKS = ("identity", "faces", "artifacts", "detail", "crop", "continuity", "timing", "audio")


def shape(value, spec, path="$", errors=None):
    """Validate the small keyword subset used by our bundled schema, not arbitrary schemas."""
    errors = [] if errors is None else errors
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "number": (int, float)}
    if "type" in spec and not isinstance(value, types[spec["type"]]):
        errors.append(path + ": invalid type")
        return errors
    if spec.get("type") == "number":
        if isinstance(value, bool) or not math.isfinite(value):
            errors.append(path + ": finite number required")
        elif ("minimum" in spec and value < spec["minimum"]) or ("exclusiveMinimum" in spec and value <= spec["exclusiveMinimum"]):
            errors.append(path + ": outside numeric bounds")
    if "enum" in spec and value not in spec["enum"]:
        errors.append(path + ": invalid enum")
    if isinstance(value, str) and "pattern" in spec and not re.search(spec["pattern"], value):
        errors.append(path + ": nonempty text required")
    if isinstance(value, dict):
        for key in spec.get("required", []):
            if key not in value:
                errors.append(path + "." + key + ": missing")
        for key, item in value.items():
            if key in spec.get("properties", {}):
                shape(item, spec["properties"][key], path + "." + key, errors)
            elif spec.get("additionalProperties") is False:
                errors.append(path + "." + key + ": unexpected")
    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0):
            errors.append(path + ": missing entries")
        for i, item in enumerate(value):
            shape(item, spec.get("items", {}), path + "[" + str(i) + "]", errors)
    return errors


def validate(d, stage="preflight"):
    if stage not in ("preflight", "enhancement", "release"):
        return ["unknown stage"]
    errors = shape(d, json.loads(SCHEMA.read_text(encoding="utf-8")))
    if errors:
        return errors

    def require(condition, message):
        if not condition:
            errors.append(message)

    voices = {v["character_id"]: v for v in d["voices"]}
    require(len(voices) == len(d["voices"]), "duplicate character voice")
    ids = [line["line_id"] for line in d["lines"]]
    require(len(set(ids)) == len(ids), "duplicate dialogue line")
    for v in d["voices"]:
        require(v["owner_approved"] and v["user_heard"], "voice requires owner approval of heard take")
        require(v["audition_project_id"] == d["project_id"], "new film requires its own voice audition approval")
    expected = []
    for line in d["lines"]:
        voice = voices.get(line["character_id"])
        require(voice is not None, "line has no approved character voice")
        if voice:
            expected.append({"line_id": line["line_id"], "character_id": line["character_id"],
                             **{k: voice[k] for k in ("provider", "voice_id", "voice_type", "take_id", "source_version", "accent", "pronunciation", "delivery")},
                             "exact_dialogue": line["exact_dialogue"]})
    camera = d["camera"]
    require(camera["approved"] == camera["submitted"] or camera["change_approved"],
            "camera/lens continuity changed without approval")
    transition = d["transition"]
    if transition["sequential"]:
        if transition["intent"] == "continuous":
            require(transition["continuous_exception_approved"], "continuous-shot exception must be explicit and approved")
        else:
            require(transition["composition_change"] == "meaningful", "sequential cut requires intentional new angle or shot size, not a tiny shift")
            if transition["reference_mode"] == "fixed_start_frame":
                alternative = transition["fixed_frame_plan"] == "supported_alternative" and transition["provider_alternative_supported"]
                trimmed = transition["fixed_frame_plan"] == "verified_trim_handles" and transition["trim_handles_verified"]
                require(alternative or trimmed, "fixed start frame needs supported alternative coverage or verified trim handles")
    submission = d["submission"]
    require(submission["actual_payload_reviewed"], "actual shot/reshoot payload not reviewed")
    if submission["route"] == "provider_bindings":
        require(submission["bindings_supported"], "voice binding route unsupported")
        require(submission["ordered_bindings"] == expected, "actual ordered voice/audio bindings mismatch")
    else:
        plan = submission["replacement_plan"]
        require(plan["approved"] and plan["ordered_lines"] == expected,
                "approved direct-edit replacement plan must cover exact voices and lines")
        require(plan["payload_version"] == submission["payload_version"], "replacement plan targets stale payload")
    audio = d["audio"]
    if audio["state"] in ("removed", "changed"):
        require(False, "audio unresolved until approved replacement is installed")
    if audio["state"] == "replaced":
        require(audio["replacement_approved"], "audio replacement not approved")
    if stage == "preflight":
        return errors
    enhancement = d["enhancement"]
    if enhancement["requested"]:
        require(enhancement["picture_edit_approved"] and enhancement["operation_approved"],
                "enhancement requires picture/edit and operation approval")
        require(enhancement["picture_edit_version"] == enhancement["source_version"], "enhancement source differs from approved picture/edit")
        require(not enhancement["paid"] or enhancement["fresh_spend_approved"],
                "paid enhancement requires fresh exact-operation spending approval")
    if stage == "enhancement":
        require(enhancement["requested"], "no enhancement requested")
        return errors
    review = d["review"]
    if transition["sequential"]:
        require(transition["normal_speed_reviewed"] and transition["seam_export_version"] == review["export_version"],
                "actual seam requires normal-speed review on current export")
        require(all(v == "pass" for v in transition["checks"].values()), "pose/action/voice/sound seam checks unresolved or failed")
    require(d["audio"]["export_version"] == review["export_version"], "listening evidence targets stale audio export")
    require(d["release"]["owner_approved"] and d["release"]["export_version"] == review["export_version"],
            "release approval must identify reviewed final export")
    require(review["method"] == "direct_listen" and not review["owner_review_pending"],
            "listening unverified; owner review gate remains open (ASR is not listening)")
    require(review["actual_export_listened"], "actual final export has not been listened to")
    require(review["listener_id"].strip().lower() not in ("unverified", "unknown", "tbd", "pending", "none"),
            "actual listener identity required")
    try:
        listened_at = datetime.fromisoformat(review["listened_at"].replace("Z", "+00:00"))
        require(listened_at.utcoffset() is not None, "listening timestamp must include timezone")
    except ValueError:
        require(False, "valid listening timestamp required")
    require(review["listened_source_id"] == audio["export_asset_id"], "listened source does not identify actual export asset")
    duration = review["duration_seconds"]
    ranges = review["listened_ranges"]
    require(bool(ranges), "actual listened time ranges required")
    covered_until = 0
    for interval in sorted(ranges, key=lambda r: r["start_seconds"]):
        start, end = interval["start_seconds"], interval["end_seconds"]
        require(start < end <= duration, "invalid listened range for export duration")
        require(start <= covered_until, "listening coverage gap in final export")
        covered_until = max(covered_until, end)
    require(covered_until == duration, "listening must cover full export including sound effects and ambience")
    require([r["line_id"] for r in review["lines"]] == ids, "final listening must cover every line in order")
    for line, heard in zip(d["lines"], review["lines"]):
        span = heard["export_range"]
        require(span["start_seconds"] < span["end_seconds"] <= duration, "invalid dialogue range in actual export")
        voice = voices.get(line["character_id"])
        if voice:
            require(heard["character_id"] == line["character_id"] and
                    heard["take_id"] == voice["take_id"] and heard["source_version"] == voice["source_version"],
                    "listened voice reference differs from approved take/version")
            require(heard["heard_accent"] == voice["accent"], "heard accent mismatch")
        require(heard["heard_words"] == line["exact_dialogue"], "heard dialogue mismatch")
        require(all(heard["checks"][k] == "pass" for k in AUDIO_CHECKS), "line listening checks unresolved or failed")
    require(enhancement["original_retained"] and enhancement["editable_retained"], "retain original and editable project")
    if submission["route"] == "direct_edit":
        require(audio["state"] == "replaced" and audio["replacement_approved"], "direct-edit audio replacement not completed and approved")
    if enhancement["requested"]:
        require(enhancement["output_version"] == review["export_version"] and
                enhancement["source_version"] != enhancement["output_version"], "review must target actual enhanced export")
        require(enhancement["actual_export_compared"] and enhancement["comparison_approved"], "enhanced export comparison not approved")
        require(all(enhancement["checks"][k] == "pass" for k in ENHANCEMENT_CHECKS), "enhancement comparison unresolved or failed")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python validate_continuity.py PACKET.json preflight|enhancement|release")
    try:
        errors = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), sys.argv[2])
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
    print("\n".join(errors) if errors else "Recorded gates consistent; no media listened to, approvals authenticated, or execution authorized.")
    raise SystemExit(bool(errors))
