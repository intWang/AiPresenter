# Cycle 163 Risk Scan: Q&A Prompt Privacy Expansion

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for the next small RingCentral Video prompt/privacy
improvement. This scan inspected:

- `tests/unit/test_questions.py`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- focused diagnostics and localization count expectations

Only this handoff file was written. No production files, test files, `.coverage`,
or acceptance evidence were modified. No full suite was run.

## Current Routing Facts

- `_match_qa()` checks exact normalized package Q&A prompts before entrypoint
  alias or token routing.
- A Q&A match returns the first `relatedEntrypointIds` value as
  `response.entrypoint_id`, then computes `can_operate` from that entrypoint.
- `create_question_interrupt_step(...)` returns `None` whenever
  `response.entrypoint_id is None` or `response.can_operate` is false.
- `ringcentral.video.top.meeting-info` and `ringcentral.video.more.notes` carry
  `questionPolicy: answerOnly`, so they stay non-operable even with open steps.
- Many privacy Q&A items intentionally omit `relatedEntrypointIds` so the answer
  can mention private surfaces without creating any entrypoint route.
- Current inventory expectations are `15/15` localized Q&A items and `139 Q&A
  question prompts` for duplicate and alias-overlap diagnostics.

## Risk Matrix

| Risk | Severity | Trigger | What Breaks | Guard |
| --- | --- | --- | --- | --- |
| Privacy Q&A becomes operable | High | New Q&A has `relatedEntrypointIds` pointing to an otherwise safe route, such as Chat, Participants, Settings, or Network quality | `response.can_operate` can become true and the controller may queue an interrupt step | Assert `response.can_operate is False` and `create_question_interrupt_step(package, response) is None` for every privacy prompt |
| Exact Q&A prompt shadows a location lookup | Medium | Adding broad prompts such as `chat`, `participants`, `notes`, `raise hand`, or `where is ...` under a privacy Q&A | User asks for location but receives a policy answer or `entrypoint_id is None` unexpectedly | Keep exact prompts command/privacy-shaped; preserve location tests like `Where is Raise hand?`, `Where are Reactions?`, and `Where are Notes and transcript` |
| Action verbs create thin entrypoint fallback | Medium | New prompt is not added to the intended Q&A item, so token routing falls through to entrypoint answer | The response starts with labels like `Meeting information:`, `Invite participants:`, or `Start recording:` instead of privacy guidance | Assert expected privacy answer fragments and assert thin fallback labels are absent |
| Alias diagnostics turn WARN | Medium | New Q&A prompt exactly equals a package-owned entrypoint alias outside its related entrypoint | Doctor reports `[WARN] qa alias overlap` and Q&A-first matching becomes ambiguous | Either avoid exact alias prompts or include the matching entrypoint in `relatedEntrypointIds` only when still safe |
| Substring risk count changes | Low/Medium | New Q&A prompt contains package-owned aliases for unrelated entrypoints, for example `chat`, `notes`, `invite`, `raise hand` | Doctor remains INFO but expected count can move from `11` to `12` or more | Update substring-risk expectation only when the new prompt is intentional and still Q&A-first safe |
| Prompt inventory counts go stale | Low | Adding exact English or localized Q&A prompts | Diagnostics and CLI tests still expect `139 Q&A question prompts` | Bump `139` to the new candidate count in diagnostics and doctor assertions |
| Q&A item localization counts go stale | Low | Adding a new top-level `qa:` item instead of only adding prompts to an existing item | `15/15` localized questions/answers becomes `16/16`, or localization completeness fails | Add zh/ja/es localized questions and answers for the new item, then update `qa_total` and CLI/diagnostic text expectations |
| Logs leak prompt or answer content | Low/Medium | Instrumenting new routing with raw question/answer logging | Private meeting IDs, links, names, or transcript requests could enter logs | Reuse existing logging tests that assert raw question and answer text are absent from messages |

## Recommended Negative Tests

