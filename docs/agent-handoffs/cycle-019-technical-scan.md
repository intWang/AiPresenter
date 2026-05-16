# Cycle 019 Technical Scan: Controller Refresh And UI State

Date: 2026-05-16

## Scope

Scan target: controller UI/performance code around refresh cadence, operator view model
computation, button state updates, expensive checks, thread/UI safety, and tests.

Safety boundary: do not run live RingCentral or desktop automation for this slice. The proposed
work should stay unit-testable with fake controller/session/checker objects.

## Current Architecture And Refresh Flow

- `src/ai_presenter/runtime/controller.py` contains two layers in one file:
  `PresenterController`, which owns demo threads, target state, question interrupts, and runner
  calls; and `run_controller()`, which builds the Tk UI and wires callbacks.
- `PresenterController` starts demos on a daemon `threading.Thread`. UI code observes it through
  properties such as `is_running`, `is_paused`, `is_stopping`, `is_switching_targets`, and
  `last_error`.
- `run_controller()` owns Tk `StringVar` values for status, source, selected package/flow/app,
  voice choices, and question text. Most callbacks call `refresh_operator_view()` after updating
  state.
- `refresh_status()` polls every 500 ms with `root.after(500, refresh_status)`. Each tick calls
  `resolve_controller_status()`, mutates `session` when a run transitions to ended/error, updates
  `status` and `pause_label`, then calls `refresh_operator_view()`.
- `refresh_operator_view()` rebuilds a pure
  `ControllerOperatorSnapshot`, calls
  `build_controller_operator_view_model()`, renders a single summary string, and configures six
  buttons individually.
- `src/ai_presenter/runtime/controller_view_model.py` is the best pure seam. It computes target
  readiness, voice readiness, labels, and button enablement from a frozen snapshot.
- Cycle 016 already added `_ControllerVoiceReadinessCache`. Ordinary UI refreshes use
  `voice_readiness_cache.get(voice)`, while Start and Submit force `refresh(current_voice())` so
  expensive local voice checks are not repeated every 500 ms.
- Running-app refresh and scan remain callback-driven. `refresh_running_windows()` enumerates
  windows and rebuilds the OptionMenu only when the operator clicks Refresh; `scan_selected_app()`
  calls desktop control listing and package synthesis only when Scan is clicked.

## Likely Bottlenecks Or UI Polish Gaps

- `refresh_status()` unconditionally recomputes and reapplies the whole operator view every
  500 ms, even when no visible state changed. The pure view model is cheap, but repeated Tk
  `StringVar.set()` and `button.configure()` calls can still cause avoidable UI churn.
- `refresh_operator_view()` reads several live controller properties one by one. Some are protected
  by `_state_lock`, but `last_error` and `_thread` state are read separately, so a snapshot can be
  slightly mixed across a thread transition. This is probably tolerable today, but the UI should
  not grow more cross-thread reads without a snapshot helper.
- `resolve_controller_status()` returns a state update, but the Tk layer does not track whether
  applying it would be a no-op. That makes it hard to skip downstream view refreshes.
- Button state updates are always applied, even when the desired state is already active. This is
  harmless functionally, but it is an easy, low-risk polish target.
- The operator summary is one long string assembled inside the Tk callback. Any future formatting
  or field-specific update optimization will be hard to test while it stays embedded there.
- Start and Submit intentionally force fresh voice readiness checks. That is correct for safety, but
  the implementation path should preserve the Cycle 016 guarantee that normal polling uses the
  cache and never calls real SAPI/Piper repeatedly.
- `refresh_running_windows()` and `scan_selected_app()` are synchronous Tk callbacks. They are not
  part of the 500 ms polling path, so they are not the first bottleneck, but slow desktop calls can
  still freeze the UI while the operator clicks Refresh or Scan. Defer threading these until a later
  slice because it increases Tk thread-safety risk.
- Tk callbacks all run on the UI thread. Background demo work should continue to communicate only
  through `PresenterController` state; no background thread should touch Tk widgets.

## Exact Files Likely To Change

First focused implementation slice:

- `src/ai_presenter/runtime/controller.py`
  - Add a small pure-ish refresh state/applier helper or module-level functions near
    `ControllerStatusUpdate`.
  - Make status polling skip `refresh_operator_view()` when status, pause label, session stopped
    marker, and operator snapshot inputs have not changed.
  - Make button configuration idempotent by checking current widget state before configuring.
- `src/ai_presenter/runtime/controller_view_model.py`
  - Optional only. Add a pure `render_operator_summary(view_model)` helper if the implementation
    wants summary rendering out of Tk for focused tests.
- `tests/unit/test_controller.py`
  - Add tests for the new refresh-decision helper and idempotent button state helper without
    creating a real Tk root.
