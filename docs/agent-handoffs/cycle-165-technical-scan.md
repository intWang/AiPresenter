# Cycle 165 Technical Scan

Scope: RingCentral Video backlog prompt routing for meeting password/passcode,
participant-role, and caption-text requests.

Repo head: `96b0dc9d108ea492660ef23611071feb0ef703d7`.

Guardrails followed: read-only probes and focused tests only. I did not edit
code or tests, did not stage or commit, and did not touch `.coverage`. The only
write from this scan is this handoff document.

## Workspace Note

Initial `git status --short` showed only:

```text
 M .coverage
```

After the read-only probes, these additional dirty files appeared from another
worker:

```text
 M packages/ringcentral-video.yaml
 M tests/unit/test_cli.py
 M tests/unit/test_diagnostics.py
 M tests/unit/test_questions.py
```

I did not revert or overwrite them. Their diff adds four participant-role
prompts to the chat/participants privacy Q&A and updates Q&A prompt counts from
157 to 161. The routing results below are from the current worktree after those
concurrent changes were present.

## Probe Results

Probe path: load `packages/ringcentral-video.yaml`, call
`answer_question(...)`, then call `create_question_interrupt_step(...)`.

| Prompt | Current route |
| --- | --- |
| `What is the meeting password?` | No exact Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer starts `I could not find a matching control...`. |
| `Read the meeting passcode` | No exact Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer starts `I could not find a matching control...`. |
| `Copy the passcode` | No exact Q&A. Thin fallback to `ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. Answer starts `Meeting information: Open meeting details...`. |
| `Show participant roles` | Exact Q&A match to `Can the presenter read meeting messages or participant names?`. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer includes the existing boundary against reading participant names, roles, chat messages, or private tabs unless explicitly asked and verified. |
| `Read caption text` | No exact Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer starts `I could not find a matching control...`. |
| `Show captions text` | No exact Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer starts `I could not find a matching control...`. |
| `Show live caption text` | No exact Q&A. Wrong thin fallback to `ringcentral.video.toolbar.audio`, `can_operate=False`, no interrupt. Answer starts `Microphone control: Toggle mute and unmute in the live meeting.` |

## Smallest Safe Target

Recommended target: caption-text exact Q&A coverage only.

Why this is the smallest technically safe slice:

- Participant-role coverage is already in the current dirty worktree, with
  package prompts and test/count updates. Do not duplicate or overwrite that
  work.
- Caption-text coverage is three exact English prompts, has an existing safety
  answer that already says not to read caption or transcript text, and requires
  no runtime logic changes.
- Password/passcode coverage is also three prompts, but it needs product/source
  confirmation and answer-copy updates before it is safe. The current meeting
  info answer mentions IDs, links, dial-in details, and host information, but
  not passwords or passcodes.

## Exact Edits

Package:

- In `packages/ringcentral-video.yaml`, under Q&A item
  `Where are captions, live transcription, and translation controls?`, add
  these `localizedQuestions.en` prompts:

```yaml
    - Read caption text
    - Show captions text
    - Show live caption text
```

Tests:

- In `tests/unit/test_questions.py`, extend
  `test_ringcentral_captions_and_translation_questions_are_answer_only` with
  the same three prompts.
- Add or keep assertions that prove the exact failure modes are gone:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.video.toolbar.audio"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
assert "read caption or transcript text" in response.answer_text
assert "Microphone control:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
```

Diagnostics and CLI count tests:

- In `tests/unit/test_diagnostics.py`, update the two RingCentral Q&A prompt
  count assertions from `161` to `164`.
- In `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`,
  update the two Q&A prompt count strings from `161` to `164`.

No `src/` code changes are needed for the caption-text slice.

## Count Impact

Current worktree baseline after the participant-role in-flight edits:

- Q&A question prompts: `161`
- Package-owned aliases: unchanged at `157`
- Q&A alias substring risk: unchanged at `11`

Caption-text target impact:

- Add 3 Q&A prompts.
- Q&A question prompts become `164`.
- Q&A alias overlap remains OK.
- Q&A alias substring risk remains `11`; the in-memory simulation did not add a
  new INFO item.

If password/passcode prompts are later added on top of the caption target, the
Q&A prompt count would become `167`.

## Password/Passcode Follow-Up

Do not add broad aliases such as `password`, `passcode`, `copy`, `read`, or
`details`.

Before implementing password/passcode coverage:

- Confirm whether the observed RingCentral Video meeting-info UI exposes a
  password or passcode field in the target state.
- If confirmed, add exact prompts under
  `How should AiPresenter handle meeting IDs and links safely?`, for example:
  `What is the meeting password?`, `Read the meeting passcode`, and
  `Copy the passcode`.
- Update English and localized answer copy to classify passwords/passcodes as
  private meeting details.
- Extend
  `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` with
  non-operable/no-interrupt assertions and negative checks for copied values,
  URLs, domains, numeric IDs, and fallback `Meeting information:` copy.

## Risks

- `Show live caption text` currently falls to Audio because no exact Q&A catches
  the request before entrypoint fallback. The caption exact prompts should guard
  this directly.
- Adding broad caption or text aliases would be riskier than exact Q&A prompts
  because they can steal unrelated location or content requests.
- Password/passcode prompts touch private meeting access details. Adding prompts
  without answer-copy and product evidence would create an incomplete privacy
  boundary.
- The participant-role slice is already dirty in the shared worktree. Coordinate
  before editing nearby lines to avoid overwriting another worker's package and
  test changes.

## Verification Run

Focused baseline commands run with coverage disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests/unit/test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package
```

Result: `27 passed in 7.04s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `1 passed in 0.47s`.

Recommended verification after the caption-text edit:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow
```