Add narrow parametrized cases to existing tests rather than new broad fixtures.
Recommended negative coverage for privacy/action prompts:

- For copy/read/send/open/start/summarize prompts, assert no interrupt:
  `assert create_question_interrupt_step(package, response) is None`.
- For prompts about private values, assert no thin fallback route text:
  `assert "Meeting information:" not in response.answer_text`,
  `assert "Invite participants:" not in response.answer_text`,
  `assert "Start recording:" not in response.answer_text`, or
  `assert "Notes and transcript:" not in response.answer_text`.
- For prompts that should not operate a live control, assert the risky route is
  not selected, especially when the target route would otherwise be safe:
  `assert response.entrypoint_id != "ringcentral.video.toolbar.chat"`,
  `assert response.entrypoint_id != "ringcentral.video.toolbar.participants"`,
  `assert response.entrypoint_id != "ringcentral.video.toolbar.react"`,
  `assert response.entrypoint_id != "ringcentral.video.toolbar.raise-hand"`.
- For exact privacy prompts without a safe entrypoint, prefer:
  `assert response.entrypoint_id is None`.
- For prompts that may mention a sensitive entrypoint but must be answer-only,
  prefer:
  `assert response.entrypoint_id == "<expected sensitive entrypoint>"`,
  `assert response.can_operate is False`, and
  `assert create_question_interrupt_step(package, response) is None`.

Good existing negative-test templates:

- `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first`
- `test_ringcentral_english_invite_privacy_questions_stay_qa_first`
- `test_ringcentral_english_recording_action_questions_stay_qa_first`
- `test_ringcentral_english_leave_end_questions_stay_qa_first`
- `test_ringcentral_english_notes_action_requests_do_not_match_start_meeting`
- `test_ringcentral_english_transcript_content_requests_stay_answer_only`
- `test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only`
- `test_ringcentral_japanese_reaction_send_requests_stay_non_operable`
- `test_ringcentral_japanese_raise_hand_toggle_requests_stay_non_operable`
- `test_ringcentral_japanese_host_signal_control_requests_stay_non_operable`

## Recommended Positive Tests

Preserve location and benign lookup behavior near any new privacy prompts:

- If adding chat or participant privacy prompts, keep location questions
  separate from content-reading questions.
- If adding reaction or raise-hand safety prompts, keep English location routing:
  `Where is Raise hand?` should still produce
  `ringcentral.video.toolbar.raise-hand` and start with `Raise hand:`.
- If adding notes/transcript action prompts, keep location prompts routing to
  `ringcentral.video.more.notes` but still non-operable.
- If adding meeting-info privacy prompts, keep `meeting information`,
  `where is the meeting ID`, and `where is the meeting link` answer-only with no
  literal URL, host, or meeting ID values in the answer.
- If adding troubleshooting prompts, keep Network quality positive behavior only
  when the prompt is a diagnostic lookup, not a privacy or content request.

Good existing positive-test templates:

- `test_ringcentral_raise_hand_location_question_still_routes_to_entrypoint`
- `test_ringcentral_reactions_location_question_still_routes_to_entrypoint`
- `test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint`
- `test_ringcentral_show_me_where_notes_remains_location_lookup`
- `test_network_quality_question_remains_operable_without_answer_only_policy`
- `test_ringcentral_japanese_audio_troubleshooting_question_stays_qa_with_aliases`
- `test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table`
- `test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table`

## Exact Assertions To Reuse

Core answer-only assertions:

```python
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

No-route privacy answer:

```python
assert response.entrypoint_id is None
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

Sensitive-entrypoint answer-only route:

