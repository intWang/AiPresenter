# Cycle 142 Rereview: CLI Spanish Entrypoint Display Guard

Date: 2026-05-17
Cycle: 142
Scope: focused rereview of `tests/unit/test_cli.py` and
`docs/agent-handoffs/cycle-142-*.md` only. This pass did not modify source or
tests.

## Findings

No findings.

The prior review findings appear resolved in the current Cycle142 diff:

- The alias guard now invokes both `Meeting toolbar` and `More menu` for
  `Spanish` and `es-MX`, so `ringcentral.video.more.background` and the
  More-menu fallback marker are covered for both aliases.
- `_assert_entrypoint_display_marker()` checks the entrypoint display line and
  the following purpose line, so the focused assertions now cover both title
  and purpose source markers while avoiding full Spanish-copy coupling for the
  alias cases.
- The technical handoff sample that previously paired
  `ringcentral.video.more.notes` with a toolbar assertion was corrected to a
  toolbar entrypoint. The remaining `more.notes` manual-probe wording is
  consistent with the current package metadata, where that entrypoint's
  `area` is `Meeting toolbar` even though the route opens More.

## Runtime Overclaims

No runtime-support overclaims found in the reviewed Cycle142 handoffs. The docs
keep `entrypoints --language` scoped to package-local display inspection and
explicitly avoid claiming Spanish provider readiness, local SAPI/Piper support,
matcher expansion, or live RingCentral acceptance.

## Brittle-Test Review

The current marker helper is appropriately scoped for this cycle. It still
depends on the CLI contract that each localized entrypoint line is immediately
followed by its purpose line, but that is the output shape under test and is
less brittle than pinning complete localized prose for every alias.

## Verification

Focused CLI test verification:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

Result: `5 passed in 2.08s`.

Style and whitespace checks:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
git diff --check -- tests/unit/test_cli.py
```

Results:

- Ruff: `All checks passed!`
- `git diff --check`: no whitespace errors; Git repeated the existing
  LF-to-CRLF working-copy warning for `tests/unit/test_cli.py`.

Final status observed:

```text
 M .coverage
 M tests/unit/test_cli.py
?? docs/agent-handoffs/cycle-142-demand-analysis.md
?? docs/agent-handoffs/cycle-142-experience.md
?? docs/agent-handoffs/cycle-142-implementation.md
?? docs/agent-handoffs/cycle-142-review.md
?? docs/agent-handoffs/cycle-142-risk-scan.md
?? docs/agent-handoffs/cycle-142-technical-scan.md
```

## Residual Risks

- I did not run the full `tests/unit/test_cli.py` module or the adjacent
  material-package and matcher-boundary sentinels; this was a focused rereview
  of the Cycle142 CLI inspection diff.
- `git diff --check` only covered the tracked test diff. The Cycle142 handoff
  docs are currently untracked, including this rereview file.
- `.coverage` was already dirty and was left untouched.
