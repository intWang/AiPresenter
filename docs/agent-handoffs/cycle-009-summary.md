# Cycle 009 Summary: Voice Language And Tone Expansion

Date: 2026-05-16

## Objective

Expand AiPresenter's language and tone handling without claiming unsupported new translation or TTS-provider capabilities.

## Outcome

- Added normalized presenter language aliases:
  - English family: `en`, `en-US`, `en-GB`, `English`
  - Chinese family: `zh`, `zh-CN`, `zh-Hans`, `zh-TW`, `zh-Hant`, `Chinese`, `中文`
- Added expanded tone modes:
  - `friendly`
  - `coach`
  - `formal`
- Added tone aliases:
  - `warm` -> `friendly`
  - `mentor` / `coaching` -> `coach`
  - `structured` -> `formal`
- Centralized voice labels and controller choices in `runtime.voice`.
- Updated controller and operator view-model labels to consume shared voice helpers.
- Preserved old deterministic behavior for existing tones, including the non-truncated Chinese question-answer path.
- Kept authored localized narration behavior intact, with existing concise first-sentence behavior only for localized narration.

## Subagent Handoffs

- Demand analysis: `docs/agent-handoffs/cycle-009-demand-analysis.md`
  - Recommended canonical `en`/`zh` only for this cycle and additive tone expansion.
- Technical scan: `docs/agent-handoffs/cycle-009-technical-scan.md`
  - Identified `PresenterVoiceSettings` as the safest normalization boundary and warned against duplicated controller label maps.
- Review: `docs/agent-handoffs/cycle-009-review.md`
  - Approved with no high-severity or blocking issues.
  - Flagged two low-risk follow-ups: do not market `zh-TW`/`zh-Hant` as Traditional Chinese support, and add explicit SAPI rate tests for new tones.

## Review Follow-Up Handled

- Added explicit SAPI rate assertions:
  - Chinese `friendly` -> `-1`
  - Chinese `coach` -> `0`
  - Chinese `formal` -> `0`

## Verification

- Focused voice/controller/provider/question tests:
  - `91 passed in 13.28s`
- Voice-only tests after review follow-up:
  - `17 passed in 0.82s`
- Quality:
  - `ruff`: passed on touched voice/controller/question test files.
  - `mypy`: passed on touched voice/controller/question test files.
  - `git diff --check`: no whitespace errors; expected CRLF conversion warnings only.
- Full suite:
  - `394 passed, 1 warning in 17.43s`

## Risks And Follow-Ups

- `zh-TW` and `zh-Hant` are compatibility aliases to the generic Chinese family, not Traditional Chinese content support.
- True new languages should be added only with package-authored localization, provider profiles, TTS acceptance, and manual review.
- CLI `--language` / `--tone` flags are a good later usability increment.
- Provider-level prosody remains limited; new tones are deterministic text style plus instruction metadata.

## Next Cycle Candidate

Cycle 010 should return to the RingCentral Video knowledge package. The best next increment is a manual/live acceptance evidence index: connect locator matrix rows, manual acceptance checklist items, observed UIA labels, and unresolved risks so future agents can pick the next RingCentral validation target without rereading every doc.
