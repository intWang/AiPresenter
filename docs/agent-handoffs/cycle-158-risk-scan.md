# Cycle 158 Risk Scan: Reactions And Raise Hand Exact Prompts

Date: 2026-05-17
Cycle: 158
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest related commit inspected: `c8069db`

## Scope

Documentation-only risk scan for RingCentral Video reaction and raise-hand
question behavior around these exact English prompts:

- `Raise my hand`
- `Lower my hand`
- `Send a thumbs up`
- `Send a reaction`
- `React with thumbs up`
- `Can you raise my hand?`

Only this handoff file was authored for the cycle. Do not treat this scan as a
source, package, runtime, test, profile, coverage, or live RingCentral
acceptance change.

The working tree already contained implementation changes before this scan:

- `packages/ringcentral-video.yaml` adds these six prompts to the existing
  visible-signal safety Q&A item.
- `tests/unit/test_questions.py` adds these six prompts to the existing
  answer-only safety test.
- `.coverage` is dirty.
- `docs/agent-handoffs/cycle-158-demand-analysis.md` is untracked.

Those files were inspected but not edited by this risk-scan pass.

## Current Runtime Baseline

Read-only probes against the current working tree show all six exact prompts now
route to the visible-signal safety Q&A answer:

| Prompt | Current route | `can_operate` | Interrupt step | Current answer shape |
| --- | --- | --- | --- | --- |
| `Raise my hand` | none | `False` | none | visible-signal safety Q&A |
| `Lower my hand` | none | `False` | none | visible-signal safety Q&A |
| `Send a thumbs up` | none | `False` | none | visible-signal safety Q&A |
| `Send a reaction` | none | `False` | none | visible-signal safety Q&A |
| `React with thumbs up` | none | `False` | none | visible-signal safety Q&A |
| `Can you raise my hand?` | none | `False` | none | visible-signal safety Q&A |

The answer text is the existing safety copy:

`Reactions and Raise hand are visible meeting signals. AiPresenter can explain where they are, but should not send a reaction, raise a hand, or leave a hand raised unless the user explicitly asks. Close the reaction strip without sending anything when the user is only exploring, and lower the hand after any confirmed demonstration.`

Location-style prompts still route to the relevant entrypoint without becoming
operable:

| Prompt | Current route | `can_operate` | Interrupt step |
| --- | --- | --- | --- |
| `Where is Raise hand?` | `ringcentral.video.toolbar.raise-hand` | `False` | none |
| `Where are Reactions?` | `ringcentral.video.toolbar.react` | `False` | none |

This is the desired split: command-shaped prompts get the safety answer, while
location-shaped prompts can explain where the controls live without queuing a
live UI action.

## Safety Boundary

The current structural safety boundary is strong:

- Q&A matching runs before entrypoint matching in
  `src/ai_presenter/runtime/questions.py`.
- `create_question_interrupt_step(...)` returns `None` whenever
  `can_operate=False`.
- `ringcentral.video.toolbar.react` is rejected by `_can_operate(...)` because
  its id/title/purpose include risky words such as `reaction` and `send`.
- `ringcentral.video.toolbar.raise-hand` is rejected by `_can_operate(...)`
  because its id/title/purpose include risky words such as `raise hand` and
  `lower hand`.
- The React entrypoint has `cleanup: escape`, so exploratory demos should close
  the reaction strip without sending anything.
- The Raise hand entrypoint has `cleanup: toggle` and an alternate target for
  `onconf.reactions.REMOVE_RAISE_HAND`, so any confirmed demo must restore the
  hand state after showing it.

Recommended risk level: medium-high. Reactions and Raise hand are less
destructive than recording or leaving a meeting, but they are externally visible
meeting signals. A false positive can embarrass the user, interrupt meeting
flow, or imply consent that was not given.

## Risk Summary

No current blocker was found in the inspected behavior. The exact prompts are
answer-only, non-operable, and create no interrupt step.

The main risks are future drift:

- turning exact Q&A prompts into broad entrypoint aliases such as `reaction`,
  `thumbs`, `hand`, `raise`, `lower`, or `send`
- weakening `_RISKY_ENTRYPOINT_WORDS` so `react` or `raise-hand` becomes
  operable from question handling
- adding live reaction-item targeting from question prompts
- treating `Lower my hand` as safe to click without verifying current hand
  state and user intent
- letting a running demo interrupt queue `React` or `Raise hand` from a
  command-shaped question
- translating action-shaped localized prompts as package-owned aliases that
  bypass the Q&A safety answer
- changing diagnostics counts mechanically without reviewing real alias and Q&A
  inventory changes

## No-Accidental-Send Boundary

Safe behavior:

- Answer all six exact prompts with visible meeting signal guidance.
- Keep `entrypoint_id is None`.
- Keep `can_operate=False`.
- Keep `create_question_interrupt_step(...) is None`.
- State that reactions and raised hands are visible to the meeting.
- State that reaction sending, hand raising, and leaving a hand raised require
  explicit user intent.
