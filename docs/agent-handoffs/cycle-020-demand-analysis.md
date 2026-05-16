# Cycle 020 Demand Analysis: Disabled Controller Action Reasons

Date: 2026-05-16
Role: demand-analysis worker
Write scope: this file only

## Read Scope

Reviewed local repository context only:

- `docs/agent-handoffs/cycle-019-summary.md`
- `docs/agent-handoffs/cycle-019-demand-analysis.md`
- `docs/agent-handoffs/cycle-019-technical-scan.md`
- `docs/agent-handoffs/cycle-016-summary.md`
- `docs/agent-handoffs/cycle-016-demand-analysis.md`
- `docs/agent-handoffs/cycle-016-technical-scan.md`
- `docs/superpowers/specs/2026-05-16-controller-operator-view-model-design.md`
- `docs/superpowers/specs/2026-05-16-controller-noop-refresh-design.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/controller_view_model.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/voice_assets.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_view_model.py`

No live RingCentral actions were run. No production code, tests, package YAML,
runbook, or knowledge docs were edited.

## Problem Statement

Cycle 019 made the 500 ms controller polling loop calmer by suppressing no-op
status and button writes. The next operator-trust gap is that disabled controls
still communicate only through button state plus broad summary labels. During a
live demo, a disabled Start or Submit can mean several different things:

- the controller is already running;
- the controller is ending and should not accept new work;
- running desktop app mode needs a selected and scanned app;
- selected local voice assets are unavailable;
- Submit has no question text yet.

Those states are mostly represented today in `ControllerOperatorViewModel` as
booleans and labels, but the view model does not expose direct action reasons.
Operators should not have to infer why a button is unavailable from a long
pipe-delimited summary while they are presenting.

## User And Operator Needs

- See an actionable reason next to or within the existing operator status area
  when Start or Submit is disabled.
- Get wording that says what to do next, not just what is wrong.
- Avoid layout churn: no large help panels, no growing text blocks, and no
  repeated widget reconfiguration from the polling loop.
- Keep voice readiness and scan readiness visible independently so one blocker
  does not hide another machine-specific problem.
- Preserve current safety behavior: risky question routes stay answer-only,
  running-app mode still requires scan, and local voice assets still block
  spoken demo work.

Recommended operator-facing reason vocabulary:

- Start enabled: no reason text, or `Start ready`.
- Start while running: `Demo already running; use Pause or End before starting another.`
- Start while ending: `Demo is ending; wait for Ended.`
- Start with no running app selected: `Select a running app, then scan it.`
- Start with selected running app not scanned: `Scan the selected running app first.`
- Start with missing local voice assets:
  `Selected voice assets unavailable: <asset detail>.`
- Defensive material-package/flow failure: `Select a package and flow.`
- Submit enabled: no reason text, or `Submit ready`.
- Submit with empty question: `Type a question to enable Submit.`
- Submit while ending: `Demo is ending; wait for Ended before asking questions.`
- Submit with no running app selected: `Select and scan a running app before questions.`
- Submit with selected running app not scanned:
  `Scan the selected running app before questions.`
- Submit with missing local voice assets:
  `Selected voice assets unavailable: <asset detail>.`

If multiple blockers exist, prefer a compact deterministic list over a hidden
priority, for example `Start unavailable: scan the selected running app first;
voice assets unavailable: speech=windows-sapi-zh requires installed SAPI voice
matching Huihui.` The existing voice-assets summary can carry the full detail if
the rendered action reason needs to stay shorter.

## Recommended Small-Cycle Scope

Make Cycle 020 a pure view-model and lightweight Tk rendering slice.

In scope:

- Extend the controller view model with action availability details, either:
  - `start_disabled_reason` and `submit_disabled_reason`; or
  - a small frozen `ControllerActionAvailability(enabled, reason)` for Start
    and Submit.
- Keep the existing `ControllerButtonStates` booleans for low-risk Tk wiring,
  or derive them from the new availability objects while preserving test names.
