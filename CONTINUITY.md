# Voice, camera and finishing gates

These are recorded-evidence checks for dialogue shots, not an audio listener, provider adapter, physical camera simulator, or authorization service. Use a private production copy of the [continuity schema](schemas/continuity.schema.json) and [fictional example](examples/fictional-continuity.json). The public example has no real assets or approvals and deliberately fails readiness. Positive tests use invented declarations only.

## Character voice lock

Audition voices for each new film. Do not automatically reuse a previous film's voice or character. For each speaking character, record provider, voice ID, voice type (such as generated take or preset), and the **exact take and immutable source version the user heard and approved**. Also record accent, pronunciation and delivery. Record exact dialogue separately for each uniquely identified line, in playback order. Silence must be deliberately planned; this dialogue-specific schema requires at least one line and is not a silent-film validator.

A preset conversion is a new candidate until the user hears and approves its actual take; matching names or IDs do not establish acoustic identity. A reference image cannot preserve voice. Treat a new take/version, changed accent, delivery or words as a change requiring review, even if visual identity remains correct. Use opaque asset/version IDs in public records; keep actual rights-cleared sources privately accessible to reviewers.

## Shot and reshoot preflight

Inspect the **actual outgoing payload**, not merely a prompt draft. Record its immutable version and supported voice/audio inputs in their actual submission order. `ordered_bindings` is a normalized review record associating each line with provider/ID/type, approved take/version, accent, pronunciation, delivery and exact words. It is not a payload format to send blindly to a provider. Inspect current provider support and bind actual assets/voice controls where supported; a text instruction or still image is not an audio binding.

If the tool cannot bind the approved voice/audio, select `direct_edit`: specify approved source takes for every line, target payload version, timeline ranges, and exact edit instructions (including sync and ambience preservation). The plan may pass preflight before replacement is performed, but release requires the replacement installed, approved and listened to in the actual export. Never assume later editing will work without this explicit plan.

Both `timeline_ranges` and `edit_instructions` must contain the completed plan, not placeholder markers such as `UNVERIFIED`, `TBD`, `pending` or `N/A`. Their approval flag cannot override unresolved text. These remain human-reviewed text fields: the validator rejects known placeholder markers but does not interpret editing instructions or authenticate their feasibility.

Removing or changing audio makes it unresolved. A replacement plan or old approval alone cannot clear it. Record `removed` or `changed` until the actual approved replacement is installed; then mark `replaced` and record replacement approval. Rerun review after any export/audio change.

## Camera and reshoot continuity

Shot cards must state intended lens/focal-length look, framing, focus/depth of field and camera movement, alongside look and aspect ratio. These are **visual intentions, not guarantees of physical model optics**. Match a reshoot to the approved shot or explicitly approve a changed intention, with a recorded reason and affected adjacent shots in the production packet. Compare actual footage for perspective, subject scale, geography, focus and transitions. The validator compares the approved/submitted camera records and rejects unapproved differences; it does not measure lens characteristics in footage. Keep shot-card and continuity-packet camera records synchronized; cross-file linkage is currently manual.

## Sequential clip transitions

Use the prior ending to preserve character positions, poses, ongoing action, prop and environment state. Do not automatically force the next opening to the identical composition. Default to an intentional different camera angle or meaningfully different shot size that cuts cleanly while preserving screen direction, eyelines, the 180-degree axis and action timing. Avoid tiny camera shifts/jump cuts, duplicated action and frozen overlap. An intentional continuous-shot exception must be explicit and approved.

Record the outgoing endpoint state, incoming shot/angle/size and cut plan; add match-on-action and edit handles where useful. Distinguish a reference used for **state continuity** from literal fixed start-frame conditioning. If the provider forces the starting frame, use a verified supported alternative reference mode or coverage approach, or trim verified footage handles. Do not promise arbitrary new angles from a fixed frame. A planned trim is not verified footage.

Before acceptance, review the actual seam at normal speed for pose, action/timing, voice and sound, including repeated action and frozen overlap. Tie this review to the actual export version. The recorded checks cannot detect a jump cut themselves. `sequential` describes connected sequential story action; `has_edited_seam` independently records whether clips meet in the edit. Simultaneous-story coverage can have `sequential: false` and still requires `has_edited_seam: true` with all seam gates. Only genuinely standalone footage without an edited join may use both false. Connected sequential clips cannot claim no seam. A false declaration cannot be detected automatically from metadata.

For each represented join, `seam_review` records the reviewer and timezone-qualified timestamp; exact final export asset/version; a review range that straddles `cut_seconds`; and both outgoing/incoming source asset IDs, immutable versions, source durations and reviewed source ranges. Export ranges use final-export seconds; source ranges use each source's own seconds. Review endpoints must be in bounds. Missing, placeholder or stale provenance blocks release even when every check says pass. This packet represents one join; repeat records for other joins outside this single-shot schema. Cross-packet completeness and source-to-timeline mapping still require manual review.

An approved continuous-shot exception changes the camera-composition requirement only. It does not waive the approved, user-heard voice recording/take and source version, actual payload binding/replacement requirements, or full actual-export listening. No new voice recording is approved by this exception.