- State cleanup expectations: close the reaction strip during exploration and
  lower the hand after any confirmed demonstration.

No-go behavior:

- Do not click `React`, `Raise hand`, `Remove raise hand`, thumbs up, heart,
  celebration, clap, smile, Be right back, or any reaction-strip item from
  these question prompts.
- Do not claim a reaction was sent.
- Do not claim the hand was raised, lowered, or already in a known state.
- Do not assume `Lower my hand` means the hand is currently raised.
- Do not queue, start, or interrupt a running demo with these actions unless a
  separate confirmed-action workflow is intentionally designed.
- Do not present package tests or doctor output as live RingCentral acceptance.

## Duplicate Alias And Matching Risks

The current shape is safer than broad aliases because the six prompts live under
the safety Q&A item rather than under the Reactions or Raise hand entrypoints.
This preserves Q&A-first matching and avoids generic entrypoint answers such as
`Reactions: Send meeting reactions without interrupting speech.` or
`Raise hand: Raise or lower hand to request attention.`

Preserve that shape. If future work adds English package-owned aliases, keep
them location-oriented, for example `where are reactions` or
`raise hand button location`. Do not add short command aliases such as `react`,
`thumbs up`, `raise hand`, `lower hand`, or `send reaction`; those are exactly
the prompts that should remain safety answers.

Localized aliases need the same care. Spanish, Japanese, and Chinese may use
short phrases that can mean both "where is the control" and "perform the
action." When the phrase is action-shaped, prefer Q&A safety prompts over
entrypoint aliases.

## Diagnostics And Localization Counts

Current diagnostics from `ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`:

- `question aliases`: `157` package-owned aliases, no cross-entrypoint
  duplicates.
- `qa questions`: `109` Q&A question prompts, no cross-item duplicates.
- `qa alias overlap`: `109` Q&A question prompts, no unsafe package-owned alias
  overlaps.
- `qa alias substring risk`: existing `INFO` with `11` prompts; Q&A-first
  matching still applies.
- Overall doctor shape: `11 ok, 1 info, 0 warnings, 0 failed`.

Current localization reports:

- Japanese: `51/51 demo steps`, `13/13 Q&A questions`, `13/13 Q&A answers`;
  aliases `13/27` entrypoints and `34` aliases.
- Chinese: `51/51 demo steps`, `13/13 Q&A questions`, `13/13 Q&A answers`;
  aliases `15/27` entrypoints and `49` aliases.

The six exact English prompts increased Q&A prompt inventory from the earlier
cycle-157 baseline. Count assertions in `tests/unit/test_diagnostics.py` and
`tests/unit/test_cli.py` now align with the current `109` Q&A prompt count.
Future cycles should rerun doctor before changing exact count strings.

## Recommended Test Guidance

Keep tests that prove:

- all six exact English prompts return the visible-signal safety answer
- all six exact prompts keep `entrypoint_id is None`
- all six exact prompts keep `can_operate is False`
- all six exact prompts create no interrupt step
- `Lower my hand` does not return generic `Raise hand:` entrypoint text
- `React with thumbs up` does not return generic `Reactions:` entrypoint text
- location prompts still route to the proper entrypoint but remain non-operable
- diagnostics counts match the actual package inventory
- localization completion remains unchanged for supported package languages

Recommended verification for an implementation or review cycle:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_raise_hand_location_question_still_routes_to_entrypoint tests\unit\test_questions.py::test_ringcentral_reactions_location_question_still_routes_to_entrypoint
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Avoid coverage-producing commands unless requested. If `.coverage` is already
dirty, leave it untouched.

## Verification Performed

Commands run during this scan:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_raise_hand_location_question_still_routes_to_entrypoint tests\unit\test_questions.py::test_ringcentral_reactions_location_question_still_routes_to_entrypoint
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
```

Results:

- `13 passed`
- `3 passed`
- Doctor completed with `11 ok, 1 info, 0 warnings, 0 failed`
- Japanese localization report complete
- Chinese localization report complete

## Go/No-Go

Go if future work:

- preserves answer-only routing for all six exact prompts
- keeps Reactions and Raise hand non-operable from question handling
- preserves location-question behavior without turning it into live operation
- keeps explicit-demo cleanup semantics intact
- updates exact diagnostics counts only from verified doctor output

No-go if it:

- sends a reaction or toggles Raise hand from any of the six exact prompts
- queues an interrupt step for a reaction or hand prompt
- claims live hand or reaction state without verified visible context
- broadens aliases beyond the six exact English prompts in this slice
- weakens risky-word gating for `reaction`, `send`, `raise hand`, `lower hand`,
  or `toggle`
- changes runtime matching, package models, profiles, acceptance evidence, or
  unrelated RingCentral safety surfaces as part of this narrow prompt slice
