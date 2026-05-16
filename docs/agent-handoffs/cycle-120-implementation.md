# Cycle 120 Implementation: Localization Runtime Diagnostics Guard

Date: 2026-05-16
Scope: CLI and diagnostics guard that separates package localization checks from runtime presenter language support.

## Decision

Cycle 120 added a `doctor --localization-language` option for package-localization diagnostics.

This lets maintainers inspect package localization keys such as `es` without passing them through runtime presenter voice parsing. It keeps the meaning of `--language` unchanged: `--language` is still the runtime presenter voice selector, and Spanish remains unsupported there.

## Files Changed

- `src/ai_presenter/cli.py`
  - Added `doctor --localization-language`.
  - When `--require-localization` is used, `--localization-language` overrides the localization check language.
  - If no explicit localization language is provided, doctor preserves the old behavior: use the selected runtime voice language when present, otherwise default to Chinese.
- `src/ai_presenter/runtime/diagnostics.py`
  - Adds a `runtime language support` diagnostic check whenever `require_localization=True`.
  - Reports package-only languages such as `es` as `FAIL` for runtime support.
  - Reports runtime-known languages such as `zh` as `OK`.
  - Does not construct `PresenterVoiceSettings` for package-only localization keys.
- `tests/unit/test_diagnostics.py`
  - Covers Spanish package-localization diagnostics with runtime support failure.
  - Covers Chinese package localization with runtime support success.
- `tests/unit/test_cli.py`
  - Covers `doctor --require-localization --localization-language es`.
  - Covers `--localization-language es` overriding a supported runtime voice check.
  - Keeps existing Spanish runtime rejection behavior.

## Red/Green Evidence

Red command before implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_require_localization_passes_for_ringcentral_chinese tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice
```

Initial result:

- `4 failed`
- Diagnostics tests failed because `runtime language support` did not exist.
- CLI tests failed because `--localization-language` did not exist.

Green command after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_require_localization_passes_for_ringcentral_chinese tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice tests\unit\test_cli.py::test_doctor_require_localization_passes_for_chinese_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime
```

Result:

- `6 passed`

## Expected CLI State

Spanish package localization diagnostics:

- `doctor --require-localization --localization-language es` reaches diagnostics.
- It reports `required es localization incomplete`.
- It reports `7/51 demo steps`, `12/12 Q&A questions`, and `12/12 Q&A answers`.
- It also reports `runtime language support` as `FAIL` because presenter runtime does not support `--language es`.

Runtime Spanish remains rejected:

- `doctor --language es` still fails during runtime voice parsing.
- `demo --language es --dry-run` still fails during runtime voice parsing.
- `voices` still lists English, Chinese, and Japanese only.

Chinese and Japanese package localization remain complete.

## Boundaries Preserved

- No Spanish runtime support was added.
- No Spanish voice catalog entry was added.
- No package YAML changed.
- No Q&A, aliases, route matching, action semantics, provider, profile, presenter skill, or localization-report behavior changed.
- No live RingCentral acceptance claim was added.
- `.coverage` remains out of scope and must not be staged.
