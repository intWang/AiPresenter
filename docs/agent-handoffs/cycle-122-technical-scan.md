# Cycle 122 Technical Scan: Spanish Meeting Controls Tour Wedge

Date: 2026-05-16
Scope: technical scan only. This handoff is the only file changed by this subagent. Do not stage or commit. Do not modify unrelated business code or revert other agents' work.

## Current state

- `packages/ringcentral-video.yaml` already has full Chinese and Japanese demo narration coverage for all 51 demo steps.
- Spanish package localization is currently a small seed wedge:
  - `vbg-blur-demo`: `4/4` Spanish narration localized.
  - `meeting-basics-demo`: `3/3` Spanish narration localized.
  - `meeting-controls-tour`: `0/22` Spanish narration localized.
  - `meeting-control-map-demo`: `0/22` Spanish narration localized.
  - Q&A Spanish coverage is complete: `12/12` localized questions and `12/12` localized answers.
  - Spanish entrypoint aliases are intentionally sparse: `questionAliases.es` appears on `1/27` entrypoints with `3` aliases.
- Verified command behavior:
  - `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es` exits `0` and reports `7/51` demo steps.
  - `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete` exits `1` and prints `Localization coverage incomplete for es.`
- `localization-report` is read-only. It counts demo narration via `step.narration.localized_text[language]`, counts Q&A localized questions/answers, and does not require alias completeness for `required_localization_complete`.
- `doctor --require-localization --localization-language es` should still fail until every Spanish demo step is localized, and runtime Spanish support should remain unsupported.
- Current dirty worktree note: `.coverage` is already modified and must remain out of scope.

## Implementation recommendation

Recommended slice: add Spanish `localizedText.es` for every step in `meeting-controls-tour` only.

Why this is the safest useful wedge:

- It matches the requested surface directly.
- It changes only package content plus tests.
- It completes one coherent user-facing tour rather than spreading partial Spanish across two 22-step flows.
- It preserves current runtime behavior: Spanish remains package-only and unsupported by presenter runtime voice routes.
- It updates report totals from `7/51` to `29/51`, which is a small, measurable increment and still keeps `--require-complete` failing.

Implementation details:

- Modify only `packages/ringcentral-video.yaml` and tests.
- For each `meeting-controls-tour` step, add a nonblank `es` entry under the existing `narration.localizedText` map.
- Do not change step IDs, action operations, entrypoint IDs, placement, `actionOffsetMs`, cleanup, safety policy, or flow ordering.
- Keep RingCentral UI labels in English where they are product labels, for example `Info`, `Network quality`, `Views`, `Report`, `Add coworkers`, `Invite`, `Participants`, `Chat`, `Mute`, `Share`, `React`, `Raise hand`, `More`, `Start recording`, `Notes`, `Background`, `Settings`, and `Leave`.
- Spanish narration must preserve the safety boundaries already present in English/Japanese/Chinese:
  - Meeting info: do not read meeting ID, links, dial-in, host, or encryption details unless explicitly asked.
  - Invite/Add coworkers: do not read names, email addresses, suggestions, or private invite links by default.
  - Participants: do not read participant names/roles or mute others without explicit instruction.
  - Chat: do not read or send chat content without explicit instruction.
  - Audio/video devices and settings: explain location, do not switch devices or durable settings by default.
  - Share: open/explain picker only; do not press final Share.
  - React/Raise hand: meeting-visible signals need user intent; if demonstrated, restore state.
  - Recording/Notes/Transcript: explain only unless user explicitly confirms.
  - Leave: explain only; never click without explicit confirmation.

Better alternate slice if implementation time is tight: add Spanish to only a tightly scoped sub-flow is not recommended because `localization-report` works at whole-step counts and the user asked specifically for a `meeting-controls-tour` wedge. A partial top-bar-only Spanish slice would create more future bookkeeping than value.

## Test plan

Red-first focused tests to add/update before YAML changes:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges tests\unit\test_cli.py::test_localization_report_outputs_spanish_short_demo_wedges tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_short_demo_wedges
```

Expected red after test expectation updates and before YAML implementation:

- Spanish demo count expected as `29/51` but actual remains `7/51`.
- `meeting-controls-tour` expected as `22/22` but actual remains `0/22`.

Required test updates:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges`
  - Change `report.demo_localized_steps` from `7` to `29`.
  - Change `meeting-controls-tour.localized_steps` from `0` to `22`.
  - Assert `meeting-controls-tour.total_steps == 22`.
  - Assert `meeting-controls-tour.missing_step_ids == ()`.
  - Keep `meeting-control-map-demo.localized_steps == 0`.
  - Keep Q&A and alias counts unchanged: `12/12`, `12/12`, `1/27`, `3`.
