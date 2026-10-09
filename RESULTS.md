# Prompt audits and private results ledger

Use [results_store.py](results_store.py) for an offline SQLite ledger and two separate recorded-evidence gates. Python 3.10+ and its bundled SQLite with JSON/window-function support are required; no dependencies or services are installed. Review code before running it. The tool stores declarations and checks consistency; it does not call a model, watch footage, listen, authenticate a reviewer or authorize generation/publication. Give the [reviewer task briefs](templates/reviewers.md) to the authorized prompt auditor and independent result checker. This supplies their workflow and evidence contract, not an autonomous agent service.

## Private storage and import

Actual prompts, references, receipts, feedback, exports and the populated database belong in an external private project directory or ignored `local-projects/` / `private/`. Only sanitized synthetic fixtures belong in this repository. SQLite files and sidecars are ignored globally; the CLI refuses databases elsewhere inside the toolkit. Ignore rules are not encryption or an access-control system; check staged files before committing. Never force-add private data. Back up the private database while no writer is active; retain source receipts privately.

```sh
mkdir -p local-projects/demo
python results_store.py --db local-projects/demo/results.sqlite3 init
python results_store.py --db local-projects/demo/results.sqlite3 import examples/fictional-results.json
python results_store.py --db local-projects/demo/results.sqlite3 gate result fictional-attempt-01
python results_store.py --db local-projects/demo/results.sqlite3 query queries/attempt_outcomes.sql
python results_store.py --db local-projects/demo/results.sqlite3 query queries/cost_comparison.sql
python results_store.py --db local-projects/demo/results.sqlite3 query queries/failure_evidence.sql
python results_store.py --db local-projects/demo/results.sqlite3 query queries/cause_hypotheses.sql
```

The fictional result gate deliberately exits 1: the invented output failed visual review and was never listened to. It is not real production evidence. A gate returns 0 only when its recorded requirements pass; the output still states its evidence limitations. Other validation errors exit nonzero. Import returns the number of inserted records; importing the same IDs and bytes again returns zero.

Make a private JSON bundle following [the import schema](schemas/results.schema.json). Records must be in dependency order: attempt before events, parent before retry, output before review. Use UTC timestamps in `YYYY-MM-DDTHH:MM:SSZ` form for the recorded action/review time, not an invented generation time. Unknown measurements/identities use `null`, never zero, a guessed UUID, or a fake hash. Zero means a known zero. Unknown review status is `unverified`; unknown job state is `unknown`. Prompt and shot text must actually exist to create an attempt; draft text is not an approved submission.

Import schema version 2 distinguishes `planned_submission` from `historical_attempt`. Historical prompts retain their exact original bytes even if they predate the CUT rule; their shot segmentation is descriptive and they cannot pass the pre-generation gate. Never rewrite historical prompts to satisfy a new rule. New submissions must enforce CUT as below.

An attempt stores the submitted brief ID/version/hash separately from the latest owner brief recorded by each review, plus project and stable prompt ID/version; exact UTF-8 prompt and SHA-256; ordered shot blocks; ordered reference IDs, hashes and roles; model/settings; audio intent; quote amount/unit/evidence; optional parent attempt and explicit retry changes. Compute the prompt hash over the exact submitted string with no normalization. For a planned submission, the prompt must equal shot blocks joined by a newline, literal uppercase `CUT`, and a newline. Every declared shot transition therefore contains `CUT`; a single-shot prompt has none. The human auditor still checks for undeclared transitions hidden inside prose. Prompt versions cannot silently refer to changed bytes. Each record also gets a canonical JSON SHA-256, covering settings and reference order. Declared asset hashes still require comparison with actual private bytes; the importer does not fetch assets.

Append separate records for:

| Kind | Recorded content |
| --- | --- |
| `audit` | Prompt auditor, decision, brief/CUT/reference/binding/performance/dialogue/settings checks, findings and evidence |
| `job` | Provider, job ID, observed status and private receipt locator |
| `cost` | Actual cumulative attempt cost, its unit and receipt evidence; append later corrections |
| `output` | Exact output hash, asset ID, duration and whether an audio track exists |
| `review` | Independent checker, exact output record, outcome, visual/audio methods and findings, watched/listened ranges, observed defects with output-relative timestamps, separate suspected causes with confidence/evidence |
| `feedback` | Owner, exact feedback, optional acceptance/rejection/revision decision and evidence |

Each review records independent `submitted_brief_compliance` and `current_brief_compliance`, plus acceptance checks naming which brief they assess. A clip may meet its submitted instructions yet fail the latest owner brief. Classify observations as `model_noncompliance`, `planning_omission`, `current_brief_change`, `technical_failure` or `unknown`; never automatically label an omitted direction as model noncompliance. The checker must justify that classification with evidence. Unknown brief IDs/versions/hashes stay null. Latest means current at that review time; a new owner brief requires a new review, not rewriting old evidence.

Empty defects means no recorded defects, not proof of a flawless result. Suspected causes remain hypotheses even at high confidence; `null` confidence means unknown. Evidence lists can be empty for an untested hypothesis. Do not label prompt length, reference count or model behavior as a proven cause without supporting comparisons. Capture failures as well as successes and retain owner feedback verbatim in private storage.

