# Validated correction record — 2026-10-07

Baseline remote commit: `57723ae5c76217e0f3335293f33ce6d27bd97d15`. Before editing, all 16 tracked local files matched fetched contents at that immutable commit; the local tree was clean. The existing draft PR remained open and unmerged. Local and remote commit histories differ, so content comparison was used instead of claiming identical local history.

Reproductions start with the invented `fixture()` in `tests/test_continuity.py`. `validate(..., "release")` is used except for the direct-edit preflight case. Empty results mean recorded gates passed, not that media was reviewed.

| Confirmed case | Baseline reproduction/result | Corrected result | Risk and compatibility |
| --- | --- | --- | --- |
| Simultaneous-story edited seam skipped | Set `sequential=false`, `normal_speed_reviewed=false`, all seam checks unverified: returned `[]` | With edited seam present, rejects missing review/checks regardless of story chronology | New required `has_edited_seam` separates edit structure from story time. Existing packets need migration; true standalone clips remain supported. Metadata cannot discover concealed joins. |
| Reversed line starts | Add matching line-02 to lines, bindings and review; line-01 at 2–4 seconds, line-02 at 0–1: returned `[]` | Rejects reversed starts | Declared playback order now requires nondecreasing starts. Equal starts and legitimate overlap still pass; do not sort records to hide an actual dialogue error. |
| Placeholder replacement plan | Select approved direct-edit route, set both timing and instructions to `UNVERIFIED`: preflight returned `[]` | Rejects unresolved plan; tests reject either field independently | Known placeholder-only text now fails. Completed instructions stay human-reviewed; this does not parse or verify edit feasibility. |
| Oversized number crashes | Set `review.duration_seconds=10**400`: uncaught `OverflowError: int too large to convert to float` | Returns a finite-representable-number diagnostic, no exception | Numeric schema and validator reject values above floating-point maximum. Practical durations unchanged; huge Python integers no longer crash the numeric check. |
| Missing seam provenance | Baseline fixture had no seam reviewer/date/source-range object and returned `[]` | Missing/new unresolved provenance, stale export, non-straddling review range and out-of-bounds source ranges fail | New required seam record needs real evidence. The validator cannot authenticate sources, map source frames into the edit or verify playback. |

Continuous-shot consistency: an explicitly approved identical-composition exception still passes with complete synthetic evidence. It never waives the exact approved/user-heard voice recording/take version, binding/replacement or final direct listening requirements; regression tests reject unapproved/unheard/stale takes and ASR in that path.

Regression suite: `python -m unittest discover -s tests -v` — **44 tests passed**. The nine correction tests in `tests/test_corrections.py` cover these cases and valid overlaps, simultaneous starts, standalone clips and continuous exceptions. Numeric error tests also cover huge listened-range and cut values. All positive evidence, reviewers, dates, durations and assets remain synthetic.

Additional checks: `python validate_shot.py examples/fictional-shot.json`; JSON parsing, relative Markdown links, sensitive-string scan and `git diff --check`. The public continuity example remains an unapproved proposal and fails all three gates. No media generation, paid actions, merge, deployment, production-asset change or analytics default was performed. Plugin/playbook changes are outside this correction.
