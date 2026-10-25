# Jev scene client — bounded prototype, live use not yet approved

[jev_scene_client.py](jev_scene_client.py) is a separate Python standard-library client for eventual TypeSafe judgments. The existing [offline audit](JEV_AUDIT.md) remains offline and its live mode still blocks. No real API request, account-access check, key setup, media inspection or calibration has been performed for this client. Tests use generated in-memory images and mocked HTTPS responses.

Three request builders are available:

- `build_text_request(state, current)` uses the existing audit's exact source validation and eight text-compliance questions. It cannot inspect reference pixels or a scene.
- `build_frame_request(png_data, metadata, current)` prepares one sampled still with three independent judgments: visible defect, visual intent readability, and evidence insufficiency. These are separate probabilities, with explicit true/false criteria in each question. A high value means the named proposition is true; intent readability therefore has a different polarity from defect or insufficiency. There is no aggregate “good scene” score or acceptance threshold.
- `build_box_request(png_data, metadata, current)` prepares one still and one described target, with an independent presence Noul and a Box localization question. Coordinates are retained for review but never activated for automatic use.

Motion, temporal continuity, audio, unsampled frames and full-scene quality always remain unknown. A favorable response cannot authorize editing, generation, release or further spending. Every receipt retains `execution_allowed: false`, `scene_verified: false` and `independent_review_required: true`.

## Documented API and deliberately narrow image support

