# Cycle 164 Risk/Test Scan - RingCentral Video Meeting Details Q&A

## Scope

- Role: Cycle164 risk/test-scan subagent.
- Stated base commit: `7627354`.
- Reviewed current workspace only. I did not edit code/tests, run the full suite, stage, commit, or touch `.coverage`.
- Only write target for this pass: `docs/agent-handoffs/cycle-164-risk-scan.md`.
- Existing dirty files were observed and treated as other agents' work. Initial status showed `.coverage` and `tests/unit/test_questions.py`; final verification also showed concurrent edits in `packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`, and `tests/unit/test_diagnostics.py`, plus untracked `docs/agent-handoffs/cycle-164-demand-analysis.md`.

## Current Observations

- `packages/ringcentral-video.yaml` defines `ringcentral.video.top.meeting-info` with `questionPolicy: answerOnly`, and its purpose names meeting title, host, meeting ID, copy link, dial-in info, encryption, and E2EE options.
- The package Q&A item `How should AiPresenter handle meeting IDs and links safely?` routes to `ringcentral.video.top.meeting-info`. The current working tree adds exact English prompts for dial-in number/details, host info, and reading meeting details aloud on top of the existing meeting link, meeting URL, and meeting ID prompts.
- No `passcode` or `password` prompt was found in `packages/ringcentral-video.yaml`, `tests/unit/test_questions.py`, `tests/unit/test_diagnostics.py`, or `tests/unit/test_cli.py`.
- The current uncommitted diffs add the same +8 exact English parameters to `packages/ringcentral-video.yaml` and `tests/unit/test_questions.py`, and update diagnostics/CLI Q&A prompt totals from `149` to `157`.
- Runtime matching checks exact Q&A first: `_answer_question()` calls `_match_qa()` before `_match_entrypoint()`, and `_match_qa()` checks `package.qa_questions_by_normalized` before fragment/token matching.
- Operability is independently gated: `_can_operate()` returns `False` when the matched entrypoint has `questionPolicy: answerOnly`, even if `_RISKY_ENTRYPOINT_WORDS` is empty.

## Risk Matrix

| Risk | Likelihood | Impact | Notes | Mitigation |
| --- | --- | --- | --- | --- |
| Passcode/password prompts fall through to generic matching | High if prompts are not added | Medium | There is no current exact passcode/password prompt. A passcode query may no-match or route by weaker tokens instead of the privacy Q&A. | Add passcode/password variants to the existing meeting IDs/links safety Q&A, not to `questionAliases`. |
| Safety answer omits passcode/password wording | High if only prompts are added | Medium | Current answer mentions IDs, links, dial-in details, and host info, but not passcodes/passwords. | If passcode/password prompts are added, update the base answer and localized answers to explicitly classify passcodes/passwords as private meeting details. |
| Exact prompts become entrypoint aliases instead of Q&A prompts | Medium | High | Entrypoint alias matching would return the generic `Meeting information:` answer instead of the safety Q&A copy. It would also change alias diagnostics counts. | Keep these in `qa[].localizedQuestions.en` for the existing safety Q&A. |
| Host-info prompts shadow participant host-control guidance | Medium | Medium | `Who is the host?` should route to meeting-info privacy guidance, while `where are host controls for participants` should keep participant safety guidance. | Reuse existing host-control negative assertions and add the new exact host prompts only to the meeting-info Q&A. |
| Invite/link wording blurs invite dialog vs meeting-info boundary | Medium | Medium | `Invite` can copy meeting links too, but exact requests to read/copy IDs, dial-in, host, passcodes, or meeting details should be privacy-first. | Keep invite prompts in the invite Q&A and sensitive value prompts in the meeting-info Q&A; assert exact expected entrypoint IDs. |
| Diagnostics count assertions become stale | High when prompt totals change | Low/Medium | `qa questions` and `qa alias overlap` assert exact Q&A prompt totals in diagnostics and CLI tests. | See count guidance below; update exact count strings only when package prompt totals change. |
| QA alias substring risk count shifts unexpectedly | Medium | Low | New prompts that contain aliases for unrelated entrypoints can increase the INFO count. Related meeting-info aliases should not be unsafe when `relatedEntrypointIds` includes `ringcentral.video.top.meeting-info`. | Run targeted diagnostics and review `qa alias substring risk` detail before changing expected count. |
| Sensitive values leak into answer text | Low/Medium | High | Meeting IDs, URLs, dial-in details, host info, and passcodes/passwords are private. | Assert no URLs, domains, numeric IDs, or passcode/password literals from fixtures appear in response text. |
| Exact prompts create an interrupt step | Low | High | A matching entrypoint with `can_operate=True` could produce an automation interrupt. Meeting-info must stay answer-only. | Assert `response.can_operate is False` and `create_question_interrupt_step(package, response) is None`. |

## Positive Test Recommendations