- `tests/unit/test_controller_view_model.py`
  - Only change if summary rendering moves into the pure view-model module.

Avoid in the first slice:

- `src/ai_presenter/desktop/*`
- `src/ai_presenter/runtime/factory.py`
- provider or RingCentral package YAML changes
- live RingCentral/manual acceptance docs

## TDD-Friendly Tests To Add

- `test_controller_refresh_decision_skips_view_refresh_when_status_update_is_unchanged`
  - Build an initial applied state such as status `Ready`, pause label `Pause`, no session stop.
  - Apply an identical `ControllerStatusUpdate`.
  - Assert the helper returns `False` for "operator view needs refresh" and does not request a
    session mutation.
- `test_controller_refresh_decision_refreshes_when_status_or_pause_label_changes`
  - Use `ControllerStatusUpdate(status="Paused", pause_label="Resume")`.
  - Assert the helper reports that Tk variables should be updated and the operator view should
    refresh once.
- `test_controller_refresh_decision_marks_session_stopped_once`
  - Apply an update with `mark_session_stopped=True`.
  - Assert it requests one `session.mark_stopped()` operation and then suppresses repeat marks for
    the same ended/error state.
- `test_apply_button_state_skips_configure_when_state_matches`
  - Use a tiny fake button with `cget("state")` and `configure(...)`.
  - Assert enabling an already-normal button does not call `configure`.
- `test_apply_button_state_configures_only_on_state_change`
  - Fake a disabled button, call the helper with `enabled=True`, and assert exactly one configure
    call to `state="normal"`.
- `test_voice_readiness_cache_is_not_refreshed_by_poll_refresh`
  - Extend or complement the existing cache test by simulating repeated operator refresh calls with
    the same voice and asserting the checker call count stays at one.
- If summary rendering moves: `test_render_operator_summary_includes_source_target_flow_voice_assets_scan_question`
  - Construct a `ControllerOperatorViewModel` directly and assert the summary string without
    involving Tk.

Suggested focused commands for the implementation worker:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
```

No test should launch RingCentral, click windows, or rely on installed voice assets.

## Edge Cases And Risks

- Skipping refreshes must not hide transitions from Running to Ended, Error, Paused, Resume, or
  Switching to answer. Tests should cover status and pause-label changes explicitly.
- `session.mark_stopped()` is side-effectful. A skip helper should ensure it is still called once
  when `resolve_controller_status()` requests it, even if visible labels are unchanged.
- Question text changes already call `refresh_operator_view()` via `question.trace_add("write", ...)`.
  Status-poll optimization must not interfere with this immediate button update path.
- Voice language/tone changes call `refresh_operator_view()` from OptionMenu commands. Preserve the
  cached `get()` behavior for passive UI updates and the fresh `refresh()` behavior for Start and
  Submit.
- Running-app selection changes can clear stale scan state. Do not cache operator snapshots so
  broadly that scan-required labels or disabled Start/Submit states lag after selection changes.
- A helper that reads Tk widget state should be testable with a fake button. Avoid requiring a real
  `tk.Tk()` in unit tests because that can be flaky on headless workers.
- Do not move desktop refresh/scan work to background threads in this slice. That likely needs a
  queue or `root.after()` marshal pattern so only the UI thread mutates Tk widgets.
- If adding a `PresenterController` state snapshot method, keep it narrow and lock-backed. Avoid
  holding the lock while calling Tk or any desktop/runner code.

## Recommended Safe Implementation Path

1. Add pure tests in `tests/unit/test_controller.py` for a small refresh-decision helper that
   receives the previously applied UI status state plus a `ControllerStatusUpdate`.
2. Implement the minimal helper in `src/ai_presenter/runtime/controller.py`, near
   `ControllerStatusUpdate`, with a tiny frozen dataclass such as `ControllerAppliedStatusState`.
3. Wire `refresh_status()` to keep the previous applied state in a closure variable. It should set
   Tk variables and call `refresh_operator_view()` only when the helper says visible or button state
   inputs changed, while still scheduling `root.after(500, refresh_status)` every time.
4. Add fake-button tests for idempotent button state updates.
5. Update `apply_button_state()` so it checks the current state before calling `configure()`.
6. Run focused controller/view-model tests.
7. If the summary string needs separate coverage, move only the formatting into
   `controller_view_model.py` and add one pure test. Otherwise leave it in `run_controller()` to keep
   the slice small.
8. Run focused ruff/mypy. A full unit run is useful before merge, but the implementation itself
   should remain offline and RingCentral-free.

Recommended first slice: optimize status/button no-op updates only. Leave asynchronous running-app
refresh/scan for a later cycle after the project has a clear Tk-safe background task pattern.
