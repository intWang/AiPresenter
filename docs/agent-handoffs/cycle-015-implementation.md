# Cycle 015 Implementation: Voice Asset Availability

Date: 2026-05-16

## Scope Summary

- Added read-only Windows SAPI voice discovery helpers and case-insensitive substring matching.
- Added read-only Piper module/model asset helpers for the default `en_US-lessac-medium` voice.
- Added `ai_presenter.runtime.voice_assets` to map resolved speech routes to local asset checks.
- Surfaced `voice assets` diagnostics after successful voice compatibility checks.
- Surfaced local asset status in `voices --profile`; targeted `voices --profile --language/--tone`
  exits nonzero when selected local assets are missing.
- Updated README and RingCentral manual acceptance notes.

No downloads, synthesis, cloud calls, or RingCentral automation were run.

## Red/Green Evidence

- Provider RED:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_windows_speech_provider.py::test_list_installed_sapi_voices_uses_injected_dispatcher tests\unit\test_windows_speech_provider.py::test_sapi_voice_available_matches_case_insensitive_substrings`
  - Result: failed during collection because `InstalledSapiVoice` did not exist.
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_piper_provider.py::test_default_piper_voice_assets_use_provider_data_dir tests\unit\test_piper_provider.py::test_piper_voice_assets_available_requires_model_and_config`
  - Result: failed during collection because `default_piper_voice_assets` did not exist.
- Provider GREEN:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py`
  - Result: `11 passed in 0.24s`.
- Runtime RED:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice_assets.py`
  - Result: failed during collection because `ai_presenter.runtime.voice_assets` did not exist.
- Runtime GREEN:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice_assets.py`
  - Result: `4 passed in 0.36s`.
- Diagnostics and CLI RED:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_voice_assets_after_supported_voice tests\unit\test_diagnostics.py::test_diagnostics_fails_for_missing_voice_assets`
  - Result: failed because `diagnostics.check_voice_asset_availability` was not imported/called.
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_profile_reports_local_asset_status tests\unit\test_cli.py::test_voices_targeted_missing_assets_exits_nonzero`
  - Result: failed because `ai_presenter.cli.check_voice_asset_availability` was not imported/called.
- Diagnostics and CLI GREEN:
  - Same focused diagnostics and CLI commands.
  - Result: `2 passed in 3.24s` for each command.
- Additional diagnostics coverage:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_piper_voice_assets tests\unit\test_diagnostics.py::test_diagnostics_fails_for_missing_piper_voice_assets`
  - Result: `2 passed in 3.41s`.

## Verification

- Focused pytest:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py tests\unit\test_voice_assets.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
  - Result: `59 passed in 6.51s`.
- Scoped ruff:
  - `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\providers\windows_speech.py src\ai_presenter\providers\piper_provider.py src\ai_presenter\runtime\voice_assets.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py tests\unit\test_voice_assets.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
  - Result: `All checks passed!`.
- Scoped mypy:
  - `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\providers\windows_speech.py src\ai_presenter\providers\piper_provider.py src\ai_presenter\runtime\voice_assets.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py tests\unit\test_voice_assets.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
  - Result: `Success: no issues found in 10 source files`.
- Full pytest:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - Result: `443 passed, 1 warning in 22.52s`.
  - Warning: known `pywinauto` STA COM threading warning.

## Notes And Concerns

- The worktree was dirty before this implementation; changes were kept inside the assigned write set.
- `voices --profile` may report local asset FAIL details on machines without SAPI voices or Piper assets,
  but matrix mode remains exit code 0.
- `doctor --language/--tone` is now stricter for local routes and fails when the selected local voice assets
  are missing.
