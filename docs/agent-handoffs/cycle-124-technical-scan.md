# Cycle 124 Technical Scan: Spanish Meeting Control Map Completion

Date: 2026-05-16

Scope: technical handoff only. This subagent must not modify business code, package YAML, tests, runtime language support, README, durable knowledge, generated artifacts, or existing handoff files. The only intended file change is this document.

## Current state

- Spanish package content is still package-local and runtime-unsupported.
- Current CLI package coverage, verified read-only in this scan:
  - `localization-report --package ringcentral-video --language es` exits `0`.
  - Spanish demo narration is `29/51`.
  - `vbg-blur-demo` is `4/4`.
  - `meeting-basics-demo` is `3/3`.
  - `meeting-controls-tour` is `22/22`.
  - `meeting-control-map-demo` is `0/22`.
  - Spanish Q&A is `12/12` localized questions and `12/12` localized answers.
  - `questionAliases.es` is present on `1/27` entrypoints with `3` aliases.
- Current strict package check:
  - `localization-report --package ringcentral-video --language es --require-complete` exits `1`.
  - It prints `Localization coverage incomplete for es.`
- Current doctor check:
  - `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` exits `1`.
  - It currently has two failures: incomplete Spanish localization and runtime language support.
  - Expected after the 22-step package completion: localization becomes `[OK]`, but `runtime language support` remains `[FAIL]`.
- Cycle 123 added the language lifecycle guardrail:
  - `docs/knowledge/language-lifecycle.md` states package completeness is separate from runtime presenter support.
  - `tests/unit/test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete` covers the future complete-package but unsupported-runtime shape with a synthetic package.
- Workspace concurrency note:
  - `tests/unit/test_material_packages.py` is already modified in the worktree by another agent or prior step. The diff renames `test_ringcentral_localization_status_reports_spanish_meeting_controls_tour` to `test_ringcentral_localization_status_reports_complete_spanish_package` and changes the real package status expectations from `29/51` and map `0/22` to `51/51` and map `22/22`.
  - `packages/ringcentral-video.yaml` still lacks `localizedText.es` for the 22 `meeting-control-map-demo` steps.
  - `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py` still expect the current incomplete real package state.
  - `.coverage` is modified generated drift. Do not stage, revert, or overwrite it in this localization slice.

## Implementation recommendation

Complete only Spanish package-local narration for the existing 22 `meeting-control-map-demo` steps in `packages/ringcentral-video.yaml`.

Expected package-only delta:

- Spanish demo narration: `29/51` -> `51/51`.
- `meeting-control-map-demo`: `0/22` -> `22/22`.
- `meeting-controls-tour`: remains `22/22`.
- `vbg-blur-demo`: remains `4/4`.
- `meeting-basics-demo`: remains `3/3`.
- Spanish Q&A: remains `12/12` questions and `12/12` answers.
- Spanish aliases: remains `1/27` entrypoints and `3` aliases.
- Spanish runtime: remains unsupported.

Add `narration.localizedText.es` for exactly these map-demo step IDs:

`control-map-overview`, `control-map-meeting-info`, `control-map-network`, `control-map-views`, `control-map-report`, `control-map-add-coworkers`, `control-map-participants`, `control-map-chat`, `control-map-microphone`, `control-map-audio-menu`, `control-map-camera`, `control-map-camera-menu`, `control-map-share`, `control-map-reactions`, `control-map-raise-hand`, `control-map-more`, `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`.

Keep product UI labels literal where the user needs to find controls, such as `Meeting information`, `Network quality`, `Views`, `Report`, `Add coworkers`, `Participants`, `Chat`, `Mute`, `Audio options`, `Start video`, `Share`, `Reactions`, `Raise hand`, `More`, `Start recording`, `Notes`, `Background`, `Settings`, and `Leave`.

Do not touch runtime language validation, voice aliases, provider catalogs, profile routes, controller language choices, `voices` output, Q&A, aliases, locators, action operations, cleanup behavior, acceptance claims, README, or durable knowledge.

## Test plan

TDD red phase:

1. Preserve the already-started material package expectation update in `tests/unit/test_material_packages.py`; re-read it first because another agent may continue editing it.
2. Update CLI and diagnostics tests before YAML implementation so the real package is expected to become Spanish-complete while runtime Spanish still fails:
   - `tests/unit/test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour`
   - `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour`
   - `tests/unit/test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language`
   - `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language`
