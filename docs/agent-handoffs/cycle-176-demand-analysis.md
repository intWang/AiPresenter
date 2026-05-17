# Cycle 176 Demand Analysis: Promote Presenter Meta Routing Knowledge

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle176 demand-analysis handoff

## Scope And Boundary

This pass only writes this handoff:

- `docs/agent-handoffs/cycle-176-demand-analysis.md`

No source, test, package YAML, coverage, staging, or commit changes were made.
The working tree already had `.coverage` dirty before this handoff; treat it as
unrelated existing work.

## Sources Read

- `docs/agent-handoffs/cycle-174-experience.md`
- `docs/agent-handoffs/cycle-175-experience.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- Focused docs/knowledge test patterns in `tests/unit/test_material_packages.py`
- Focused RingCentral knowledge indexes:
  - `docs/knowledge/ringcentral-video/source-index.md`
  - `docs/knowledge/ringcentral-video/evidence-index.md`

## User Need

Cycles 174 and 175 established a practical runtime lesson: when users ask
AiPresenter to change how it answers, they are not asking RingCentral Video to
move the meeting UI.

Examples include:

- language requests such as `Answer in Chinese`, `Answer in English`, or
  Chinese equivalents
- tone requests such as `Switch to careful tone`, `Use privacy tone`, or
  friendlier/more professional Chinese phrasing
- detail and pacing requests such as `Be more concise`, `Explain more slowly`,
  `Please make it simpler`
- familiarity requests such as `I am new to RingCentral Video` or Chinese
  beginner/familiarity prompts

The user-facing need for Cycle176 is knowledge durability. Future agents should
not have to rediscover that Presenter expression requests belong in runtime
question routing as answer-only guards, not in the RingCentralVideo package YAML,
aliases, or Q&A content. The RingCentral Video runtime safety knowledge package
should capture the lesson clearly enough that the next implementation or review
cycle can preserve it without reading every Cycle174/175 handoff.

## Target Docs

Primary target:

- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`

Recommended placement inside that file:

- Add a short section after `Tone Is Style-Only`, tentatively titled
  `Presenter Meta Requests Are Answer-Only`.
- Extend `Current Runtime Anchors` with a concise maintainer rule for Presenter
  meta routing, if the section alone does not make the boundary visible enough.
- Optionally add Cycle174 and Cycle175 rows to `Recent Cycle Anchors`, but only
  if stable commit identifiers are available in the implementation cycle. Do not
  invent commit hashes or imply merged history without evidence.

Secondary target, only if a test edit is in scope for the implementation cycle:

- `tests/unit/test_material_packages.py`

Existing pattern confirmed:

- `test_ringcentral_knowledge_docs_preserve_evidence_boundaries` reads
  `runtime-safety-routing.md` and asserts literal docs-contract phrases.
- `test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes` keeps
  `docs/knowledge/ringcentral-video/*.md` registered in source/evidence indexes.

Because the primary target is an existing registered doc, `source-index.md` and
`evidence-index.md` should not need navigation updates for this slice.

## Recommended Scope

Recommended implementation slice:

1. Update `docs/knowledge/ringcentral-video/runtime-safety-routing.md` with a
   durable Presenter meta routing rule.
2. Explain that Presenter expression requests are runtime guards:
   Q&A-first safety still wins, pure meta requests return no entrypoint and no
   operation, and mixed prompts may route only through explicit RingCentralVideo
   Q&A, aliases, meeting-info location lookup, or entrypoint titles.
3. State explicitly that Presenter meta prompts do not belong in
   `packages/ringcentral-video.yaml`, because they are AiPresenter behavior
   requests rather than RingCentralVideo product knowledge.
4. State explicitly that language/tone/detail/familiarity text must not change
   route choice, `entrypoint_id`, `can_operate`, `questionPolicy`, or interrupt
   creation.
5. Add a small docs-contract test only if the implementation cycle is allowed to
   modify tests. The smallest test is an adjacent assertion in
   `test_ringcentral_knowledge_docs_preserve_evidence_boundaries`, or a tiny new
   test near it, that checks for the new runtime-safety boundary phrases.

Suggested docs wording to preserve:

