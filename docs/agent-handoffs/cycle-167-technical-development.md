# Cycle 167 Technical Development: Caption Export Action-Content Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle167 technical-development handoff subagent

## Scope

Technical-development handoff for the current Cycle167 caption/transcript
action-content implementation. This subagent wrote only this document.

Source code, package YAML, tests, `.coverage`, staging, commits, resets,
checkouts, and full-suite verification were left untouched by this handoff
pass.

Important context: earlier Cycle167 demand/technical scans recommended pinning
already-safe caption/transcript variants through a larger `173 -> 179` Q&A
inventory move. The main session intentionally chose the true red
misroute/no-match slice instead: six caption/transcript action-content prompts
that were not already safely pinned.

## Changed Files Observed

Dirty tracked files from the main-session implementation:

- `.coverage` is modified in the working tree, but it is unrelated to this
  handoff and was not touched here.
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Existing Cycle167 context docs already present:

- `docs/agent-handoffs/cycle-167-demand-analysis.md`
- `docs/agent-handoffs/cycle-167-risk-scan.md`
- `docs/agent-handoffs/cycle-167-technical-scan.md`

This handoff adds:

- `docs/agent-handoffs/cycle-167-technical-development.md`

## Exact Implementation Edits

`packages/ringcentral-video.yaml` adds six English `localizedQuestions`
prompts to the existing Q&A item,
`Where are captions, live transcription, and translation controls?`:

- `Copy captions`
- `Can you copy the captions?`
- `Export captions`
- `Save captions`
- `Download captions`
- `Download transcript text`

`tests/unit/test_questions.py` mirrors those same six prompts in
`test_ringcentral_captions_and_translation_questions_are_answer_only`.
The test keeps the caption/transcript action-content requests answer-only and
privacy-bounded:

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- answer text includes `Notes and Transcript`
- answer text includes `Settings`
- answer text includes `caption or transcript text`
- answer text does not include `Microphone control:`
- answer text does not include `Meeting information:`
- answer text does not include `Notes and transcript:`
- answer text does not include `I could not find a matching control`
- answer text does not include `The caption says`
- answer text does not include `Here are the captions`

`tests/unit/test_diagnostics.py` updates exact Q&A prompt inventory
expectations:

- `167 Q&A question prompts have no cross-item duplicates`
  -> `173 Q&A question prompts have no cross-item duplicates`
- `167 Q&A question prompts have no unsafe package-owned alias overlaps`
  -> `173 Q&A question prompts have no unsafe package-owned alias overlaps`

`tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow` updates
the same doctor-output expectations from `167` to `173`.

No runtime matcher code, entrypoint aliases, related entrypoints, open steps,
profile data, clipboard/export/download operations, caption controls,
transcript controls, or localization item-count expectations were changed.

## Routing Behavior Fixed

The fix is data-only and relies on existing Q&A-first routing. `_match_qa()`
matches normalized authored Q&A prompts before entrypoint aliases and fallback
matching. Adding the six exact caption/transcript action-content requests to
the existing captions/live transcription Q&A makes them return the authored
privacy/location answer instead of falling through to no-match text or
unrelated control guidance.

Clean-baseline routing risk fixed by this slice:

| Prompt | Previous route risk | Current route |
| --- | --- | --- |
| `Copy captions` | no-match or thin fallback | captions Q&A answer-only |
| `Can you copy the captions?` | no-match or thin fallback | captions Q&A answer-only |
| `Export captions` | no-match or thin fallback | captions Q&A answer-only |
| `Save captions` | no-match or thin fallback | captions Q&A answer-only |
| `Download captions` | no-match or thin fallback | captions Q&A answer-only |
| `Download transcript text` | possible Notes/Transcript fallback | captions Q&A answer-only |

Expected behavior for all six prompts:

- return the existing captions/live transcription answer
- do not route to Audio, Meeting information, Notes, Transcript, or any
  operable entrypoint
- keep `entrypoint_id is None`
- keep `can_operate is False`
- do not queue an interrupt or demo step
- do not start notes, live transcription, captions, or translation
- do not copy, export, save, download, quote, invent, summarize, or expose
  caption or transcript text
- preserve the boundary that caption or transcript text should only be read
  when the user explicitly asks and visible context is verified

This keeps AiPresenter helpful about where caption, transcription, and
translation controls live while preventing action-content wording from turning
private live meeting text into an operation or unrelated fallback response.

## TDD Evidence

Reported main-session evidence:

- Targeted red before the package YAML edit: `6 failed, 11 passed`.
- Targeted green after adding the six package prompts: `17 passed`.
- Focused package/diagnostics/doctor verification set: `160 passed`.

This handoff subagent did not rerun tests, per instruction and to avoid
touching `.coverage`.

Targeted red/green command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

Focused package/diagnostics/doctor verification command shape:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Before staging in the main session:

```powershell
git diff --check
git status --short
```

Recommended full verification before merge, outside this restricted handoff:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
```

Only stage intended package/test/docs files. Do not stage `.coverage`.

## Diagnostics Impact

The six authored English Q&A prompts explain the Q&A inventory move:

- Q&A prompt duplicate check: `167 -> 173`
- Q&A alias-overlap check: `167 -> 173`
- Package-owned alias count should remain `157`
- Q&A alias substring-risk count should remain `11`
- Q&A localization item totals should remain item-based, not prompt-variant
  based

## Residual Backlog

Already-safe caption/transcript variants remain a backlog item. The earlier
Cycle167 demand/technical scan path recommended pinning those variants through
a larger `173 -> 179` inventory move, but the main session deliberately chose
the true red misroute/no-match slice above. Treat safe-variant pinning as a
separate follow-up, not part of this cycle's implemented behavior.

Possible future exact Q&A variants, only if the coordinator approves another
small pinning slice:

- `Can you export the captions?`
- `Can you save captions?`
- `Can you download captions?`
- `Can you download the transcript?`
- `Export transcript text`
- `Save transcript text`

Keep future additions as exact Q&A prompts under the captions/live
transcription Q&A. Avoid broad aliases such as `caption`, `captions`,
`transcript`, `copy`, `export`, `save`, or `download` because they can steal
legitimate location/control questions or route private-content asks to thin
entrypoint fallback text.

Password/passcode remains deferred. Do not add password, passcode, access-code,
or meeting-credential prompts until product/source evidence confirms whether
RingCentral Video exposes those values on Meeting information or another
verified surface. If approved later, add exact Q&A prompts and update answer
copy so passwords/passcodes are explicitly classified as private meeting access
details.
