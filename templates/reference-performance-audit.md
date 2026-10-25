# Reference-binding and distinct-performance audit

Keep completed records private. This supplements the [reviewer briefs](reviewers.md) and [immutable attempt ledger](../RESULTS.md); it does not authorize uploads, generation or spending.

Attempt ID / exact prompt version and SHA-256:
Exact payload snapshot and hash / model, provider, version and mode:
Current brief version/hash / reviewer / UTC time:
Primary notation source and date checked / evidence strength / unresolved questions:

## Subject and attachment mapping

For every generated subject, inspect the actual approved assets and fill a row for each required role. A role missing an approved reference remains unresolved; bounded exploration requires the existing explicit exploration decision. Do not invent hashes, UUIDs or approvals.

| Internal alias | Private audit: visible identity anchors and shot role | Reference role (identity, wardrobe, prop, etc.) | Source asset/version and SHA-256 | Actual payload attachment position, UUID and API role | Provider image ordinal and exact prompt notation | Prompt phrase assigning subject/role |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

- Match each row to the exact ordered provider attachment, not a filename or remembered character name. For mixed media, record both payload position and provider image ordinal; do not assume they are identical. Inspect prepared/normalized bindings where available. Uncertain ordering is unresolved.
- API binding selects the media asset. Model-visible prompt notation explains how that reference participates in the shot. Neither a UUID in a ledger nor a name in prose establishes both. Check that each subject/role phrase points to the intended actual attachment and that no unsupported tags were invented.
- Names may remain useful aliases after explicit mapping. Record visible identity anchors for private audit traceability; do not automatically copy them into generation prose. Identify the subject with supported reference notation and a clear role, adding visual anchors only where needed to resolve ambiguity. A face-only reference does not establish wardrobe approval.
- When the attached approved reference already defines unchanged wardrobe, omit redundant descriptions of its color from the generation prompt. Bind that reference and direct the new action/performance. If the owner approves a wardrobe change, explicitly describe the requested new outfit (for example, new beach outfits) and scope the reference to identity or other unchanged roles; do not accidentally preserve its old clothing. This is not a universal ban on visual descriptions. In either case retain the exact UUID/order/hash mapping and supported ordinal notation in the audit.
- Remove irrelevant named negative constraints when that character/reference is not in the shot. Describe the intended subject count and roles positively when needed. Keep genuinely relevant, brief-supported constraints; do not apply a lexical name ban.

## Provider notation evidence

Verified 2026-10-25 from primary sources:

