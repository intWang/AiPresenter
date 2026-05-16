# Cycle 012 Implementation Handoff

## Scope

Implemented `docs/superpowers/plans/2026-05-16-voice-profile-preflight.md`
within the worker-owned file set.

## Changes

- Enriched `validate_profile_voice()` errors with profile id, configured speech provider,
  and normalized voice label.
- Added CLI profile/voice preflight for `demo` and `controller` before dry-run completion
  or runtime invocation.
- Added runtime preflight before material-demo desktop drivers, provider registries, window
  binding, or existing-window demo setup.
- Added controller preflight before initial UI setup and before presenter controller run
  threads are launched.
- Updated README and the RingCentral manual acceptance runbook with voice compatibility notes.

## TDD Evidence

- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_validation_error_includes_profile_provider_and_voice`
  - Result: failed, `1 failed`, because the message lacked profile/provider/voice context.
- GREEN: same command
  - Result: passed, `1 passed in 0.47s`.
- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_demo_rejects_unsupported_profile_voice_before_runtime tests\unit\test_cli.py::test_controller_rejects_unsupported_profile_voice_before_runtime`
  - Result: failed, `2 failed`, because both CLI dry-runs exited 0.
- GREEN: same command
  - Result: passed, `2 passed in 3.75s`.
- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_factory.py::test_run_material_demo_validates_voice_before_desktop_driver tests\unit\test_runtime_factory.py::test_existing_window_material_demo_validates_voice_before_desktop_driver tests\unit\test_controller.py::test_run_controller_validates_initial_voice_before_desktop_driver`
  - Result: failed, `3 failed`, because runtime/controller paths touched desktop setup first.
- GREEN: same command
  - Result: passed, `3 passed in 4.60s`.
- RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_validates_voice_before_runner_thread`
  - Result: failed, `1 failed`, because `PresenterController.start()` did not raise.
- GREEN: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_validates_voice_before_runner_thread tests\unit\test_runtime_factory.py::test_run_material_demo_validates_voice_before_desktop_driver tests\unit\test_runtime_factory.py::test_existing_window_material_demo_validates_voice_before_desktop_driver tests\unit\test_controller.py::test_run_controller_validates_initial_voice_before_desktop_driver`
  - Result: passed, `4 passed in 4.40s`.

## Verification

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_voice.py tests\unit\test_controller_session.py`
  - Result: passed, `90 passed in 13.76s`.
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\cli.py src\ai_presenter\runtime\factory.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_voice.py`
  - Result: passed, `All checks passed!`.
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\cli.py src\ai_presenter\runtime\factory.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_runtime_factory.py tests\unit\test_controller.py tests\unit\test_voice.py`
  - Result: passed, `Success: no issues found in 8 source files`.
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: passed, `407 passed, 1 warning in 20.97s`. Warning was the known pywinauto STA COM threading warning.

## Review Notes

- No callable review subagent is available in this session. Local review and verification
  were used instead.
- `git diff --check -- src/ai_presenter/runtime/voice.py src/ai_presenter/cli.py src/ai_presenter/runtime/factory.py src/ai_presenter/runtime/controller.py tests/unit/test_voice.py tests/unit/test_cli.py tests/unit/test_runtime_factory.py tests/unit/test_controller.py README.md docs/runbooks/ringcentral-manual-acceptance.md docs/agent-handoffs/cycle-012-implementation.md`
  - Result: exit 0, no whitespace errors. Git emitted existing LF-to-CRLF normalization warnings for tracked files.

## Concerns

- The worktree had pre-existing dirty changes in owned and unowned files. This worker only
  edited the scoped files requested for Cycle 012.
