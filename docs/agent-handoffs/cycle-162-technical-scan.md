# Cycle 162 Technical Scan: Link Variant Routing

Scope: inspect current RingCentral question routing for these exact prompts only:

- `Can you copy the meeting link?`
- `Copy the invite link`
- `Copy the meeting URL`
- `Can you paste the meeting link?`
- `Read the meeting link aloud`

Per instruction, this scan did not edit source or tests and did not run git add, commit, reset, or checkout. The only file written by this scan is this handoff.

## Finding

The current runtime already routes all five prompts to answer-only privacy Q&A with no interrupt step:

| Prompt | Current route | Operable | Interrupt | Answer family |
| --- | --- | --- | --- | --- |
| `Can you copy the meeting link?` | `ringcentral.video.top.meeting-info` | `False` | none | meeting ID/link privacy Q&A |
| `Copy the invite link` | `ringcentral.video.toolbar.invite` | `False` | none | invite privacy Q&A |
| `Copy the meeting URL` | `ringcentral.video.top.meeting-info` | `False` | none | meeting ID/link privacy Q&A |
| `Can you paste the meeting link?` | `ringcentral.video.top.meeting-info` | `False` | none | meeting ID/link privacy Q&A |
| `Read the meeting link aloud` | `ringcentral.video.top.meeting-info` | `False` | none | meeting ID/link privacy Q&A |

This is safe at runtime now. In the live working tree, the four meeting-link variants are now explicit package-authored meeting-info Q&A prompts. `Copy the invite link` still routes safely through token overlap with `Read the invite link`, but it is not yet an explicit package-authored invite Q&A prompt.

## Current Routing Mechanics

- `src/ai_presenter/runtime/questions.py`
  - `_match_qa()` checks exact normalized Q&A prompts first.
  - It then allows candidate fragment matches and token-overlap matches.
  - `_can_operate()` returns `False` for `questionPolicy: answerOnly`, for missing `openSteps`, and for risky entrypoint words such as `invite` or `send`.
- `packages/ringcentral-video.yaml`
  - `ringcentral.video.top.meeting-info` is `questionPolicy: answerOnly`.
  - Existing meeting-info privacy Q&A starts at `How should AiPresenter handle meeting IDs and links safely?`
  - Existing English meeting-info localized questions in the current working tree are:
    - `Copy meeting link`
    - `Can you copy the meeting link?`
    - `Copy the meeting URL`
    - `Can you paste the meeting link?`
    - `Read the meeting link aloud`
    - `Can you read the meeting ID?`
  - Existing invite privacy Q&A starts at `How can I bring people into the meeting?`
  - Existing English invite localized questions are currently:
    - `Read the invite link`
    - `Invite John`
    - `Send the invite`
    - `Who can I invite?`

## Recommended Source/Test Updates

No Python source code changes are needed.

Remaining recommended package update:

- File: `packages/ringcentral-video.yaml`
- Add `Copy the invite link` to the existing invite Q&A English `localizedQuestions`.
- The four meeting-info variants are already present in the current working tree.

Recommended test update:

- File: `tests/unit/test_questions.py`
- Current local working tree already contains the expected test additions as dirty changes. I did not create or modify them.
- `test_ringcentral_english_invite_privacy_questions_stay_qa_first` is extended from 4 to 5 parameter cases with `Copy the invite link`.
- `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` is extended from 2 to 6 parameter cases with the four meeting-link variants above.
- With those local test additions, the two focused tests contain 11 total parameter cases and pass.

Recommended diagnostics update:

- File: `tests/unit/test_diagnostics.py`
- Current local working tree already bumps the Q&A prompt count from 134 to 138 for the four meeting-info YAML prompts.
- If `Copy the invite link` is added explicitly to package YAML, bump the diagnostics expectations again from 138 to 139.

Do not add broad aliases such as `copy`, `paste`, `read`, `link`, `URL`, `invite`, or `meeting`. Exact Q&A prompts are enough and avoid stealing unrelated prompt routing.

## Focused Commands

Direct routing probe used:

```powershell
@'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path('packages/ringcentral-video.yaml'))
for prompt in [
    'Can you copy the meeting link?',
    'Copy the invite link',
    'Copy the meeting URL',
    'Can you paste the meeting link?',
    'Read the meeting link aloud',
]:
    response = answer_question(package=package, question=prompt, voice=PresenterVoiceSettings())
    interrupt = create_question_interrupt_step(package, response)
    print(f'{prompt} | entrypoint={response.entrypoint_id} | can_operate={response.can_operate} | interrupt={interrupt is not None} | answer={response.answer_text}')
'@ | .\.venv\Scripts\python.exe
```

Focused test command used:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_english_invite_privacy_questions_stay_qa_first tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first
```

Result in the current working tree:

```text
11 passed in 7.64s
```

Useful inspection commands:

```powershell
rg -n -C 8 "How can I bring people into the meeting|How should AiPresenter handle meeting IDs and links safely|Copy meeting link|Read the invite link" packages\ringcentral-video.yaml
rg -n -C 6 "test_ringcentral_english_invite_privacy_questions_stay_qa_first|test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first" tests\unit\test_questions.py
rg -n "def _match_qa|def _can_operate|_RISKY_ENTRYPOINT_WORDS" src\ai_presenter\runtime\questions.py
git diff -- tests/unit/test_questions.py
```

## Commit Guidance For Main Agent

If Cycle162 is meant to make these exact prompts explicit and reviewable, the remaining source delta is the single invite Q&A prompt `Copy the invite link` plus the matching diagnostics count bump to 139. The current working tree already has the four meeting-info package prompts, their diagnostics bump to 138, and the focused question-test cases. Do not edit routing code. Do not make any link prompt operable. Do not touch clipboard behavior, invite search fields, live meeting values, meeting IDs, invite suggestions, or voice reading of exact links.
