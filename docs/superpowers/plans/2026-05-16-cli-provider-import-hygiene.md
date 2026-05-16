# CLI Provider Import Hygiene Plan

Date: 2026-05-16
Cycle: 027

## Steps

1. Strengthen CLI import tests so the subprocess probe asserts diagnostics, voice assets, and provider modules are not loaded by `import ai_presenter.cli`.
2. Add a package-only subprocess probe for `localization-report --package ringcentral-video --language zh` and assert it also avoids diagnostics, voice assets, and provider modules.
3. Remove top-level CLI imports for `runtime.diagnostics` and `runtime.voice_assets`.
4. Add CLI-level lazy wrappers for diagnostics formatting, diagnostics execution, and voice asset availability.
5. Run focused CLI tests for import hygiene, voices, doctor, and localization-report.
6. Run full verification: pytest, mypy, and ruff.
7. Request implementation review from a subagent and document the cycle handoff.

## Verification Targets

- `python -m pytest tests/unit/test_cli.py --no-cov`
- `python -m pytest tests/unit/test_cli.py tests/unit/test_voice_assets.py --no-cov`
- `python -m pytest`
- `python -m mypy src tests`
- `python -m ruff check src tests`
