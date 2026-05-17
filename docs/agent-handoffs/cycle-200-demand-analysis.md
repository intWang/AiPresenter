# Cycle 200 Demand Analysis: Localization Report Readiness Boundary

Date: 2026-05-17

## Scope

Evaluate a narrow CLI discoverability improvement for
`ai-presenter localization-report` after Cycle 199's `voices` readiness note.

`localization-report` answers whether package-local text exists for a selected
package language. It should not be read as proof that the presenter runtime can
speak that language with the selected profile, that the selected provider route
is compatible, that local voice assets exist, or that RingCentral Video has
live acceptance evidence.

## User And Operator Value

Operators can run `ai-presenter localization-report --package ringcentral-video --language <lang>`
and immediately see the boundary between package coverage and demo readiness.

This is especially useful for Spanish and future package-only languages:
`--require-complete` may pass, while provider compatibility, local SAPI/Piper
support, and live RingCentral acceptance remain separate checks.

## Recommendation

Add a compact `Readiness boundary:` block in `localization-report` output near
the final summary:

- `This report checks package localization text only.`
- `Use --language with voices, doctor, demo, or controller for runtime voice checks.`
- `Live RingCentral acceptance requires a dated acceptance run.`

Keep the command an offline package inspection tool, not a diagnostics or
acceptance command.

## Acceptance Criteria

- `ai-presenter localization-report --package ringcentral-video --language es`
  prints the existing coverage counts plus a compact readiness boundary note.
- The note says package localization text is the only thing being checked.
- The note points users to `--language` usage with `voices`, `doctor`, `demo`, or
  `controller` for runtime voice checks.
- The note says live RingCentral acceptance requires a dated acceptance run.
- `--require-complete` behavior is unchanged.
- Unknown package-only language keys, such as `de`, remain raw package lookup
  keys and do not fail runtime language validation inside `localization-report`.
- Existing coverage counts for Spanish, Chinese, and Japanese remain unchanged.
- Output remains ASCII-safe for legacy Windows console rendering.

## Non-Goals

- Do not add runtime language support.
- Do not change provider routing, profile compatibility, voice aliases, local
  SAPI/Piper assets, or OpenAI speech behavior.
- Do not change package YAML, localized text, aliases, Q&A, entrypoints, demo
  flows, or localization completeness semantics.
- Do not make `localization-report` load profiles, inspect voice assets, call
  OpenAI, launch RingCentral, run automation, or record acceptance evidence.
- Do not change privacy, safety, question routing, operation eligibility, or
  controller behavior.

## Privacy And Routing Constraints

`localization-report` must remain package-local and offline. It may read
material package metadata, but it must not inspect meetings, windows,
participants, chat messages, invite links, transcripts, screenshots, audio
devices, provider credentials, or live RingCentral state.

The note must not imply that localized package text changes runtime safety
routing. Question policy, `can_operate`, confirmation boundaries, answer-only
rules, interrupt creation, and privacy-sensitive RingCentral routes remain
separate from localization coverage.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py::test_localization_report_explains_readiness_boundaries tests/unit/test_cli.py::test_localization_report_outputs_complete_spanish_package tests/unit/test_cli.py::test_localization_report_keeps_unknown_package_language_key_raw
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language de
git diff --check
```
