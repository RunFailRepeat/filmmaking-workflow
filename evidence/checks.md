# Reproducible check evidence

Checked 2026-10-06 with Python 3 standard library only.

- python -m unittest discover -s tests -v: 10 tests passed.
- python validate_shot.py examples/fictional-shot.json: metadata valid.
- The unfilled Markdown template is expected to fail check_packet.py readiness.

Coverage: missing fields/approvals, duplicate approval fields, nonfinite duration, unresolved ending, edit-range overrun, missing camera and invalid review coverage. The example is newly invented, not a private production shot or generated result.

Schema string patterns are also checked against the fictional field values and whitespace-only input. Publication review corrected an over-escaped non-whitespace pattern; this regression check uses the patterns loaded from the actual JSON schema.

Source review: scripts read text/JSON and print diagnostics; no network, dependencies, subprocesses, writes, billing or model execution. No actual footage was reviewed. These checks cannot authenticate approvals, prove rights or judge cinematography.
