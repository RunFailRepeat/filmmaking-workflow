# Duration, coverage and coordinate contracts

Use the user's current duration target and allowed window. There is no fixed episode-length range. Record beat windows in export seconds within that target; overlapping beats may be intentional and do not add to runtime. The [planning schema](schemas/plan.schema.json), [fictional plan](examples/fictional-plan.json) and [validator](validate_plan.py) check a bounded, normal-speed hard-cut timeline. They do not plan a film automatically or authorize production.

## Coordinates and trims

Every clip records immutable source ID/version, original source duration, retained `source_in` and `source_out`, and final `export_start` and `export_end`. Seconds are measured from the original source or final export origin respectively. `source_in` is the head trim, including zero. Source and export durations must match for this normal-speed contract. Clips partition the target export without gaps or overlaps; retiming, dissolves, freeze frames and layered picture tracks require a separately reviewed mapping and are not supported here.

For a time inside a retained clip:

```text
source_time = source_in + (export_time - export_start)
```

At a cut with requested before/after handles, the planned outgoing source window ends at `source_out`; the incoming source window starts at `source_in`, not zero unless the head trim is zero. Bound both handles by the retained clips. Store the export review window and both source windows separately, with their source versions. The validator checks every adjacent join, independent of sequential versus simultaneous story time. Numeric equality uses a 0.0000001-second tolerance; it is not frame quantization or a guarantee of media precision.

The fictional example includes zero and nonzero head trims, a line spanning a cut, and a silent reaction. These are invented planning values, not reviewed footage. `seam_windows` derives proposed ranges from already-validated clips/handles; it does not inspect a file or establish a clean seam.

## Preserve dialogue across coverage cuts

Keep the exact approved dialogue ledger separate from coverage: unique line ID, speaker, exact text, approved export start/end and playback order. The planned coverage must preserve that sequence, speaker and text exactly. A line can span multiple clips through contiguous segments; record each segment's export range and trim-aware source range. Do not repeat the line for each camera angle or omit part of its timing. Equal starts and overlapping speakers are allowed; each line's own segments must fully cover its approved window without gaps or duplication.

This checks declarations, not actual words in audio. Actual export listening against approved voice recordings, unclipped timing, speaker identity and sound checks remain mandatory. Do not infer acoustic preservation from matching text.

## Silent shots and evidence

Use `dialogue_mode: silent` with no dialogue segments on a silent clip; an entirely silent plan can have empty dialogue ledgers. Silent means no spoken dialogue, not necessarily no ambience, effects or music. Still record start/end state IDs and every seam. Adjacent state IDs must match the expected continuity handoff; resolve deliberate time jumps or state changes in a reviewed plan rather than silently dropping checks. Store detailed poses, props, geography and sound intent in the private shot cards referenced by those state IDs.

The planning validator accepts only `evidence_kind: planning_only`. A passing plan is not generated footage, visual QA, listening, an approval or release readiness. Derived windows are proposed review coverage, not proof somebody watched them. After real media exists, record actual asset versions, reviewer/listener, timestamps, observed ranges and findings separately. The existing `validate_continuity.py` remains dialogue-specific; do not invent spoken lines to force silent footage through it. Full silent-export visual/sound acceptance remains a human review process, not an automated release validator in this repository.

## Work-cycle alignment

Before work, inspect the current repo branch/head, installed plugin version/release, relevant guidance and private project brief. Compare them to the last [work-cycle record](templates/work-cycle.md); report stale or unavailable sources rather than assuming synchronization. Read current instructions before reusing a legacy helper's assumptions.

After a reusable correction: reproduce the defect, isolate generic guidance/code from private project context, preserve original evidence and version history, update the authorized repo and plugin surfaces, and test both. Repo code needs focused regressions and the full suite; a skills-only plugin needs package/link validation plus the same fictional scenarios checked against its guidance. Use code tests too if its package actually includes code. Compare the final wording and scope across surfaces.

Record the tested repo base/result commits, plugin before/after version and release, commands/results, review limitations and unresolved drift. A pending plugin update means alignment is pending, not completed; retain that handoff until the guarded update and readback succeed. Preserve project-specific scripts, assets, decisions and approvals in private project files, not generic public examples. Each work cycle is explicit work, not a new schedule or background updater. No merge, deployment, spend or access change is implied.
