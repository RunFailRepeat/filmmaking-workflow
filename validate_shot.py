"""Validate reusable shot metadata only; no generation or external calls."""
import json
import math
import sys
from pathlib import Path

TEXT = ("shot_id purpose camera lens look aspect_ratio dialogue delivery "
        "start_state action end_state eyelines prop_state reference_ids payload_version "
        "framing focus_depth_of_field movement reshoot_continuity "
        "outgoing_endpoint_state incoming_angle_size cut_plan match_action_edit_handles").split()
def validate(d):
    if not isinstance(d, dict):
        return ["shot must be an object"]
    errors = [k + " must be nonempty text" for k in TEXT
              if not isinstance(d.get(k), str) or not d[k].strip()]
    for k in ("source_seconds", "edit_seconds"):
        v = d.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
            errors.append(k + " must be finite and positive")
    if not errors and d["edit_seconds"] > d["source_seconds"]:
        errors.append("edit_seconds exceeds source_seconds")
    for k, allowed in {"review_coverage": ["none", "sampled_frames", "full_motion", "full_motion_and_audio"],
                       "status": ["proposal", "approved", "generated", "reviewed"]}.items():
        if d.get(k) not in allowed: errors.append(k + " invalid")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("Usage: python validate_shot.py SHOT.json")
    errors = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print("\n".join(errors) if errors else "Metadata valid; approvals and visual quality not verified.")
    raise SystemExit(bool(errors))
