# Cycle 160 Technical Scan: System-Audio Sharing Prompts

Scope: read-only technical scan for AiPresenter routing around these English prompts:

- `Share system audio`
- `Turn on share system audio`
- `Include system audio`
- `Share computer audio`
- `Can you share system audio?`

User constraint for this scan: do not edit source/tests, do not git add/commit/reset. This handoff is the only file written.

## Current Finding

No source or test extension is needed in the current tree. The existing screen-sharing safety Q&A has already been extended to cover all five system-audio prompts, and the current routing sends each prompt to the screen-sharing safety answer rather than the audio-device menu.

Observed behavior from direct routing probes:

| Prompt | Entrypoint | Operable | Interrupt | Answer route |
| --- | --- | --- | --- | --- |
| `Share system audio` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Turn on share system audio` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Include system audio` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Share computer audio` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |
| `Can you share system audio?` | `ringcentral.video.toolbar.share` | `False` | none | screen-sharing safety Q&A |

The returned answer starts with:

> Screen sharing can expose private content and changes what other people see.

This is the desired answer-only route for system-audio sharing requests. It avoids treating system audio as microphone/speaker device routing and avoids toggling `Share system audio`.

## Files Inspected

- `packages/ringcentral-video.yaml`
  - Screen-sharing safety Q&A: `How should AiPresenter handle screen sharing safely?`
  - Current English `localizedQuestions` already include the six Cycle 159 screen-sharing prompts plus these five Cycle 160 system-audio prompts.
  - The Q&A is related to `ringcentral.video.toolbar.share`.

- `tests/unit/test_questions.py`
  - `test_ringcentral_english_screen_sharing_questions_stay_qa_first` already parametrizes all eleven prompts:
    - six screen-sharing prompts from Cycle 159
    - five system-audio prompts from this scan
  - The test asserts:
    - `entrypoint_id == "ringcentral.video.toolbar.share"`
    - `can_operate is False`
    - screen-sharing safety answer text is returned
    - entrypoint-style labels such as `Screen sharing:` and `Start meeting:` are absent
    - `create_question_interrupt_step(...) is None`

- `src/ai_presenter/runtime/questions.py`
  - Routing checks exact/precomputed Q&A candidates before entrypoint matching.
  - That makes the existing Q&A alias extension the right implementation point for exact English system-audio sharing prompts.

- `tests/unit/test_material_packages.py`
  - Existing localization status counts remain item-count based for Q&A coverage, not alias-count based.
  - Adding English aliases to an existing Q&A item does not require changing the localized Q&A count assertions.

## Counts To Update

None in the current tree.

Current durable counts that should stay unchanged for this slice:

- `qa_total == 14`
- Chinese: `qa_localized_questions == 14`, `qa_localized_answers == 14`
- Japanese: `qa_localized_questions == 14`, `qa_localized_answers == 14`
- Spanish: `qa_localized_questions == 14`, `qa_localized_answers == 14`

Reason: the change belongs as additional English exact prompts under an existing Q&A item, not as a new Q&A item and not as localized aliases.

## Tests To Update

None in the current tree.

If a later branch somehow lacks this work, the focused implementation should be:

1. Add exactly these five English prompts to `packages/ringcentral-video.yaml` under `How should AiPresenter handle screen sharing safely?`
2. Add the same five prompts to `tests/unit/test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first`
3. Do not add broad aliases such as `audio`, `system audio`, `computer audio`, `share audio`, `share`, `sound`, `turn on`, or `include`
4. Do not change source routing code unless exact Q&A matching fails

## Focused Commands

Direct routing probe:

```powershell
$env:PYTHONPATH='src'; @'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path('packages/ringcentral-video.yaml'))
prompts = [
    'Share system audio',
    'Turn on share system audio',
    'Include system audio',
    'Share computer audio',
    'Can you share system audio?',
]
for prompt in prompts:
    response = answer_question(package=package, question=prompt, voice=PresenterVoiceSettings())
    interrupt = create_question_interrupt_step(package, response)
    print(prompt, response.entrypoint_id, response.can_operate, interrupt is not None, response.answer_text)
'@ | .\.venv\Scripts\python.exe -
```

Focused regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package
```

Note: running the same partial pytest selection without `--no-cov` makes the selected tests pass but exits nonzero because the repo-wide coverage gate sees only partial-suite coverage. In this scan, the corrected `--no-cov` command passed: `14 passed`.

## Verification Performed

- Direct routing probe: all five requested prompts route to `ringcentral.video.toolbar.share`, `can_operate=False`, no interrupt, screen-sharing safety answer.
- Focused pytest with `--no-cov`: `14 passed`.
- Focused pytest without `--no-cov`: selected tests passed, command failed only on global coverage threshold for partial run (`total of 39 is less than fail-under=80`).

## Recommendation

Treat Cycle 160 as already covered in the current working tree. The main agent should not add another Q&A item or edit routing code for this prompt set. If committing this area, include the existing `packages/ringcentral-video.yaml` and `tests/unit/test_questions.py` changes already present in the tree, subject to the main agent's ownership of the commit.