- Compute reasons from the same cached snapshot facts already used for button
  enablement: source mode, scan state, run/ending state, question text, and
  cached voice readiness.
- Render the reasons in the current controller surface without a layout rewrite.
  Best first fit: add concise `Actions: Start ... | Submit ...` text to the
  existing operator summary or replace the single summary with stable compact
  rows only if the implementation worker is already touching summary rendering.
- Preserve Cycle 019's no-op behavior by continuing to use `_apply_button_state`
  and by not forcing fresh voice readiness checks from passive refreshes.
- Add focused pure tests in `tests/unit/test_controller_view_model.py` for the
  reason strings and composition cases.
- Add controller tests only if the implementation moves summary rendering into
  a pure helper or needs to prove no-op button writes are preserved.

Out-of-scope items:

- Live RingCentral interaction or manual acceptance promotion.
- New RingCentral package routes, route metadata, safety policy, or evidence
  schema changes.
- Replacing Tk, adding custom tooltip infrastructure, or introducing a browser
  controller.
- Async running-app scanning or background refresh workers.
- Changing voice provider routing, voice aliases, SAPI/Piper discovery, or
  asset installation behavior.
- Allowing text-only answers when voice assets are missing. That may be useful
  later, but the current controller model blocks Submit because safe questions
  can start or queue spoken demo work.
- Broad action reasons for every button. Start and Submit are the high-confusion
  controls; Scan/Refresh/Pause/End can be a later polish pass if needed.

## Acceptance Criteria

- The view model exposes a deterministic reason for disabled Start and disabled
  Submit, and an empty reason or ready label when each action is enabled.
- Material package mode with a valid flow and no local-asset requirement keeps
  Start enabled and shows no blocking reason.
- Running desktop app mode with no selected app disables Start and Submit with
  wording that tells the operator to select and scan an app.
- Running desktop app mode with a selected but unscanned app disables Start and,
  when question text exists, Submit with scan-first wording.
- A scanned running app with missing local voice assets disables Start and
  Submit and includes the concrete asset detail from `ControllerVoiceReadiness`,
  such as `Huihui`, `Zira`, `piper`, or a Piper model name.
- Running state disables Start with a running-demo reason while keeping Submit
  available when the current question, target, and voice conditions allow it.
- Ending state disables Start and Submit with wait-for-ended wording.
- Empty question text disables Submit with `Type a question to enable Submit.`
  without obscuring scan and voice readiness labels elsewhere in the summary.
- Existing button enablement behavior is unchanged for Start, Pause, End,
  Refresh, Scan, and Submit.
- Passive status refresh continues to use cached voice readiness and does not
  add fresh SAPI/Piper checks to the 500 ms polling path.
- Focused controller/view-model tests pass without RingCentral, Tk event-loop
  automation, SAPI voices, Piper models, or live desktop scanning.

## Risks

- Reason precedence risk: showing only the first blocker can hide a missing
  voice asset until after scanning. Prefer deterministic compact composition or
  keep voice-assets detail visible in the same summary.
- Layout risk: long asset details can stretch the existing 720x500 Tk window.
  Keep action reasons concise and put full asset detail in the existing voice
  readiness label if needed.
- Polling risk: adding reasons must not undo Cycle 019's no-op suppression or
  Cycle 016's cached passive voice readiness.
- Safety risk: Submit reasons must not imply risky routes will become
  executable. This cycle explains availability only; route safety remains in
  `describe_question_result()` and package policy.
- Test fragility risk: avoid GUI assertions where pure view-model tests can
  cover the behavior.
- Scope risk: tooltips, every-button explanations, and status-row redesigns are
  tempting but not required for the small cycle.

## Recommendation

Priority: medium-high for operator trust, low for automation breadth.

Recommended Cycle 020 target: add Start and Submit action-reason fields to the
pure controller view model, cover them with focused unit tests, and render them
compactly in the existing operator status surface. This directly follows Cycle
019's no-op refresh work because the UI can explain unavailable actions without
adding new polling side effects or broader layout churn.
