# Controller Disabled Action Reasons Design

Date: 2026-05-16

## Context

Cycle 016 made voice asset readiness visible and blocked Start/Submit when selected local voice assets are missing. Cycle 019 reduced controller polling churn by skipping no-op status and button writes.

The remaining operator-trust gap is explanatory: Start and Submit can be disabled for several different reasons, but the controller currently exposes only broad summary labels and boolean button state. During a live presentation, the operator should not have to infer the next action from a disabled button.

## Chosen Slice

Add pure view-model fields for disabled Start and Submit reasons, then render those reasons compactly in the existing operator summary. Keep the existing Tk layout, button names, callbacks, and automation behavior.

This slice explains availability; it does not change route safety, desktop scanning, voice provider behavior, or question execution.

## Data Model

Add a frozen dataclass in `src/ai_presenter/runtime/controller_view_model.py`:

```python
@dataclass(frozen=True)
class ControllerDisabledActionReasons:
    start: str = ""
    submit: str = ""
```

Add `disabled_reasons: ControllerDisabledActionReasons` to `ControllerOperatorViewModel`.

Keep `ControllerButtonStates` unchanged so existing Tk wiring and tests continue to assert the same booleans.

## Reason Policy

Reasons are derived only from `ControllerOperatorSnapshot` facts already used for button enablement. They must not call voice asset discovery, desktop scanning, package loading, or Tk APIs.

Start reason precedence:

1. `is_stopping`: `Controller is ending; wait for Ended.`
2. `is_running`: `Demo is already running.`
3. running-app source with no selected window: `Select a running app, then scan it.`
4. running-app source with selected but unscanned window: `Scan the selected running app first.`
5. missing material package/flow: `Select a material package and flow.`
6. voice not ready: `Selected voice assets are not ready: <voice readiness label>`
7. enabled: empty string

Submit reason precedence:

1. `is_stopping`: `Controller is ending; wait for Ended.`
2. empty or whitespace question: `Type a question to enable Submit.`
3. running-app source with no selected window: `Select and scan a running app before questions.`
4. running-app source with selected but unscanned window: `Scan the selected running app before questions.`
5. missing material package/flow: `Select a material package and flow.`
6. voice not ready: `Selected voice assets are not ready: <voice readiness label>`
7. enabled: empty string

When a voice failure is present, use the existing voice readiness label helper so concrete details such as SAPI voice names or Piper model names remain visible.

## UI Rendering

`run_controller().refresh_operator_view()` should append an `Actions:` segment only when at least one reason exists:

```text
Actions: Start blocked: ...; Submit blocked: ...
```

When both actions are ready, omit the segment to avoid adding noise.

The Start and Submit callbacks remain authoritative guards. The Return-key binding still invokes `submit_question()` directly, so callback checks must remain intact.

## Non-Goals

- No live RingCentralVideo interaction.
- No Tk redesign, tooltip infrastructure, browser UI, or screenshots.
- No async Refresh/Scan work.
- No changes to RingCentral package YAML, route safety, evidence docs, or acceptance-record behavior.
- No changes to speech provider routing, voice aliasing, or asset detection.
- No disabled reasons for Pause, End, Refresh, or Scan in this cycle.

## Acceptance Criteria

- Ready material package mode keeps Start enabled with no Start reason.
- Empty question text disables Submit with `Type a question to enable Submit.`
- Running desktop app mode without selection disables Start/Submit with select-and-scan wording.
- Running desktop app mode with selected but unscanned app disables Start/Submit with scan-first wording.
- Missing local voice assets disable Start/Submit and include concrete readiness detail.
- Running state disables Start with `Demo is already running.` while preserving Submit availability when target, voice, and question are ready.
- Ending state disables Start and Submit with wait-for-ended wording.
- Existing Start, Pause, End, Refresh, Scan, and Submit enablement behavior remains unchanged.
- Passive controller refresh continues to use cached voice readiness and Cycle 019 no-op button/status behavior.
- Focused tests pass without RingCentral, Tk event-loop automation, installed SAPI voices, Piper models, or live desktop scanning.

## Risks

- Long voice asset details can stretch the current summary line. This cycle accepts the existing summary surface but keeps reason text concise.
- Showing only the first reason can hide secondary blockers; the existing target/scan/voice labels still expose those independent statuses.
- Reason helpers must remain pure so they do not reintroduce polling cost.
