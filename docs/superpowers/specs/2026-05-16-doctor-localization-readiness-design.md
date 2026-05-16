# Doctor Localization Readiness Design

Date: 2026-05-16

## Goal

Add optional strict localization readiness to `ai-presenter doctor` so operators can use the main pre-demo diagnostic command to catch missing package localization before a RingCentral Video demo.

## Context

`localization-report --require-complete` already verifies that demo narration and Q&A localization are complete for a package language. `doctor` already validates profile, package, flow, RingCentral config, voice compatibility, and voice assets. The gap is that `doctor --language zh-CN` can validate voice readiness without validating that the selected package has complete localized material.

## Design

Add `--require-localization` to the `doctor` command.

The CLI continues to normalize `--language` and `--tone` through `PresenterVoiceSettings` when either option is supplied. When the localization flag is set, it passes the canonical voice language into diagnostics. If no voice was selected, diagnostics defaults the strict localization language to `zh`, matching the existing `localization-report` default.

`diagnose_configuration()` owns the new diagnostic check:

- Missing package: `FAIL localization`.
- Complete required localization: `OK localization`.
- Incomplete required localization: `FAIL localization`.

The check reuses `build_localization_status()` and its `required_localization_complete` property. The pass/fail contract remains limited to demo narration, localized Q&A questions, and localized Q&A answers. Entrypoint alias coverage remains informational and is not required.

## Behavior Contract

- Existing `doctor` output is unchanged unless `--require-localization` is used.
- Existing voice validation remains independent.
- Unsupported voice languages remain unsupported.
- `localization-report` behavior remains unchanged.
- No package YAML changes are required.
- No live RingCentral action is performed.

## Diagnostic Copy

Localization diagnostics should stay compact:

- OK: `required zh localization complete: 51/51 demo steps, 8/8 Q&A questions, 8/8 Q&A answers`
- FAIL: `required zh localization incomplete: 1/2 demo steps, 1/1 Q&A questions, 0/1 Q&A answers`
- Missing package: `--require-localization requires --package`

## Tests

Add diagnostics tests for missing package, complete RingCentral Chinese coverage, and incomplete package coverage.

Add CLI tests for the missing-package failure and a RingCentral Chinese strict-doctor success path with RingCentral config discovery and voice assets mocked.

## Out Of Scope

- No Japanese or additional voice language support.
- No new package translations.
- No tone expansion.
- No alias completeness requirement.
- No full localization report embedded in doctor output.
