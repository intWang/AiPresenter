# Cycle 166 Technical Scan: Caption Text Privacy Variants

Scope: RingCentral Video caption-content prompts:
`Read caption text`, `Show captions text`, `Show live caption text`, and
`Read captions aloud`.

Repo head: `62b0f750232e1eb75bac29561a376816f1eef4a3`.

Guardrails followed: read-only probes and focused tests only. I did not edit
code or tests, did not stage or commit, and did not touch `.coverage`. The only
write from this scan is this handoff document.

## Workspace Note

Initial and final `git status --short` included existing dirty files:

```text
 M .coverage
 M packages/ringcentral-video.yaml
 M tests/unit/test_cli.py
 M tests/unit/test_diagnostics.py
 M tests/unit/test_questions.py
```

Those package/test edits appear to be another worker's caption slice. I did not
overwrite or revert them. The recommendations below distinguish the clean HEAD
baseline from the current dirty worktree.

## Probe Results

Probe path: load a `MaterialPackage`, call `answer_question(...)`, then call
`create_question_interrupt_step(...)`.

### Clean HEAD Baseline

Using `git show HEAD:packages/ringcentral-video.yaml` in memory:

| Prompt | Route at `62b0f75` |
| --- | --- |
| `Read caption text` | No Q&A match. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer starts `I could not find a matching control...`. |
| `Show captions text` | No Q&A match. `entrypoint_id=None`, `can_operate=False`, no interrupt. Answer starts `I could not find a matching control...`. |
| `Show live caption text` | Wrong fallback to `ringcentral.video.toolbar.audio`, `can_operate=False`, no interrupt. Answer starts `Microphone control: Toggle mute and unmute in the live meeting.` |
| `Read captions aloud` | Wrong fallback to `ringcentral.video.top.meeting-info`, `can_operate=False`, no interrupt. Answer starts with meeting ID/link privacy guidance. |

Root cause: the four exact caption-content prompts are absent from Q&A, so the
matcher reaches entrypoint fallback for two prompts. The fallbacks do not create
interrupts because the target entrypoints are not operable from questions, but
they still return the wrong answer copy.

### Current Dirty Worktree

The current worktree already adds the four prompts to the captions Q&A. All four
now route as answer-only privacy guidance:

| Prompt | Current route |
| --- | --- |
| `Read caption text` | Exact captions Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Show captions text` | Exact captions Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Show live caption text` | Exact captions Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. |
| `Read captions aloud` | Exact captions Q&A. `entrypoint_id=None`, `can_operate=False`, no interrupt. |

The answer is the existing safe copy: use Notes and Transcript / Settings as
discovery surfaces, but do not start notes, transcription, captions, or
translation, read caption or transcript text, or promise summaries unless the
user explicitly asks and visible context is verified.

## Exact Edits

If implementing from clean HEAD, make these package/test edits. In the current
dirty worktree, these edits are already present.

Package:

- In `packages/ringcentral-video.yaml`, under Q&A item
  `Where are captions, live transcription, and translation controls?`, add four
  `localizedQuestions.en` prompts:

```yaml
    - Read caption text
    - Show captions text
    - Show live caption text
    - Read captions aloud
```

Question tests:

- In `tests/unit/test_questions.py`, extend
  `test_ringcentral_captions_and_translation_questions_are_answer_only` with the
  same four prompts.
- Keep assertions that pin answer-only routing and block the two observed
  fallback failures:

```python
assert response.entrypoint_id is None
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
assert "caption or transcript text" in response.answer_text
assert "Microphone control:" not in response.answer_text
assert "Meeting information:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
```

Diagnostics and CLI count tests:

- In `tests/unit/test_diagnostics.py`, update the RingCentral Q&A count strings
  from `161` to `165` in:
  `test_diagnostics_reports_qa_questions_ok_for_ringcentral_package` and
  `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`.
- In `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`,
  update the same two count strings from `161` to `165`.

No `src/` runtime code changes are needed. Do not add entrypoint
`questionAliases` or `relatedEntrypointIds` for this slice.

## Diagnostics Impact

Clean HEAD baseline:

- Package-owned aliases: `157`
- Q&A question prompts: `161`
- Q&A alias overlap prompt count: `161`
- Q&A alias substring risk: `11`

Caption-text target impact:

- Adds 4 Q&A prompts.
- Q&A question prompts become `165`.
- Q&A alias overlap prompt count becomes `165`.
- Package-owned aliases remain `157`.
- Q&A alias substring risk remains `11`.

## Risks

- `Show live caption text` falls to Audio at clean HEAD; the exact Q&A prompt
  must remain in the Q&A layer so it wins before entrypoint fallback.
- `Read captions aloud` falls to Meeting information at clean HEAD; tests should
  explicitly reject `Meeting information:` answer copy.
- Broad aliases such as `caption`, `captions`, `text`, `read`, or `show` would
  be riskier than exact Q&A prompts because they can steal location/control
  requests or unrelated entrypoint matches.
- Caption text is live private meeting content. The safe answer should stay
  privacy-bounded and should not claim visible caption text, speaker identity,
  translation state, summaries, or transcript access.
- The shared worktree is dirty. Coordinate before editing nearby package/test
  lines so another worker's changes are not overwritten.

## Verification

Focused checks run with coverage and pytest cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

Result: `9 passed in 3.73s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

Result: `3 passed in 2.28s`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result after rerun: `1 passed in 0.52s`. An earlier parallel run failed while
the CLI count assertion was still changing from `161` to `165`; after the file
settled, it passed.

Final combined focused verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result: `13 passed in 2.86s`.
