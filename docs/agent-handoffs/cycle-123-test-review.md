# Cycle 123 Test Review: Language Lifecycle Guardrail

Date: 2026-05-16

## Review scope

Reviewed current uncommitted changes for the Cycle 123 language lifecycle guardrail:

- `README.md` lifecycle link near localization and doctor guidance.
- `docs/knowledge/language-lifecycle.md` package-local versus runtime lifecycle wording.
- `tests/unit/test_diagnostics.py` synthetic diagnostics regression for complete package localization with unsupported runtime `es`.
- Current workspace hygiene around generated artifacts.

## Findings

- P2: `.coverage` is modified in the working tree. This is a generated test artifact and should be excluded before final staging/commit. The new lifecycle document also explicitly says not to stage generated artifacts such as `.coverage`.

No blocking issue found in the lifecycle documentation, README link, or diagnostics synthetic regression. The synthetic test does lock the important future state: a package can report complete `es` localization while the separate `runtime language support` diagnostic still fails because presenter runtime does not support `--language es`.

## Verification run

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Result: `3 passed in 1.38s`.

```powershell
git diff --check -- README.md docs/knowledge/language-lifecycle.md tests/unit/test_diagnostics.py docs/agent-handoffs/cycle-123-demand-analysis.md docs/agent-handoffs/cycle-123-implementation.md docs/agent-handoffs/cycle-123-risk-scan.md docs/agent-handoffs/cycle-123-technical-scan.md
```

Result: no whitespace errors; PowerShell surfaced expected LF-to-CRLF working-copy warnings for `README.md` and `tests/unit/test_diagnostics.py`.

```powershell
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
```

Result: exit `1`; `[FAIL] localization: required es localization incomplete: 29/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers`; `[FAIL] runtime language support: localization language es is package-only here; presenter runtime does not support --language es`.

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
```

Result: exit `0`; Spanish remains partial at `29/51` demo steps, Q&A `12/12`, aliases on `1/27` entrypoints with `3` aliases.

## Residual risk

- The guardrail is diagnostics-level and documentation-level. It does not prevent a future runtime-promotion change from adding `es`; it ensures that completing package localization alone is not enough to make diagnostics pass runtime language support.
- The current real RingCentral Spanish package is still incomplete, so the future complete-package case is represented by a focused synthetic package rather than the real package.
- `.coverage` remains a workspace hygiene risk until excluded from final staging.

## Decision

Pass with cleanup note. The Cycle 123 guardrail is fit for the stated purpose once `.coverage` is kept out of the final submitted changes.
