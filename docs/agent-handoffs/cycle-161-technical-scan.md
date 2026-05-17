# Cycle 161 Technical Scan: Invite and Meeting-Link Privacy Prompts

Scope: read-only technical scan for AiPresenter routing around these English prompts:

- `Copy meeting link`
- `Read the invite link`
- `Invite John`
- `Send the invite`
- `Who can I invite?`
- `Can you read the meeting ID?`

User constraint for this scan: do not edit source/tests, do not git add/commit/reset. This handoff is the only file written.

## Current Finding

No source or test extension is needed in the current tree. The requested invite and meeting-link prompts are already covered by package-owned Q&A routes, and all six stay answer-only with no interrupt step.

Observed behavior from direct routing probes:

| Prompt | Entrypoint | Operable | Interrupt | Answer route |
| --- | --- | --- | --- | --- |
| `Copy meeting link` | `ringcentral.video.top.meeting-info` | `False` | none | meeting ID/link privacy Q&A |
| `Read the invite link` | `ringcentral.video.toolbar.invite` | `False` | none | invite privacy Q&A |
| `Invite John` | `ringcentral.video.toolbar.invite` | `False` | none | invite privacy Q&A |
| `Send the invite` | `ringcentral.video.toolbar.invite` | `False` | none | invite privacy Q&A |
| `Who can I invite?` | `ringcentral.video.toolbar.invite` | `False` | none | invite privacy Q&A |
| `Can you read the meeting ID?` | `ringcentral.video.top.meeting-info` | `False` | none | meeting ID/link privacy Q&A |

The invite answer says not to read private invite links, names, emails, or suggestions, and not to send invites unless the user explicitly asks and visible content is verified.

The meeting-info answer says meeting IDs and links are private meeting details, and AiPresenter should not copy, read aloud, or expose exact IDs, links, dial-in details, or host information unless the user explicitly asks and visible content is verified.

## Files Inspected

- `src/ai_presenter/runtime/questions.py`
  - `_answer_question()` checks package Q&A before entrypoint matching.
  - `_can_operate()` returns `False` for `questionPolicy: answerOnly`, missing `openSteps`, or risky entrypoint words such as `invite`, `send`, and other state-changing terms.
  - This means exact English privacy prompts belong in package Q&A aliases, not matcher code.

- `packages/ringcentral-video.yaml`
  - Invite Q&A: `How can I bring people into the meeting?`
    - Current English `localizedQuestions` include:
      - `Read the invite link`
      - `Invite John`
      - `Send the invite`
      - `Who can I invite?`
    - Related entrypoint: `ringcentral.video.toolbar.invite`.
  - Meeting ID/link Q&A: `How should AiPresenter handle meeting IDs and links safely?`
    - Current English `localizedQuestions` include:
      - `Copy meeting link`
      - `Can you read the meeting ID?`
    - Related entrypoint: `ringcentral.video.top.meeting-info`.
  - Existing entrypoint notes already mark meeting IDs, links, dial-in details, invite links, names, emails, and suggestions as sensitive.

- `tests/unit/test_questions.py`
  - `test_ringcentral_english_invite_privacy_questions_stay_qa_first` covers the four invite prompts.
  - `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` covers the two meeting-link / meeting-ID prompts.
  - Both tests assert:
    - the expected entrypoint
    - `can_operate is False`
    - Q&A privacy answer text is returned
    - entrypoint-style fallback labels are absent
    - `create_question_interrupt_step(...) is None`

- `tests/unit/test_material_packages.py`
  - Localization status counts are item-count based for Q&A coverage, not English alias-count based.
  - The current Q&A item count is already updated to `14`.

## Counts To Update

None in the current tree.

Current durable counts that should stay unchanged for this slice:

- `qa_total == 14`
- Chinese: `qa_localized_questions == 14`, `qa_localized_answers == 14`
- Japanese: `qa_localized_questions == 14`, `qa_localized_answers == 14`
- Spanish: `qa_localized_questions == 14`, `qa_localized_answers == 14`

Reason: the six requested prompts are already assigned to existing Q&A items. No new Q&A item, localization count, or package model count is required.

## Tests To Update

None in the current tree.

If a later branch lacks this work, the focused implementation should be:

1. Add the four invite prompts as English `localizedQuestions` under `packages/ringcentral-video.yaml` Q&A item `How can I bring people into the meeting?`.
2. Add or keep the answer wording that explicitly blocks reading private invite links, names, emails, suggestions, and sending invites unless the user explicitly asks and visible content is verified.
3. Add the two meeting-link / meeting-ID prompts as English `localizedQuestions` under `How should AiPresenter handle meeting IDs and links safely?`.
4. Keep related entrypoints as `ringcentral.video.toolbar.invite` for invite prompts and `ringcentral.video.top.meeting-info` for meeting ID/link prompts.
5. Do not change matcher code unless exact Q&A matching fails.
6. Do not add broad aliases such as `link`, `ID`, `read`, `copy`, `send`, `invite`, `John`, or `who`; broad aliases can steal unrelated prompt routing.

## Focused Commands

Direct routing probe:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH='src'; @'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path('packages/ringcentral-video.yaml'))
prompts = [
    'Copy meeting link',
    'Read the invite link',
    'Invite John',
    'Send the invite',
    'Who can I invite?',
    'Can you read the meeting ID?',
]
for prompt in prompts:
    response = answer_question(package=package, question=prompt, voice=PresenterVoiceSettings())
    interrupt = create_question_interrupt_step(package, response)
    print(prompt, response.entrypoint_id, response.can_operate, interrupt is not None, response.answer_text)
'@ | .\.venv\Scripts\python.exe -
```

Focused regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_questions.py::test_ringcentral_english_invite_privacy_questions_stay_qa_first tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first
```

Optional package-count guard if files are touched:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package
```

## Verification Performed

- Direct routing probe: all six requested prompts route to the expected invite or meeting-info privacy Q&A, `can_operate=False`, no interrupt.
- Focused pytest with `--no-cov`: `6 passed`.

## Recommendation

Treat Cycle 161 as already covered in the current working tree. The main agent should not add another Q&A item or edit runtime routing for this prompt set. If committing this area, include the existing `packages/ringcentral-video.yaml` and `tests/unit/test_questions.py` changes already present in the tree, subject to the main agent's ownership of the commit.