Primary documentation checked on 2026-10-25, alongside the installed official TypeSafe skill: [index](https://docs.typesafe.ai/llms.txt), [images](https://docs.typesafe.ai/images), [System One](https://docs.typesafe.ai/api/system-one), [Noul](https://docs.typesafe.ai/primitives/noul), [Box](https://docs.typesafe.ai/primitives/box), and [models/pricing](https://docs.typesafe.ai/models).

The pinned model is `jev-1.14.0`. Before submitting an authorized assessment, the client makes an authenticated `GET https://api.typesafe.ai/v1/models`. The [current model documentation](https://docs.typesafe.ai/models#listing-models) says that this list may contain aliases only and that versioned IDs are accepted even when absent from it. Consequently the receipt records whether the pin was listed but treats this GET as metadata only; absence does not block or establish unavailability. The client never substitutes an alias. It then makes at most one `POST https://api.typesafe.ai/v1/systemone` with the exact pin, `state`, independent `questions`, and, for either still path, `assets`. Only a valid POST response with the exact pinned model establishes that the request was served by that version. Expected answer types are Noul, plus Box for the localization path; usage must contain nonnegative integer input/output counts. Unknown or missing fields, malformed JSON, duplicate JSON keys and unexpected models fail closed.

Images are experimental, not production-ready. The documented API permits PNG/JPEG stills for Jev 1.13/1.14 with `TypeSafe-Danger-Zone-Images: true`. The client supports a smaller subset: one static, noninterlaced, 8-bit RGB/RGBA PNG, 280–1568 pixels on each axis. Only `IHDR`, `IDAT`, and `IEND` chunks are accepted. JPEG, GIF, palette/grayscale PNG, APNG and ancillary metadata chunks are rejected. The client validates chunk structure, CRCs, dimensions, decompression length, filter bytes and the exact source hash. It does not resize, convert, extract frames or modify images. The 16 MiB image-byte/decompressed-data limits and 32 MiB serialized request limit are enforced locally. The asset UUID appears once in state as a value, so repeated substitution cannot multiply the image payload. No audio/video or media URLs are supported.

The only experimental opt-in sent is exactly `TypeSafe-Danger-Zone-Images: true` on the still POST. Neither long-context nor diagnostic opt-ins are sent. Multipart upload is the documentation's preferred image path; JSON/base64 is also supported and is used here to keep one bounded, hashable request format without adding a multipart subsystem. Repeated asset references, including UUID occurrences embedded in longer metadata strings, are rejected.

The separate localization builder is pinned to Jev 1.14. Its Box question uses `type: box` and instructions, with no criteria. Validation requires exactly four finite normalized edges with `0 <= left < right <= 1` and `0 <= top < bottom <= 1`, plus finite confidence in `[0,1]`; booleans are rejected as numbers. The [Box contract](https://docs.typesafe.ai/primitives/box) always returns coordinates even when the target is absent, so the same request includes an independent presence Noul that names the target and image. There is no fabricated `not_found` response or universal presence/confidence threshold.

No calibrated localization policy is implemented. **Every box remains inactive**, including high-presence/high-confidence answers: receipts set `localization.box_use` to `ignored_pending_independent_review` and `active_box` to null. This ensures absent and uncertain targets cannot yield an automatic crop or action. Raw coordinates and the separate presence probability remain available to a reviewer. No coordinate-to-pixel conversion, cropping, retry, editor integration or automatic approval is introduced.

## Local dry run and source metadata

The request and receipt types are frozen dataclasses containing immutable bytes. `as_dict()` returns a detached copy for display or storage. Request hashes cover the exact canonical UTF-8 JSON bytes to be transmitted. Editing a source, image, question or payload requires a new prepared request and approval. The source pins are caller-provided declarations, not authenticated provenance; resolve them from independently reviewed current sources rather than copying a changed candidate just to pass validation.

A text-only dry run can use the fictional audit bundle:

```sh
python jev_scene_client.py examples/fictional-jev-audit.json --kind text_compliance
```

This emits a receipt containing the request hash and source hashes, with no key read or network call. The fictional bundle is not a production packet or approval.

For the frame builder, `metadata` has exactly this shape (placeholders below are not executable evidence):

```json
{
  "repo_commit": "<40 lowercase hex characters>",
  "scene_intent": {
    "version": "approved-intent-v1",
    "text": "The intended visual beat, narrowly stated.",
    "sha256": "<SHA-256 of exact UTF-8 intent text>"
  },
  "frame": {
    "source_id": "approved-source-frame-v1",
    "source_sha256": "<SHA-256 of exact PNG bytes>",
    "sample_time_seconds": 0
  }
}
```

Its independently checked `current` contains exactly `metadata_sha256` (the audit module's sorted compact JSON hash of the whole metadata object) and `frame_sha256` (the exact PNG hash). The CLI bundle contains only `metadata` and `current`. Then use an explicitly chosen local PNG:

```sh
python jev_scene_client.py /private/scene-bundle.json --kind sampled_frame --png /private/approved-frame.png
```

Only that named file is read. The module does not discover or sample footage. Metadata is included in the remote state if live submission is subsequently authorized; keep local paths, secrets, unrelated notes and personal data out of it. Source labels and hashes cannot establish which footage a frame actually came from. Independent source/frame review remains required.

For localization, add `localization_target` to metadata with exactly `version`, `text`, and `sha256` over the target's exact UTF-8 description. Use a specific target such as “the red coffee mug nearest the sink,” and include the added object in the independently checked `metadata_sha256`. The builder names that target in both questions, rather than relying on question IDs. The CLI is the same as above with `--kind sampled_box`; the PNG restrictions and approval requirements are unchanged.

Callable use is `prepared = build_text_request(state, current)`, `prepared = build_frame_request(png_bytes, metadata, current)` or `prepared = build_box_request(png_bytes, metadata, current)`, followed by `receipt = assess(prepared)` for a dry run. `receipt.as_dict()` provides a copy. Mock tests call `assess(..., mode='mock', authorization=..., mock_transport=...)`; mock provenance is always `mock_not_Jev_verification`, the real environment key is never read, and `jev_response_received` remains false. Injected transports are forbidden in live mode. There is no mock CLI option.

## Cost and authorization prerequisites

There is no documented per-request `max_tokens` or spend-cap parameter, and image-token estimation guidance is unavailable. This client invents neither. All builders enforce a separate conservative **16 KiB UTF-8 JSON bound** over model, state metadata and all questions, excluding the image asset's base64 data. Oversized text blocks locally before network access. The documented 64,000-token per-request context is state plus all questions combined; the 32,000-token per-question context is state plus one question. These are provider limits, not local tokenizer measurements. The 16 KiB check is not a token guarantee, and local byte checks do not establish that the request fits a token limit, especially with images.

At the dated price of $0.042 per million input tokens, with output tokens free, 64,000 × $0.042 / 1,000,000 is **$0.002688**. The receipt calls this `context_cost_assumption_usd`: an illustrative cost assuming that the documented context bound corresponds to billed input usage. It is **not an image-token estimate, an invoice guarantee or a hard spend cap**. Failure billing and provider/account behavior are not established by these docs. Recheck pricing and account billing before any authorized attempt. If the price or context contract differs, this client blocks until the pinned assumptions are updated and reviewed.

No authorization means a zero budget and no network. Live use requires all of the following:

1. Independently review the exact minimal request and source evidence, then approve its emitted request hash for one assessment attempt.
2. Verify the account's billing status, available allowance/credits and payment consequences, and verify the dated pricing/context assumptions. A free allowance is never assumed. The approval requires recent account and pricing verification timestamps.
3. Explicitly accept the lack of a provider-enforced per-request spending ceiling. Requests that require a guaranteed hard cap block; this prototype has no verified account-enforcement integration.
4. Supply a nonzero authorized risk budget at least as large as the illustrative $0.002688 assumption, short-lived approval metadata, and, for a frame, explicit experimental-image consent.
5. Configure an existing authorized key only in `TYPESAFE_API_KEY`, then separately and deliberately select live mode. No key belongs in a request, receipt, CLI argument, configuration file, repository or approval JSON.

Approval timestamps must be timezone-aware. `approved_at <= now < expires_at`, with at most one hour between approval and expiry. Pricing and account verification must be within the preceding 24 hours. The client snapshots the approval before preflight and checks that same snapshot again immediately before POST; metadata lookup cannot extend its validity, nor can mutation of the caller's approval. Expiry during GET blocks before POST. `approved_by` identifies the approving person; `authorization_id` is a canonical UUID. These fields are review attestations supplied by the caller, not authenticated approvals. A file's existence does not prove permission.

The following is the **disabled** approval schema. Fill it only from actual evidence and approval; do not turn its false values into consent automatically:

```json
{
  "authorization_id": "<fresh canonical UUID>",
  "approved_by": "<actual approving person>",
  "approved_at": "<timezone-aware timestamp>",
  "expires_at": "<timezone-aware timestamp within one hour>",
  "request_sha256": "<exact dry-run request hash>",
  "model": "jev-1.14.0",
  "budget_usd": "0",
  "allow_live": false,
  "minimal_transfer_approved": false,
  "experimental_images_approved": false,
  "accept_unenforced_billing_risk": false,
  "require_hard_spend_cap": true,
  "account_billing_verified_at": "<actual verification timestamp>",
  "pricing": {
    "source": "https://docs.typesafe.ai/models",
    "verified_at": "<actual verification timestamp>",
    "currency": "USD",
    "input_usd_per_million": "0.042",
    "output_usd_per_million": "0",
    "request_context_tokens": 64000,
    "question_context_tokens": 32000
  }
}
```

An approved attempt needs `allow_live`, `minimal_transfer_approved`, and `accept_unenforced_billing_risk` to be true; `require_hard_spend_cap` must be false. `experimental_images_approved` must be true for either still path and can remain false for text. No extra fields are accepted. `budget_usd` is a decimal string. The approval hash and ID, pricing, request/source/question hashes, requested/returned model, reported usage and usage-derived cost are retained in the receipt. Usage-derived cost is not the provider invoice. Reported input usage above the assumed context ceiling or cost above the risk budget produces an uncertain outcome, never a retry or acceptance.

For a fully validated assessment response, the immutable receipt also retains `response` (parsed typed answers), `raw_response_base64` (the exact received bytes, including whitespace), and `raw_response_sha256`. `response_sha256` remains the canonical parsed-object hash; it can differ from the raw-byte hash. These fields are frozen inside the receipt's byte-backed snapshot, and dictionary exports are detached copies. Non-200 error bodies and malformed or schema-invalid responses are not preserved or echoed; those outcomes retain sanitized reasons and uncertain billing status. Raw preservation is deliberately limited to valid expected typed responses, preventing arbitrary error text or unexpected server fields from entering receipts.

## Secure key configuration and eventual one-attempt invocation

No key is present or needed for dry runs and tests. When an authorized account owner is ready, configure an existing key in a trusted Bash shell without echoing or saving it:

```sh
set +x
read -r -s -p 'TypeSafe API key: ' TYPESAFE_API_KEY
printf '\n'
export TYPESAFE_API_KEY
```

The prompt input is not a command-line argument or shell-history command. Do not paste the key into this chat or print the environment. The key is used only for an `Authorization: Bearer ...` header. Unset it after the approved invocation with `unset TYPESAFE_API_KEY`. Any separate key creation, rotation or account changes require their own authorization; this client performs none.

Only after the prerequisites and exact one-attempt approval are complete, the frame invocation is:

```sh
python jev_scene_client.py /private/scene-bundle.json --kind sampled_frame --png /private/approved-frame.png --mode live --authorization /private/one-attempt-approval.json
```

For text, use `--kind text_compliance` and omit `--png`. This documentation is not authorization to execute either live command.

The smallest proposed trial is one public or wholly synthetic 280×280 RGB PNG, a short visual-intent sentence, and the three fixed still questions. A proposed **$0.01 risk budget for one assessment attempt** provides headroom over the illustrative context cost; it is not a provider-enforced cap. Review the exact PNG, text, metadata, hashes and budget before approval. No real scene or private reference needs to be the first trial. This trial would test transport and bounded still judgments; it would not calibrate quality thresholds or demonstrate full-scene assessment.

The [synthetic manifest](examples/fictional-jev-scene-calibration.json) prepares that trial without binary media in the repository. It includes a deterministic PNG recipe, exact image/request/question hashes, metadata/current pins and provisional qualitative labels. Despite its filename, it is one smoke-trial fixture, not a representative calibration dataset. Its `live_authorization` is null. The stored-deflate recipe avoids compressor-version differences; the test helper contains the complete standard-library generator. To reproduce it locally into a fresh temporary directory and print only its dry-run receipt:

```sh
python - <<'PY'
import json
from pathlib import Path
import runpy
import tempfile
from jev_scene_client import assess, build_frame_request, sha_bytes

manifest = json.loads(Path('examples/fictional-jev-scene-calibration.json').read_text())
make_png = runpy.run_path('tests/test_jev_scene_client.py')['manifest_png']
png = make_png(manifest['image_recipe'])
assert sha_bytes(png) == manifest['image_sha256']
bundle = manifest['bundle']
prepared = build_frame_request(png, bundle['metadata'], bundle['current'])
assert prepared.request_sha256 == manifest['request_sha256']
folder = Path(tempfile.mkdtemp(prefix='jev-synthetic-trial-'))
(folder / 'frame.png').write_bytes(png)
(folder / 'bundle.json').write_text(json.dumps(bundle, indent=2) + '\n')
print(folder)
print(json.dumps(assess(prepared).as_dict(), indent=2))
PY
```

This recipe generates only a uniform grey synthetic still and makes no network call. Proposed labels must be reviewed before any eventual trial; no model answer or calibration result is prefilled.

## Failure handling and limits

Transport uses direct standard-library HTTPS to the fixed host with system-trust certificate and hostname validation. There are no configurable endpoints, redirect following, SDKs, proxy discovery or automatic retries. The timeout is **10 seconds per blocking socket operation**, not a total wall-clock deadline. Request and response bodies are bounded to 32 MiB and 1 MiB respectively. Error response bodies are neither exposed nor consumed. Exceptions become fixed reason codes without keys, source text, server bodies or exception text.

GET failures, invalid metadata or local prerequisite failures block before POST. A missing version pin in valid model metadata does not block. Once a POST is attempted, timeout, rate limiting, redirects, malformed responses or other transport failures are conservatively marked uncertain: the provider may have received or billed the request. Do not repeat an uncertain request automatically. Preserve its receipt and resolve provider/account outcome before considering a separately authorized attempt. Successful responses only route to independent review with uncalibrated judgments.

The client bounds attempts **within one invocation**; it does not persist an authorization-consumption ledger or offer exactly-once delivery. Approval metadata must not be reused for a second invocation. The caller must record consumption externally, including uncertain outcomes. Do not use a shell retry loop, scheduled retry or a new invocation to bypass this boundary. Receipts are immutable in memory, but not signed, authenticated or automatically persisted; save them privately under the existing review process.

Validation, with no API traffic:

```sh
python -m unittest discover -s tests -p test_jev_scene_client.py -v
python -m unittest discover -s tests -v
```