## Two independent gates

Before submission, import the immutable attempt and audit, then run `gate prompt ATTEMPT_ID`. It requires a passing audit with evidence, resolved checks, known model/settings/audio intent and known IDs/hashes for listed references. A job already recorded means this is no longer a pre-generation gate. Quote completeness, owner spending limits, provider support and execution permission remain separate workflow gates: an audit is never permission to spend.

After generation, import actual job/output records and the independent review, then run `gate result ATTEMPT_ID`. It requires a completed identified job, an audit before job history, the latest output hash, and a checker identity different from the prompt auditor. The latest review must identify the current owner brief and pass its compliance and acceptance checks, then accept that output with no unresolved defects, full normal-speed visual playback and—when audio is expected or present—full direct listening. An intentional no-audio output needs explicit not-applicable audio review, not fake dialogue. A silent shot with ambience/effects still requires listening. Metadata, audio-track presence, ASR and sampled frames cannot satisfy these gates. Record per-line voice/word/timing and seam details using the existing [continuity guidance](CONTINUITY.md); this ledger does not replace those checks or release approval.

A later output invalidates an earlier review. Later review records may supersede findings only with actual re-review and a clear disposition in notes; old records remain. Review all rejected, failed, repair and keep-fragment attempts, recording unreviewable failures as `unverified` with reasons rather than inventing footage evidence. Provider failures without output retain job/receipt and feedback records; no output review can be claimed.

## History, migrations and analysis

Imports are transactional. Record IDs are immutable: identical repeats are no-ops; conflicting content rolls back the whole import. Equivalent same-time events under another ID are rejected, and a provider job cannot be assigned to a second attempt. Append new status/cost/review records with new IDs and actual later timestamps. Retry attempts require an existing same-project parent and a nonempty changes list; a new prompt needs a new version. History is never overwritten by retry results. Different timestamps/IDs do not establish distinct real-world observations; the ingesting reviewer must retain stable source record IDs.

[Migration 001](migrations/001_results.sql) creates the tables, views and update/delete rejection triggers. [Migration 002](migrations/002_brief_analysis.sql) adds brief-compliance, classified-defect and acceptance-check views without modifying historical rows. Version-1 database records remain queryable; missing brief provenance stays unknown and blocks gates instead of being invented. New imports require version 2 and its explicit fields; do not rewrite or reimport existing record IDs to backfill history. `PRAGMA user_version` tracks the schema; initialization is atomic and repeatable, and unsupported versions fail. Add a numbered migration and compatibility tests before changing the schema; never rewrite an applied migration or silently reset a private database. Triggers protect the application workflow, not against someone modifying the file or disabling triggers directly. Hashes are integrity aids, not signatures or authenticated provenance.

Queries run through a read-only SQLite authorizer. [Attempt outcomes](queries/attempt_outcomes.sql) include retry ancestry/changes; [cost comparison](queries/cost_comparison.sql) uses the latest cumulative actual total, compares matching units only, and leaves missing values NULL. [Failure evidence](queries/failure_evidence.sql) and [cause hypotheses](queries/cause_hypotheses.sql) deliberately remain separate. Views include historical reviews: count distinct attempts for attempt failure rates and explicitly select latest reviews if studying current dispositions. Recorded outcomes are not computed gate passes. Do not infer causation from small observational samples or compare attempts without considering model/settings/references and multiple simultaneous changes.

Use [brief compliance](queries/brief_compliance.sql) to compare the two compliance judgments, and the `classified_defects` and `acceptance_checks` views for their detailed evidence.

These records stay local. Repository-only workflow is supported; no plugin loading or synchronization is required.

## Independent observation and hypothesis analytics

[findings_store.py](findings_store.py) imports complete findings into a separate append-only SQLite table using [the findings schema](schemas/findings.schema.json). This closes the gap between aggregate review checks and independently queryable observations/hypotheses. It preserves qualitative confidence verbatim, optional numeric confidence, source evidence/details, attempt links, source-document hash, recorded time, unknown observation time and whether the source is a summary. Empty attempt links mean unresolved association, not a guessed attempt; details may retain unresolved observation IDs. No finding import changes a review outcome or grants acceptance.

```sh
python findings_store.py --db local-projects/demo/results.sqlite3 examples/fictional-findings.json
python results_store.py --db local-projects/demo/results.sqlite3 query queries/observations.sql
python results_store.py --db local-projects/demo/results.sqlite3 query queries/hypotheses.sql
```

[Migration 003](migrations/003_findings.sql) adds `findings`, `current_findings` and `finding_analysis` without modifying existing rows. The database is now version 3; production-record imports remain schema version 2 and findings imports use their own version 1. Findings require stable source IDs. Exact repeats insert zero; conflicting IDs or duplicate roots are rejected atomically. Corrections use a new immutable ID with `supersedes` pointing to the current revision of the same kind/source ID; branches are rejected. All historical rows remain queryable in `findings`, while the bundled queries show current revisions. Missing source records remain missing—never synthesize them from a related hypothesis. Record quality defects independently from an owner's decision to keep a fragment for later editing.
