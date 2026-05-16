# Cycle 088 Implementation: control-map-audio-menu JA

Date: 2026-05-16

## Scope

Added Japanese narration for `meeting-control-map-demo` step `control-map-audio-menu`.

This cycle intentionally kept the slice narrow:

- no locator changes
- no route or cleanup changes
- no Q&A changes
- no alias changes
- no neighboring control-map step localization
- no device or audio-route behavior changes

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_audio_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Red result: `5 failed`.

Expected failures:

- JA demo coverage remained `38/51` instead of expected `39/51`.
- `meeting-control-map-demo` remained `9/22` instead of expected `10/22`.
- `control-map-audio-menu` had no `localizedText.ja`.
- CLI and diagnostics still reported `38/51`.

Green command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_audio_menu_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Green result: `5 passed`.

## Behavior Preserved

The focused guard test preserves the Audio menu route:

- `entrypointId: ringcentral.video.toolbar.audio-menu`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- `clickWindowControl`
- target `More`
- `occurrence: '1'`
- `controlType: button`
- `cleanup: escape`

It also verifies no Japanese aliases were added to this entrypoint, global Japanese alias coverage remains unchanged, and presenter notes still describe the observed menu sections plus the system-default-device toast caution.

## Localization Result

Expected Japanese coverage after this slice:

- overall demo coverage: `39/51`
- `meeting-control-map-demo`: `10/22`
- first remaining missing control-map step: `control-map-camera`
- Q&A coverage unchanged: `12/12` questions and `12/12` answers
- alias coverage unchanged: `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese still fails because later control-map steps remain untranslated

## Copy Boundary

The Japanese text describes the audio menu as the recovery entry point for audio issues and identifies where microphone, speaker, computer audio, phone audio, and audio settings live. It treats device names and audio levels as private, and says devices or audio connection will not be touched unless the user explicitly asks.

The copy avoids saying AiPresenter selects or switches devices, leaves computer audio, uses phone audio, opens deeper settings, tests audio, reads device names, or changes the live audio route.
