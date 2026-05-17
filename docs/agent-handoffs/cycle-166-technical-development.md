# Cycle 166 Technical Development: Caption Text Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle166 technical-development handoff subagent

## Scope

Technical-development handoff for the current Cycle166 caption/caption-text
privacy implementation. This subagent wrote only this document.

Source code, package YAML, tests, `.coverage`, staging, commits, resets,
checkouts, and full-suite verification were left untouched by this handoff
pass.

## Changed Files Observed

Dirty tracked files from the main-session implementation:

- `.coverage` is modified in the working tree, but it is unrelated to this
  handoff and was not touched here.
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Existing Cycle166 context docs already present:

- `docs/agent-handoffs/cycle-166-demand-analysis.md`
- `docs/agent-handoffs/cycle-166-risk-scan.md`
- `docs/agent-handoffs/cycle-166-technical-scan.md`

This handoff adds:

- `docs/agent-handoffs/cycle-166-technical-development.md`

## Exact Implementation Edits

`packages/ringcentral-video.yaml` adds four English `localizedQuestions`
prompts to the existing Q&A item,
`Where are captions, live transcription, and translation controls?`:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`

`tests/unit/test_questions.py` mirrors those same four prompts in
`test_ringcentral_captions_and_translation_questions_are_answer_only`.
The test keeps the prompts answer-only and privacy-bounded:

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- answer text includes `Notes and Transcript`
- answer text includes `Settings`
- answer text includes `caption or transcript text`
- answer text includes `explicitly asks`
- answer text includes `verified`
- answer text does not include `Microphone control:`
- answer text does not include `Meeting information:`
- answer text does not include `I could not find a matching control`

`tests/unit/test_diagnostics.py` updates exact Q&A prompt inventory
expectations:

- `161 Q&A question prompts have no cross-item duplicates`
  -> `165 Q&A question prompts have no cross-item duplicates`
- `161 Q&A question prompts have no unsafe package-owned alias overlaps`
  -> `165 Q&A question prompts have no unsafe package-owned alias overlaps`

`tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow` updates
the same doctor-output expectations from `161` to `165`.

No runtime matcher code, entrypoint aliases, related entrypoints, open steps,
profile data, transcript operations, caption controls, or localization
item-count expectations were changed.

## Routing Behavior Fixed

The fix is data-only and relies on existing Q&A-first routing. `_match_qa()`
matches normalized authored Q&A prompts before entrypoint fallback matching.
Adding the four exact caption-content requests to the existing captions/live
transcription Q&A makes them return the authored privacy answer instead of
falling through to unrelated control guidance.

Clean-baseline routing risk fixed by this slice:

| Prompt | Previous route risk | Current route |
| --- | --- | --- |
| `Read caption text` | no-match fallback | captions Q&A answer-only |
| `Show captions text` | no-match fallback | captions Q&A answer-only |
| `Show live caption text` | Audio fallback, `Microphone control:` | captions Q&A answer-only |
| `Read captions aloud` | Meeting information fallback | captions Q&A answer-only |

Expected behavior for all four prompts:

- return the existing captions/live transcription privacy answer
- do not route to Audio, Meeting information, Notes, Transcript, or any
  operable entrypoint
- keep `entrypoint_id is None`
- keep `can_operate is False`
- do not queue an interrupt or demo step
- do not start notes, transcription, captions, or translation
- do not read, quote, invent, summarize, save, copy, export, or speak caption
  or transcript text
- preserve the boundary that caption or transcript text should only be read
  when the user explicitly asks and visible context is verified

This keeps AiPresenter helpful about where caption, transcription, and
translation controls live while preventing private live meeting content wording
from becoming a control action or an unrelated fallback answer.

## TDD Evidence

Reported main-session evidence:

- Targeted red before the package YAML edit: `4 failed, 5 passed`.
- Targeted green after adding the four package prompts: `9 passed`.
- Focused package/diagnostics/doctor verification set: `152 passed`.

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

The four authored English Q&A prompts explain the Q&A inventory move:

- Q&A prompt duplicate check: `161 -> 165`
- Q&A alias-overlap check: `161 -> 165`
- Package-owned alias count should remain `157`
- Q&A alias substring-risk count should remain unchanged unless future prompts
  add unsafe package-owned alias substrings outside related entrypoints
- Q&A localization item totals should remain item-based, not prompt-variant
  based

## Residual Backlog

Password/passcode remains deferred. Do not add password, passcode, access-code,
or meeting-credential prompts until product/source evidence confirms whether
RingCentral Video exposes those values on Meeting information or another
verified surface.

If product evidence later confirms a safe surface, add exact Q&A prompts under
the meeting-info privacy item, not broad aliases. Candidate prompts should stay
narrow, for example:

- `What is the meeting password?`
- `Read the meeting password`
- `Copy the meeting password`
- `What is the meeting passcode?`
- `Read the meeting passcode`
- `Copy the meeting passcode`

Before adding those prompts, update English and localized meeting-info privacy
answers so passwords/passcodes are explicitly classified as private meeting
access details. Tests should assert answer-only routing, no interrupt step, no
clipboard/readout action, and no fallback to unrelated controls.

Possible future caption wording expansion, only if the coordinator approves
another small exact-Q&A slice:

- `Can you read the captions?`
- `Show caption text`
- `Read live captions aloud`
- `Read the live transcript text`

Keep these as exact Q&A prompts. Avoid broad aliases such as `caption`,
`captions`, `text`, `read`, `show`, `live`, `copy`, or `export` because they
can steal legitimate location/control questions or route private-content asks
to thin entrypoint fallback text.

## Coordinator Update After Review

After the test-review pass, Cycle166 accepted two additional exact caption
readout prompts:

- `Can you read the captions?`
- `Can you read captions?`

The final shipped implementation is therefore a six-prompt caption/privacy
slice, and the Q&A prompt count moves from `161` to `167`. The focused
verification set was re-run after this update. `Show caption text` remains a
separate future exact-variant candidate.
