# Cycle 123 Technical Scan: Spanish Meeting Control Map

Date: 2026-05-16

Scope: technical scan only. This handoff is the only file changed by this subagent. Do not modify business code, package YAML, tests, runtime language support, README, durable knowledge, generated artifacts, or existing handoffs in this scan.

## Current state

- Spanish package localization is currently partial but well bounded:
  - `vbg-blur-demo`: `4/4` Spanish narration localized.
  - `meeting-basics-demo`: `3/3` Spanish narration localized.
  - `meeting-controls-tour`: `22/22` Spanish narration localized after Cycle 122.
  - `meeting-control-map-demo`: `0/22` Spanish narration localized.
  - Overall Spanish demo narration: `29/51`.
  - Spanish Q&A remains complete: `12/12` localized questions and `12/12` localized answers.
  - Spanish aliases remain intentionally sparse: `questionAliases.es` appears on `1/27` entrypoints with `3` aliases.
- Read-only verification in this scan:
  - `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es` exits `0` and reports `29/51`, `meeting-controls-tour: 22/22`, and `meeting-control-map-demo: 0/22`.
  - `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete` exits `1` and prints `Localization coverage incomplete for es.`
- Runtime Spanish remains unsupported by design:
  - `tests/unit/test_cli.py::test_demo_rejects_unknown_language_before_runtime` asserts `demo --language es --dry-run` fails with `Unsupported presenter language: es`.
  - `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language` asserts `localization language es is package-only` and `does not support --language es`.
- README/runbook examples continue to promote English and Chinese runtime paths, while README already states localization keys are separate from runtime presenter voice support.
- Existing Cycle 123 demand/risk handoffs agree that `.coverage` is unrelated generated drift and must stay out of any localization submission.

## Implementation recommendation

Recommended minimum verifiable implementation slice: complete Spanish package-local narration for `meeting-control-map-demo` only.

Expected coverage delta:

- Spanish demo narration moves from `29/51` to `51/51`.
- `meeting-control-map-demo` moves from `0/22` to `22/22`.
- `meeting-controls-tour` stays `22/22`.
- `vbg-blur-demo` stays `4/4`.
- `meeting-basics-demo` stays `3/3`.
- Spanish Q&A stays `12/12` questions and `12/12` answers.
- Spanish aliases stay `1/27` entrypoints with `3` aliases.
- Spanish runtime stays unsupported.

This is the smallest coherent package-local slice because it completes the only remaining Spanish demo-flow gap without touching voice routes, controller language choices, providers, profiles, Q&A, aliases, locators, action semantics, or docs claiming runtime support. A one-step map-demo slice would be technically smaller, but it would leave the same flow incomplete and create another count-only bookkeeping cycle.

Implementation boundaries:

- Add `narration.localizedText.es` for exactly the 22 existing `meeting-control-map-demo` steps in `packages/ringcentral-video.yaml`.
- Do not change English, Chinese, Japanese text, step IDs, entrypoint IDs, operation types, `placement`, `actionOffsetMs`, `openSteps`, cleanup behavior, `questionPolicy`, Q&A, aliases, runtime code, CLI semantics, README, runbooks, or durable knowledge.
- Keep RingCentral product labels in English where the operator must locate UI, including `Meeting information`, `Network quality`, `Views`, `Report`, `Add coworkers`, `Invite`, `Participants`, `Chat`, `Mute`, `Audio options`, `Start video`, `Share`, `Reactions`, `Raise hand`, `More`, `Recording`, `Notes`, `Background`, `Settings`, and `Leave`.

## Test plan

TDD red phase before YAML edits:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_meeting_controls_tour tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_meeting_controls_tour_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language
```

Expected red after updating tests but before YAML implementation:

- Spanish report expectations move to `51/51`, but actual remains `29/51`.
- `meeting-control-map-demo` expectations move to `22/22`, but actual remains `0/22`.
- `--require-complete` Spanish CLI expectation should change from failing to passing for package localization, but actual remains exit `1`.
- Doctor/diagnostics expectations should still fail on runtime language support for `es`; only the localization detail changes from incomplete to complete.

Focused test updates:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_meeting_controls_tour`
  - Rename if useful, for example to `test_ringcentral_localization_status_reports_complete_spanish_package`.
  - Change `report.demo_localized_steps` from `29` to `51`.
  - Change `report.required_localization_complete` from `False` to `True`.
  - Assert `meeting-control-map-demo.localized_steps == 22`, `total_steps == 22`, and `missing_step_ids == ()`.
  - Keep Q&A and alias counts unchanged.
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_qas_and_meeting_controls_tour_are_localized`
  - Rename if useful, for example to `test_ringcentral_spanish_qas_and_demo_flows_are_localized`.
  - Extend `expected_spanish_demo_steps` with all 22 `meeting-control-map-demo:*` step IDs.
  - Add representative assertions for map-demo Spanish wording and preserved UI labels.
- `tests/unit/test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour`
  - Expect `- meeting-control-map-demo: 22/22 narration localized`.
  - Expect `Localization report: 51/51 demo steps`.
  - Keep exit code `0`.
- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour`
  - Rename to show Spanish package completeness now passes.
  - Change expected exit code from `1` to `0`.
  - Remove the `Localization coverage incomplete for es.` expectation.
  - Expect `51/51`, with all four flows complete.
