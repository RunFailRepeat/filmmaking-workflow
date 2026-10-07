# Reference transfers into Higgsfield

Tool contracts reviewed **2026-10-07**. This documents supported routes; it does not execute uploads, authorize generation or prove that a particular asset was transferred. Recheck the currently exposed contracts before use. Keep transfer receipts in the private production ledger, not this public repository.

## Resolve identity before transferring

A ChatGPT Library ID, client-local file path, confirmed Higgsfield media UUID and completed generation-job UUID identify different things. A display name is not a binding. Never substitute one identifier for another, invent a URL, or assume a remote sandbox shares the client's filesystem.

First inspect existing authorized assets and successful receipts. Reuse a compatible confirmed binding instead of importing the same asset or asking the user to attach it again. Verify source version and reference role; matching filenames alone do not establish identical bytes. Inspect visual references before image-dependent generation. Preserve approved face identity and the separate approved voice/take: an image reference does not preserve voice.

## Choose the documented route

| Actual source | Supported route and completion evidence |
| --- | --- |
| User-provided ChatGPT attachment | `media_upload_and_confirm`, one attachment per call. The helper uploads and confirms; reuse the successful returned `media_id`. **Do not call `media_confirm` again.** Although its file argument uses a client path, this is an attachment-only helper. Do not silently reclassify an assistant-generated local file as a user attachment. |
| Authorized HTTPS image reference | `estimate_image_cost` and `generate_image` accept HTTPS image references and import/confirm them automatically. **Estimation can write/upload**, despite not submitting a generation job. Confirm asset-transfer authority first, avoid repeated URL imports, and preserve/reuse resolved IDs or `prepared_params` when returned. A quote does not validate media existence or generation readiness. |
| File produced inside Higgsfield `sandbox_exec` | Request the `media_upload` slot **before** the producing command. Produce the file and PUT its bytes to the returned `upload_url` in that **same command**, verify HTTP 200, then call `media_confirm`. Reuse the confirmed media ID. This OpenAI routing is for sandbox-produced files, not an assumed route from an unrelated local filesystem. |
| Existing confirmed media or completed generation job | Reuse its verified UUID where the selected model's current media-role contract permits. Confirm that the job is actually completed and the reference type/role is supported. |
| Library item materialized only to a local path | A local path alone does not establish a compatible Higgsfield binding or HTTPS source. Inspect supported tools and prior receipts for a bridge; do not fabricate one. |

The Higgsfield sandbox is remote and ephemeral. Export results before its producing command ends using the documented upload sequence; do not rely on local files or later sandbox persistence. Never publish temporary signed URLs or retain credentials in documentation or logs. A general-file upload is not automatically an image/video/audio generation input.

## Operational checklist

1. Resolve the approved source and origin; record its immutable version/hash and inspect actual visual content. Locate existing confirmed receipts before requesting another attachment.
2. Verify transfer authority, current source route, selected model's reference roles, and target workspace/project/folder. Maintain one canonical project per film and a separate organization for reusable cast references. Resolve authorized destinations from actual returned IDs; do not guess or silently reuse a different conversation's destination.
3. Transfer only through the applicable supported route. For sandbox-produced files, preserve the slot → same-command production/PUT → HTTP 200 → confirmation order. For attachment helper or automatic HTTPS imports, avoid a second confirmation/import.
4. Record origin, source version/hash, destination workspace/project/folder, transfer method, confirmed media ID, ordered reference roles, exact final payload/quote, job ID and verification. Record tool adjustments and reuse resolved identifiers when exposed. Keep sensitive receipts private and redact temporary authorization URLs.
5. Verify actual destination contents after import/generation. Project/folder creation proves only that a container exists, not that assets were filed there. List the destination assets and reconcile them with returned media/job IDs; if listing is unavailable, label placement unverified. Preserve originals.
6. Before generation, review the exact ordered references, approved identities and final payload; obtain the separate required execution/spending authorization. A transfer, project creation or estimate is not that authorization.

## Failure and uncertainty handling

Distinguish `not attempted`, `submitted/outcome unknown`, `confirmed`, `placement unverified` and `failed with observed error`. An unavailable bridge is not a failed upload. After a timeout, inspect receipts/status before retrying to avoid duplicate imports or spending. If an attempted call returns an authorization denial, stop and report it; do not switch routes to bypass it.

If Library materialization supplies only a local file and no supported bridge is available, name the precise missing step: making the approved bytes available through a supported Higgsfield source. Ask for a user attachment or an authorized browser upload only after checking existing receipts and compatible tools. Verify that transfer's returned binding; do not claim success from a filename or assume browser upload supports a downstream model without checking.

Evidence distinction: a reviewed historical production record reports successful generation from two already-confirmed media references originating as JPEG attachments. The original upload-call receipt was not retained. That supports the downstream reference binding, **not** a claim that any assistant-generated local-file transfer route was historically tested. New references remain untransferred until their own confirmation evidence exists. No transfer was attempted to validate this document.

## Sources and scope

Sources are the currently exposed Higgsfield tool contracts, inspected on the review date: `media_upload_and_confirm`, `media_upload`, `media_confirm`, `sandbox_exec`, `estimate_image_cost` and `generate_image` (including `medias[].value`, reference roles, destination guidance and resolved parameters). These are tool-contract citations, not invented public documentation URLs. Historical downstream-binding evidence is labeled separately above. Tool availability, supported roles and return fields may change; missing receipts or unsupported routes stay unresolved.
