# Controller No-Op Refresh Design

Date: 2026-05-16

## Context

The Tk controller refreshes status every 500 ms. Each polling tick currently recomputes the operator view model, writes the status and pause labels, and reconfigures every button even when nothing visible changed.

Cycle 016 already removed the biggest expensive repeat check by caching voice asset readiness for passive refreshes. Cycle 019 takes the next small step: suppress no-op Tk updates while keeping the polling model simple and safe.

## Chosen Slice

Add pure helpers for:

- Deciding whether a `ControllerStatusUpdate` changes visible status/pause state or requires a session-stop side effect.
- Applying button enabled/disabled state only when the widget state actually changes.

Then wire the helpers into `run_controller()` without changing automation behavior, RingCentral routes, question behavior, running-app scan behavior, or voice readiness semantics.

## Architecture

In `src/ai_presenter/runtime/controller.py`:

- Add `ControllerAppliedStatusState`, a frozen dataclass with `status` and `pause_label`.
- Add `ControllerStatusApplication`, a frozen dataclass with:
  - `state`
  - `status_changed`
  - `pause_label_changed`
  - `mark_session_stopped`
  - `refresh_operator_view`
- Add `plan_controller_status_application(current, update)` as a pure function.
- Add `_apply_button_state(button, enabled) -> bool` as a module-level helper. It should call `button.configure(state=...)` only when the current widget state differs from the desired state.

In `run_controller()`:

- Replace the nested `apply_button_state()` with `_apply_button_state()`.
- In `refresh_status()`, call `plan_controller_status_application()` using the current Tk `status` and `pause_label`.
- Apply `session.mark_stopped()` when requested.
- Set Tk variables only when changed.
- Call `refresh_operator_view()` only when status/pause changed or a session-stop mark was applied.
- Always schedule `root.after(500, refresh_status)`.

## Non-Goals

- No Tk layout redesign in this slice.
- No background threading for Refresh or Scan.
- No RingCentral live automation.
- No changes to controller question safety.
- No changes to voice readiness cache semantics.
- No package YAML, evidence, or acceptance-record changes.

## Acceptance Criteria

- A repeated identical status update does not request operator-view refresh.
- Status or pause-label changes do request operator-view refresh.
- Session stop marking requests operator-view refresh even when labels are unchanged.
- Applying an already-correct button state skips `configure()`.
- Applying a changed button state configures exactly once.
- Focused controller tests pass.
- Full test suite, ruff, and mypy pass.

## Risks

- Skipping refreshes must not hide transitions into Running, Paused, Ending, Ended, Error, or Switching to answer.
- Question text, language/tone, running-app selection, Refresh, and Scan callbacks must still call `refresh_operator_view()` directly as they do today.
- The helper must not cache broad operator snapshots because running-app scan validity can change after operator callbacks.
