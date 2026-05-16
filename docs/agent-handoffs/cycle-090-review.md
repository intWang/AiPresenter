# Cycle 090 Review

## Reviewed files

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/source-index.md`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_diagnostics.py`

## Findings

None.

## Verification readout

- Diff review confirms `meeting-control-map-demo` only adds Japanese narration for `control-map-camera-menu`; `control-map-share` remains the first missing Japanese narration step in that flow.
- Japanese localization status from package parsing is `41/51` demo steps overall and `12/22` for `meeting-control-map-demo`, with first missing step `control-map-share`.
- `control-map-camera-menu` still uses `operation: open`, `placement: during`, `actionOffsetMs: 350`, and route `ringcentral.video.toolbar.video-menu`.
- The camera menu entrypoint still opens target `More` with `occurrence: 2` and cleanup `escape`.
- The Japanese narration describes camera candidates, `More video settings`, and the camera/background/quality appearance route. It does not say to select or switch cameras, read device names, open deeper settings, change background or quality, inspect preview, auto-fix anything, or keep the menu open.
- `questionAliases.ja` was not expanded for the camera menu; package parsing reports `3` localized entrypoints and `9` aliases.
- Tests cover the CLI localization report, material package status/report path, diagnostics localization detail, and the camera menu route/cleanup/safety boundary.

Command run:

```powershell
.venv\Scripts\python.exe -m pytest tests/unit/test_cli.py tests/unit/test_material_packages.py tests/unit/test_diagnostics.py
```

Result: `171 passed`; coverage gate reached with total coverage `80.36%`.

The first attempted global-Python command failed because that interpreter does not have `pytest` installed:

```powershell
python -m pytest tests/unit/test_cli.py tests/unit/test_material_packages.py tests/unit/test_diagnostics.py
```

Failure: `No module named pytest`.

## Commit readiness

Ready to commit the intended package, source-index, and test changes, plus this review handoff if desired.

Do not include `.coverage`; it is modified by the verification run and is unrelated generated state. The other untracked cycle-090 handoff files should be staged only if they are part of the planned cycle bundle.

## Next risk for cycle 091

The next localization step is likely `control-map-share`. Keep the same narrow scope discipline: localize only the next missing narration step, update the expected counts, and preserve the safety boundary around not reading share candidates or pressing the final Share button without explicit user confirmation.
