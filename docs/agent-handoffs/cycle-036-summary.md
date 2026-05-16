# Cycle 036 Summary: Strict Doctor Localization Readiness

Date: 2026-05-16
Cycle: 036
Commit target: `feat: add doctor localization readiness`

## Outcome

Cycle 036 added optional strict localization readiness to `ai-presenter doctor` through `--require-localization`.

When the flag is present, `diagnose_configuration()` now adds a compact `localization` diagnostic check. The check reuses `build_localization_status()` and therefore follows the same required-completeness contract as `localization-report --require-complete`: demo narration, localized Q&A questions, and localized Q&A answers must be complete. Entrypoint alias localization remains informational.

## Files Changed

- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/agent-handoffs/cycle-036-demand-analysis.md`
- `docs/agent-handoffs/cycle-036-technical-scan.md`
- `docs/agent-handoffs/cycle-036-review.md`
- `docs/agent-handoffs/cycle-036-summary.md`
- `docs/superpowers/specs/2026-05-16-doctor-localization-readiness-design.md`
- `docs/superpowers/plans/2026-05-16-doctor-localization-readiness.md`

## Behavior

- Plain `doctor` output remains unchanged when `--require-localization` is absent.
- `doctor --require-localization` without `--package` reports `[FAIL] localization: --require-localization requires --package`.
- `doctor --package ringcentral-video --language zh-CN --tone friendly --require-localization` reports `[OK] localization: required zh localization complete`.
- If no voice language is selected, strict localization defaults to `zh`, matching the existing localization-report default.
- Voice compatibility and voice asset diagnostics remain independent.
- No live RingCentral action or evidence promotion was performed.

## TDD And Review

Red phase:

- Targeted diagnostics and CLI tests initially failed because `diagnose_configuration()` did not accept `require_localization` / `localization_language`, and `doctor` did not yet expose `--require-localization`.

Green phase:

- Added diagnostics-layer localization check and CLI pass-through.
- Added tests for missing package, RingCentral Chinese success, incomplete package failure, plain doctor compatibility, and default strict language behavior.

Review:

- Reviewer found no critical or important issues.
- Reviewer suggested two minor regression guardrails; both were added and verified.

## Verification

Focused verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_material_packages.py`
  - `104 passed`
- `.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
  - `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
  - `Success: no issues found in 4 source files`

Final verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - `552 passed, 1 warning`
- `.\.venv\Scripts\ruff check --no-cache .`
  - `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src tests`
  - `Success: no issues found in 81 source files`
- `git diff --check`
  - Only LF-to-CRLF working-copy warnings were reported; no whitespace errors.

## Next Handoff Ideas

- Implement the deferred Cycle 036 technical-scan idea: cache controller voice readiness by normalized `(language, tone)` key to reduce repeated asset checks when toggling voices.
- Consider a future strict package-readiness mode that combines localization, validation targets, evidence status, and voice readiness into one pre-demo checklist.