Record actual-output `pass` / `fail` / `unverified` results for `incoming_angle_shot_size`, `axis_180`, `screen_direction`, `eyelines`, `props_environment` and `sound_effects`, in addition to pose/action/voice/sound/timing checks. Planned text does not satisfy these checks. Missing, failed or unverified results block release. For an approved continuous-shot exception, `incoming_angle_shot_size: pass` means the actual seam matches that approved continuous composition, not that a new angle was forced; all other continuity checks still apply.

## Listen to the final actual export

Listen at normal speed to **every line** against the approved voice take/version. Check voice identity **and accent**, exact words/pronunciation/delivery, unclipped starts/ends and pauses, sync, unintended speakers and ambience. Log each line's result for the exact final export version. For overlapping dialogue, use separate line records and inspect the overlap, not just isolated stems. Review picture at normal speed too; this audio gate does not replace full visual QA.

Also check sound-effect preservation explicitly using each line's `sound_effects` result; ambience alone is insufficient. Record the actual listener's stable ID (`listener_id`), timezone-qualified ISO timestamp (`listened_at`), and exact listened asset (`listened_source_id`, matching `audio.export_asset_id`). The existing `export_version` identifies the version. Record actual export `duration_seconds`, the listener's `listened_ranges`, and each line's `export_range`, all in seconds relative to that same export. Numeric ranges must be finite, nonnegative, ordered and within the export; the union of listened ranges must cover the full export, including gaps between dialogue with effects/ambience. Multiple adjacent or overlapping listening sessions are allowed. Line ranges may overlap for overlapping speakers. Do not substitute the original take's timestamps for final-export timestamps.

Declared playback line order must have nondecreasing actual start times. Overlapping lines and equal starts are allowed; line IDs matching does not excuse reversed starts. Numeric metadata outside the supported finite floating-point range is rejected with a diagnostic rather than an exception; the schema declares the same upper bound.

Until someone actually listens, leave listener/date as `UNVERIFIED` and listened ranges empty; keep the owner gate open. The validator rejects missing provenance, placeholder listeners, invalid/timezone-free dates, stale asset IDs, invalid ranges and coverage gaps at release. It does not verify listener identity, timestamp truth, declared duration, actual sound effects or whether playback occurred. Fixtures' listener IDs, dates and ranges are synthetic declarations only.

ASR/transcripts do not establish listening, voice identity, accent or synchronization. If direct listening is unavailable, record `unavailable`, leave checks `unverified`, and keep `owner_review_pending: true`. The owner or another authorized listener must actually listen and supply the missing evidence; an approval flag cannot turn ASR into listening. Never describe metadata validation as an actual listen. Any new export invalidates prior listening until reviewed against its own version.

## Enhancement and release

Approve picture/edit first. Record the exact approved source version, proposed grading, sharpening and upscale settings (explicitly `none` for unused operations), and operation approval. A paid operation requires a fresh exact-settings quote and spending approval; earlier generation approval is insufficient. `enhancement` checks planning records only and do not authorize execution.

Compare the **actual enhanced export** against the approved source for identity, faces, artifacts, real detail versus invented texture, crop, continuity, timing and audio. Record both source and output versions and each comparison result. Listen to the enhanced export again; a source review does not transfer automatically. Failed or unverified comparisons block release readiness. Retain the original and editable project; enhancement cannot repair a missing event or establish identity fidelity.

Release additionally requires actual-export owner approval and the separate workflow's rights, destination and publication approvals. A passing `release` invocation is only internal consistency of these recorded gates, never permission to publish.

## Commands and limitations

```sh
python validate_continuity.py examples/fictional-continuity.json preflight
python validate_continuity.py examples/fictional-continuity.json enhancement
python validate_continuity.py examples/fictional-continuity.json release
```

All three intentionally fail on the unapproved example. Run `python -m unittest discover -s tests -v` for invented passing and failing cases. `validate_continuity.py` validates only the type/enum/pattern/object/array/numeric-bound keyword subset used in its bundled JSON schema, plus cross-record gates. It does not implement a general JSON Schema engine. The older `check_packet.py` remains a basic field/marker checker, not this continuity or release validator.

Not implemented: provider payload extraction, cryptographic hashes or signed approvals, asset retrieval, automatic auditioning, waveform/ASR analysis, media playback, lip-sync or accent detection, footage comparison, cross-file camera matching, billing enforcement or publishing. Humans must truthfully record actual review, approval provenance and supported provider bindings. A fabricated record can pass; boolean approval fields cannot authenticate a person or a take.

Compatibility: packets made before the seam correction need `has_edited_seam` and `seam_review` fields. Populate them from real review evidence, never by copying the synthetic example as proof. Earlier packets with reversed line timing or unresolved direct-edit plans now fail intentionally. No production media, camera defaults, installed plugin or playbook is changed by this validator correction.

The new fields are structurally required at every stage, including preflight and standalone packets. Before review, or for a genuine no-seam standalone packet, retain explicit `UNVERIFIED` provenance placeholders and structurally valid proposed ranges; do not invent completed evidence. Seam provenance must be completed to pass release when `has_edited_seam` is true. Known placeholder-only tokens are rejected where completed evidence is required; arbitrary unresolved prose is not semantically analyzed.
