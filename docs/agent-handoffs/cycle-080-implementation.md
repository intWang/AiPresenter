# Cycle 080 Implementation: JA Control Map Meeting Info

Date: 2026-05-16

## Scope

Added Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-meeting-info`.

This is a localization-only slice. The implementation preserves:

- `entrypointId: ringcentral.video.top.meeting-info`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- entrypoint route `clickWindowRelative` -> `Meeting information`
- route coordinates `x: '31'`, `y: '21'`
- `cleanup: escape`

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_meeting_info_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Observed red state: `5 failed`. Failures showed the expected current baseline: `30/51`, `meeting-control-map-demo: 1/22`, and missing `localizedText.ja` for `control-map-meeting-info`.

Green result after YAML and source-index update:

```text
5 passed in 1.48s
```

## Content Notes

The Japanese narration explains that `Meeting information` is the meeting-information entry point for `Meeting ID`, links, dial-in information, and encryption status.

The text keeps those values private by default. It says the tour explains only the location and role, and that exact values are not read aloud unless the user explicitly asks.

## Expected Coverage

- Japanese demo narration: `31/51`
- `meeting-control-map-demo`: `2/22`
- First remaining control-map gap: `control-map-network`
- Japanese Q&A remains `12/12` questions and `12/12` answers
- Japanese aliases remain `3/27` entrypoints and `9` aliases

## Next Slice

Cycle 081 should localize `meeting-control-map-demo` -> `control-map-network`, focusing on packet loss, jitter, latency, and meeting health without diagnosing beyond visible metrics.
