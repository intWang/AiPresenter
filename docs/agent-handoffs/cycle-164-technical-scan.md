# Cycle 164 Technical Scan: Meeting Information Private Value Q&A

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `7627354`

## Scope

Scan-only handoff for RingCentral Video Meeting information private-value
question routing. I did not edit production code or tests, did not stage or
commit, and did not touch `.coverage`. The only file written by this subagent
is this handoff.

During the scan, concurrent Cycle 164 work appeared in:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-164-demand-analysis.md`

I treated those as other agents' work. The current dirty diff already adds the
host/dial-in package prompts and matching tests described below.

## Files Inspected

- `packages/ringcentral-video.yaml`
  - `ringcentral.video.top.meeting-info` has `questionPolicy: answerOnly`.
  - The Meeting information notes say the popover can expose private meeting
    identifiers and copy-link controls.
  - The existing privacy Q&A item says exact IDs, links, dial-in details, and
    host information should not be copied, read aloud, or exposed unless the
    user explicitly asks and visible content is verified.
- `src/ai_presenter/runtime/questions.py`
  - `_match_qa()` is Q&A-first, then safety helpers, then Q&A fragment/token
    scoring, then entrypoint alias/fallback matching.
  - Q&A matches return the first `relatedEntrypointIds` entry as context, then
    `_can_operate(...)` decides whether an interrupt can be queued.
  - `_can_operate(...)` returns false for `questionPolicy: answerOnly`, so
    Meeting information can be identified without opening the popover.
- `src/ai_presenter/runtime/session.py`
  - `create_question_interrupt_step(...)` only queues an interrupt when
    `entrypoint_id` is set and `can_operate` is true.
- `tests/unit/test_questions.py`
  - Current dirty tree extends
    `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first`
    with eight host/dial-in exact prompts.
- `tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py`
  - Current dirty tree updates Q&A prompt-count expectations from `149` to
    `157`.
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
  - Meeting information includes meeting ID, link, dial-in, host identity, and
    encryption details. Exact values require confirmation.
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
  - Meeting information safe default is location/purpose explanation; unsafe
    default is reading/copying exact values without explicit request and
    verified visible context.

## Current Behavior Probe

Read-only probe command used:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; @'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path('packages/ringcentral-video.yaml'))
prompts = [
    'Read the dial-in number',
    'What is the dial-in number?',
    'Who is the host?',
    'Read the host information?',
    'Copy host info?',
    'What is the meeting password?',
    'Read the meeting password',
    'Copy the meeting password',
    'What is the passcode?',
    'Read the passcode',
]
for prompt in prompts:
    response = answer_question(package=package, question=prompt, voice=PresenterVoiceSettings())
    interrupt = create_question_interrupt_step(package, response) is not None
    answer = ' '.join(response.answer_text.split())
    print(f'{prompt}\tentrypoint={response.entrypoint_id}\tcan_operate={response.can_operate}\tinterrupt={interrupt}\tanswer={answer[:180]}')
'@ | .\.venv\Scripts\python.exe -
```

| Prompt | Current behavior in dirty tree |
| --- | --- |
| `Read the dial-in number` | Privacy Q&A, `entrypoint=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. |
| `What is the dial-in number?` | Privacy Q&A, `entrypoint=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. |
| `Who is the host?` | Privacy Q&A, `entrypoint=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. |
| `Read the host information?` | Privacy Q&A via fragment match, `entrypoint=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. |
| `Copy host info?` | Privacy Q&A via fragment match, `entrypoint=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. |
| `What is the meeting password?` | No match fallback, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Read the meeting password` | No match fallback, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Copy the meeting password` | Thin Meeting information entrypoint fallback, `entrypoint=ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. |
| `What is the passcode?` | No match fallback, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Read the passcode` | No match fallback, `entrypoint=None`, `can_operate=False`, no interrupt. |

Additional spot checks show `Can you read the dial-in number?`, `Can you read
the host name?`, `Can you copy host information?`, and `Copy the host
information` also resolve to the Meeting information privacy Q&A with
`can_operate=False` and no interrupt under the current dirty tree, but they are
not all authored as exact package prompts.

## Recommended Exact Edits

If implementing from clean `7627354`, keep the slice package/test-only and add
these exact English prompts under the existing Q&A item
`How should AiPresenter handle meeting IDs and links safely?`:

```yaml
    - Read the dial-in number
    - What is the dial-in number?
    - Copy the dial-in details
    - Read dial-in details aloud
    - Who is the host?
    - Read the host information
    - Copy host info
    - Read meeting details aloud