- `tests/unit/test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language`
  - Keep exit code `1`.
  - Change localization assertion to `[OK] localization: required es localization complete`.
  - Expect `51/51 demo steps`, `12/12 Q&A questions`, and `12/12 Q&A answers`.
  - Keep `[FAIL] runtime language support`, `package-only`, and `does not support --language es`.
- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language`
  - Keep runtime-language failure assertions unchanged.
  - Change localization check to status `OK`, detail `required es localization complete`, and `51/51 demo steps`.

Recommended new or expanded material-package assertions:

- Load `meeting-control-map-demo` and assert every step has nonblank `localized_text["es"]`.
- Assert all 22 expected step IDs are covered:
  - `control-map-overview`
  - `control-map-meeting-info`
  - `control-map-network`
  - `control-map-views`
  - `control-map-report`
  - `control-map-add-coworkers`
  - `control-map-participants`
  - `control-map-chat`
  - `control-map-microphone`
  - `control-map-audio-menu`
  - `control-map-camera`
  - `control-map-camera-menu`
  - `control-map-share`
  - `control-map-reactions`
  - `control-map-raise-hand`
  - `control-map-more`
  - `control-map-recording`
  - `control-map-notes`
  - `control-map-background`
  - `control-map-settings`
  - `control-map-leave`
  - `control-map-summary`
- Assert safety-sensitive Spanish text preserves the existing boundaries:
  - Meeting info does not read private values.
  - Report issue does not diagnose without observed values.
  - Invite/Add coworkers avoids private invite data.
  - Participants and Chat avoid reading names or message content.
  - Share does not press final `Share`.
  - Reactions and Raise hand are visible meeting signals.
  - Recording, Notes, Settings, Background, and Leave remain confirmation-bound or explain-only.

Green verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_meeting_controls_tour tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_meeting_controls_tour_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
git status --short
```

Expected green behavior:

- Spanish localization report exits `0` and reports `51/51`, `meeting-control-map-demo: 22/22`, Q&A `12/12`, and aliases `1/27 (3 aliases)`.
- Spanish `--require-complete` localization report exits `0` because package-local Spanish coverage is complete.
- Spanish doctor command exits `1` only because runtime language support for `es` still fails.
- Spanish demo dry-run exits nonzero before runtime launch with `Unsupported presenter language: es`.
- Chinese and Japanese `--require-complete` reports still exit `0`.

## Safety notes

- Completing Spanish package localization is not Spanish runtime support. Do not add `es` to presenter runtime language validation, voice aliases, provider catalogs, controller language choices, profile routes, or `voices` output.
- Do not update README, runbooks, or durable knowledge to say Spanish is supported, runnable, voice-ready, live-ready, manually accepted, or available through `demo/controller --language es`.
- Do not add Spanish Q&A or aliases in this slice. Alias expansion affects routing and diagnostics and should be its own reviewed change.
- Do not change locators, cleanup, action timing, entrypoint policy, or live RingCentral acceptance evidence.
- Treat map-demo Spanish wording as safety-critical operator guidance, not just translation coverage.
- `.coverage` is already dirty in the worktree; do not stage, revert, or overwrite it unless a separate owner explicitly asks.
- If another agent changes `packages/ringcentral-video.yaml` or the focused tests concurrently, re-read the current sections and merge additively. Do not overwrite adjacent localized text.

## Exact handoff

You are the Cycle 123 implementation subagent for AiPresenter. Implement only the Spanish package-local `meeting-control-map-demo` narration completion. First update focused tests so Spanish package coverage is expected to move from `29/51` to `51/51`, `meeting-control-map-demo` from `0/22` to `22/22`, Spanish `--require-complete` localization-report from exit `1` to exit `0`, and Spanish doctor localization from incomplete to complete while runtime language support still fails for `es`. Confirm the focused tests fail for the expected count/content reasons before editing package YAML.

Then add `narration.localizedText.es` for exactly these 22 `meeting-control-map-demo` steps in `packages/ringcentral-video.yaml`: `control-map-overview`, `control-map-meeting-info`, `control-map-network`, `control-map-views`, `control-map-report`, `control-map-add-coworkers`, `control-map-participants`, `control-map-chat`, `control-map-microphone`, `control-map-audio-menu`, `control-map-camera`, `control-map-camera-menu`, `control-map-share`, `control-map-reactions`, `control-map-raise-hand`, `control-map-more`, `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`.

Preserve all existing English, Chinese, Japanese, `placement`, `actionOffsetMs`, actions, locators, cleanup, Q&A, aliases, diagnostics semantics, runtime voice validation, provider routing, presenter skills, README, durable knowledge, and live-acceptance claims. Run the green verification commands above. Final implementation notes should state exact before/after Spanish counts, the runtime rejection result, and that `.coverage` was not staged.