- Extend `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` for any new exact English passcode/password prompts, for example:
  - `Read the meeting passcode`
  - `What is the meeting passcode?`
  - `Read the meeting password aloud`
  - `Copy the meeting password`
- Reuse the existing meeting-info privacy assertions:

```python
assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
assert response.can_operate is False
assert "Meeting IDs and links are private meeting details" in response.answer_text
assert "Meeting information:" not in response.answer_text
assert create_question_interrupt_step(package, response) is None
```

- If the answer copy is updated for passcodes/passwords, add a content assertion such as:

```python
assert "passcode" in response.answer_text.casefold()
```

- Preserve the existing targeted privacy leak assertions where generic meeting-info answers are expected:

```python
assert "https://" not in response.answer_text
assert "ringcentral.com" not in response.answer_text
assert "123456789" not in response.answer_text
```

- Keep `test_meeting_info_privacy_gate_does_not_depend_on_risky_words` as the core defense that `questionPolicy: answerOnly` is doing the safety work, not just risky-word matching.

## Negative Test Recommendations

- Keep `test_ringcentral_host_controls_question_returns_participants_guidance` and `test_ringcentral_careful_tone_preserves_privacy_question_route` passing so participant host-control questions do not get swallowed by meeting-info prompts.
- Keep `test_ringcentral_participant_host_action_requests_stay_answer_only` passing for `Mute all participants`, `Remove a participant`, and `Lock the meeting`.
- Add a negative check if passcode/password prompts are introduced:

```python
assert response.entrypoint_id != "ringcentral.video.toolbar.invite"
assert response.entrypoint_id != "ringcentral.video.toolbar.participants"
```

- Do not assert that all meeting-info lookups must use the privacy Q&A. Existing tests intentionally allow generic answer-only entrypoint responses for location-style questions like `meeting information`, `where is the meeting ID`, and `where is the meeting link`.
- Avoid adding exact prompts that are only generic UI location lookups, such as `where is meeting information`, to the privacy Q&A. Those are already covered by entrypoint alias routing and should remain answer-only.

## Diagnostics Count Guidance

Observed count values:

- `157 package-owned aliases have no cross-entrypoint duplicates`
- Clean commit `7627354` baseline before the +8 exact host/dial-in/meeting-detail prompts was `149 Q&A question prompts`.
- Current working-tree expectation after the +8 prompt diff is `157 Q&A question prompts have no cross-item duplicates`.
- Current working-tree expectation after the +8 prompt diff is `157 Q&A question prompts have no unsafe package-owned alias overlaps`.
- `11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`
- Localization remains `15/15 Q&A questions` and `15/15 Q&A answers` for zh/es/ja because there are 15 Q&A items.

Count rules:

- Adding `N` more exact prompts under `qa[].localizedQuestions.en` on the existing meeting IDs/links safety Q&A should change Q&A prompt totals from the current working-tree `157` to `157 + N` in both `qa questions` and `qa alias overlap` assertions. From a clean `7627354` baseline, the +8 host/dial-in/meeting-detail prompts explain the move from `149` to `157`.
- That same change should not change `15/15 Q&A questions` or `15/15 Q&A answers`, because localization coverage counts Q&A items, not individual English prompt variants.
- That same change should not change the `157 package-owned aliases` count because no entrypoint aliases were added.
- The `qa alias substring risk` count should remain `11` only if new prompts contain no unsafe alias substring for an unrelated entrypoint. Verify before updating or preserving this assertion.
- Adding a new Q&A item instead of new prompts on the existing item changes localization totals from `15/15` to `16/16` only if every required language has nonblank localized questions and answers. If localized copy is missing, `--require-localization` should fail.
- Adding prompts to `questionAliases` changes alias counts and can bypass the safety Q&A answer text. Avoid this for host, dial-in, passcode/password, and exact meeting-detail value requests.

## Final Verification Checklist For Implementer

- Confirm `packages/ringcentral-video.yaml` contains the intended exact prompts under the existing meeting IDs/links safety Q&A, not under `questionAliases`.
- Confirm passcode/password prompts, if added, have matching safety answer copy and localized answer copy updates.
- Confirm `tests/unit/test_questions.py` covers host, dial-in, meeting details, and passcode/password exact prompts with non-operable and no-interrupt assertions.
- Confirm participant host-control tests still route to participant guidance and remain non-operable.
- Confirm diagnostics/CLI exact count strings are updated only for the counts that actually changed.
- Suggested targeted tests only, not full suite:
  - `pytest tests/unit/test_questions.py -k "meeting_info_privacy or invite_privacy or host_controls or sensitive_prompt_routing" -q`
  - `pytest tests/unit/test_diagnostics.py -k "ringcentral_package or qa_alias or localization" -q`
  - `pytest tests/unit/test_cli.py -k "localization_report_outputs or doctor_loads_profile_package_and_flow" -q`
- Before handoff, run `git status --short` and verify no accidental edits to `.coverage`, code, or unrelated tests.
