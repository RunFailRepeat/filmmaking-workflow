# Voice, camera and finishing gates

These are recorded-evidence checks for dialogue shots, not an audio listener, provider adapter, physical camera simulator, or authorization service. Use a private production copy of the [continuity schema](schemas/continuity.schema.json) and [fictional example](examples/fictional-continuity.json). The public example has no real assets or approvals and deliberately fails readiness. Positive tests use invented declarations only.

## Character voice lock

Audition voices for each new film. Do not automatically reuse a previous film's voice or character. For each speaking character, record provider, voice ID, voice type (such as generated take or preset), and the **exact take and immutable source version the user heard and approved**. Also record accent, pronunciation and delivery. Record exact dialogue separately for each uniquely identified line, in playback order. Silence must be deliberately planned; this dialogue-specific schema requires at least one line and is not a silent-film validator.

A preset conversion is a new candidate until the user hears and approves its actual take; matching names or IDs do not establish acoustic identity. A reference image cannot preserve voice. Treat a new take/version, changed accent, delivery or words as a change requiring review, even if visual identity remains correct. Use opaque asset/version IDs in public records; keep actual rights-cleared sources privately accessible to reviewers.

## Shot and reshoot preflight

Inspect the **actual outgoing payload**, not merely a prompt draft. Record its immutable version and supported voice/audio inputs in their actual submission order. `ordered_bindings` is a normalized review record associating each line with provider/ID/type, approved take/version, accent, pronunciation, delivery and exact words. It is not a payload format to send blindly to a provider. Inspect current provider support and bind actual assets/voice controls where supported; a text instruction or still image is not an audio binding.

If the tool cannot bind the approved voice/audio, select `direct_edit`: specify approved source takes for every line, target payload version, timeline ranges, and exact edit instructions (including sync and ambience preservation). The plan may pass preflight before replacement is performed, but release requires the replacement installed, approved and listened to in the actual export. Never assume later editing will work without this explicit plan.

Removing or changing audio makes it unresolved. A replacement plan or old approval alone cannot clear it. Record `removed` or `changed` until the actual approved replacement is installed; then mark `replaced` and record replacement approval. Rerun review after any export/audio change.

## Camera and reshoot continuity

Shot cards must state intended lens/focal-length look, framing, focus/depth of field and camera movement, alongside look and aspect ratio. These are **visual intentions, not guarantees of physical model optics**. Match a reshoot to the approved shot or explicitly approve a changed intention, with a recorded reason and affected adjacent shots in the production packet. Compare actual footage for perspective, subject scale, geography, focus and transitions. The validator compares the approved/submitted camera records and rejects unapproved differences; it does not measure lens characteristics in footage. Keep shot-card and continuity-packet camera records synchronized; cross-file linkage is currently manual.

## Sequential clip transitions

Use the prior ending to preserve character positions, poses, ongoing action, prop and environment state. Do not automatically force the next opening to the identical composition. Default to an intentional different camera angle or meaningfully different shot size that cuts cleanly while preserving screen direction, eyelines, the 180-degree axis and action timing. Avoid tiny camera shifts/jump cuts, duplicated action and frozen overlap. An intentional continuous-shot exception must be explicit and approved.

Record the outgoing endpoint state, incoming shot/angle/size and cut plan; add match-on-action and edit handles where useful. Distinguish a reference used for **state continuity** from literal fixed start-frame conditioning. If the provider forces the starting frame, use a verified supported alternative reference mode or coverage approach, or trim verified footage handles. Do not promise arbitrary new angles from a fixed frame. A planned trim is not verified footage.

Before acceptance, review the actual seam at normal speed for pose, action/timing, voice and sound, including repeated action and frozen overlap. Tie this review to the actual export version. The recorded checks cannot detect a jump cut themselves. For nonsequential standalone footage, record `sequential: false` truthfully; it is not an escape from review when a seam exists.

## Listen to the final actual export

Listen at normal speed to **every line** against the approved voice take/version. Check voice identity **and accent**, exact words/pronunciation/delivery, unclipped starts/ends and pauses, sync, unintended speakers and ambience. Log each line's result for the exact final export version. For overlapping dialogue, use separate line records and inspect the overlap, not just isolated stems. Review picture at normal speed too; this audio gate does not replace full visual QA.

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

All three intentionally fail on the unapproved example. Run `python -m unittest discover -s tests -v` for invented passing and failing cases. `validate_continuity.py` validates only the type/enum/pattern/object/array keyword subset used in its bundled JSON schema, plus cross-record gates. It does not implement a general JSON Schema engine. The older `check_packet.py` remains a basic field/marker checker, not this continuity or release validator.

Not implemented: provider payload extraction, cryptographic hashes or signed approvals, asset retrieval, automatic auditioning, waveform/ASR analysis, media playback, lip-sync or accent detection, footage comparison, cross-file camera matching, billing enforcement or publishing. Humans must truthfully record actual review, approval provenance and supported provider bindings. A fabricated record can pass; boolean approval fields cannot authenticate a person or a take.