- [Higgsfield Seedance 2.5 comparison examples](https://higgsfield.ai/blog/seedance-2-5) use `@image1` and `@image2` in ACTIVE REFERENCES and shot descriptions. Use this example-backed convention for the applicable Higgsfield Seedance workflow after matching its current attachment order. The article also demonstrates the prompts on Seedance 2.0; this is not a compatibility guarantee for every mode/version.
- [ByteDance Seedance 2.5 introduction](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) uses `@Image 1`. This establishes another primary example convention, not proof that capitalization or spacing is interchangeable across providers.
- The inspected Higgsfield MCP `generate_video` contract accepts ordered `params.medias` entries with `role` and `value` (media UUID), and maps canonical roles to model-specific backend keys. The current Seedance mapping normalizes `image` to `image_references`. Preserve the actual selected model contract and prepared mapping in the private audit evidence; recheck on provider/version changes. This contract exposes no formal prompt-token parser grammar.

These are example-backed notation and API-contract facts of different strength. Do not claim the markers are mandatory, case-sensitive or parser-enforced without a current explicit contract. If the selected interface's notation or ordinal mapping is unverified, mark it unresolved before calling the binding ready. Do not generalize these spellings to other providers.

## Performance comparison

When the brief calls for different responses across sequential character shots, complete and compare every row. Distinct intent/action, gesture, eyeline and timing are required; name-swapped copies fail this manual review. Do not manufacture different reactions when the brief deliberately asks for synchronized or matching behavior; record that intention instead.

| Shot and subject mapping | Intent / response and visible action | Gesture | Eyeline target/direction | Action onset, peak and resolution in source time | Planned retained source window / corresponding edit beat | Shared mood and continuity locks |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Preserve shared mood, axis, setting and state continuity while directing individual responses. Timing includes pace and the response's relation to the preceding beat. Put the essential action and readable reaction inside the retained window, not just in discarded setup or tail footage. Label windows as planned until real media exists; use the [source/edit coordinate contract](../PLANNING.md) and verify the retained performance and actual seam at normal speed after generation.

## Audit disposition

- Overall audit decision: `pass`, `revise` or `unverified`. Record the existing `reference_readiness`, `bindings` and `performance` checks as `pass`, `fail` or `unverified` (the prompt gate requires `pass` for these checks), with concrete evidence and unresolved items. Link this completed record in the existing audit evidence; do not add unsupported schema keys or treat a metadata gate as semantic validation.
- Compare exact prompt bytes, settings, ordered media IDs/roles and source versions with the reviewed payload immediately before submission. Any payload change invalidates the previous audit for the new submission, even if the prompt text is unchanged. Preserve prior history and create a new immutable attempt with a fresh audit; update the prompt version when its bytes change.
- Keep observed defects separate from cause hypotheses. Alias wording alone does not establish why an earlier model output failed. Record uncertainty and supporting/counter-evidence rather than assigning an unsupported cause.


## Required entity check and workflow consumption

Use the existing image-ordinal and ordered-media checks rather than maintaining a second reference order. The additive [reference binding validator](../validate_reference_bindings.py) calls `jev_audit.validate_state` unchanged, then compares each declared subject with a separately reviewed required-entity manifest. Each specific prop gets its own entity, actual media ID/hash and explicit prop role. A character match cannot silently satisfy a missing prop. The [fictional fixture](../examples/fictional-reference-bindings.json) is invented metadata, not real asset or provider evidence.

The bounded adapter supports one distinct reference per entity and the existing image-only ordinal conventions. Mixed-media ordinals, multiple views of one entity or shared composite assets require a separate reviewed mapping, not fabricated unique IDs or a claim this adapter supports them. Pin the approved requirements separately from the candidate. Check the provider/model/mode-specific notation source and date; unsupported notation remains unresolved. `Prop1` may be an internal alias, but must not be presented as provider-native syntax. Never invent token grammar from a local parser's acceptance. The adapter's limited numbered-@ scan cannot identify all possible unsupported prose aliases.

Before marking the audit passed, an actual reviewer must compare the prompt and ordered source assets:

- Does every numbered model-visible token identify the intended character/prop through its actual ordered media ID and hash?
- Is each specific prop bound with its intended role, including held/contact-critical items, rather than merely named in prose?
- Does the approved reference already define identity and wardrobe? Remove redundant colors and appearance descriptions that override or compete with that reference. Retain only action-essential details or explicit owner-approved changes, with the approval source/version. Do not reconstruct good characters to compensate for a mapping mistake.
- Does the prompt preserve the latest specific action, gesture and eyeline instructions? Are these attached to the correct subject?
- For speech, has the approved expressive performance and actual audio binding been preserved? A preset name/ID is neither a performance match nor an audio attachment. Apply [performance](../PERFORMANCE.md) and [continuity](../CONTINUITY.md) checks separately; a semantic flag cannot replace heard review.

Record each result as pass/fail/unverified with named reviewer, date and evidence pinned to the entire state, required-entity manifest and notation evidence. This is a semantic review checklist, not automatic image recognition or a word/color blacklist. A valid declaration cannot establish that the reviewer actually inspected an image or heard a recording.

The production handoff must record consumed repository commit; rules version/hash; latest owner-correction version/hash; exact payload hash; consumer/reviewer and date; remaining unresolved roles; installed-plugin version if used; and whether this is planning consumption or a completed prompt/submission review. The validator's `consumption` block checks declared pins for a completed candidate review. If no final payload or approved prop exists, retain an unresolved planning handoff rather than manufacturing a passing fixture. After any correction or binding/payload change, consume the current rules again and refresh the exact review. A local commit, pushed branch or draft PR does not itself install the plugin, merge the workflow or prove production adoption.
