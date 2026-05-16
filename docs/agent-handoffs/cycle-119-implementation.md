# Cycle 119 Implementation: Spanish Meeting Basics Narration Wedge

Date: 2026-05-16
Scope: package-local Spanish narration for the three-step RingCentral Video meeting-basics demo.

## Decision

Cycle 119 added Spanish narration for `meeting-basics-demo` only.

Target movement:

- Spanish demo narration: `4/51` -> `7/51`
- `vbg-blur-demo`: remains `4/4`
- `meeting-basics-demo`: `0/3` -> `3/3`
- `meeting-controls-tour`: remains `0/22`
- `meeting-control-map-demo`: remains `0/22`
- Spanish Q&A remains `12/12` questions and `12/12` answers
- Spanish aliases remain `1/27` entrypoints and `3` aliases
- Spanish runtime remains unsupported

This advances Spanish package localization through another complete short demo while keeping the runtime-language boundary intact.

## Files Changed

- `packages/ringcentral-video.yaml`
  - Added `localizedText.es` for:
    - `meeting-basics-demo:show-mic`
    - `meeting-basics-demo:show-participants`
    - `meeting-basics-demo:show-chat`
  - Preserved visible RingCentral UI labels `Participants` and `Chat`.
  - Kept the microphone line focused on local audio readiness.
  - Kept the Participants line from reading names or private details by default.
  - Kept the Chat line from reading chat contents unless the user explicitly asks.
- `tests/unit/test_material_packages.py`
  - Updated Spanish localization status expectations to `7/51`.
  - Proves Spanish demo narration exists only for VBG plus meeting-basics short demos.
  - Adds Spanish text guards for `Participants`, `Chat`, and chat privacy wording.
- `tests/unit/test_cli.py`
  - Updates Spanish localization-report expectations to show `meeting-basics-demo: 3/3` and total `7/51`.
  - Keeps Spanish `--require-complete` failing because the two large demo flows remain untranslated.

## Red/Green Evidence

Red command before package edits:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_short_demo_wedges_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_short_demo_wedges tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_short_demo_wedges
```

Initial result:

- `4 failed`
- Failures showed Spanish total still `4/51` and `meeting-basics-demo` still `0/3`.

Green command after package edits:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_short_demo_wedges_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_short_demo_wedges tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_short_demo_wedges tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime
```

Result:

- `5 passed`

## Expected CLI State

Spanish localization report should now show:

- `vbg-blur-demo: 4/4 narration localized`
- `meeting-basics-demo: 3/3 narration localized`
- `meeting-controls-tour: 0/22 narration localized`
- `meeting-control-map-demo: 0/22 narration localized`
- `7/51` demo steps
- `12/12` Q&A questions
- `12/12` Q&A answers
- `questionAliases.es present on 1/27 entrypoints (3 aliases)`

Spanish `--require-complete` should still fail because Spanish demo narration remains partial.

Spanish runtime should still reject `--language es`; this cycle did not add voice, provider, profile, or runtime support.

## Boundaries Preserved

- No Spanish runtime support was added.
- No `voices` Spanish language listing was added.
- No provider/profile changes were made.
- No Spanish aliases were added beyond the existing background/privacy aliases.
- No Q&A, route matching, locator, policy, cleanup, action placement, or offset behavior was changed.
- No live RingCentral acceptance claim was added.
- `.coverage` remains out of scope and must not be staged.
