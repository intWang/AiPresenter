# Cycle 165 Risk/Test Scan: Next Prompt Privacy Slice

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `96b0dc9d108ea492660ef23611071feb0ef703d7`
Role: Cycle165 risk/test-scan subagent

## Scope

- Reviewed the next backlog choices across password/passcode, participant roles, and caption text variants.
- Only wrote this handoff: `docs/agent-handoffs/cycle-165-risk-scan.md`.
- Did not edit code, tests, package YAML, `.coverage`, or any other docs.
- Did not run the full suite, stage, or commit.
- Initial workspace status showed `.coverage` dirty; treated it as pre-existing work and left it alone.
- Final workspace verification also showed concurrent package/test edits in `packages/ringcentral-video.yaml`, `tests/unit/test_questions.py`, `tests/unit/test_diagnostics.py`, and `tests/unit/test_cli.py`, plus untracked Cycle165 demand/technical handoffs. This scan did not write those files.

## Current Routing Snapshot

- Clean `HEAD` at `96b0dc9` expects `157 Q&A question prompts`, `157 package-owned aliases`, `11 Q&A alias substring risks`, and `15/15 Q&A questions` plus `15/15 Q&A answers` for localization.
- The concurrent working-tree diff currently adds four participant-role prompts and updates Q&A prompt-count expectations from `157` to `161`. Treat those edits as another agent's work unless the coordinator says otherwise.
- Meeting-info privacy Q&A now covers meeting links, URL, ID, dial-in, host, and broad meeting-detail readout prompts. It does not author password/passcode prompts.
- Password/passcode probes are non-operable today, but several are weak: `What is the meeting password?`, `Read the meeting password`, `What is the meeting passcode?`, and `Read the passcode` no-match; `Copy the meeting password` and `Copy the meeting passcode` fall to the thin `Meeting information:` answer.
- Against clean `HEAD`, participant-role prompts are still a valid backlog slice. In the current concurrent working tree, `Show participant roles`, `Read participant roles`, `List participant roles`, and `Who is host or moderator?` are authored and covered as answer-only. `Show roles` still no-matches, which is safer than operating but weaker than privacy guidance.
- Caption-text prompts remain the best immediate gap: `Read caption text` and `Show captions text` no-match, while `Show live caption text` routes to `ringcentral.video.toolbar.audio` and starts `Microphone control:`. `Read the live transcript text` currently reaches the captions/transcript Q&A but is not explicitly covered.

## Recommended Slice Order

1. Caption text variants: smallest high-value slice if the concurrent participant-role diff lands. The existing captions answer already says not to read caption or transcript text, so exact prompts can fix no-match/audio drift without answer-copy expansion.
2. Participant-role variants: still the clean-HEAD slice if the concurrent diff is discarded; otherwise use only for nearby wording beyond the already covered role prompts, such as `Show roles` or `What are participant roles?`.
3. Password/passcode: defer until product/source evidence confirms RingCentral Video exposes password/passcode on Meeting information or another verified surface. If approved, update answer copy and localized answers, not just prompt inventory.

## Risk Matrix

| Area | Risk | Likelihood | Impact | Guard |
| --- | --- | --- | --- | --- |
| Caption text | `Show live caption text` keeps routing to Audio by token fallback | High until exact prompt is authored | Medium | Add exact Q&A prompt under captions/transcript safety item; assert not `ringcentral.video.toolbar.audio` and no `Microphone control:` text. |
| Caption text | Read/show caption prompts remain thin no-match | High | Medium | Add exact prompts and assert the answer includes `Notes and Transcript`, `read caption or transcript text`, `explicitly asks`, and `verified`. |
| Caption text | Location prompts get over-hardened | Medium | Medium | Keep `Where are captions?`, `Can I use live transcription?`, and `Turn on captions` on the current answer-only Q&A behavior. |
| Participant roles | New role prompt accidentally routes to Participants panel | Medium | High | Keep prompts in the existing privacy Q&A with no `relatedEntrypointIds`; assert `entrypoint_id is None`, not Participants, no interrupt. |
| Participant roles | Broad role wording swallows unrelated role/host-control questions | Medium | Medium | Prefer exact prompts such as `Show roles` or `What are participant roles?`; avoid broad aliases `roles`, `host`, `moderator`, or `participant`. |
| Participant roles | Tests miss weaker no-match variants | Medium | Low/Medium | Add one or two representative variants if implemented; do not require broad semantic coverage from matcher changes. |
| Password/passcode | Prompts get authored without product evidence | Medium | Medium | First confirm whether passcode/password exists in observed RingCentral Video UI and which surface owns it. |
| Password/passcode | Safety answer omits password/passcode wording | High if prompts are added only to `localizedQuestions.en` | Medium | Update English and localized safety answers to classify passwords/passcodes/access codes as private meeting details. |
| Password/passcode | Copy/read prompts fall to thin Meeting information answer | Current behavior for copy variants | Medium | If approved, add exact Q&A prompts and assert `Meeting information:` is absent. |
| All | Diagnostics count strings go stale | High when prompt inventory changes | Low/Medium | Update count expectations by the actual authored prompt delta and verify targeted diagnostics. |
| All | New prompt creates alias overlap or substring-risk drift | Medium | Low/Medium | Run targeted diagnostics; only update substring-risk count after reviewing detail text. |

## Recommended Assertions

Core answer-only assertions for every new privacy prompt:

