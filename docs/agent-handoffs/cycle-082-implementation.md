# Cycle 082 Implementation: JA Control Map View Layout

Date: 2026-05-16

## Scope

Added Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-views`.

This is a localization-only slice. The implementation preserves:

- `entrypointId: ringcentral.video.top.views`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- entrypoint route `clickWindowRelative` -> `Views`
- route coordinate `xFromRight: '237'`, `y: '21'`
- `cleanup: escape`

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_views_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Observed red state: `5 failed`. Failures showed the expected current baseline: `32/51`, `meeting-control-map-demo: 3/22`, and missing `localizedText.ja` for `control-map-views`.

Green result after YAML and source-index update:

```text
5 passed in 1.68s
```

## Content Notes

The Japanese narration explains that `Views` is the `View layout` menu for seeing layout options such as `Gallery view` and `Full screen`.

The text intentionally avoids saying AiPresenter switches or selects a layout. It also keeps the boundary that this step does not handle audio, video, sharing, or participant state.

## Expected Coverage

- Japanese demo narration: `33/51`
- `meeting-control-map-demo`: `4/22`
- First remaining control-map gap: `control-map-report`
- Japanese Q&A remains `12/12` questions and `12/12` answers
- Japanese aliases remain `3/27` entrypoints and `9` aliases

## Next Slice

Cycle 083 should localize `meeting-control-map-demo` -> `control-map-report`, treating Report issue as an escalation dialog and avoiding automatic report submission.