3. Run focused tests and confirm they fail for expected count/content reasons before editing YAML.

Recommended test expectation changes:

- Material package status: real Spanish package reports `51/51`, map demo `22/22`, `required_localization_complete is True`, Q&A and alias counts unchanged.
- Material package content: extend the Spanish expected demo-step list with all 22 `meeting-control-map-demo:*` IDs and add representative wording checks for UI-label preservation and safety boundaries.
- CLI plain report: expect `- meeting-control-map-demo: 22/22 narration localized` and `Localization report: 51/51 demo steps`.
- CLI `--require-complete`: rename the test to a passing Spanish completeness case, expect exit `0`, and remove the incomplete-coverage assertion.
- Doctor real package: keep exit `1`, expect `[OK] localization: required es localization complete`, expect `51/51 demo steps`, and keep `[FAIL] runtime language support`.
- Diagnostics real package: change only the localization check from incomplete `FAIL` to complete `OK`; keep package-only runtime language failure assertions.
- Keep `tests/unit/test_cli.py::test_demo_rejects_unknown_language_before_runtime` unchanged so `demo --language es --dry-run` still rejects before runtime launch.

Focused red/green command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_meeting_controls_tour_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_meeting_controls_tour tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_meeting_controls_tour tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_diagnostics.py::test_diagnostics_require_localization_flags_package_only_runtime_language tests\unit\test_diagnostics.py::test_diagnostics_runtime_language_support_stays_separate_after_package_localization_complete
```

Green verification after YAML implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
git status --short
```

Expected green outcomes:

- Spanish non-strict report exits `0` with `51/51`, map demo `22/22`, Q&A `12/12`, and aliases `1/27 (3 aliases)`.
- Spanish `--require-complete` report exits `0`. This is a package pass only.
- Spanish doctor exits `1` because the separate runtime language support check still fails for `es`.
- Spanish demo dry-run exits nonzero with `Unsupported presenter language: es`.
- Chinese and Japanese strict localization reports still pass.

## Safety notes

- `--require-complete` becoming green means package localization is complete; it does not mean AiPresenter can run, speak, or accept Spanish in demo/controller runtime.
- Doctor must be allowed to show `[OK] localization` and `[FAIL] runtime language support` in the same run.
- Spanish narration must not read meeting IDs, meeting links, dial-in numbers, invite data, participant names, chat contents, notes, transcript contents, recording metadata, or device names unless a separate explicit user request and safety path owns that behavior.
- State-changing or sensitive controls must stay bounded: `Share`, `Recording`, `Raise hand`, `Reactions`, `Background`, `Settings`, `Notes`, microphone/camera toggles, invite flows, and `Leave` must be explain-only or confirmation-bound as their existing actions require.
- Do not add Spanish aliases in this cycle. Alias expansion changes matching and diagnostics risk.
- Do not claim Spanish is supported, voice-ready, live-ready, manually accepted, or available through `demo/controller --language es`.
- Because other agents are active, re-read current diffs before editing and merge additively. Do not overwrite the existing uncommitted material-package test change.

## Exact handoff

You are the Spanish `meeting-control-map-demo` completion implementation subagent for AiPresenter. Work TDD-first and package-local only.

First, re-read `git diff -- tests/unit/test_material_packages.py` because another agent has already started the red phase by changing the real Spanish status expectation to `51/51` and map demo to `22/22`. Update the remaining focused tests so the real RingCentral package is expected to have complete Spanish package localization while Spanish runtime support remains rejected. Confirm the focused test command fails for expected Spanish count/content reasons before editing `packages/ringcentral-video.yaml`.

Then add `localizedText.es` to exactly the 22 existing `meeting-control-map-demo` narration blocks. Preserve all existing English, Chinese, Japanese, step IDs, entrypoint IDs, operations, placements, action offsets, locators, cleanup, Q&A, aliases, diagnostics semantics, runtime voice support, provider routing, controller language choices, docs, and acceptance evidence.

After implementation, Spanish `localization-report --require-complete` should pass as a package check, but `doctor --require-localization --localization-language es` should still fail only on `runtime language support`, and `demo --language es --dry-run` should still reject `es` before runtime launch. Keep `.coverage` out of staging and do not revert other agents' changes.
