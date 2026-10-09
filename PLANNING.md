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

Before work, establish the owner's currently selected source scope. Inspect the current repo branch/head, relevant repository guidance and private project brief. Compare them to the last [work-cycle record](templates/work-cycle.md); report stale or unavailable in-scope sources. Read current instructions before reusing a legacy helper's assumptions. If the owner selects repository-only operation, do not load, update or synchronize an excluded plugin. Historical plugin handoffs do not override the current scope or block repository work.

After a reusable correction: reproduce the defect, isolate generic guidance/code from private project context, preserve original evidence and version history, update the authorized repository files, and test the changes. Repo code needs focused regressions and the full suite; documentation corrections need relevant consistency/link checks and applicable existing tests. Record tested base/result commits, commands/results, review limitations and unresolved in-scope issues. Repository-only work can be marked complete after those checks and remote readback; no plugin certification is implied or required.

Only when the owner also authorizes additional surfaces, inspect their current versions and include them in the work-cycle scope. For a plugin, record before/after version and release, validate package/links and the same fictional scenarios against its guidance, and run code tests if its package includes code. Compare final wording and scope across the authorized surfaces. A pending authorized plugin update means multi-surface alignment is pending; report that separately from completed repository work. An excluded plugin is OUT OF SCOPE, not a pending dependency. If later reauthorized, inspect its then-current state before reconciling it.

For example, an owner selects the repository as the sole workflow source. Inspect its current commit, correct and test a generic rule, verify remote bytes and record completion; mark plugin fields OUT OF SCOPE without accessing the plugin. Preserve earlier multi-surface records as history rather than treating them as current instructions.

Preserve project-specific scripts, assets, decisions and approvals in private project files, not generic public examples. Each work cycle is explicit work, not a new schedule or background updater. No merge, deployment, spend or access change is implied.
