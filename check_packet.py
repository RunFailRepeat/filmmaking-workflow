"""Check a plain-text production packet. No network, writes, installs or execution."""
import re
import sys
from pathlib import Path

FIELDS = ("project_id objective obstacle ending edit_duration_seconds delivery_format "
          "reference_ids shot_id source_duration_seconds usable_range start_state "
          "action end_state screen_direction exact_dialogue ordered_reference_ids "
          "model_and_mode settings_version acceptance_checks").split()
APPROVALS = ("rights_review", "story_approval", "prompt_approval", "execution_approval")
UNRESOLVED = {"", "tbd", "pending", "unknown", "not granted"}

def check(text):
    values = {}
    errors = []
    for line in text.splitlines():
        match = re.fullmatch(r"([a-z_]+):\s*(.*)", line)
        if match:
            key, value = match.groups()
            if key in values:
                errors.append("duplicate field: " + key)
            values[key] = value.strip()
    for key in FIELDS:
        if values.get(key, "").lower() in UNRESOLVED:
            errors.append("unresolved field: " + key)
    for key in APPROVALS:
        if values.get(key) != "APPROVED":
            errors.append("approval not recorded: " + key)
    for key in ("edit_duration_seconds", "source_duration_seconds"):
        try:
            n = float(values.get(key, ""))
            if not 0 < n < float("inf"):
                raise ValueError
        except ValueError:
            errors.append("invalid positive duration: " + key)
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python check_packet.py PACKET.md")
    problems = check(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print("\n".join(problems) if problems else "Field checks passed; human review still required.")
    raise SystemExit(bool(problems))
