# Cycle 036 Technical Scan: Strict Doctor Localization Readiness

Date: 2026-05-16
Role: technical discovery
Scope: read-only technical scan. No implementation changes were made in this pass.

## Recommendation

Implement strict localization readiness in the diagnostics layer, with the CLI only exposing the flag and passing the canonical language.

## Files

- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/runbooks/ringcentral-manual-acceptance.md`

## Existing Boundaries

`doctor` loads profile, optional package, optional flow, and optional voice settings, then calls `diagnose_configuration()`.

`localization-report` already uses:

- `build_localization_status(package, language=...)`
- `LocalizationStatusReport.required_localization_complete`
- `render_localization_status_lines(report)`

The new feature should reuse that package logic instead of duplicating localization counting rules in CLI code.

## Data Flow

Add parameters to `diagnose_configuration()`:

- `require_localization: bool = False`
- `localization_language: str | None = None`

When localization is required:

- If `material_package is None`, append `DiagnosticCheck("FAIL", "localization", "--require-localization requires --package")`.
- Otherwise build the localization report for `localization_language or voice.language or "zh"`.
- Append an OK check when `required_localization_complete` is true.
- Append a FAIL check when incomplete.

CLI should:

- Add `--require-localization` to `doctor`.
- Pass `localization_language=voice.language if voice is not None else None`.
- Keep existing language/tone voice validation behavior unchanged.

## Diagnostic Detail

The localization check should be one-line and count-based:

- OK example: `required zh localization complete: 51/51 demo steps, 8/8 Q&A questions, 8/8 Q&A answers`
- FAIL example: `required zh localization incomplete: 1/2 demo steps, 1/1 Q&A questions, 0/1 Q&A answers`

Keep alias coverage out of pass/fail because existing localization status treats aliases as informational.

## Tests

Add diagnostics tests:

- missing package + required localization yields FAIL check.
- RingCentral zh package yields OK localization.
- a tiny package missing one narration/answer yields FAIL localization.

Add CLI tests:

- `doctor --require-localization` without package exits 1 and prints the clear localization failure.
- `doctor --package ringcentral-video --language zh-CN --tone friendly --require-localization` exits 0 when RingCentral config discovery and voice assets are mocked safe, and prints `[OK] localization:`.

## Risks

- Do not let `--require-localization` turn unsupported languages into supported voice choices. `doctor --language ja` should still be rejected by existing voice normalization unless a future language expansion explicitly changes voice support.
- Do not make `doctor` print the full localization report; keep output compact.
- Do not change `localization-report` behavior.
- Do not require alias localization for pass/fail.
