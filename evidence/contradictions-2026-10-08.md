# Bounded contradiction review

Reviewed the repository workflow, production template, planning and continuity contracts, transfer guide, and currently readable plugin entrypoint and bindings/estimates reference. Private project guidance was not independently inspected in this repository task; its reconciliation remains with the owner/coordinating agent. No private project content was imported.

## Confirmed conflicts and corrections

- The production template directed all material into a dialogue-only schema, although PLANNING.md and CONTINUITY.md explicitly support silent planning outside that schema. The template now routes speaking material to dialogue checks and silent clips to visual/action planning plus actual human visual/sound review. The workflow's voice-payload instruction now explicitly applies to speaking shots.
- The plugin's instruction to verify pricing is read-only conflicts with tools that import URL references while estimating. MEDIA_TRANSFERS.md already describes this side effect and reuse of confirmed IDs/prepared parameters correctly. The main workflow now links that contract and makes transfer authority distinct from generation authority. No provider call was made to test side effects.
- Purposeful angle changes and avoiding frozen overlap were already explicit. Added only the missing distinction between director intent (performance, reaction, motion already in progress when requested) and mechanical inspection notes. Contact checks must not accidentally direct a held pose. No model failure is attributed to prompt length; controlled comparisons are hypotheses until supported by observations.
- Expanded existing reference readiness to required recurring wardrobe, locations, complex props and background ensembles. A structural pass cannot replace actual approved visual references or performance/footage review. Owner-authorized exploration with disclosed gaps remains exploration, with separate execution/spending gates.

## Fictional scenario review and executable checks

1. A silent adult moves a cup, followed by a silent reaction. Empty dialogue ledgers are valid for the entirely silent plan; no invented speech/voice approvals. Changing the incoming state still fails planning validation. Existing test_plan.py exercises these cases; final visual and sound review remains unverified until performed.
2. A confirmed fictional location ID already matches the intended source version and role. Reuse it for a supported estimate; do not reimport its URL. A new URL requires checking import side effects and transfer authority. Neither result grants generation approval. This is a guidance scenario, not an executed provider test.
3. A fictional adult is already walking and notices a dropped envelope. The prompt preserves ongoing movement, reaction and a motivated closer angle; foot/contact checks stay review criteria unless needed to constrain the physical action. No held starting pose is introduced solely to satisfy QA. No footage was generated or reviewed.
4. A recurring fictional uniform or intricate prop lacks approved visual references. Mark the design unresolved. Explicitly authorized exploration may test the gap within its approved scope, but a filled form or passing schema cannot relabel it production-ready.

Commands: `python -m unittest discover -s tests -p test_plan.py -v` (12 passed); `python -m unittest discover -s tests -v` (56 passed); `python validate_plan.py examples/fictional-plan.json` (planning metadata consistent only). Relative Markdown links, JSON parsing, privacy-string review and `git diff --check` passed. No runtime/schema changes or dependencies were needed for these wording corrections.

Plugin corrections and version/readback checks remain a separate guarded update. Do not claim alignment until the coordinating agent verifies it and reconciles private project guidance; preserve the result in a private work-cycle record.
