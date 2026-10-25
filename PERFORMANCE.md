# Preserve the performance, not just the voice ID

An approved recording establishes a performance reference. Matching its preset, model and stability does not establish equivalent delivery in new dialogue. Before dependent picture work, compare a newly heard take against that reference and the current creative intent. A successful request or complete file is not acceptance.

## Record the reference and the actual request

Keep the exact approved recording ID, immutable version/hash, stable source and approval evidence in the private project packet. Record the provider, model, voice ID/type, supported parameters, exact expressive cues and their positions in the text. Keep canonical spoken words separate from control tags. Preserve punctuation and capitalization unless an explicit wording change is approved. Do not silently strip every bracketed span: an unknown instruction or spoken bracket may otherwise disappear unnoticed.

Compare the approved request with the candidate request before execution. A missing expressive cue is a material performance change even when every voice setting matches. A different scene may need different cues: record that as a deliberate reviewed change, never silently infer approval from the old performance. The candidate should preserve the intended energy while serving the new beat; repeating a previous line is not a substitute for recording new words.

Record the current provider/connector contract, retrieval date and parameter values. For Eleven v4, the official voice-settings reference limits settings to stability and similarity boost, excludes speed/style, and the best-practices guide excludes SSML breaks. The selected connector may expose less; use the intersection of verified support, not another model's fields. A price quoted in credits is never a speed setting. Tags affect delivery probabilistically and may misfire; no tag or numeric value guarantees emotion. See [sources](RESEARCH_SOURCES.md).

## Hear the performance before committing picture to it

Use the smallest authorized audition that tests the actual risk. Compare it with the approved source at comparable playback level. Record the listener, date, exact candidate ID/version/hash, reviewed ranges, and separate results for identity, accent, words, pronunciation, energy/delivery, intelligibility, unintended spoken controls or effects, and unclipped starts/ends. Listen at normal speed. Retain the owner's actual verdict independently of automated metadata and ASR. Unknown, partial, unheard and rejected are not accepted.

If it fails, keep the evidence and identify the failed dimension. Prepare one controlled change for review rather than automatically spending on a batch. Audition approval does not approve unrecorded lines or dependent visuals, nor authorize additional spend.

## Bind continuous sound across motivated picture cuts

Keep one continuous approved performance per character where practical, with source/version and exact line ranges. Record pauses used for other speakers; never split a word to satisfy a picture edit. For every picture span, record the bound recording, source range, export range and canonical line IDs. Consecutive picture cuts within a spoken line must preserve the same take and contiguous source audio. A direct-edit audio replacement still needs an applied binding and actual sync review; a written replacement plan alone resolves nothing.

Use a reaction when information changes the listener's understanding, and an arena/object insert when a gesture or gaze directs attention to something the viewer needs to inspect. Let existing audio continue over an insert with an L cut. Establish spatial relationships and preserve axis, eyeline, movement direction, action phase, hand/prop state and camera intention. Do not add arbitrary cuts to hit a pace target. These are editorial proposals derived from the source principles, not requirements to copy source films.

Keep dialogue and ambience stems separate. Maintain coherent acoustic perspective and room tone across cuts; change perspective when location/action motivates it. Ambience cannot recover clipped words. Review the assembled seam and final export, not only isolated clips. New media remains unresolved until normal-speed picture review, direct listening, synchronization and owner acceptance are recorded.

## Offline validation and its limits

The additive [performance validator](validate_performance.py), [schema](schemas/performance.schema.json) and [fictional fixture](examples/fictional-performance.json) check declared records only. They do not call a provider, listen, authenticate approvals, or establish energy, quality, rights or spending authority. Run them alongside existing continuity, planning and release checks; this tool is not wired into providers or the action ledger.

Use [the review worksheet](templates/performance-review.md) privately. Preserve old rejected and approved artifacts as separate versions. Keep project scripts, media, receipts and character identities out of repository fixtures. Provider capabilities must be freshly checked before a real payload; a recorded capability list is not an independently authenticated API contract.

The current validator is deliberately bounded: one character per record, identical prefix-only cues on every line, and one contiguous normal-speed audio interval. It does not encode cue placement inside a line, varying cues per line, multi-speaker interleaving, silence insertion, retiming, or actual ordered video-provider payloads. Keep those in a separately reviewed assembly/binding plan; never claim a single-character pass verifies the whole scene. Its planning mode also requires declared numeric ranges and source identities, so leave it unapplied when actual ranges are unknown rather than inventing placeholder media evidence.
