# Cycle 081 Implementation: JA Control Map Network Quality

Date: 2026-05-16

## Scope

Added Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-network`.

This is a localization-only slice. The implementation preserves:

- `entrypointId: ringcentral.video.top.network-quality`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- entrypoint route `clickWindowRelative` -> `Network quality`
- route coordinates `x: '68'`, `y: '21'`
- `cleanup: escape`

## TDD Evidence

Red command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_network_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Observed red state: `5 failed`. Failures showed the expected current baseline: `31/51`, `meeting-control-map-demo: 2/22`, and missing `localizedText.ja` for `control-map-network`.

Green result after YAML and source-index update:

```text
5 passed in 2.38s
```

## Content Notes

The Japanese narration frames `Network quality` as the meeting-health area for checking whether audio, video, or sharing instability is related to packet loss, jitter, or latency.

The text intentionally avoids over-diagnosis and repair promises. It says AiPresenter does not decide the cause or promise repair without observed values.

## Expected Coverage

- Japanese demo narration: `32/51`
- `meeting-control-map-demo`: `3/22`
- First remaining control-map gap: `control-map-views`
- Japanese Q&A remains `12/12` questions and `12/12` answers
- Japanese aliases remain `3/27` entrypoints and `9` aliases

## Next Slice

Cycle 082 should localize `meeting-control-map-demo` -> `control-map-views`, keeping layout changes distinct from media or meeting-state changes.
