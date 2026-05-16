# Controller Operator View-Model Design

Date: 2026-05-16

## Context

Cycle 001 made safe question interruptions resumable. Cycle 004 hardened the `Add coworkers` RingCentral route. The next highest-leverage UI improvement is to make the controller more trustworthy during live operation without replacing Tk or touching desktop automation.

The current controller builds UI state inline inside `run_controller()`. Some pure helpers already exist in `src/ai_presenter/runtime/controller.py`, but target readiness, scan freshness, voice display, question state, and button enablement are still spread across `StringVar` updates and callbacks.

## Design

Add a small pure module, `src/ai_presenter/runtime/controller_view_model.py`, that turns controller facts into display labels and button states.

The first slice covers:

- Source mode: material package vs running desktop app.
- Target label and flow label.
- Voice label.
- Scan status for running desktop apps.
- Current run status.
- Last question outcome text.
- Button states for Start, Pause/Resume, End, Refresh, Scan, and Submit.

This module does not know about Tk, desktop automation, packages, or sessions. It accepts plain strings, booleans, and `PresenterVoiceSettings`, then returns immutable dataclasses.

## UI Wiring

`run_controller()` will keep its existing layout and add only a compact operator summary line. Button widgets will be stored in local variables so `refresh_status()` can apply the pure view-model's enabled/disabled states.

No hero UI, no redesign, no new framework. This is operational polish: fewer ambiguous states, fewer accidental actions, and clearer readiness.

## Button Policy

- Start is enabled only when not running/stopping and the selected target is ready.
- Pause/Resume is enabled only while a demo is running and not ending.
- End is enabled while running or ending.
- Refresh is disabled while running to avoid target churn during demos.
- Scan is enabled only for a selected running desktop app while idle.
- Submit is enabled only when the question text is non-empty. For running desktop apps, it also requires a scanned selection.

## Running-App Scan Policy

For material package mode, target readiness is always true because the package and flow are known.

For running desktop app mode:

- No selected window: target is not ready, scan status is `No running app selected`.
- Selected but unscanned window: target is not ready, scan status is `Scan required`.
- Selected and scanned window: target is ready, scan status is `Scanned <package_id>`.

## Testing

Add pure unit tests for:

- Material package mode labels and enabled states.
- Running app selected but unscanned state.
- Running app scanned state.
- Running state disabling Start/Refresh/Scan and enabling Pause/End.
- Question text enabling Submit, with scan-required behavior in running-app mode.

Controller Tk wiring remains visually/manual-testable for now; the correctness-critical state rules live in pure tests.

## Out Of Scope

- Tracking current/next demo step.
- Async scan responsiveness or timing telemetry.
- Replacing Tk.
- Changing controller threading or desktop automation.
- Changing question matching or safety policy.

## Cycle Handoff

Cycle 005 should implement this view-model first with TDD, then wire it minimally into `run_controller()`, run focused tests, dispatch review, and record a summary.
