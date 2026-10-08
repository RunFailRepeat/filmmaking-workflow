# Filmmaking workflow

A reference-first planning and review kit for AI-assisted shorts. It helps define shots, preserve continuity, review actual footage and control approvals. It does not generate media or authorize spending.

- [Workflow](WORKFLOW.md)
- [Planning duration/coverage contracts and owner-selected workflow sources](PLANNING.md), [planning schema](schemas/plan.schema.json), [fictional plan](examples/fictional-plan.json), and [work-cycle record](templates/work-cycle.md)
- [Content analytics definitions and exploratory timing proposal](ANALYTICS.md)
- [Reference transfer routes and verification checklist](MEDIA_TRANSFERS.md)
- [Production packet template](templates/production.md)
- [Packet checker](check_packet.py)
- [Check evidence](evidence/checks.md)
- [Reusable shot JSON schema](schemas/shot.schema.json) and [fictional example](examples/fictional-shot.json)
- [Voice, camera and finishing gates](CONTINUITY.md), [continuity schema](schemas/continuity.schema.json), [fictional packet](examples/fictional-continuity.json) and [recorded-evidence validator](validate_continuity.py)

## Run the checks

Python 3 standard library only. Review the scripts before execution.

```sh
python -m unittest discover -s tests -v
python check_packet.py templates/production.md
python validate_shot.py examples/fictional-shot.json
python validate_plan.py examples/fictional-plan.json
python validate_continuity.py examples/fictional-continuity.json preflight
```

The templates intentionally fail readiness because fields or approvals are unresolved. Fill a copy outside this public repository. The continuity validator has preflight, enhancement and release stages. It checks declared voice/take bindings, camera changes, final-listening records and enhancement approvals; it never listens to media or authenticates approvals. The basic packet checker checks explicit fields and approval markers, not creative quality or rights validity.

## Status and scope

This repository contains reusable guidance, original utility code and synthetic test evidence. It contains no private production scripts, characters, reference images or completed-film claims. Review substantial changes through a draft PR. No automatic merge, release, paid retries or model execution.

Public availability does not grant rights to third-party models or assets. No third-party source code, model weights or private production material is distributed.

Roadmap: evaluate a real approved production packet, add immutable job-ledger and editable-timeline interchange schemas, and validate those with actual reviewed exports. No provider integration, footage QA automation or production-quality result is implemented. The JSON Schema defines field constraints; validate_shot.py also checks edit duration against source duration. Neither verifies approvals or media.
