# Cycle 157 Risk Scan: RingCentral Video Leave And End Meeting Prompts

Date: 2026-05-17
Cycle: 157
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest related commit inspected: `6fef0f7`

## Scope

Documentation-only risk scan for the current RingCentral Video leave/end meeting
question behavior around these exact English prompts:

- `Leave meeting`
- `End meeting`
- `Hang up`
- `End call`
- `Close meeting`
- `Can you leave the meeting?`

Only this handoff file was authored for the cycle. Do not treat this scan as a
source, package, runtime, test, profile, coverage, or live RingCentral acceptance
change.

## Current Runtime Baseline

Current prompt probes against `packages/ringcentral-video.yaml` and
`answer_question(...)` produced:

| Prompt | Current route | `can_operate` | Interrupt step | Current answer shape |
| --- | --- | --- | --- | --- |
| `Leave meeting` | `ringcentral.video.toolbar.leave` | `False` | none | leave/end safety Q&A |
| `End meeting` | `ringcentral.video.toolbar.leave` | `False` | none | leave/end safety Q&A |
| `Hang up` | `ringcentral.video.toolbar.leave` | `False` | none | leave/end safety Q&A |
| `End call` | `ringcentral.video.toolbar.leave` | `False` | none | leave/end safety Q&A |
| `Close meeting` | `ringcentral.video.toolbar.leave` | `False` | none | leave/end safety Q&A |
| `Can you leave the meeting?` | `ringcentral.video.toolbar.leave` | `False` | none | leave/end safety Q&A |

The answer text is:

`Leaving or ending a meeting is destructive and can affect the current user or everyone in the room. Treat it as explain-only until the user explicitly confirms the visible choice and its impact.`

The current structural safety boundary is strong:

- `ringcentral.video.toolbar.leave` has `openSteps: []`.
- Its package notes explicitly say it is destructive, can immediately show the
  left-meeting state, and needs verbal confirmation before any leave or end
  action.
- `_can_operate(...)` also rejects it because the entrypoint id/title/purpose
  contains risky words such as `leave` and `end`.
- `create_question_interrupt_step(...)` returns `None` whenever
  `can_operate=False`, so controller question handling stays answer-only instead
  of queuing or starting a live UI step.

## Risk Summary

The useful product goal is safe explanation and confirmation design, not live
meeting-exit authority.

These prompts are high-risk because they can map to different RingCentral UI
states depending on role and meeting context: personal leave, host-only end for
everyone, transfer-host or assign-host prompts, a close-window path, or an
already-left state. A broad synonym such as `Hang up` or `Close meeting` must
not be interpreted as permission to click Leave or confirm an exit.

Current behavior is safe from accidental live operation. The main risks are
future drift:

- adding executable `openSteps` to `ringcentral.video.toolbar.leave`
- changing the Q&A answer into a generic `Leave meeting:` entrypoint answer
- treating `End meeting`, `Hang up`, `End call`, or `Close meeting` as direct
  commands instead of safety questions
- letting controller interruption create a queued step for a destructive prompt
- adding localized aliases that bypass the existing Q&A-first safety copy
- updating diagnostic counts mechanically while missing real alias or Q&A
  inventory changes

Recommended risk level: high. The code paths are small, but the user-visible
effect can remove the user from a live meeting or, for hosts, affect everyone.

## Answer-Only Boundary

Keep all six prompts answer-only in the current product surface.

Safe behavior:

- Route to `ringcentral.video.toolbar.leave` for context.
- Keep `can_operate=False`.
- Keep `create_question_interrupt_step(...) is None`.
- Answer with safety copy that explains impact and visible-choice confirmation.
- Distinguish leaving personally from ending for everyone when the UI exposes
  that choice.
- Require a separate explicit confirmation design before any live leave/end
  automation is considered.

No-go behavior:

- Do not click `Leave`, `Leave meeting`, `End meeting`, `End meeting for all`,
  `Confirm`, `OK`, close-window confirmation buttons, or equivalent controls.
- Do not queue an interrupt step for these prompts during a running demo.
- Do not say the meeting has been left, ended, closed, or hung up.
- Do not claim the user is host, not host, alone, or safe to leave unless the
  visible meeting context is verified.
- Do not choose between personal leave and end-for-everyone automatically.
- Do not present unit tests, doctor output, or package routing as live
  RingCentral acceptance.

## Duplicate Alias And Matching Risks

The current leave entrypoint has Spanish and Chinese package-owned aliases, but
no English package-owned aliases. The exact English prompts are handled as Q&A
localized questions with `relatedEntrypointIds:
["ringcentral.video.toolbar.leave"]`, which is the safer shape because Q&A-first
matching returns the safety answer before entrypoint matching renders a generic
entrypoint answer.