```python
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

Caption text variants:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.video.toolbar.audio"
assert "Notes and Transcript" in response.answer_text
assert "read caption or transcript text" in response.answer_text
assert "explicitly asks" in response.answer_text
assert "verified" in response.answer_text
assert "Microphone control:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
```

Recommended caption prompts if this is the selected slice:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- Optional if the slice wants transcript-text symmetry: `Read the live transcript text`

Participant-role variants:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.video.toolbar.participants"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
assert "participant names" in response.answer_text
assert "roles" in response.answer_text
assert "verified" in response.answer_text
assert "Participants panel:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
```

Participant prompts already covered at baseline:

- `Show participant roles`
- `Read participant roles`
- `List participant roles`
- `Who is host or moderator?`

Possible incremental prompts only if needed:

- `Show roles`
- `What are participant roles?`
- `Read host role`
- `List attendee roles`

Password/passcode variants, only after product evidence:

```python
assert response.entrypoint_id == "ringcentral.video.top.meeting-info"
assert response.can_operate is False
assert "Meeting IDs and links are private meeting details" in response.answer_text
assert "password" in response.answer_text.casefold() or "passcode" in response.answer_text.casefold()
assert "Meeting information:" not in response.answer_text
assert "https://" not in response.answer_text
assert "ringcentral.com" not in response.answer_text
assert "123456789" not in response.answer_text
assert "copied" not in response.answer_text.casefold()
assert "dialed" not in response.answer_text.casefold()
assert create_question_interrupt_step(package, response) is None
```

Candidate password/passcode prompts if approved:

- `What is the meeting password?`
- `Read the meeting password`
- `Copy the meeting password`
- `What is the meeting passcode?`
- `Read the passcode`
- `Copy the meeting passcode`

Nearby behavior to preserve:

- `participants` should still route to `ringcentral.video.toolbar.participants`, remain operable, and queue an interrupt.
- `Where are captions?` should remain captions/transcript guidance with no interrupt.
- `meeting information` should remain a location-style Meeting information answer-only lookup, not the private-value Q&A.
- `Copy meeting link` should stay on the Meeting information privacy Q&A.
- Host-control prompts such as `where are host controls for participants` should stay non-operable participant safety guidance.

## Diagnostics Count Guidance

Clean baseline at commit `96b0dc9`:

- Q&A prompt count: `157`
- Q&A alias-overlap prompt count: `157`
- Package-owned alias count: `157`
- Q&A alias substring-risk count: `11`
- Q&A localization item count: `15/15` questions and `15/15` answers

Concurrent working-tree participant-role diff:

- Adds four exact participant-role prompts.
- Updates Q&A prompt count expectations from `157` to `161`.
- Leaves package-owned alias count at `157`.
- Does not create a new Q&A item, so localization item totals should remain `15/15`.

Count rules:

- Adding `N` exact English prompts to an existing `qa:` item changes both Q&A prompt-count expectations from `157` to `157 + N`.
- Adding prompts to an existing Q&A item should not change `15/15` localized Q&A item totals.
- Adding prompts to an existing Q&A item should not change the `157 package-owned aliases` count because no entrypoint aliases were added.
- The `11` substring-risk count may remain unchanged, but must be rechecked. Prompts containing package-owned aliases such as `participants`, `meeting details`, `meeting link`, or related localized aliases can move this INFO count.
- Adding a new top-level Q&A item changes localization totals to `16/16` only if zh, ja, and es localized questions and answers are complete.
- Adding entrypoint `questionAliases` instead of Q&A prompts changes alias counts and can bypass authored privacy answers; avoid this for these slices.

Expected examples from clean `96b0dc9`:

- Caption-only with the three recommended exact prompts: `157 -> 160` Q&A prompts.
- Caption plus `Read the live transcript text`: `157 -> 161` Q&A prompts.
- Participant-role clean-HEAD slice with the four currently concurrent prompts: `157 -> 161` Q&A prompts.
- Participant-role follow-up with two additional exact prompts: `157 -> 159` Q&A prompts if the concurrent role diff is not present, or `161 -> 163` if it is retained.
- Password/passcode with all six candidate prompts: `157 -> 163` Q&A prompts, plus answer/localized-answer updates.

Expected examples if the current participant-role diff is retained:

- Caption-only with the three recommended exact prompts: `161 -> 164` Q&A prompts.
- Caption plus `Read the live transcript text`: `161 -> 165` Q&A prompts.
- Password/passcode with all six candidate prompts: `161 -> 167` Q&A prompts, plus answer/localized-answer updates.

## Focused Verification Checklist

- Confirm prompts are added under the intended existing Q&A item, not under entrypoint `questionAliases`.
- Confirm no new `relatedEntrypointIds` are added to the chat/participants privacy Q&A.
- Confirm caption text prompts do not route to Audio and do not use no-match fallback.
- Confirm participant-role prompts do not route to Participants panel or queue interrupts.
- Confirm password/passcode work, if selected, includes product evidence and updated English plus localized answer copy.
- Confirm diagnostics/CLI exact count strings are updated only for the actual prompt delta.
- Run focused question tests only, with coverage disabled:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first
```

- If Q&A prompt counts changed, run focused diagnostics/CLI checks only:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow
```

- Before any implementation handoff, run `git diff --check` and `git status --short`.
- Verify `.coverage` remains unmodified by the implementation pass and is not staged.
- Do not run the full suite for this narrow backlog slice unless a later coordinator explicitly asks for it.
