# Cycle 110 Test/Code Review

Date: 2026-05-16
Reviewer: Codex
Scope reviewed: current Cycle 110 working-tree changes only. Existing `.coverage` dirtiness was ignored.
Note: `docs/agent-handoffs/cycle-110-experience.md` appeared untracked after the initial status check. I read it during final sanity review, left it untouched, and treat it as a docs-only aligned handoff that should be staged only if its owner intended it for this cycle.

## Verdict

Approve.

Cycle 110 stays within the requested test-only plus docs scope. I found no production code, package YAML, localization, or diagnostics changes in the working-tree diff. The added regression in `tests/unit/test_questions.py` is table-driven, avoids exact `answer_text` equality across tones, includes blocked sensitive routes and positive operable sentinels, and explicitly pins the professional baseline route tuple before comparing other tones.

## Findings

No blocking findings.

Review notes:

- `tests/unit/test_questions.py:405` adds one parametrized matrix for the RingCentral sensitive route-parity regression.
- `tests/unit/test_questions.py:414` and `tests/unit/test_questions.py:416` cover answer-only privacy/Q&A routes with `entrypoint_id is None`.
- `tests/unit/test_questions.py:415`, `tests/unit/test_questions.py:422`, `tests/unit/test_questions.py:423`, and `tests/unit/test_questions.py:425` cover blocked routed entrypoints for meeting info, invite, screen share, and leave.
- `tests/unit/test_questions.py:424` and `tests/unit/test_questions.py:426` provide positive operable sentinels for Participants and Network quality. The `participants` expectation is consistent with the current package policy: the plain panel route has `openSteps` and is not risky-word blocked, while the separate host-control/name-reading prompts remain answer-only in existing tests.
- `tests/unit/test_questions.py:443` through `tests/unit/test_questions.py:445` explicitly assert the professional baseline expected `entrypoint_id`, `can_operate`, and interrupt presence, so baseline drift cannot hide a tone-parity failure.
- `tests/unit/test_questions.py:447` compares the required tones: `friendly`, `coach`, `support`, and `privacy`.

## Test Gaps

- I did not require a full all-tone matrix for `conversational`, `concise`, `formal`, or canonical `careful`; the implemented matrix matches the requested professional baseline plus friendly/coach/support/privacy tones.
- The host-controls privacy Q&A already has professional/privacy coverage nearby, but it is not included in the new friendly/coach/support/privacy matrix. This is acceptable for Cycle 110 because the new matrix includes a chat/participant-content privacy Q&A row plus routed blocked prompts; it could be a future small expansion if the team wants every participant-sensitive Q&A phrasing cross-toned.
- Localized cross-tone parity is not added in this cycle. Existing localized safety tests remain separate.
- I did not run the full suite; see recommended verification below.

## Verification Run

Passed:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant -q -o addopts=""
```

Result: `9 passed in 1.65s`.

Passed:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_questions.py::test_meeting_info_privacy_gate_does_not_depend_on_risky_words tests\unit\test_questions.py::test_notes_privacy_gate_does_not_depend_on_risky_words -q -o addopts=""
```

Result: `12 passed in 2.34s`.

Recommended before merge if time allows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o addopts=""
```

## Commit Readiness

Ready to commit after adding this review document. Stage the Cycle 110 files only:

- `tests/unit/test_questions.py`
- `docs/agent-handoffs/cycle-110-demand-analysis.md`
- `docs/agent-handoffs/cycle-110-experience.md`, if the late-arriving handoff is intended for this cycle
- `docs/agent-handoffs/cycle-110-technical-scan.md`
- `docs/agent-handoffs/cycle-110-risk-scan.md`
- `docs/agent-handoffs/cycle-110-test-review.md`

Do not stage `.coverage`.