- `Presenter expression requests are runtime answer-only guards, not
  RingCentralVideo package aliases or Q&A.`
- `Pure Presenter meta requests should not produce an entrypoint, operation
  permission, or question interrupt.`
- `Language, tone, detail, and familiarity wording may change answer style, not
  route choice or safety policy.`
- `Do not claim persistent language or tone state changes unless controller or
  voice state mutation is implemented and tested.`

Suggested small test shape:

```python
runtime_text = Path(
    "docs/knowledge/ringcentral-video/runtime-safety-routing.md"
).read_text(encoding="utf-8")

assert (
    "Presenter expression requests are runtime answer-only guards"
) in runtime_text
assert "not RingCentralVideo package aliases or Q&A" in runtime_text
assert "should not produce an entrypoint" in runtime_text
assert "Do not claim persistent language or tone state changes" in runtime_text
```

Keep the test literal and narrow. Do not add a markdown parser or broaden this
into a full documentation linter.

## Acceptance Criteria

For a future implementation cycle, acceptance should require:

- `runtime-safety-routing.md` contains a dedicated Presenter meta routing rule
  covering language, tone, detail, pacing, and familiarity requests.
- The doc preserves Q&A-first ordering: safety Q&A must still beat Presenter
  meta and broad token fallback.
- The doc says pure Presenter meta prompts are answer-only, non-operable, and
  no-interrupt.
- The doc says mixed prompts may route RingCentralVideo only through explicit
  package Q&A, aliases, meeting-info location lookup, or entrypoint titles.
- The doc says Presenter meta requests do not belong in
  `packages/ringcentral-video.yaml`.
- The doc says language/tone/detail/familiarity wording must not change
  `entrypoint_id`, `can_operate`, `questionPolicy`, or
  `create_question_interrupt_step(...)`.
- The doc does not claim live RingCentral acceptance, persistent voice state
  mutation, or durable user preference storage.
- If tests are allowed, a small existing-pattern docs-contract assertion guards
  the new rule in `tests/unit/test_material_packages.py`.
- If tests are not allowed, the implementation should at least run
  `git diff --check -- docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  and report that the test guard was intentionally deferred.

Suggested focused verification if tests are edited:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes
git diff --check -- docs\knowledge\ringcentral-video\runtime-safety-routing.md tests\unit\test_material_packages.py
```

## Non-Goals

- Do not modify runtime question routing in this slice.
- Do not modify `src/ai_presenter/**`.
- Do not modify `packages/ringcentral-video.yaml`.
- Do not add RingCentralVideo aliases, localized aliases, Q&A items, localized
  Q&A, demo flows, entrypoints, or package diagnostics.
- Do not implement persistent natural-language language/tone/detail/familiarity
  settings.
- Do not change controller UI, CLI flags, provider support, SAPI/Piper/OpenAI
  behavior, or profile compatibility.
- Do not broaden the Presenter meta matcher or add new multilingual runtime
  prompts as part of the docs promotion.
- Do not claim live RingCentral acceptance or record acceptance evidence.
- Do not stage or commit `.coverage` or unrelated files.

## Risk Notes

- The main risk is overclaiming. A durable knowledge doc can accidentally sound
  like a runtime feature guarantee. Keep the language scoped to route safety
  policy and tested repo behavior.
- Avoid saying "AiPresenter switches to Chinese" or "tone is now privacy mode"
  unless a future slice actually mutates and tests voice/controller state.
- Avoid moving Presenter meta prompts into RingCentralVideo package content.
  That would blur Presenter behavior with product knowledge and create
  localization/diagnostic count churn.
- Keep the docs-contract test small. The goal is to preserve the safety
  boundary, not freeze every sentence in the runtime guide.

## Status

Cycle176 demand analysis complete. Recommended next slice: update
`docs/knowledge/ringcentral-video/runtime-safety-routing.md` to promote
Cycle174/175 Presenter meta routing lessons into the RingCentralVideo runtime
safety knowledge package, with a narrow docs-contract test in
`tests/unit/test_material_packages.py` only if tests are allowed in that cycle.

Changed file path:

- `docs/agent-handoffs/cycle-176-demand-analysis.md`