- `tests/unit/test_material_packages.py::test_ringcentral_spanish_qas_and_short_demo_wedges_are_localized`
  - Rename if desired, or expand expected Spanish demo step IDs to include all 22 `meeting-controls-tour` steps.
  - Keep product-label assertions for `Participants`, `Chat`, and privacy wording.
- `tests/unit/test_cli.py::test_localization_report_outputs_spanish_short_demo_wedges`
  - Expect `- meeting-controls-tour: 22/22 narration localized`.
  - Expect `- meeting-control-map-demo: 0/22 narration localized`.
  - Expect `Localization report: 29/51 demo steps`.
  - Keep exit code `0` without `--require-complete`.
- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_spanish_short_demo_wedges`
  - Expect the same `29/51` and `meeting-controls-tour: 22/22` report.
  - Keep exit code `1`, because `meeting-control-map-demo` remains `0/22`.
- `tests/unit/test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language`
  - Change expected localization detail from `7/51 demo steps` to `29/51 demo steps`.
  - Keep runtime language support failure assertions unchanged.

Recommended new safety/content test:

- Add one Spanish `meeting-controls-tour` test in `tests/unit/test_material_packages.py`, mirroring the Japanese safety tests but consolidated:
  - Load `meeting-controls-tour`.
  - Assert all 22 steps have nonblank `localized_text["es"]`.
  - Assert key product labels remain present in representative steps: `Meeting ID`, `Invite`, `Participants`, `Chat`, `Share`, `Start recording`, `Notes`, `Leave`.
  - Assert safety/privacy terms appear in Spanish, for example `privado`, `confirm`, `no leo`, `no envio`, or exact phrasing chosen by the implementer.
  - Assert final action-sensitive steps mention no automatic execution for `Share`, `Start recording`, and `Leave`.

Green verification:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_spanish_short_demo_wedges tests\unit\test_material_packages.py::test_ringcentral_spanish_qas_and_short_demo_wedges_are_localized tests\unit\test_cli.py::test_localization_report_outputs_spanish_short_demo_wedges tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_spanish_short_demo_wedges tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_cli.py
git status --short
```

Expected green behavior:

- Non-`--require-complete` Spanish report exits `0`.
- `--require-complete` Spanish report still exits `1`.
- Spanish report shows `meeting-controls-tour: 22/22`, `meeting-control-map-demo: 0/22`, and `Localization report: 29/51 demo steps`.
- Q&A and alias counts stay unchanged.

## Rollback/safety notes

- Rollback is simple: remove only `localizedText.es` entries added to `meeting-controls-tour` and revert the corresponding test expectation changes.
- Do not touch `.coverage`, profiles, runtime voice support, diagnostics code, CLI command shape, presenter skills, README, or knowledge docs for this wedge.
- Do not add Spanish runtime support or normalize `es` as a presenter voice language in this cycle.
- Do not use `--require-complete` success as an acceptance target; it must remain failing until `meeting-control-map-demo` also receives Spanish narration.
- Avoid changing existing Japanese/Chinese/English text. The YAML has many adjacent localized lines, so review the final diff carefully for accidental edits.
- If another agent edits `packages/ringcentral-video.yaml` concurrently, re-read the flow section and merge additively. Do not overwrite their localized text.

## Exact handoff for implementation

1. Update tests first:
   - Adjust Spanish expected report totals from `7/51` to `29/51`.
   - Change Spanish `meeting-controls-tour` expectations from `0/22` to `22/22`.
   - Leave `meeting-control-map-demo` at `0/22`.
   - Leave Spanish Q&A and alias expectations unchanged.
   - Add or expand a package test proving all 22 `meeting-controls-tour` Spanish narrations are present and preserve safety wording.
2. Run the focused red command and confirm failures are only the expected Spanish count/content gaps.
3. Edit `packages/ringcentral-video.yaml`:
   - Add `es:` under `narration.localizedText` for these 22 step IDs:
     - `meeting-overview`
     - `explain-meeting-info`
     - `explain-network-quality`
     - `explain-view-layout`
     - `explain-report-issue`
     - `explain-add-coworkers`
     - `explain-invite`
     - `explain-participants`
     - `explain-chat`
     - `explain-microphone`
     - `explain-audio-menu`
     - `explain-camera`
     - `explain-camera-menu`
     - `explain-share`
     - `explain-reactions`
     - `explain-raise-hand`
     - `explain-more`
     - `explain-recording`
     - `explain-notes`
     - `explain-background-settings`
     - `explain-settings`
     - `explain-leave`
4. Use natural Spanish, but keep product labels in English and preserve privacy/safety caveats. Favor concise presenter narration over literal translation.
5. Run the green verification commands from the test plan.
6. Write an implementation handoff noting:
   - Changed files.
   - Exact before/after Spanish localization totals.
   - Test command results.
   - Confirmation that `--require-complete` still fails for Spanish because `meeting-control-map-demo` remains untranslated.
