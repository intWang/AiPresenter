# Cycle 142 Review: CLI Spanish Entrypoint Display Guard

Date: 2026-05-17
Cycle: 142
Scope: review of `tests/unit/test_cli.py` and
`docs/agent-handoffs/cycle-142-*.md` only. This review intentionally did not
modify source or tests.

## Findings

1. **P2 - Spanish alias coverage does not include the More-menu Cycle140 entry.**
   `tests/unit/test_cli.py:798-831` checks `ringcentral.video.more.background`
   only for `--language es`, while
   `tests/unit/test_cli.py:834-869` parameterizes `Spanish` and `es-MX` only
   against the `Meeting toolbar` area. That leaves
   `ringcentral.video.more.background` and a More-menu fallback entry
   unasserted for the alias inputs, even though
   `docs/agent-handoffs/cycle-142-demand-analysis.md:141-149` requires all
   three language inputs to prove the three Cycle140 entries and both toolbar
   and More-menu fallback markers. The implementation handoff documents the
   same limit at
   `docs/agent-handoffs/cycle-142-implementation.md:102-121` and defers the
   More-menu alias guard to a later cycle at
   `docs/agent-handoffs/cycle-142-implementation.md:211-221`, which means the
   current Cycle142 implementation does not meet the demand-analysis acceptance
   criteria. Manual probes show the CLI currently renders the More-menu alias
   output correctly, so this is a missing regression guard, not a broken runtime
   path. Recommended fix: for each of `es`, `Spanish`, and `es-MX`, invoke the
   `More menu` area and assert `Language: es`,
   `ringcentral.video.more.background` localized title/purpose markers, and
   `ringcentral.video.more.recording` fallback title/purpose markers.

2. **P3 - The alias assertions are more copy-coupled than the marker contract
   needs, and they miss some purpose markers.** In
   `tests/unit/test_cli.py:853-869`, the alias test pins full Spanish prose for
   `audio-menu`, checks only the `video-menu` localized title marker, and checks
   only the direct `audio` fallback title marker. A regression that drops the
   `video-menu` localized purpose marker or the fallback purpose marker under
   `Spanish` / `es-MX` would still pass. Meanwhile, harmless Spanish copy edits
   could fail the test even if the CLI preserved the meaningful contract. This
   cuts against the risk-scan guidance at
   `docs/agent-handoffs/cycle-142-risk-scan.md:93-110`, which centers resolved
   language, entrypoint id/area, and localized/fallback title/purpose markers.
   Recommended fix: use small marker-focused helpers that check each entrypoint
   line and its following purpose marker; keep exact localized copy assertions
   only where they prove a specific display lookup that marker checks cannot.

3. **P3 - The technical handoff's recommended assertion block is internally
   inconsistent.** `docs/agent-handoffs/cycle-142-technical-scan.md:71-77`
   recommends expanding alias coverage over `es`, `Spanish`, and `es-MX`, but
   the sample at `docs/agent-handoffs/cycle-142-technical-scan.md:127-129`
   expects `ringcentral.video.more.notes` in `[Meeting toolbar]`. That looks
   like a More-menu entrypoint id paired with the toolbar area, and following
   the sample would either fail or distract from the actual Cycle142 gap:
   alias coverage for `ringcentral.video.more.background`. Recommended fix:
   correct the sample or remove the misleading line, and align the technical
   handoff with the demand-analysis acceptance criteria.

## Runtime Overclaims

No runtime-support overclaims found in the reviewed handoffs. The docs
consistently frame `entrypoints --language` as package-local display
inspection, not proof of Spanish voice/provider readiness, live RingCentral
acceptance, or matcher eligibility.

## Verification

Focused pytest command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_entrypoints_language_uses_package_local_metadata_without_runtime_voice_validation tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

Result: `5 passed in 1.68s`.

Manual probes:

```powershell
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es-MX
```

Both probes printed `Language: es`, localized title/purpose markers for
`ringcentral.video.more.background`, and fallback title/purpose markers for
`ringcentral.video.more.recording`.

## Residual Risks

- I did not run the full `tests/unit/test_cli.py` module or ruff because this
  was a review-only pass and the focused assertions were enough to validate the
  suspected gap.
- `.coverage` was already dirty in the worktree and was left untouched.

## Main-Session Resolution

All three findings were addressed after this review:

- `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
  now invokes both `Meeting toolbar` and `More menu` for `Spanish` and `es-MX`.
- The alias path now asserts localized title and purpose markers for
  `audio-menu`, `video-menu`, and `more.background`, plus fallback title and
  purpose markers for `toolbar.audio` and `more.recording`.
- The new helper checks the CLI marker contract around the entrypoint line and
  following purpose line, reducing coupling to the exact Spanish copy.
- The inconsistent `ringcentral.video.more.notes` / `[Meeting toolbar]` sample
  in `cycle-142-technical-scan.md` was corrected to
  `ringcentral.video.toolbar.audio`.

Post-resolution focused verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

Expected result: passing focused CLI inspection guard.
