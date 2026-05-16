# Cycle 088 Summary: Audio Menu Japanese Narration

Date: 2026-05-16

## Outcome

Cycle 088 localized the `meeting-control-map-demo` `control-map-audio-menu` narration for Japanese.

The slice improves RingCentral Video control-map coverage by explaining the audio recovery menu while keeping device names, audio levels, and route changes private and explanation-only.

## Demand Signal

Japanese users need to know where to recover from wrong microphone, wrong speaker, computer-audio, phone-audio, or deeper audio settings issues. The presenter should open and explain the menu, then close it, without selecting devices, reading device names, interpreting audio levels, leaving computer audio, using phone audio, or opening deeper settings.

## Technical Change

Updated `packages/ringcentral-video.yaml`:

- added `localizedText.ja` under `meeting-control-map-demo` -> `control-map-audio-menu`
- preserved `entrypointId: ringcentral.video.toolbar.audio-menu`
- preserved `operation: open`
- preserved `placement: during`
- preserved `actionOffsetMs: 350`
- preserved `More` occurrence `1` and `cleanup: escape`

Updated tests:

- advanced Japanese demo coverage expectations from `38/51` to `39/51`
- advanced `meeting-control-map-demo` from `9/22` to `10/22`
- moved first missing control-map step from `control-map-audio-menu` to `control-map-camera`
- added a focused guard for the audio-menu route, no Japanese alias expansion, presenter notes, toast caution, and no device/audio-route changes

Updated knowledge index:

- marked the audio-menu step as part of current Japanese control-map coverage

## Verification

Focused red result before YAML implementation:

- `5 failed`
- failures showed coverage still at `38/51`, control-map still at `9/22`, and missing `localizedText.ja`

Focused green result after implementation:

- `5 passed`

Full verification:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests` -> `681 passed, 1 warning`
- `.\.venv\Scripts\ruff check --no-cache .` -> `All checks passed!`
- `.\.venv\Scripts\mypy --no-incremental src tests` -> `Success: no issues found in 81 source files`
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` -> `11 ok, 1 info, 0 warnings, 0 failed`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language zh --require-complete` -> `51/51`
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` -> `39/51`, `meeting-control-map-demo: 10/22`, first missing `control-map-camera`
- Japanese `--require-complete` returned `exit_code=1`, still expected because later control-map steps remain untranslated
- `git diff --check` -> no whitespace errors; only CRLF working-copy warnings

## Next Candidate

Cycle 089 should continue with `meeting-control-map-demo` step `control-map-camera`, keeping camera visibility and video state explanation-only unless explicitly requested and verified.
