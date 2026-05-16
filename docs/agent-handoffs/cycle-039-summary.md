# Cycle 039 Summary: Doctor Question Alias Readiness

Date: 2026-05-16
Cycle: 039
Commit target: `feat: report duplicate package question aliases`

## Outcome

Cycle 039 added a `doctor` diagnostic for package-owned `questionAliases`.

Healthy packages now show an explicit readiness line confirming that package-owned aliases have no cross-entrypoint duplicates. Packages with ambiguous aliases emit a non-fatal warning naming the normalized alias, languages, competing entrypoints, and current first-match entrypoint.

## Files Changed

- `src/ai_presenter/runtime/diagnostics.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-039-demand-analysis.md`
- `docs/agent-handoffs/cycle-039-technical-scan.md`
- `docs/agent-handoffs/cycle-039-review.md`
- `docs/agent-handoffs/cycle-039-summary.md`
- `docs/superpowers/specs/2026-05-16-doctor-question-alias-readiness-design.md`
- `docs/superpowers/plans/2026-05-16-doctor-question-alias-readiness.md`

## Behavior

- `doctor --package` includes `[OK] question aliases` for healthy packages.
- Cross-entrypoint duplicate normalized aliases produce `[WARN] question aliases`.
- Duplicate aliases on the same entrypoint do not warn.
- Cross-language duplicates warn because runtime alias matching ignores language.
- Runtime matching behavior remains unchanged.

## TDD And Review

Red phase:

- Diagnostics tests could not find `question aliases` checks.
- CLI tests could not find the new OK/WARN output.

Green phase:

- Added `_diagnose_question_aliases()`.
- Grouped package-owned aliases by normalized alias.
- Reported only cross-entrypoint conflicts.
- Kept warnings non-fatal.

Review:

- Reviewer found no code issues.
- Added an extra cross-language duplicate test after review to preserve the alias-only grouping rule.

## Verification

Focused verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py tests\unit\test_questions.py tests\unit\test_material_packages.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\diagnostics.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\diagnostics.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Result:

- `144 passed`
- `All checks passed!`
- `Success: no issues found in 3 source files`

Full verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Result:

- `567 passed, 1 warning`
- `All checks passed!`
- `Success: no issues found in 81 source files`
- `git diff --check` reported only LF-to-CRLF working-copy warnings; no whitespace errors.

## Next Handoff Ideas

- Consider a future package-author lint mode that also reports same-entrypoint duplicate aliases as cleanup suggestions.
- Continue expanding language and tone coverage after alias readiness remains stable.
