# Jev prompt-compliance adapter — offline, not activated

[jev_audit.py](jev_audit.py) prepares a TypeSafe System One request and validates/routes synthetic responses. It has **no network transport**, reads no credentials, installs nothing, and never writes an approval or changes the production ledger. `--mode live` always blocks. This offline module does not prove that Jev catches the supplied failure cases. The separate [HTTPS scene client](JEV_SCENE_CLIENT.md) adds an explicit callable transport and experimental sampled-frame request path; it does not change this module’s dry-run/fixture behavior or activate access.

## Contract and evidence

Primary documentation inspected 2026-10-25:

- [Index](https://docs.typesafe.ai/llms.txt), [System One HTTP contract](https://docs.typesafe.ai/api/system-one), and [Python SDK](https://docs.typesafe.ai/sdk/python).
- [Noul](https://docs.typesafe.ai/primitives/noul), [confidence](https://docs.typesafe.ai/confidence), and [guardrails cookbook](https://docs.typesafe.ai/cookbooks/llm_guardrails).
- [Current models and pricing](https://docs.typesafe.ai/models): pinned `jev-1.14.0`, text input, $0.042 per million input tokens; output tokens free. Account allowance and billing limits were not verified. Do not assume a free allowance or treat this dated list price as a cap.

The prepared HTTP body uses `model`, `state` and named `questions`, each with `type: noul`, instructions and true/false criteria. Responses contain `model`, matching typed answers with a `noul` probability, and integer input/output token usage. No generated explanations or separate Noul confidence field are expected. Fixed routing reasons come from code, not Jev. The SDK package is `typesafe-sdk`; none is required here.

Eight separate violation judgments cover mapping, intent/action, gesture, eyeline, performance timing, latest corrections, reference-driven wardrobe and irrelevant named negatives. Each of the intent/action, gesture and eyeline questions asks about omitted or contradictory subject-specific requirements in the authoritative brief or shot plan, as well as required differentiation. Distinct performances can still violate the requirements when assigned to the wrong subject. Each question states its own criterion because questions are evaluated independently and their IDs are not sent to the model. A high probability means a violation, not good compliance. Questions evaluate the exact prompt against supplied source text; they cannot authenticate that text, actual provider attachments or unseen images. No image assets, vision headers, audio/video or capability assumptions are used. Human inspection of actual reference bytes remains mandatory even if text scores look favorable.

## Prepare a private evidence bundle

Use [the fictional bundle](examples/fictional-jev-audit.json) as a structural example only. Keep actual packets outside the public repository. The adapter accepts these state fields only:

- `repo_commit`: the exact inspected workflow commit.
- `rules`, `owner_corrections`, `brief`: nonempty version, relevant exact text, SHA-256 over UTF-8 text. Include all currently applicable owner corrections, not a stale summary.
- `payload`: exact prompt, actual supported settings, and ordered `medias` entries with `role`/`value`.
- `references`: ordered subject, provider UUID, role, actual source-file SHA-256, image ordinal, supported prompt notation, and private audit description. Do not substitute a text description hash for the actual asset hash. Synthetic hashes in the example are deliberately not real asset evidence.
- `shots`: stable ID/subject, intent/action, gesture, eyeline, essential performance interval and retained interval, both in source seconds. Only ordinary contiguous source intervals are supported here.

A separately maintained `current` snapshot pins the repository commit and hashes of rules, corrections, brief, payload, manifest and shot plan. Source text hashes use exact UTF-8; object hashes use sorted compact JSON with no NaN. Do not derive current pins from a candidate simply to make validation pass. Resolve them independently from the latest owner-approved sources and exact prepared submission. The fixture test helper does re-seal artificial examples; it is not a production provenance procedure.

`gates` binds the external mandatory check results to the entire state hash. All seven named checks must be `pass`: `asset_bytes`, `provider_bindings`, `provider_notation`, `exact_invariants`, `owner_restrictions`, `cost`, `permissions`. These are trusted caller evidence declarations, not authenticated approvals. Existing tools and reviewers must compare actual bytes, bindings, exact dialogue/settings, price limits and authority; Jev cannot supply these passes. The adapter additionally compares ordered media entries against the manifest, validates timing containment and source hashes, and rejects mismatched current pins.

The local audit accepts two example-backed spellings, `@imageN` and `@Image N`, with N equal to the one-based position in the ordered attachment manifest. It rejects duplicate/wrong ordinals, notation-number mismatches and embedded token collisions such as `@image1` inside `@image10` or a word. These conservative local boundaries are not a claimed provider parser grammar or a universal notation requirement. Other conventions require an explicit reviewed adapter update. The mandatory external `provider_notation` and `provider_bindings` checks still verify applicability to the actual provider/version and submitted attachments; local token membership cannot establish subject identity or provider interpretation.

State is deliberately limited to this review. Do not include API keys, credentials, unrelated notes, full conversations, local paths or media URLs. The top-level allowlist is not a secret scanner: callers must inspect allowed text/settings fields too before any future transfer. No private state is sent anywhere by this implementation.

## Run offline

Python 3 standard library only:

```sh
python -m unittest discover -s tests -p test_jev_audit.py -v
python -m unittest discover -s tests -v
python jev_audit.py examples/fictional-jev-audit.json
python jev_audit.py examples/fictional-jev-audit.json --mode fixture_replay
python jev_audit.py examples/fictional-jev-audit.json --mode live
```

Dry run prepares and hashes a request without a judgment; exit 2 and route `blocked` are expected. `build_request(state, current)` exposes the body to local callers without sending it. Fixture replay returns `independent_review` (exit 0) for the compliant artificial case; that means the offline routing test completed, not readiness or approval. Live mode returns blocked/exit 2 even if a key exists. Malformed input, missing/stale sources, mismatched hashes/order, missing mandatory checks, missing responses and unsupported models also block.

The `replay` wrapper binds the API-shaped response to the exact request hash. A receipt retains source/request/prompt/question/response/policy hashes, requested/returned model and reported usage, while explicitly recording `jev_verified: false`, `live_status: disabled`, and synthetic provenance. Retained source pins and usage are deep-copied so subsequent mutation of caller inputs cannot change the returned evidence. The returned receipt itself is an ordinary mutable dictionary, not a signed or tamper-proof record. These fields are the basis for an eventual live receipt, not evidence that a fixture was served by Jev. Token counts in fixtures are invented.

## Conservative routing and activation boundary

There are no default deployment confidence thresholds. Without a routing policy the adapter blocks as uncalibrated. Only a policy explicitly scoped `synthetic_routing_test_only` can exercise the offline routing paths. It binds model, questions, rules and an evaluation-evidence hash, with separate lower review and upper revise bounds for every criterion. The example's 0.1/0.9 bounds exist solely to test branch behavior; they are not recommended, measured or approved deployment thresholds.

Any violation signal above its upper bound routes to `revise`. An intermediate probability blocks for uncertainty. Only when every criterion is below its review bound does the synthetic path route to independent review. No averaging can hide a violation. A failed mandatory check blocks before probabilities are considered. Every result retains `execution_allowed: false` and `independent_review_required: true`.

The regression suite recreates failure *patterns* with fictional text: missing mapping, wrong order, copied performances, swapped-but-distinct performances, isolated action/gesture/eyeline mismatches and omissions, an omitted latest outfit change, stale owner correction, redundant unchanged color, and a compliant pair of distinct responses. Contract assertions check that the three subject-specific questions include omission, contradiction and differentiation requirements. Scores are hand-authored to verify routing and receipt validation; they are not actual Jev classifications of those cases. They do not measure semantic accuracy, calibration or Jev's historical performance. Evaluate actual judgments separately once a bounded live experiment is authorized.

Before adding live transport, establish existing authenticated access without creating credentials here, verify account allowance/pricing and an enforceable request/spend bound, approve the exact minimal transfer, and review a version-pinned calibration dataset with independent labels. Verify model support/context limits; obtain explicit authorization for any calibration calls. Specify timeouts, no automatic paid retries, receipt persistence, uncertain-outcome handling and stale-evidence rechecks. Add and review transport tests and a separate live provenance path. Do not turn a fixture flag into live activation. An unavailable service must leave the semantic review unresolved.

A human/independent reviewer must inspect the prompt, latest corrections and actual reference assets even after future favorable Jev judgments. Attach the receipt as supplementary evidence to the [prompt audit](templates/reviewers.md); it cannot replace the existing [ledger gates](RESULTS.md), spending authorization or owner restrictions. Any exact payload/source change invalidates the receipt for the new submission.

## Narrow edit-scope regression

The fictional bundle also contains one anonymized regression for a narrow arrival-removal instruction. Its model-visible brief carries the owner-approved target description, versioned source/hash, exact source-frame boundaries, protected middle beats and a protected-look mapping. Each protected look binds a subject and beat ID to the approved reference UUID and source hash. Its prompt/settings carry the proposed removal, retention, sequence and look assignments. The corrected case removes only `[513,585)` and retains `[585,1320)`, then adds the guard and courier closeups in that order, restoring both approved looks. These are explicitly half-open frame-boundary intervals, not source seconds; no frame rate or footage inspection is invented.

The existing owner-corrections question provides a place for future text-only semantic review. The regression independently compares exact intervals, required sequence and proposed look assignments against the fixture's authoritative protected mapping before supplying the mandatory gate result. A broad middle deletion blocks even with favorable invented probabilities. A separate negative variant preserves the correct intervals and sequence but assigns the courier's look reference to the guard closeup; the deterministic check blocks it despite favorable invented probabilities. Ambiguous target identity leaves the owner-restriction check unresolved and blocks for independent identification; it never expands the deletion. The corrected fixture only reaches independent review. This is a fixture-side deterministic check example, not a general edit validator: real source/frame checks, protected-look checks and target identification must remain authoritative outside Jev. Do not substitute synthetic source hashes, replayed scores or descriptions for actual footage evidence. No editor subsystem or live semantic validation is introduced.
