# Cycle 163 Technical Scan: Participant Role And Caption Text Prompt Hardening

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `46103c6`

## Scope

Scan-only handoff for package/question routing. I did not edit production or
test files, did not stage or commit, and did not touch `.coverage`.

During the scan, concurrent Cycle163 work appeared in:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-163-demand-analysis.md`
- `docs/agent-handoffs/cycle-163-risk-scan.md`

This handoff treats those as other agents' work. The current prompt inventory in
the dirty tree is `149 Q&A question prompts`, not the committed `139` baseline.

## Files Inspected

- `src/ai_presenter/runtime/questions.py`
  - `_match_qa()` is Q&A-first.
  - `_match_entrypoint()` falls back to token scoring when no alias or Q&A wins.
  - `_score_entrypoint_match()` can select an entrypoint from a single non-generic token.
  - `_can_operate()` marks Chat and Participants operable because they have open steps and no risky words in their id/title/purpose.
- `src/ai_presenter/runtime/session.py`
  - `create_question_interrupt_step()` queues an interrupt whenever `entrypoint_id` is set and `can_operate` is true.
- `src/ai_presenter/packages/models.py`
  - Q&A prompt candidates are precomputed from canonical and localized question strings.
- `packages/ringcentral-video.yaml`
  - Existing participant/chat privacy Q&A: `Can the presenter read meeting messages or participant names?`
  - Existing captions/transcripts Q&A: `Where are captions, live transcription, and translation controls?`
- `tests/unit/test_questions.py`
  - Existing exact-prompt tests cover several chat, participant identity, host-action, and caption/transcription prompts.
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
  - Current dirty-tree expected Q&A prompt count is `149`.

## Current Probe Results

Command used:

```powershell
$env:PYTHONIOENCODING='utf-8'; @'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path('packages/ringcentral-video.yaml'))
prompts = [
    'Can you read chat messages?',
    'Show chat messages',
    'Who is in the meeting?',
    'Show participant roles',
    'Read caption text',
    'Show captions text',
    'Show live caption text',
    'Can you start live transcription?',
]
for prompt in prompts:
    response = answer_question(package=package, question=prompt, voice=PresenterVoiceSettings())
    interrupt = create_question_interrupt_step(package, response) is not None
    answer = response.answer_text.replace('\n',' ')
    print(f'{prompt} | entrypoint={response.entrypoint_id} | can_operate={response.can_operate} | interrupt={interrupt} | answer={answer[:120]}')
'@ | .\.venv\Scripts\python.exe -
```

| Prompt | Current behavior |
| --- | --- |
| `Can you read chat messages?` | Safe Q&A, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Show chat messages` | Safe by current Q&A token overlap, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Who is in the meeting?` | Safe exact Q&A after concurrent edits, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Show participant roles` | Unsafe/thin: routes to `ringcentral.video.toolbar.participants`, `can_operate=True`, interrupt queued, answer starts `Participants panel:`. |
| `Read caption text` | Thin no-match fallback, no interrupt. |
| `Show captions text` | Thin no-match fallback, no interrupt. |
| `Show live caption text` | Wrong thin entrypoint fallback: routes to `ringcentral.video.toolbar.audio`, `can_operate=False`, no interrupt, answer starts `Microphone control:`. |
| `Can you start live transcription?` | Safe Q&A, `entrypoint=None`, `can_operate=False`, no interrupt. |

I also ran the current focused tests after the concurrent edits:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_chat_content_requests_stay_answer_only tests/unit/test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

Result: `12 passed`.

## Recommended Candidate

Implement an exact package/test-only Q&A prompt hardening slice. Do not change
runtime matcher code.

Add this prompt under existing Q&A item
`Can the presenter read meeting messages or participant names?`:

```yaml
    - Show participant roles
```

Add these prompts under existing Q&A item
`Where are captions, live transcription, and translation controls?`:

```yaml
    - Read caption text
    - Show captions text
    - Show live caption text
```

Expected dirty-tree count impact: `149 -> 153 Q&A question prompts` if these
four prompts are added on top of the current concurrent Cycle163 edits. If the
implementation starts from committed `46103c6` instead, re-count from the
actual prompt inventory rather than hard-coding this handoff's number.

## Recommended Tests

Extend `tests/unit/test_questions.py`:

- Add `Show participant roles` to `test_ringcentral_participant_identity_requests_stay_answer_only`, or add a sibling test named `test_ringcentral_participant_role_requests_stay_answer_only`.
- Add `Read caption text`, `Show captions text`, and `Show live caption text` to `test_ringcentral_captions_and_translation_questions_are_answer_only`.

Assertions to require:

- Participant role prompt:
  - `response.entrypoint_id is None`
  - `response.entrypoint_id != "ringcentral.video.toolbar.participants"`
  - `response.can_operate is False`
  - `create_question_interrupt_step(package, response) is None`
  - answer contains `participant names` or `roles`
  - answer contains `verified`
  - answer does not contain `Participants panel:`
- Caption text prompts:
  - `response.entrypoint_id is None`
  - `response.entrypoint_id != "ringcentral.video.toolbar.audio"`
  - `response.can_operate is False`
  - `create_question_interrupt_step(package, response) is None`
  - answer contains `Notes and Transcript`
  - answer contains `read caption or transcript text`
  - answer contains `explicitly asks` and `verified`
  - answer does not contain `Microphone control:`
  - answer does not contain the no-match fallback `I could not find`

If the package prompt count changes, update:

- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`

For the current dirty tree, the expected value would become `153 Q&A question
prompts`. The package-owned alias count should remain `157`. The substring-risk
INFO count should be rechecked because `Show participant roles` contains no
package-owned alias, while the caption prompts may or may not affect substring
risk depending on normalized alias inventory.

## Risks

- Do not add broad aliases such as `roles`, `captions`, `caption`, `text`,
  `show`, `read`, or `live`; exact Q&A prompts are safer.
- Do not add a new top-level Q&A item unless zh/ja/es localization and
  localization-count expectations are updated too.
- Do not set `relatedEntrypointIds` on the participant-role privacy Q&A just to
  identify Participants; that would risk reintroducing an operable interrupt.
- Do not route caption text prompts to Audio just because `live` overlaps with
  the audio purpose text.
- Do not change `_GENERIC_ENTRYPOINT_TOKENS` or token scoring in this cycle;
  that could affect unrelated fallback behavior.
- Do not change Chat or Participants `openSteps`; location-style prompts like
  `participants` and chat-panel lookup prompts are currently expected to remain
  operable.

## Verification Commands

Recommended focused verification after implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

If diagnostics/CLI counts are touched:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow
```

Status check before handoff/commit:

```powershell
git status --short
```

Confirm `.coverage` is not staged and this technical scan did not overwrite the
concurrent package/test changes owned by other agents.
