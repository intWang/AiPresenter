# Cycle 087 Summary: Microphone Japanese Narration

Date: 2026-05-16

## Outcome

Cycle 087 localized the `meeting-control-map-demo` `control-map-microphone` narration for Japanese.

The slice improves RingCentral Video control-map coverage by explaining the microphone as the speaking-readiness and audio privacy checkpoint while preserving explain-only behavior.

## Demand Signal

Japanese users need to understand where to check mute/unmute readiness before speaking. The presenter should point to the microphone control and explain how to read it, without clicking it, muting, unmuting, testing audio, naming devices, or changing live media state.

## Technical Change

Updated `packages/ringcentral-video.yaml`:

- added `localizedText.ja` under `meeting-control-map-demo` -> `control-map-microphone`
- preserved `entrypointId: ringcentral.video.toolbar.audio`
- preserved `operation: point`
- preserved `placement: before`
- preserved absent/default `actionOffsetMs`
- preserved the `Mute`/`Unmute` route and no cleanup

Updated tests:

- advanced Japanese demo coverage expectations from `37/51` to `38/51`
- advanced `meeting-control-map-demo` from `8/22` to `9/22`
- moved first missing control-map step from `control-map-microphone` to `control-map-audio-menu`
- added a focused guard for point-only microphone behavior, existing Japanese aliases, route fields, presenter notes, and no mute/unmute state changes

Updated knowledge index:

- marked the microphone step as part of current Japanese control-map coverage

## Verification

Focused red result before YAML implementation:

- `5 failed`
- failures showed coverage still at `37/51`, control-map still at `8/22`, and missing `localizedText.ja`

Focused green result after implementation:

- `5 passed`

Full verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests` -> `680 passed, 1 warning`
- `.\.venv\Scripts\ruff check --no-cache .` -> `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src tests` -> `Success: no issues found in 81 source files`
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` -> `11 ok, 1 info, 0 warnings, 0 failed`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete` -> `51/51`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` -> `38/51`, `meeting-control-map-demo: 9/22`, first missing `control-map-audio-menu`
- Japanese `--require-complete` returned `exit_code=1`, still expected because later control-map steps remain untranslated
- `git diff --check` -> no whitespace errors; only CRLF working-copy warnings

## Next Candidate

Cycle 088 should continue with `meeting-control-map-demo` step `control-map-audio-menu`, keeping device names, audio route changes, phone audio, and deeper audio settings explanation-only unless explicitly requested and verified.
