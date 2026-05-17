# Cycle 165 Technical Development: Participant Role Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle165 technical-development handoff subagent

## Scope

Technical-development handoff for the current dirty Cycle 165 implementation.
This subagent inspected the current worktree and wrote only this document.
Source code, tests, package YAML, `.coverage`, staging, commits, resets,
checkouts, and full-suite verification were left untouched.

Important context: other Cycle 165 agents recommended caption-text privacy as
the next slice, but the main-session implementation had already started with
participant-role/private-identity prompts. This handoff documents the
implementation that actually exists in the worktree: participant roles under
the existing chat/participants privacy Q&A.

## Changed Files Observed

Dirty tracked files from the main-session implementation:

- `.coverage` is modified in the working tree, but it is unrelated to this
  handoff and was not touched here.
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Untracked Cycle 165 context docs already present:

- `docs/agent-handoffs/cycle-165-demand-analysis.md`
- `docs/agent-handoffs/cycle-165-risk-scan.md`
- `docs/agent-handoffs/cycle-165-technical-scan.md`

This handoff adds:

- `docs/agent-handoffs/cycle-165-technical-development.md`

## Exact Implementation Edits

`packages/ringcentral-video.yaml` adds four English `localizedQuestions`
prompts to the existing Q&A item,
`Can the presenter read meeting messages or participant names?`:

- `Show participant roles`
- `Read participant roles`
- `List participant roles`
- `Who is host or moderator?`

`tests/unit/test_questions.py` mirrors those same four prompts in
`test_ringcentral_participant_identity_requests_stay_answer_only`.
The test keeps them answer-only and privacy-bounded:

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- answer text includes `participant names`, `roles`, and `verified`
- answer text does not include `Participants panel:`
- answer text does not include `I could not find a matching control`

`tests/unit/test_diagnostics.py` updates exact Q&A prompt inventory
expectations:

- `157 Q&A question prompts have no cross-item duplicates`
  -> `161 Q&A question prompts have no cross-item duplicates`
- `157 Q&A question prompts have no unsafe package-owned alias overlaps`
  -> `161 Q&A question prompts have no unsafe package-owned alias overlaps`

`tests/unit/test_cli.py` updates the same doctor-output expectations from
`157` to `161`.

No runtime matcher code, entrypoint aliases, open steps, profile data,
participant toolbar behavior, or localization item-count expectations were
changed.

## Behavior Fixed

The fix is data-only and relies on existing Q&A-first routing. `_match_qa()`
matches normalized authored Q&A prompts before entrypoint aliases and fallback
matching. Adding these exact participant-role/private-identity requests to the
existing chat/participants privacy Q&A makes them return the authored privacy
answer instead of no-match fallback text or Participants-panel guidance.

Expected behavior for all four prompts:

- return the existing chat/participants privacy answer
- do not route to `ringcentral.video.toolbar.participants`
- do not open the Participants panel
- do not read, list, infer, expose, or summarize participant roles
- do not queue an interrupt or other demo step
- preserve the boundary that participant names, roles, chat messages, and
  private tabs should only be read when the user explicitly asks and visible
  context has been verified

This keeps AiPresenter helpful about the relevant safety boundary without
turning role/private-identity wording into an operation on live participant
data.

## TDD Evidence

Reported main-session evidence:

- Targeted red before the package YAML edit: `3 failed, 4 passed`.
- Targeted green after adding the package prompts: `7 passed`.
- Focused package/diagnostics/doctor verification set: `150 passed`.

This handoff subagent did not rerun tests, per instruction and to avoid
touching `.coverage`.

## Diagnostics Impact

The four authored English Q&A prompts explain the Q&A inventory move:

- Q&A prompt duplicate check: `157 -> 161`
- Q&A alias-overlap check: `157 -> 161`
- Package-owned alias count should remain `157`
- Q&A localization item totals should remain item-based, not prompt-variant
  based
- Existing substring-risk expectation should remain unchanged unless future
  prompts add unsafe package-owned alias substrings outside related
  entrypoints

## Residual Backlog

Caption text remains the best next privacy-hardening slice recommended by the
Cycle 165 demand, technical-scan, and risk-scan agents. Prompts such as `Read
caption text`, `Show captions text`, and `Show live caption text` should be
added under the existing captions/live transcription Q&A if that slice is
selected next. Keep them exact Q&A prompts, not broad entrypoint aliases, and
assert they do not fall to Audio guidance, no-match fallback, or transcript
operations.

Password/passcode remains deferred. Current handoffs repeatedly warn not to add
password/passcode prompts until product/source evidence confirms whether
RingCentral Video exposes password, passcode, or access-code values on Meeting
information or another verified surface. If approved later, add exact Q&A
prompts and update English plus localized answer copy so passwords/passcodes
are explicitly classified as private meeting details.

Possible participant-role follow-up variants, only if product need justifies
another small slice:

- `Show roles`
- `What are participant roles?`
- `Read host role`
- `List attendee roles`

Avoid broad aliases such as `roles`, `host`, `moderator`, or `participant`
because they can steal legitimate location/control prompts.

## Verification Recommendations

Focused verification for this participant-role slice:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only
```

Focused package/diagnostics/doctor verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
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