```

Extend
`tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first`
with the same prompts and keep the assertions:

- `response.entrypoint_id == "ringcentral.video.top.meeting-info"`
- `response.can_operate is False`
- answer includes `Meeting IDs and links are private meeting details`
- answer does not include `Meeting information:`
- `create_question_interrupt_step(package, response) is None`

The current dirty tree already has those exact package/test edits.

Consider adding test-only coverage for punctuation/framing variants that already
pass via fragment/token scoring:

- `Read the host information?`
- `Copy host info?`
- `Can you read the dial-in number?`
- `Can you read the host name?`

Do not add broad aliases such as `host`, `number`, `phone`, `password`,
`passcode`, `copy`, `read`, `dial`, or `details`.

Meeting password/passcode prompts are not covered by the current package Q&A.
They do not create interrupts today, but some return a thin no-match or Meeting
information fallback instead of privacy guidance. Treat password/passcode as a
separate follow-up unless product evidence confirms those values belong on the
RingCentral Video Meeting information surface. If that follow-up is approved,
add exact prompts to the same privacy Q&A and update diagnostics counts by the
actual number of authored prompts.

## Diagnostics Impact

Current committed baseline at `7627354` expected:

- `149 Q&A question prompts have no cross-item duplicates`
- `149 Q&A question prompts have no unsafe package-owned alias overlaps`
- `157 package-owned aliases have no cross-entrypoint duplicates`
- `11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`

Current dirty tree with the eight host/dial-in prompts reports:

- `157 Q&A question prompts have no cross-item duplicates`
- `157 Q&A question prompts have no unsafe package-owned alias overlaps`
- `157 package-owned aliases have no cross-entrypoint duplicates`
- substring-risk count remains `11`

So the expected count impact for the host/dial-in slice is:

- Q&A prompt inventory: `149 -> 157`
- QA alias overlap detail: `149 -> 157`
- package-owned alias count: unchanged at `157`
- substring-risk INFO count: unchanged at `11`

If additional exact password/passcode or punctuation variants are authored in
package YAML, bump the `157` Q&A counts by that exact authored-prompt delta and
re-run diagnostics before updating expectations.

## Risks

- Broad aliases could steal unrelated prompts and create surprising
  Meeting-information routing. Prefer exact Q&A prompts.
- `questionPolicy: answerOnly` is the important interrupt guard. Do not remove
  it from Meeting information.
- Do not change runtime matcher/token scoring for this slice; package-authored
  exact prompts are enough and lower blast radius.
- Do not claim actual host, dial-in, password/passcode, encryption, or meeting
  state has been verified. This scan only proves routing behavior.
- Do not add a new Q&A item unless zh/ja/es localization and localization-count
  expectations are updated.
- Do not treat password/passcode as equivalent to host/dial-in without product
  evidence. Today those prompts are non-operable but not all privacy-guided.
- Existing `.coverage` is dirty; do not stage it.

## Verification Run During Scan

Focused checks run with pytest addopts overridden so coverage was not updated:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `17 passed in 3.48s`.

## Focused Verification Commands

After implementation, run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first
```

If package prompt counts changed, also run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Before staging or handoff, run:

```powershell
git diff --check
git status --short
```

Only stage the intended package/test/docs files. Do not stage `.coverage`.
