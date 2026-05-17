# Cycle 192 Technical Scan: Scan Telemetry

Date: 2026-05-17

## Findings

- Runtime language/tone coverage is broad but provider-gated: `en`, `zh`, `ja`, `es`, and eight
  tones are supported by the runtime, while Japanese and Spanish speech require OpenAI-backed
  profiles.
- Timed logging already exists for package actions and questions through
  `runtime.logging.log_timed_event`, but not for running-app scans.
- The synchronous scan path lives inside `run_controller()` and calls `handle_from_window`,
  `desktop.list_visible_controls()`, and `ControllerSession.scan_running_app()`.
- Running-app scan state already invalidates stale selections; this cycle should not change that
  behavior.
- `docs/knowledge/language-lifecycle.md` had stale Spanish Q&A counts (`12/12`) while current
  localization reports are `16/16`.

## Implementation Shape

- Add a private `_scan_running_app_for_controller()` helper so scan telemetry can be tested
  without launching Tk.
- Use `perf_counter`, `elapsed_ms`, and `log_timed_event`.
- Return a `RunningAppScanResult` with package, flow, handle, counts, duration, and a compact
  status message.
- Keep the UI status privacy-aware by naming the generated package id instead of the window
  title.

## Tests To Touch

- `tests/unit/test_controller.py` for success/error telemetry privacy.
- `tests/unit/test_cli.py` for the language lifecycle count guard.
- Existing focused scan/session/temporary-package tests for regression coverage.
