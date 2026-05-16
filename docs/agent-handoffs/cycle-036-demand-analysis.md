# Cycle 036 Demand Analysis: Strict Doctor Localization Readiness

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made in this pass.

## Recommended Slice

Add an optional `--require-localization` flag to `ai-presenter doctor`.

The operator-facing command should be able to fail fast when the selected package language is not fully localized for demo narration and Q&A.

## User Value

Operators already use `doctor` as the pre-demo confidence command. Localization coverage is available through `localization-report --require-complete`, but it is separate, so a Chinese or future-language demo can pass profile and voice checks while still missing package localization.

This closes a readiness gap in the path operators are most likely to run before a live RingCentral Video demo.

## Success Criteria

- `doctor --require-localization` adds a localization diagnostic check.
- `zh-CN` uses canonical `zh` coverage when a voice language is selected.
- RingCentral Chinese package coverage reports OK.
- A package with incomplete required Chinese localization reports FAIL.
- Existing `doctor` behavior is unchanged unless the new flag is used.
- `--require-localization` without `--package` fails clearly.

## Minimum Scope

- Add `--require-localization` to `doctor`.
- Thread the flag into diagnostics.
- Reuse `build_localization_status()`.
- Add one diagnostic check named `localization`.
- Only require demo narration, Q&A localized questions, and Q&A localized answers, matching `required_localization_complete`.
- Update the RingCentral manual acceptance runbook with the strict pre-demo example.

## Must Preserve

- Plain `doctor` behavior and output remain unchanged.
- `localization-report --require-complete` remains unchanged.
- Alias coverage remains informational, not required.
- Voice compatibility and voice asset checks remain independent.
- No package YAML, RingCentral route, presenter skill, matcher order, or evidence-level changes.
- No live RingCentral action or acceptance evidence promotion.

## Suggested Tests

- Diagnostics OK when `require_localization=True` and RingCentral package coverage is complete for `zh`.
- Diagnostics FAIL when `require_localization=True` and a package has incomplete Chinese coverage.
- Diagnostics FAIL clearly when localization is required without a package.
- CLI OK for `doctor --package ringcentral-video --language zh-CN --require-localization` with voice assets mocked available.
- CLI FAIL for `doctor --require-localization` without `--package`.
- Regression: existing doctor tests keep passing without the new flag.

## Out Of Scope

- No new language translations.
- No tone expansion.
- No change to localization completeness rules.
- No live RingCentral validation.
- No changes to acceptance drafts, validation targets, evidence docs, or package routes.