Preserve that shape. If future work adds English package-owned aliases such as
`leave`, `hang up`, `end call`, or `close meeting`, it risks stealing prompts
away from Q&A safety copy and making diagnostics harder to reason about. Short
aliases like `leave` are especially risky because they can appear inside broader
questions whose safest response should remain a policy answer.

If localized leave/end prompts are added, prefer exact Q&A prompts first. Only
add entrypoint aliases when the wording is clearly location-oriented, for
example "where is the Leave button", and still keep the entrypoint non-operable.

## Diagnostics And Count Risks

Current live diagnostics from `diagnose_configuration(...)`:

- `question aliases`: `157` package-owned aliases, no cross-entrypoint
  duplicates.
- `qa questions`: `102` Q&A question prompts, no cross-item duplicates.
- `qa alias overlap`: `102` Q&A question prompts, no unsafe package-owned alias
  overlaps.
- `qa alias substring risk`: existing `INFO` with `11` prompts; Q&A-first
  matching still applies.
- Overall doctor shape: `11 ok, 1 info, 0 warnings, 0 failed`.

Concrete test drift found during this scan:

- `tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`
  still expects `92 Q&A question prompts...`, but runtime diagnostics now report
  `102`.
- `tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow` also
  contains old `92` expectations for `qa questions` and `qa alias overlap`.

The targeted prompt behavior passed, but the stale diagnostics expectations
should be corrected in an implementation cycle after confirming the added Q&A
inventory is intentional. Do not hide this by relaxing diagnostics; update exact
counts only after rerunning doctor and reviewing whether overlap/substrings are
still safe.

## Localization Side Effects

Current package state:

- The leave entrypoint intentionally has no Japanese `questionAliases.ja`; prior
  Japanese coverage is narration and Q&A safety, not operable alias expansion.
- The leave entrypoint has Chinese aliases for leaving/exiting/ending the
  meeting, but the runtime remains non-operable because `openSteps` is empty and
  risky-word gating rejects it.
- Spanish aliases are location/option oriented and currently pass duplicate
  alias diagnostics.

Future localization risks:

- Translated terms for "end", "close", "hang up", or "leave" may be action
  commands, not location questions.
- Some languages may use the same phrase for leaving a call and ending it for
  all participants; answers must keep that ambiguity explicit.
- Adding aliases increases localization report counts and may affect doctor
  expected strings.
- Mojibake in PowerShell output can make Japanese/Chinese review hard; inspect
  files with UTF-8-aware tools or tests rather than relying on console-rendered
  glyphs alone.

## Recommended Test Guidance

For future implementation cycles touching this area, keep or add tests that
prove:

- all six exact English prompts route to
  `ringcentral.video.toolbar.leave`
- all six exact prompts return `can_operate is False`
- `create_question_interrupt_step(...) is None`
- answer text contains destructive/impact/explicit-confirmation safety copy
- answer text does not contain the generic prefix `Leave meeting:`
- behavior is tone-invariant
- controller `submit_question(...)` reports text-only or answered-only behavior,
  never `queued` or `started`
- diagnostics counts match the actual package inventory after the change

No-go test patterns:

- Do not make the tests pass by removing `leave` or `end` from
  `_RISKY_ENTRYPOINT_WORDS`.
- Do not add `openSteps` to the leave entrypoint for question-routing tests.
- Do not assert live RingCentral state, host role, visible dialog options, or
  meeting membership from package/runtime unit tests.
- Do not broaden this slice into recording, notes, sharing, invite, host
  controls, or live acceptance.

Recommended verification for an implementation cycle:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_leave_end_questions_stay_qa_first tests\unit\test_questions.py::test_risky_entrypoint_answer_is_not_operable tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages\ringcentral-video.yaml src\ai_presenter\runtime\questions.py src\ai_presenter\runtime\session.py src\ai_presenter\runtime\controller.py tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Avoid coverage-producing commands unless requested. If `.coverage` is already
dirty, leave it untouched.

## Go/No-Go

Go if future work:

- preserves answer-only routing for all exact leave/end prompts
- keeps the leave entrypoint without executable `openSteps`
- preserves no-interrupt behavior in session/controller code
- keeps exact Q&A prompts separate from broad aliases
- explicitly states visible-choice and impact confirmation
- updates diagnostics counts from actual rerun output

No-go if it:

- adds live leave/end automation to the question path
- treats any synonym as sufficient confirmation to leave or end a meeting
- queues a demo interrupt for Leave
- claims host status, participant impact, or current dialog options without
  verified observation
- expands localized aliases in a way that bypasses Q&A-first safety copy
- changes expected diagnostics counts without reviewing the underlying package
  inventory
