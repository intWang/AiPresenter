# Cycle 118 Implementation: Spanish VBG Demo Narration Wedge

Date: 2026-05-16
Scope: package-local Spanish narration for one RingCentral Video demo flow.

## Decision

Cycle 118 implemented the smaller demand/risk-aligned slice instead of the full 51-step technical option:

- Add Spanish `localizedText.es` for all four `vbg-blur-demo` steps.
- Move Spanish demo narration coverage from `0/51` to `4/51`.
- Keep `meeting-basics-demo`, `meeting-controls-tour`, and `meeting-control-map-demo` untranslated in Spanish.
- Keep Spanish Q&A coverage at `12/12` questions and `12/12` answers.
- Keep Spanish runtime presenter support disabled.

This gives Spanish a complete, reviewable demo wedge for the virtual-background privacy workflow without implying Spanish presenter support.

## Files Changed

- `packages/ringcentral-video.yaml`
  - Added Spanish narration for:
    - `open-video-settings`
    - `open-background-panel`
    - `select-blur`
    - `verify-meeting-video`
  - Preserved literal RingCentral UI labels: `Settings`, `Background`, `Blur`, and `Stop video`.
  - Did not change actions, placements, offsets, aliases, Q&A, entrypoints, locators, or policies.
- `tests/unit/test_material_packages.py`
  - Updates Spanish localization status expectations to `4/51`.
  - Proves only the four `vbg-blur-demo` steps have Spanish demo narration.
  - Proves the required Spanish Q&A report coverage remains complete.
- `tests/unit/test_cli.py`
  - Updates Spanish localization-report expectations to show `vbg-blur-demo: 4/4`.
  - Keeps Spanish `--require-complete` failing because the other 47 demo steps remain untranslated.

## Red/Green Evidence

Red command before package edits:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_vbg_demo_wedge tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_vbg_demo_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_vbg_demo_wedge tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_vbg_demo_wedge
```

Initial result:

- `4 failed`
- Failures showed Spanish demo narration still at `0/51` and `vbg-blur-demo` still at `0/4`.

Green result after package edits:

- `4 passed`

## Expected CLI State

Spanish localization report should now show:

- `vbg-blur-demo: 4/4 narration localized`
- `meeting-basics-demo: 0/3 narration localized`
- `meeting-controls-tour: 0/22 narration localized`
- `meeting-control-map-demo: 0/22 narration localized`
- `4/51` demo steps
- `12/12` Q&A questions
- `12/12` Q&A answers
- `questionAliases.es present on 1/27 entrypoints (3 aliases)`

Spanish `--require-complete` should still fail because Spanish demo narration remains partial.

Spanish runtime should still reject `--language es`; this cycle did not add voice/provider/runtime support.

## Boundaries Preserved

- No `PresenterVoiceSettings(language="es")` support.
- No `voices` Spanish language listing.
- No provider or profile changes.
- No Spanish aliases beyond the existing background/privacy aliases.
- No live RingCentral acceptance claim.
- No private meeting content, participant names, chat text, links, recordings, transcripts, summaries, or state-changing claims in the Spanish narration.
- `.coverage` remains out of scope and must not be staged.
