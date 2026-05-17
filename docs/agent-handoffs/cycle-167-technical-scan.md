# Cycle 167 Technical Scan: Caption Variant Routing

Scope: RingCentral Video exact prompt variants:
`Show caption text`, `Read live captions aloud`, `Read live caption text`,
`Read the live caption text`, `Read the live transcript text`, and
`Show transcript text`.

Repo head: `2ce39f43a7d8751ddf223705f6918e00d559c2bf`.

Guardrails followed: read-only probes only until this handoff write. I did not
edit code or tests, did not stage or commit, and did not touch `.coverage`. The
only write from this scan is this document.

## Workspace Note

Initial `git status --short` showed only:

```text
 M .coverage
```

I left it untouched. During the scan, these additional dirty files appeared from
another worker:

```text
 M packages/ringcentral-video.yaml
 M tests/unit/test_cli.py
 M tests/unit/test_diagnostics.py
 M tests/unit/test_questions.py
```

Their diff adds `Copy captions`, `Can you copy the captions?`,
`Export captions`, `Save captions`, `Download captions`, and
`Download transcript text`, with Q&A count assertions moving from `167` to
`173`. I did not edit, revert, or overwrite those package/test changes. The
probe results and count baseline below are from the current worktree after those
concurrent changes were present.

Final status also showed untracked
`docs/agent-handoffs/cycle-167-demand-analysis.md` and
`docs/agent-handoffs/cycle-167-risk-scan.md` from other workers. I did not
create or edit those files.

## Current Routing

Probe path: load `packages/ringcentral-video.yaml`, call
`answer_question(...)`, then call `create_question_interrupt_step(...)`.

| Prompt | Current route |
| --- | --- |
| `Show caption text` | Captions/live transcription Q&A, `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Read live captions aloud` | Captions/live transcription Q&A, `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Read live caption text` | Captions/live transcription Q&A, `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Read the live caption text` | Captions/live transcription Q&A, `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Read the live transcript text` | Captions/live transcription Q&A, `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Show transcript text` | Captions/live transcription Q&A, `entrypoint_id=None`, `can_operate=False`, no interrupt. |

All six answers start with the existing safe copy:

```text
Use Notes and Transcript as the known discovery surface for transcript-related controls, and use Settings for Translation-related meeting preferences...
```

They also preserve the privacy boundary already asserted by tests: do not start
notes, transcription, captions, or translation; do not read caption or
transcript text; do not promise summaries unless the user explicitly asks and
visible context is verified.

## Match Source

None of the six prompts are exact Q&A prompts in the package today.

| Prompt | Match source |
| --- | --- |
| `Show caption text` | Q&A token fallback to captions/live transcription Q&A. |
| `Read live captions aloud` | Q&A token fallback to captions/live transcription Q&A. |
| `Read live caption text` | Q&A token fallback to captions/live transcription Q&A. |
| `Read the live caption text` | Q&A token fallback to captions/live transcription Q&A. |
| `Read the live transcript text` | `_match_notes_transcript_safety_qa(...)` guard. |
| `Show transcript text` | `_match_notes_transcript_safety_qa(...)` guard. |

The current behavior is operationally safe, but the first four are less pinned
than prior exact variants because they depend on general Q&A token overlap.

## Recommended Exact Edits

No `src/` runtime change is needed.

Package:

- In `packages/ringcentral-video.yaml`, under Q&A item
  `Where are captions, live transcription, and translation controls?`, append
  these `localizedQuestions.en` prompts:

```yaml
    - Show caption text
    - Read live captions aloud
    - Read live caption text
    - Read the live caption text
    - Read the live transcript text
    - Show transcript text
```

Question tests:

- In `tests/unit/test_questions.py`, extend
  `test_ringcentral_captions_and_translation_questions_are_answer_only` with
  the same six prompts.
- Keep the existing assertions that prove answer-only privacy routing:

```python
assert response.entrypoint_id is None
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
assert "Notes and Transcript" in response.answer_text
assert "Settings" in response.answer_text
assert "caption or transcript text" in response.answer_text
assert "Microphone control:" not in response.answer_text
assert "Meeting information:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
```

Diagnostics and CLI count tests:

- In `tests/unit/test_diagnostics.py`, update
  `test_diagnostics_reports_qa_questions_ok_for_ringcentral_package` and
  `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` from
  `173` to `179`.
- In `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`,
  update the two `173 Q&A question prompts...` strings to `179`.

Do not add broad entrypoint `questionAliases` such as `caption`, `captions`,
`live caption`, `transcript`, `read`, `show`, or `text`.

## Diagnostics Impact

Current baseline from `doctor --profile profiles\ringcentral-video.yaml
--package ringcentral-video`:

- Package-owned aliases: `157`
- Q&A question prompts: `173`
- Q&A alias overlap prompt count: `173`
- Q&A alias substring risk: `11`
- Doctor summary: `10 ok, 1 info, 0 warnings, 0 failed`

In-memory simulation after appending the six exact English prompts:

- Package-owned aliases remain `157`.
- Q&A question prompts become `179`.
- Q&A alias overlap prompt count becomes `179`.
- Q&A alias substring risk remains `11`.
- Doctor summary remains `10 ok, 1 info, 0 warnings, 0 failed`.

Required localization counts stay complete because this adds English variants to
an existing Q&A item, not new Q&A items:

- `zh`: `51/51` demo steps, `15/15` Q&A questions, `15/15` Q&A answers.
- `ja`: `51/51` demo steps, `15/15` Q&A questions, `15/15` Q&A answers.
- `es`: `51/51` demo steps, `15/15` Q&A questions, `15/15` Q&A answers.

The default fake-speech profile still fails voice checks for `zh`, `ja`, and
`es` when `--require-localization --language ...` also validates runtime voice;
that failure is pre-existing and unrelated to these English prompt additions.

## Risks

- Leaving the first four variants as token-fallback-only means a future Q&A item
  or matcher scoring change could move them without changing the package prompt
  list. Exact Q&A prompts are the smallest stable pin.
- Broad aliases would be riskier than exact Q&A prompts because they can steal
  safe location/control requests and unrelated entrypoint matches.
- Caption and transcript text are private live-meeting content. The answer must
  not claim actual caption text, speaker identity, transcript contents,
  translation state, post-meeting summaries, or artifact availability.
- Do not attach `relatedEntrypointIds` to this Q&A for these prompts. Keeping
  `entrypoint_id=None` avoids downstream UI or interrupt logic treating a
  private content read request as a request to open Notes and Transcript.

## Focused Verification Commands

Run with coverage and pytest cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Optional direct route probe after implementation:

```powershell
@'
from pathlib import Path
from ai_presenter.packages.loader import load_material_package
from ai_presenter.runtime.questions import answer_question
from ai_presenter.runtime.session import create_question_interrupt_step
from ai_presenter.runtime.voice import PresenterVoiceSettings

package = load_material_package(Path("packages/ringcentral-video.yaml"))
for question in [
    "Show caption text",
    "Read live captions aloud",
    "Read live caption text",
    "Read the live caption text",
    "Read the live transcript text",
    "Show transcript text",
]:
    response = answer_question(
        package=package,
        question=question,
        voice=PresenterVoiceSettings(),
    )
    interrupt = create_question_interrupt_step(package, response) is not None
    print(question, response.entrypoint_id, response.can_operate, interrupt)
'@ | .\.venv\Scripts\python.exe -
```
