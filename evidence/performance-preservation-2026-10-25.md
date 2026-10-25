# Performance preservation verification — 2026-10-25

Base: `64383bce7954f0a7ab0ddf21aff63a24ee0121ba`. Work isolated on local branch `draft/performance-preservation`; prior clean Jev checkout and older dirty toolkit checkout left untouched. No applicable repository/ancestor AGENTS.md or .agents/skills were found in inspected paths. Original clean checkout rechecked at the same base. Exact edit ownership was recorded outside the repository before edits.

Changed paths: README.md; PERFORMANCE.md; RESEARCH_SOURCES.md; templates/performance-review.md; validate_performance.py; schemas/performance.schema.json; examples/fictional-performance.json; tests/test_performance.py; this evidence file. All other tracked base files, including Jev clients/tests, remain unchanged.

Separate implementation and independent review agents examined the changes. Review prompted explicit owner-heard evidence distinct from a technical listener's approval, SHA-256 source bindings, voice type and approved parameter equality, expanded hearing checks, and known-model rejection of unsupported controls even when supplied contract metadata claims support. Review finished with no blocking findings.

Validation on the final implementation:

- `python3 -m unittest discover -s tests -v`: 153 passed, including 15 new performance tests.
- `python3 validate_performance.py examples/fictional-performance.json acceptance`: passed; explicitly synthetic declared evidence, no media-quality verdict.
- `python3 validate_shot.py examples/fictional-shot.json`: metadata valid.
- `python3 validate_plan.py examples/fictional-plan.json`: metadata consistent.
- `python3 validate_continuity.py examples/fictional-continuity.json preflight`: expected exit 1 for missing heard owner approval and unreviewed actual payload in the existing unfinished fixture.
- `python3 check_packet.py templates/production.md`: expected exit 1 for unresolved template fields/approvals.
- JSON parsing, changed-document relative links and `git diff --check`: passed.
- Private canon preparation: three checks passed, including missing/duplicate/reordered/changed dialogue rejection, packet hash and byte-identical source copies. Private scripts/media/IDs are outside this repository.

The new validator is additive and not connected to provider execution or canonical action ledgers. It checks a single character's declared normal-speed contiguous recording with identical prefix cues. It does not authenticate documents or signatures, fetch capability contracts, listen, judge excitement, verify real bindings or a multi-speaker final edit. Synthetic passing evidence is not a real accepted performance. Guidance covers the broader manual workflow and explicitly records these implementation limits.

No provider jobs, paid generation, uploads, merge, deploy, installation, GPU, browser UI or input focus was used. Public source text was retrieved through read-only web tools. No licensed full-book text was imported. Plugin/repository release synchronization and remote publication are outside this local change; no push or PR was created.
