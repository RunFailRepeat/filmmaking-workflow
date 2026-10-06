# Reproducible check evidence

Checked 2026-10-06 with Python 3 standard library only.

- python -m unittest discover -s tests -v: 35 tests passed.
- python validate_shot.py examples/fictional-shot.json: metadata valid.
- The unfilled Markdown template is expected to fail check_packet.py readiness.
- The fictional continuity packet conforms to the bundled shape but intentionally fails preflight/enhancement/release approval gates. No actual audio or export exists.

Continuity tests cover invented consistent records, missing audio/voice data, unapproved/unheard takes, changed take/type/version, per-film auditions, reordered bindings, unsupported routes, missing payload review, direct-edit plans and replacement completion, removed/changed audio, lens/framing/focus/movement changes, accent/word/take mismatches, ASR/unavailable listening, every line and audio check, stale export review, picture/edit and paid enhancement approval, exact enhanced-export comparison and retention. Positive fixtures are fabricated declarations, not real approvals or production results.

Transition tests reject tiny/identical sequential cuts unless an explicit approved continuous-shot exception applies; fixed-start-frame assumptions require supported alternative coverage or verified trim handles. Normal-speed seam review must target the actual export, with pose/action/voice/sound/timing and no-duplicate/no-frozen-overlap checks. No footage was generated or watched for these tests.

Cross-surface review repairs add actual-output angle/shot-size, axis, direction, eyeline, props/environment and sound-effect findings. Tests reject missing/fail/unverified findings while retaining an approved continuous-shot exception. Listening provenance tests require a listener, timezone-qualified timestamp, exact export asset, finite bounded per-line ranges and complete listened-range coverage. Negative cases cover missing fields, placeholders, stale assets, gaps, invalid numeric values and sound effects failing despite ambience passing. All identities, timestamps and ranges in positive fixtures remain synthetic, not evidence of actual playback.

Coverage: missing fields/approvals, duplicate approval fields, nonfinite duration, unresolved ending, edit-range overrun, missing camera and invalid review coverage. The example is newly invented, not a private production shot or generated result.

Schema string patterns are also checked against the fictional field values and whitespace-only input. This regression check uses the patterns loaded from the actual JSON schema; the existing non-whitespace patterns passed unchanged.

Source review: scripts read text/JSON and print diagnostics; no network, dependencies, subprocesses, writes, billing or model execution. No actual footage was reviewed. These checks cannot authenticate approvals, prove rights or judge cinematography.
