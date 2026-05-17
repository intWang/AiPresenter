# Cycle 176 Technical Scan: Document Presenter Meta Routing

Date: 2026-05-17

## Scope

- Inspected `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.
- Inspected `src/ai_presenter/runtime/questions.py` at `b5db04c`.
- Inspected `tests/unit/test_questions.py`.
- Inspected docs/knowledge invariant tests in `tests/unit/test_material_packages.py`.
- Did not modify source, tests, RingCentralVideo YAML, or git staging.
- Existing dirty file before this scan: `.coverage`.

## Current Baseline

`runtime-safety-routing.md` already documents the main RingCentralVideo safety model:
Q&A-first routing, package aliases after Q&A, `questionPolicy: answerOnly`,
`_can_operate(...)`, `create_question_interrupt_step(...)`, tone as style-only,
and current localization/diagnostics counts.

The code now has one more stable runtime pattern that is not yet documented there:
Presenter expression/meta requests are handled in `src/ai_presenter/runtime/questions.py`,
not in `packages/ringcentral-video.yaml`.

Current anchors:

- `_PRESENTER_META_REQUEST_ANSWER` and `_PRESENTER_META_REQUEST_FRAGMENTS` live at `questions.py:224`.
- `_answer_question(...)` runs `_match_qa(...)` before checking `_is_presenter_meta_request(...)`.
- If a prompt is meta, `_answer_question(...)` uses `_match_explicit_entrypoint(...)` instead of broad token fallback.
- Pure meta prompts return the Presenter settings answer with `entrypoint_id=None` and `can_operate=False`.
- Mixed meta plus explicit RingCentralVideo intent can still route through Q&A, package alias, meeting-info location lookup, or entrypoint title.
- `_match_contained_qa_question(...)` runs inside `_match_qa(...)` before alias/location guards, protecting authored Q&A embedded in longer prompts.

## Recommended Slice

Make a documentation-only update to `docs/knowledge/ringcentral-video/runtime-safety-routing.md`.

Add a concise section, probably after `Tone Is Style-Only`, named something like
`Presenter Meta Requests Are Runtime Guards`.

The section should say:

- Presenter expression requests such as language, tone, pacing, brevity, and beginner guidance are runtime question-routing guards.
- They are not RingCentralVideo app facts, aliases, Q&A, localization, or YAML metadata.
- Q&A-first still wins before Presenter meta handling.
- Contained authored Q&A must still win before package aliases when a style modifier is prepended.
- Pure meta requests are answer-only: no RingCentralVideo entrypoint, `can_operate=False`, and no interrupt step.
- Mixed requests with explicit RingCentralVideo intent still route through the explicit route path and keep existing operation gates.
- Broad CJK fragments are risky. Avoid bare terms such as standalone language, safety, privacy, status, or tone words as meta guards or Q&A fragments unless focused tests prove they cannot steal app routes.

Do not edit `packages/ringcentral-video.yaml`. This slice should not change package counts, localization reports, doctor diagnostics, runtime languages, voice settings, or live RingCentral acceptance claims.

## Exact Files To Edit

- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  - Add the short Presenter meta section.
  - Keep it as policy/maintenance guidance, not new behavior evidence.
  - Do not change current count bullets unless a separate package/YAML slice changes counts.

- `tests/unit/test_material_packages.py`
  - Extend `test_ringcentral_knowledge_docs_preserve_evidence_boundaries` with one or two stable assertions that the runtime doc preserves the new boundary.
  - Recommended assertion fragments:
    - `"Presenter expression requests"`
    - `"not RingCentralVideo app facts, aliases, Q&A, localization, or YAML metadata"`
    - `"Pure meta requests are answer-only"`
  - Keep the existing negative-overclaim checks intact.

No other tests should need edits for the documentation-only slice.

## Existing Test Patterns To Reuse

Docs/knowledge invariants:

- `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries`
  - Reads `runtime-safety-routing.md` and asserts durable safety/evidence wording.
  - Best place to lock this new doc boundary.
- `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes`
  - No edit needed because this updates an existing registered doc.
- `tests/unit/test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes`
  - No edit needed, but useful if running the local docs/knowledge sentinel group.
- `tests/unit/test_material_packages.py::test_ringcentral_source_index_test_references_exist`
  - No edit needed unless `source-index.md` is touched, which this slice should avoid.

Runtime behavior already covered:

- `tests/unit/test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls`
- `tests/unit/test_questions.py::test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls`
- `tests/unit/test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents`
- `tests/unit/test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents`
- `tests/unit/test_questions.py::test_chinese_bare_safety_words_do_not_match_presenter_meta_or_security`
- `tests/unit/test_questions.py::test_chinese_presenter_meta_mojibake_does_not_match`

Diagnostics/count sentinels to keep unchanged:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package`
- `tests/unit/test_cli.py::test_doctor_reports_question_alias_and_qa_diagnostics`

Current expected count strings include `165 package-owned aliases`, `220 Q&A question prompts`,
and the existing INFO-level `qa alias substring risk`. A docs-only slice should not change them.

## Focused Commands

For the docs-only implementation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes
git diff --check -- docs\knowledge\ringcentral-video\runtime-safety-routing.md tests\unit\test_material_packages.py
```

If the implementer wants to prove the documented behavior still matches runtime:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_bare_safety_words_do_not_match_presenter_meta_or_security tests\unit\test_questions.py::test_chinese_presenter_meta_mojibake_does_not_match
```

If any YAML, alias, Q&A, or diagnostic wording is accidentally touched, broaden to:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_reports_question_alias_and_qa_diagnostics
```

## Risks

- Documentation drift: describing Presenter meta as a package rule would imply future YAML edits. Keep it explicitly runtime-only.
- Overclaim risk: do not say the Presenter settings answer changes persistent voice settings. It only answers the runtime question safely.
- Route-order risk: the doc should preserve Q&A-first and contained-QA-before-alias, not imply meta handling is the first gate.
- CJK fragment risk: broad terms can steal RingCentralVideo privacy, status, security, meeting-info, notes/transcript, recording, chat, participant, share, or host-control prompts. Document the risk without adding new fragments.
- Count churn risk: editing YAML or adding package Q&A would change alias/Q&A counts and doctor diagnostics. That is outside this slice.
- Acceptance-evidence risk: this is repo-local routing documentation, not live RingCentral acceptance evidence.

## Status

Technical scan complete. Source, tests, and knowledge docs were inspected only. This handoff is the only intended file change.

Changed file: `docs/agent-handoffs/cycle-176-technical-scan.md`
