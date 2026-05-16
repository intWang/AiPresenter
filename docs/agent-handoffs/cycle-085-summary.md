# Cycle 085 Summary: Participants Japanese Narration

Date: 2026-05-16

## Outcome

Cycle 085 localized the `meeting-control-map-demo` `control-map-participants` narration for Japanese.

The slice improves RingCentral Video control-map coverage by explaining the roster and people-controls panel while keeping participant identity, roles, and host actions private unless explicitly requested and verified.

## Demand Signal

Japanese users need to know where the participant roster and people controls live after the invite entry points. The presenter should explain the `Participants` panel and close it before Chat, without reading names, searching participants, locking the meeting, muting others, or changing attendee state.

## Technical Change

Updated `packages/ringcentral-video.yaml`:

- added `localizedText.ja` under `meeting-control-map-demo` -> `control-map-participants`
- preserved `entrypointId: ringcentral.video.toolbar.participants`
- preserved `operation: open`
- preserved `placement: during`
- preserved `actionOffsetMs: 350`
- preserved toggle cleanup on the toolbar `Participants` route

Updated tests:

- advanced Japanese demo coverage expectations from `35/51` to `36/51`
- advanced `meeting-control-map-demo` from `6/22` to `7/22`
- moved first missing control-map step from `control-map-participants` to `control-map-chat`
- added a focused guard for the Participants route, toggle cleanup, existing Japanese aliases, presenter notes, roster privacy, and host-control non-actions

Updated knowledge index:

- marked the participants step as part of current Japanese control-map coverage

## Verification

Focused red result before YAML implementation:

- `5 failed`
- failures showed coverage still at `35/51`, control-map still at `6/22`, and missing `localizedText.ja`

Focused green result after implementation:

- `5 passed`

Full verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests` -> `678 passed, 1 warning`
- `.\.venv\Scripts\ruff check --no-cache .` -> `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src tests` -> `Success: no issues found in 81 source files`
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` -> `11 ok, 1 info, 0 warnings, 0 failed`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete` -> `51/51`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` -> `36/51`, `meeting-control-map-demo: 7/22`, first missing `control-map-chat`
- Japanese `--require-complete` returned `exit_code=1`, still expected because later control-map steps remain untranslated
- `git diff --check` -> no whitespace errors; only CRLF working-copy warnings

## Next Candidate

Cycle 086 should continue with `meeting-control-map-demo` step `control-map-chat`, keeping public/private message contents private unless explicitly requested and visible content is verified.
