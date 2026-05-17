# Cycle 169 Technical Development: Full-Screen Views Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle169 technical-development handoff subagent

## Scope

Technical-development handoff for the current Cycle169 RingCentral Video
full-screen/view-layout routing implementation. This handoff pass wrote only
this document.

Source code, package YAML, tests, `.coverage`, staging, commits, resets,
checkouts, and full-suite verification were left untouched by this subagent.

Important context: Cycle169 demand and technical scans also suggested a
Meeting information encryption-status Q&A slice. The main session implemented
the full-screen/views routing slice instead. Treat encryption-status as
backlog, not part of this implemented behavior.

## Changed Files Observed

Dirty tracked files from the main-session implementation:

- `.coverage` is modified in the working tree, but it is unrelated to this
  handoff and was not touched here.
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`

Existing Cycle169 context docs already present:

- `docs/agent-handoffs/cycle-169-demand-analysis.md`
- `docs/agent-handoffs/cycle-169-risk-scan.md`
- `docs/agent-handoffs/cycle-169-technical-scan.md`

This handoff adds:

- `docs/agent-handoffs/cycle-169-technical-development.md`

## Exact Implementation Edits

`packages/ringcentral-video.yaml` adds eight English package-owned
`questionAliases` to the existing meeting-window entrypoint:
`ringcentral.video.top.views`.

The actual YAML aliases under `View layout menu` are:

- `Full screen view`
- `Show full screen`
- `Switch to full screen`
- `Where is full screen?`
- `Go full screen`
- `Enter full screen mode`
- `Exit full screen`
- `Leave full screen mode`

No generic `screen`, `full`, `display`, `exit`, or `leave` alias was added.
The implementation keeps the route exact to the Views layout menu, whose
purpose is to switch local meeting layout, including Gallery view and Full
screen.

`tests/unit/test_questions.py` adds
`test_ringcentral_full_screen_questions_route_to_view_layout` for the same
eight user prompts:

- `Show full screen`
- `Switch to full screen`
- `Where is full screen?`
- `Full screen view`
- `Go full screen`
- `Enter full screen mode`
- `Exit full screen`
- `Leave full screen mode`

For each prompt, the test asserts:

- `response.entrypoint_id == "ringcentral.video.top.views"`
- the response does not route to `ringcentral.video.toolbar.share`
- the response does not route to `ringcentral.video.toolbar.leave`
- `response.can_operate is True`
- `create_question_interrupt_step(package, response) is not None`
- the answer starts with `View layout menu:`
- the answer does not contain `Screen sharing:`

`tests/unit/test_diagnostics.py` updates the package-owned alias duplicate
count expectation:

- `157 package-owned aliases have no cross-entrypoint duplicates`
  -> `165 package-owned aliases have no cross-entrypoint duplicates`

`tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow` updates
the same doctor-output expectation:

- `157 package-owned aliases have no cross-entrypoint duplicates`
  -> `165 package-owned aliases have no cross-entrypoint duplicates`

The intermediate count during development was `161`; the final count is `165`
because the completed slice adds eight exact English package-owned aliases.

No runtime matcher code, Q&A prompts, Q&A answers, localized full-screen
aliases, screen-sharing safety Q&A, Meeting information encryption Q&A,
profile data, `questionPolicy`, open-step coordinates, or demo flows were
changed.

## Routing Behavior Fixed

The product routing gap was that common full-screen layout phrases containing
`screen`, `exit`, or `leave` could be pulled toward unrelated entrypoints such
as Screen sharing or Leave when they were not exact aliases for Views.

The final behavior makes all eight exact full-screen prompts route to
`ringcentral.video.top.views`. The question interrupt opens the Views layout
menu; it does not claim that Full screen has already been selected and does
not add a step to click the Full screen option.

Expected behavior for all eight prompts:

- return the Views answer text beginning with `View layout menu:`
- route to `ringcentral.video.top.views`
- remain operable only at the level of opening the Views menu
- create a question interrupt for the Views menu
- avoid the Screen sharing route and answer copy
- avoid the Leave route
- avoid broad aliases that could steal screen-sharing, meeting-exit, or
  meeting-information prompts

This keeps full-screen wording attached to local meeting layout rather than
to sharing the screen or leaving the meeting.

## Root Cause

There were two separate root causes during the implementation:

1. The routing gap itself was data ownership, not matcher logic. Full-screen
   wording needed exact package-owned aliases on
   `ringcentral.video.top.views`, because token fallback could otherwise let
   `screen` drift to `ringcentral.video.toolbar.share` and `exit`/`leave`
   wording drift toward the leave surface.
2. An intermediate YAML edit accidentally placed the early full-screen aliases
   on the pre-meeting `ringcentral.develop.video.tab` entrypoint instead of
   the in-meeting `ringcentral.video.top.views` entrypoint. That explained the
   first mismatch after the initial red test run. The correction was to move
   the exact aliases to the Views entrypoint and then expand coverage to the
   final eight prompt set.

The final diff shows the aliases only under `ringcentral.video.top.views`.

## TDD Evidence

Reported main-session evidence:

- Initial targeted red: `3 failed, 1 passed`.
- Root-cause correction after aliases accidentally landed on the develop video
  tab.
- Expanded targeted red after adding the full eight-prompt expectation:
  `4 failed, 4 passed`.
- Final targeted green for the full-screen test: `8 passed`.
- Focused package/diagnostics/doctor verification set: `151 passed`.

This handoff subagent did not rerun tests, did not run the full suite, and did
not touch `.coverage`, per instruction.

Recommended full verification before merge, outside this restricted handoff:

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
```

Only stage intended package/test/docs files. Do not stage `.coverage`.

## Diagnostics Impact

The eight authored English aliases explain the package-owned alias inventory
move:

- Package-owned aliases: `157 -> 165`
- Intermediate package-owned alias count observed during development: `161`
- Q&A question prompt duplicate check remains `178`
- Q&A alias-overlap prompt count remains `178`
- Q&A alias substring-risk count remains `11`

This slice changes entrypoint alias inventory only. It should not change Q&A
prompt totals or localization item totals.

## Residual Backlog

Encryption-status Q&A remains backlog. Cycle169 demand and technical scans
recommended exact Meeting information encryption-status prompts, but the main
implementation did not add encryption prompts, answer copy, localized answers,
tests, or source-backed UI claims. Keep that as a separate privacy-sensitive
slice. Do not add broad aliases such as `encryption`, `security`, `settings`,
`status`, `copy`, or `details`; prefer exact Q&A prompts with answer-only
behavior and require product/source evidence before claiming any live
encryption state.

Manual UI acceptance for full screen remains separate from this routing test
evidence. The current slice verifies that prompts open the Views menu; it does
not verify selecting the Full screen menu item or the live RingCentral visual
state after selection.

Localized full-screen prompt variants were not added. If needed later, add
localized aliases and tests together so diagnostics and routing expectations
move deliberately.

Future full-screen work should continue to avoid broad `screen` aliases,
because those can steal screen-sharing safety prompts such as `Share screen`,
`Can you share system audio?`, or questions about visible screen content.
