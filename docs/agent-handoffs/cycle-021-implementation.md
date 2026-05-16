# Cycle 021 Implementation Handoff

## Summary

- Added offline validation-target discovery for RingCentralVideo.
- Added read-only `validation-targets` CLI.
- Preserved existing acceptance draft and package commands.

## Changed Paths

- `src/ai_presenter/acceptance/validation_targets.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_validation_targets.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-021-implementation.md`

## TDD Evidence

- Pure RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py` failed during collection with `ModuleNotFoundError: No module named 'ai_presenter.acceptance.validation_targets'`.
- Pure GREEN: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py` passed with `9 passed in 2.11s`.
- CLI RED: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets` failed with `assert 2 == 0` before command registration.
- CLI GREEN: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_validation_targets.py` passed with `55 passed in 10.41s`.

## Verification

- Ruff: `.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py` passed with `All checks passed!`.
- Mypy: first run caught a missing helper return annotation in `tests\unit\test_validation_targets.py`; after adding it, `.\.venv\Scripts\python -m mypy --no-incremental src tests` passed with `Success: no issues found in 79 source files`.
- Full pytest: final run of `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q` passed with `491 passed, 1 warning in 26.91s`. Warning was the existing pywinauto `Revert to STA COM threading mode`.
- Diff check: `git diff --check -- src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py docs\agent-handoffs\cycle-021-implementation.md` exited `0`; Git printed LF-to-CRLF warnings for `src/ai_presenter/cli.py` and `tests/unit/test_cli.py`.
- CLI smoke: `validation-targets --package ringcentral-video --priority P0` listed `p0-add-coworkers-modal` and `p0-controller-queued-chat-question`; `--target p0-add-coworkers-modal` showed cleanup, privacy, and the entrypoint draft command; `--include-blocked` listed `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave` with `Do not execute`.

## Notes

- No live RingCentralVideo interaction was performed.
- No desktop automation was performed.
- No evidence file or acceptance run was written.
- Default output includes `Note: repo-derived planning list only; not live acceptance evidence.`
- Default output excludes `Do Not Execute Yet` rows unless `--include-blocked` is passed.

## Main-Session Review Fix

The first review found a P2 import-isolation issue: the new `validation-targets`
command body was read-only, but importing `ai_presenter.cli` still loaded
`ai_presenter.runtime.factory`, `ai_presenter.runtime.controller`, and
`ai_presenter.desktop.windows` before Typer dispatch.

Root cause:

- `src/ai_presenter/cli.py` imported `run_desktop_profile`, `run_material_demo`,
  and `run_controller` at module import time.

Fix:

- Replaced those top-level runtime imports with same-name lazy wrapper functions.
- Kept the existing monkeypatch seam for CLI tests.
- Added `test_cli_import_does_not_load_desktop_runtime_modules`, which checks
  a fresh subprocess import of `ai_presenter.cli`.

TDD evidence:

- RED:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules`
  failed because all three probed modules were already loaded.
- GREEN:
  the same focused test passed with `1 passed in 1.84s`.
- Direct probe after fix:
  `desktop.windows False`, `runtime.factory False`, `runtime.controller False`.
- Focused Cycle 021 tests:
  `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py`
  passed with `56 passed in 9.33s`.
- Focused ruff:
  `.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\acceptance\validation_targets.py src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py`
  passed with `All checks passed!`.
