# Cycle 087 Implementation: control-map-microphone JA

Date: 2026-05-16

## Scope

Added Japanese narration for `meeting-control-map-demo` step `control-map-microphone`.

This cycle intentionally kept the slice narrow:

- no locator changes
- no route or cleanup changes
- no Q&A changes
- no alias changes
- no neighboring control-map step localization
- no mute/unmute behavior changes

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_microphone_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Red result: `5 failed`.

Expected failures:

- JA demo coverage remained `37/51` instead of expected `38/51`.
- `meeting-control-map-demo` remained `8/22` instead of expected `9/22`.
- `control-map-microphone` had no `localizedText.ja`.
- CLI and diagnostics still reported `37/51`.

Green command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_microphone_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Green result: `5 passed`.

## Behavior Preserved

The focused guard test preserves the Microphone route and explain-only semantics:

- `entrypointId: ringcentral.video.toolbar.audio`
- `operation: point`
- `placement: before`
- `actionOffsetMs: 0`
- `clickWindowControl`
- target `Mute`
- `alternateTargets: Unmute`
- `controlType: button`
- no `cleanup`

It also verifies existing Japanese aliases remain unchanged and presenter notes still explain that button text alternates between `Unmute` and `Mute`, and that this entry point is for audio privacy and meeting readiness.

## Localization Result

Expected Japanese coverage after this slice:

- overall demo coverage: `38/51`
- `meeting-control-map-demo`: `9/22`
- first remaining missing control-map step: `control-map-audio-menu`
- Q&A coverage unchanged: `12/12` questions and `12/12` answers
- alias coverage unchanged: `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese still fails because later control-map steps remain untranslated

## Copy Boundary

The Japanese text describes the Microphone button as the main privacy switch for checking local mute readiness before speaking. It says the presenter is explaining location and how to read state, and that mute or unmute will not be changed unless the user explicitly asks.

The copy avoids saying AiPresenter clicks the button, mutes, unmutes, toggles audio, changes media state, tests audio, captures audio, names devices, or opens the audio menu.
