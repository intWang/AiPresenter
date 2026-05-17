# Cycle 192 Technical Development: Privacy-Safe Scan Telemetry

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/controller.py`
  - Adds `RunningAppScanResult`.
  - Adds `_scan_running_app_for_controller()` with timed success/error telemetry.
  - Updates controller scan status to show package id, controls, entrypoints, and elapsed time.
- `tests/unit/test_controller.py`
  - Adds success/error telemetry tests that assert private title, control names, and exception
    text are not logged.
- `docs/knowledge/language-lifecycle.md`
  - Corrects Spanish Q&A counts from `12/12` to `16/16`.
- `tests/unit/test_cli.py`
  - Guards the Spanish lifecycle count text.

## Telemetry Shape

Successful scans log:

```text
running_app_scanned status=ok duration_ms=... process=... window_class=... pid=... control_count=... entrypoint_count=... openable_count=... explain_only_count=... package=... flow=...
```

Failed scans log:

```text
running_app_scanned status=error duration_ms=... process=... window_class=... pid=... control_count=...
```

The failed path omits package, flow, entrypoint counts, exception text, window title, and control
names.
