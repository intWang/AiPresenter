# Cycle 174 Follow-up Test Review

## Findings

No new blocking findings in the current uncommitted diff.

The earlier P2 is resolved by the current ordering in `src/ai_presenter/runtime/questions.py`: `_match_qa(...)` now runs before presenter meta handling, so RingCentralVideo privacy/security/host-control Q&A can still win when a style modifier is attached. Pure presenter meta requests return the `Presenter settings:` answer without an entrypoint or interrupt, while meta plus an explicit package alias/title/location can still route through `_match_explicit_entrypoint(...)`.

## P2 Resolution

Resolved.

Focused checks confirm the previously failing mixed-intent prompts now keep their RingCentralVideo intent:

| Prompt class | Current behavior |
| --- | --- |
| `Please be brief and read meeting information aloud` / `Use privacy tone and read meeting information aloud` | Meeting-info privacy Q&A, answer-only, no interrupt |
| `Be concise: is this meeting encrypted?` | Meeting-info security Q&A, answer-only, no interrupt |
| `Use coach tone and mute all participants` | Host-controls safety Q&A, answer-only, no interrupt |
| `Please be brief and go full screen` | Routes to `ringcentral.video.top.views`, remains operable, creates the safe interrupt |

The added tests in `tests/unit/test_questions.py` exercise both sides of the boundary: pure meta requests do not operate RingCentral controls, and mixed meta modifiers do not steal explicit RingCentralVideo safety/control intents.

## Verification Performed

- Reviewed the uncommitted diff for `src/ai_presenter/runtime/questions.py` and `tests/unit/test_questions.py`.
- Checked the new routing order around `answer_question(...)`, `_match_qa(...)`, `_is_presenter_meta_request(...)`, and `_match_explicit_entrypoint(...)`.
- Ran with system Python first:
  - `python -m pytest tests/unit/test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests/unit/test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls`
  - Result: blocked because system Python has no `pytest` module.
- Ran via repo venv with default coverage enabled:
  - `.\.venv\Scripts\python.exe -m pytest tests/unit/test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests/unit/test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls`
  - Result: all 15 selected tests passed, but pytest exited nonzero because partial coverage total was below the configured 80% fail-under.
- Ran the focused tests without coverage:
  - `.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests/unit/test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls`
  - Result: `15 passed in 4.09s`.
- Ran a broader related `test_questions.py` slice without coverage:
  - `.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_questions.py -k "presenter_meta or ringcentral_full_screen_questions_route_to_view_layout or english_invite_privacy_questions_stay_qa_first or meeting_info"`
  - Result: `129 passed, 261 deselected in 25.10s`.

## Residual Risks

- The meta fragment list remains English-only. That does not reopen the reviewed P2, but localized presenter-settings requests may still fall through to ordinary Q&A or entrypoint matching.
- Mixed meta prompts now route only when the RingCentralVideo intent is explicit enough for Q&A, a package alias, a location phrase, or a title match. That is consistent with the stated fix boundary, but fuzzy mixed commands without aliases may still answer as presenter meta.
- Partial pytest selections trip the repository coverage fail-under unless run with `--no-cov`; full coverage was not run in this follow-up review.

## Recommendation

Accept the follow-up fix. The P2 regression is covered by targeted tests, the safety-first ordering is restored, and pure presenter settings remain answer-only with no RingCentral operation.

## Status

Status: follow-up review complete; no source or test files were modified, staged, or committed.

Changed file: `docs/agent-handoffs/cycle-174-followup-test-review.md`
