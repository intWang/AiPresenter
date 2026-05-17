# Cycle 160 Risk Scan: RingCentral Video System Audio Sharing Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for the Cycle160 RingCentral Video system-audio
sharing prompt slice. Per instruction, this scan did not stage, commit, reset,
or edit source/package/test/runtime files.

Proposed prompt surface:

- `Share system audio`
- `Turn on share system audio`
- `Include system audio`
- `Share computer audio`
- `Can you share system audio?`

Only this handoff file was written.

## Current Evidence

The current dirty tree already contains package/test changes for all five
proposed prompts:

- `packages/ringcentral-video.yaml` adds the five English prompts to the
  existing Q&A item `How should AiPresenter handle screen sharing safely?`.
- `tests/unit/test_questions.py` includes all five prompts in
  `test_ringcentral_english_screen_sharing_questions_stay_qa_first`.
- No runtime matcher source changes were observed for this slice.

Direct runtime probe for the five prompts:

```text
Share system audio | entrypoint=ringcentral.video.toolbar.share | can_operate=False | interrupt=False
Turn on share system audio | entrypoint=ringcentral.video.toolbar.share | can_operate=False | interrupt=False
Include system audio | entrypoint=ringcentral.video.toolbar.share | can_operate=False | interrupt=False
Share computer audio | entrypoint=ringcentral.video.toolbar.share | can_operate=False | interrupt=False
Can you share system audio? | entrypoint=ringcentral.video.toolbar.share | can_operate=False | interrupt=False
```

All five answers returned the existing screen-sharing safety answer beginning
with `Screen sharing can expose private content`.

Doctor output currently reports:

```text
[OK] qa questions: 124 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 124 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 11 ok, 1 info, 0 warnings, 0 failed.
```

Focused test command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Result: `11 passed, 2 failed`. The eleven prompt-routing cases passed. The two
failures are stale diagnostics count expectations: tests still expect `119`
Q&A prompts, while the package now exposes `124`.

## Safety Assessment

No current evidence that the five proposed prompts expose private computer
audio, toggle system audio, press the final `Share` button, or create a
question interrupt step.

The chosen route is the right safety shape: these prompts map to
`ringcentral.video.toolbar.share`, not `ringcentral.video.toolbar.audio-menu`.
System audio is part of the share picker and can broadcast local computer
audio into a live meeting, so treating it as screen-sharing safety guidance is
safer than framing it as normal microphone or speaker device recovery.

`create_question_interrupt_step(package, response)` returned `None` for all
five prompts because each response has `can_operate=False`. This prevents the
question path from queuing `openSteps` for the Share toolbar, selecting the
`Share system audio` checkbox, choosing a source tile, or pressing the final
`Share` button.

## Risks Found

### Blocking Before Commit: Stale Counts

Diagnostics and CLI tests still assert the old `119` Q&A prompt count:

- `tests/unit/test_diagnostics.py` expects `119 Q&A question prompts...`.
- `tests/unit/test_cli.py` expects `119 Q&A question prompts...`.

Because five English prompts were added to an existing Q&A item, the correct
prompt count is now `124`. Doctor already emits `124` with OK status. Update
only the count expectations; Q&A item localization totals remain `14/14`.

### Medium: Answer Text Is Screen-Share General, Not System-Audio Specific

The current answer is safe but generic. It warns that screen sharing can expose
private content, but it does not explicitly say that system/computer audio can
include notification sounds, media playback, calls, recordings, or other app
audio.

This is not a blocker for the narrow answer-only route, but the next agent
should decide whether to keep the reused screen-sharing answer or add one
short system-audio sentence without implying that audio was enabled, disabled,
muted, shared, safe, or verified.

### Low: Alias Overlap Remains OK, But Keep Scope Exact

Doctor reports no unsafe Q&A alias overlap at `124` prompts. Keep the authored
prompt set exact. Do not add broad aliases such as `audio`, `system audio`,
`computer audio`, `share audio`, `sound`, `share`, `screen`, `start`, or
`turn on`; broad aliases would risk stealing ordinary audio-device, screen
sharing, or command-shaped prompts.

## What Not To Change

- Do not make system-audio sharing operable from question prompts.
- Do not add or change `openSteps`.
- Do not click or queue `Share`, the final picker `Share` button,
  `Share system audio`, screen/window tiles, or audio menu controls.
- Do not claim system audio is shared, stopped, enabled, disabled, muted,
  safe, private, or verified.
- Do not read picker entries, app names, window titles, thumbnails, browser
  tabs, notification contents, or local audio sources aloud.
- Do not edit runtime matcher logic unless a later failing test proves it is
  necessary.
- Do not touch `.coverage`, profiles, README, runbooks, acceptance evidence,
  or unrelated handoff docs.

## Recommended Acceptance

Before the main agent commits, verify:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests/unit/test_questions.py::test_ringcentral_english_screen_sharing_questions_stay_qa_first tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Expected after count fixes:

- All five system-audio prompts route to `ringcentral.video.toolbar.share`.
- Each response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- Neither prompt family routes to `ringcentral.video.toolbar.audio-menu`.
- Doctor reports `124 Q&A question prompts` for both Q&A duplicate and alias
  overlap checks.
- Localization counts remain `14/14 Q&A questions` and `14/14 Q&A answers`.

## Handoff Note

This risk-scan agent only inspected the current package/tests/runtime behavior
and wrote this document. It did not run `git add`, `git commit`, or `git reset`.