```python
assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

Meeting-link privacy answer family:

```python
assert "Meeting IDs and links are private meeting details" in response.answer_text
assert "Meeting information:" not in response.answer_text
assert create_question_interrupt_step(package, response) is None
```

Meeting-info value leakage guard:

```python
assert "https://" not in response.answer_text
assert "ringcentral.com" not in response.answer_text
assert "123456789" not in response.answer_text
```

Invite privacy answer family:

```python
assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
assert response.can_operate is False
assert "private invite links" in response.answer_text
assert "send invites" in response.answer_text
assert "Invite participants:" not in response.answer_text
assert create_question_interrupt_step(package, response) is None
```

Recording safety answer family:

```python
assert response.entrypoint_id == "ringcentral.video.more.recording"
assert response.can_operate is False
assert "Recording changes the meeting state" in response.answer_text
assert "Start recording:" not in response.answer_text
assert create_question_interrupt_step(package, response) is None
```

Notes/transcript action guard:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.develop.video.start"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
assert "Notes and Transcript" in response.answer_text
```

Transcript content guard:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.video.more.notes"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
assert "transcript" in response.answer_text.casefold()
```

Reaction and raise-hand safety guard:

```python
assert response.entrypoint_id is None
assert response.can_operate is False
assert "Reactions" in response.answer_text
assert "Raise hand" in response.answer_text
assert "visible meeting signals" in response.answer_text
assert "explicitly asks" in response.answer_text
```

Location behavior guard:

```python
assert response.entrypoint_id == "ringcentral.video.toolbar.raise-hand"
assert response.can_operate is False
assert response.answer_text.startswith("Raise hand:")
```

Tone-invariance guard:

```python
assert response.entrypoint_id == baseline.entrypoint_id
assert response.can_operate is baseline.can_operate
assert (create_question_interrupt_step(package, response) is not None) is (
    baseline_interrupt
)
```

Privacy logging guard:

```python
assert "question_answered" in message
assert "private board agenda" not in message
assert "private answer text" not in message
```

## Diagnostics Count Updates

If the next change only adds one exact Q&A prompt under an existing `qa:` item:

- `qa_total` remains `15`.
- Localization report text remains `- localized questions: 15/15` and
  `- localized answers: 15/15`.
- Q&A prompt-candidate count moves from `139` to `140`.
- Update these exact expectations if the new prompt is committed:
  - `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
  - `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
  - `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`
- Keep package-owned alias count at `157` unless entrypoint aliases change.
- Keep substring risk at `11` only if the new prompt does not introduce an
  unrelated package-owned alias substring; otherwise update the INFO count and
  verify the detail still says `Q&A-first matching still applies`.

If the next change adds a new top-level `qa:` item:

- Add localized questions and answers for zh, ja, and es.
- Update material package localization status from `15` to `16`:
  `qa_localized_questions`, `qa_localized_answers`, and `qa_total`.
- Update CLI and diagnostics text from `15/15 Q&A questions` and
  `15/15 Q&A answers` to `16/16` only after localization is complete.
- Update Q&A prompt-candidate count by the number of authored canonical and
  localized prompt strings, not just by one top-level item.

## Final Verification Checklist

- `git status --short` shows only the intended package/test changes plus this
  handoff if the implementation owner uses it; `.coverage` is not staged or
  edited by this scan.
- Every new privacy prompt has a focused question test.
- Every new privacy/action prompt asserts `response.can_operate is False`.
- Every new privacy/action prompt asserts
  `create_question_interrupt_step(package, response) is None`.
- Answers use authored privacy guidance and do not fall back to thin entrypoint
  labels such as `Meeting information:`, `Invite participants:`,
  `Start recording:`, or `Notes and transcript:`.
- Answers do not include real-looking URLs, `ringcentral.com`, meeting IDs,
  host details, participant names, chat messages, transcript text, invite
  suggestions, email addresses, or success claims for copy/paste/read/send/start
  actions.
- Nearby location prompts still route as intended.
- Focused diagnostics or doctor expectations are updated only for the exact Q&A
  prompt inventory delta.
- Do not run the full suite for this handoff. Recommended focused commands for
  the implementation owner are targeted `test_questions.py` cases plus the two
  Q&A diagnostics count tests when counts change.
