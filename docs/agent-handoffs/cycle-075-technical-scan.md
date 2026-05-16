# Cycle 075 Technical Scan: meeting-controls-tour / explain-notes JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-notes`
- Entrypoint: `ringcentral.video.more.notes`
- Operation: `open`

This is a narrow localization slice. Do not edit runtime behavior, locators, aliases, Q&A, diagnostics implementation, CLI implementation, flow order, or adjacent narration. Preserve the existing `open` semantics and side-panel cleanup expectations: this step opens the Notes and Transcript panel for explanation only, then leaves starting notes, recording, reading content, or changing meeting state under explicit user control.

Current repository state already has `explain-recording` localized and expects the next missing Japanese controls-tour step to be `explain-notes`:

```text
- meeting-controls-tour: 18/22 narration localized
  missing: explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 25/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

## Exact Source Step

From `packages/ringcentral-video.yaml`, `meeting-controls-tour` currently has English and Chinese narration only for `explain-notes`:

```yaml
  - id: explain-notes
    title: Notes and transcript
    action:
      entrypointId: ringcentral.video.more.notes
      operation: open
    narration:
      text: Notes opens the Notes and Transcript panel. It can start meeting notes and can also record the meeting,
        so those actions stay under user control.
      localizedText:
        zh: Notes 会打开 Notes and Transcript 面板。这里可以启动会议笔记，也可能涉及录制相关操作，所以这些动作继续由用户控制。
      placement: during
      actionOffsetMs: 400
```

Related entrypoint details:

```yaml
- id: ringcentral.video.more.notes
  title: Notes and transcript
  area: Meeting toolbar
  purpose: Open the Notes and Transcript side panel.
  questionAliases:
    zh:
    - 笔记
    - 转录
    - 会议笔记
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '3'
      controlType: button
  - action: clickWindowControl
    target: onconf.controls.NOTES
    match:
      alternateTargets: Notes
      controlType: menuitem
      cleanup: sidePanel
  presenterNotes:
  - In the current observed build, Notes is nested under the More menu.
  - The clickable menu item is exposed to UI Automation as onconf.controls.NOTES, while Notes is visible text.
  - Older layouts may expose Notes directly on the toolbar; prefer the More menu route when a direct Notes button is absent.
  - Observed panel offers Start notes and Also record this meeting.
  - Starting notes or recording changes meeting state, so the default tour only explains the panel.
  - Close the panel before continuing.
```

Related explainer wording in the package:

```yaml
  notes:
    shortScript: Notes opens the Notes and Transcript panel, but starting notes or recording changes meeting state.
    details:
    - Use this to show where meeting notes live.
    - Do not start notes or enable recording unless the user asks.
    relatedEntrypointIds:
    - ringcentral.video.more.notes
```

Relevant knowledge notes:

- `docs/knowledge/ringcentral-video/locator-matrix.md` lists `ringcentral.video.more.notes` as `UIA More occurrence 3 -> onconf.controls.NOTES, alternate Notes`, cleanup `sidePanel`, with low repo confidence and a reminder to resolve direct Notes versus More Notes variants separately.
- `docs/knowledge/ringcentral-video/privacy-matrix.md` treats Notes and transcript as meeting notes, transcription, and recording linkage. Starting notes/transcript, recording, or reading content requires user confirmation.

Important source semantics:

- The step operation is `open`, not `select`, `toggle`, `explain`, or a notes/recording start action.
- The route opens `More` via occurrence `3`, then opens `onconf.controls.NOTES` with alternate visible target `Notes`.
- The second open step has `cleanup: sidePanel`; preserve the side-panel close expectation.
- `placement: during` and `actionOffsetMs: 400` mean the narration is synchronized while the panel opens.
- The panel may expose `Start notes` and `Also record this meeting`; do not start either action in this localization slice.
- Do not add a direct-toolbar locator, locator fallback, route change, alias, Q&A item, runtime behavior, or diagnostics behavior in this slice.

## Recommended Japanese Text

```yaml
        ja: Notes は Notes and Transcript パネルを開きます。ここには Start notes と Also record this meeting があり、会議メモの開始や会議の録画につながるため、ユーザーが明確に求めるまで操作しません。ツアーではパネルの場所と役割だけを説明し、説明後はパネルを閉じます。
```

Rationale:

- Preserves `Notes`, `Notes and Transcript`, `Start notes`, and `Also record this meeting` as source UI labels.
- Mirrors the English source: the panel can start meeting notes and can also record the meeting.
- Reinforces open-only behavior: the tour opens the panel to explain where notes live, but does not start notes or recording.
- Keeps notes, transcript, and recording actions under explicit user control.
- Preserves the existing side-panel cleanup expectation.
- Avoids runtime, locator, alias, Q&A, operation, or diagnostics changes.

## Expected Count Changes

After adding only the Japanese narration for `explain-notes`:

- Japanese demo narration: `25/51` -> `26/51`
- `meeting-controls-tour.localized_steps`: `18/22` -> `19/22`
- First missing `meeting-controls-tour` step: `explain-notes` -> `explain-background-settings`
- Remaining missing `meeting-controls-tour` steps: `explain-background-settings`, `explain-settings`, `explain-leave`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not use this slice to localize control-map narration.

## TDD Test Updates

Recommended red-first test work:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `25` -> `26`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `18` -> `19`
  - Add `test_meeting_controls_tour_has_japanese_notes_narration`, adjacent to `test_meeting_controls_tour_has_japanese_recording_narration`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests:
    - `Localization report: 25/51 demo steps` -> `26/51`
    - `- meeting-controls-tour: 18/22 narration localized` -> `19/22`
    - `missing: explain-notes` -> `missing: explain-background-settings`
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `25/51 demo steps` -> `26/51 demo steps`

Focused material-package test assertions should cover:

- `step.id == "explain-notes"` found from `meeting-controls-tour`
- `step.action.entrypoint_id == "ringcentral.video.more.notes"`
- `step.action.operation == "open"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 400`
- `package.entrypoint_by_id("ringcentral.video.more.notes")` still has the two-step route: `More` occurrence `3`, then `onconf.controls.NOTES` with alternate `Notes` and `cleanup: sidePanel`
- Japanese text exists and `has_cjk(ja_text)` is true
- Includes `Notes`, `Notes and Transcript`, `Start notes`, `Also record this meeting`, `会議メモ`, `録画`, `ユーザー`, `明確に求める`, `操作しません`, `場所`, `役割`, and `閉じます`
- Does not include action wording that would imply execution, such as `開始します`, `録画します`, `クリック`, `押します`, `選択します`, `Start notes を押します`, `Also record this meeting を選択します`, or `録画を開始します`
- Does not add or require `questionAliases.ja`, direct Notes locators, route changes, cleanup changes, runtime routing, Q&A changes, or diagnostics changes

Focused verification command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_notes_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

## Expected CLI Output

After implementation, `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` should include:

```text
Package: ringcentral-video
Package version: 1
Language: ja

Demo flows:
- vbg-blur-demo: 4/4 narration localized
- meeting-basics-demo: 3/3 narration localized
- meeting-controls-tour: 19/22 narration localized
  missing: explain-background-settings, explain-settings, explain-leave
- meeting-control-map-demo: 0/22 narration localized
  missing: control-map-overview, control-map-meeting-info, control-map-network, control-map-views, control-map-report, control-map-add-coworkers, control-map-participants, control-map-chat, control-map-microphone, control-map-audio-menu, control-map-camera, control-map-camera-menu, control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary

Q&A:
- localized questions: 12/12
- localized answers: 12/12

Entrypoint aliases:
- questionAliases.ja present on 3/27 entrypoints (9 aliases)

Localization report: 26/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` should still exit `1` and append:

```text
Localization coverage incomplete for ja.
```

The focused diagnostics detail should move to:

```text
[FAIL] localization: required ja localization incomplete: 26/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
```

Note: running `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization` in the current profile can also fail the voice check because `ringcentral-video-bind-speaker` uses `windows-sapi-en`; that is separate from the localization-count assertion.

## Guardrails

- Edit only the `localizedText.ja` entry for `meeting-controls-tour` -> `explain-notes` during implementation.
- Preserve `operation: open`, `placement: during`, and `actionOffsetMs: 400`.
- Preserve `ringcentral.video.more.notes` entrypoint details, including `More` occurrence `3`, `onconf.controls.NOTES`, alternate `Notes`, and `cleanup: sidePanel`.
- Preserve locators, entrypoint IDs, flow order, aliases, Q&A, runtime behavior, CLI formatting, diagnostics logic, and More menu behavior.
- Do not add `questionAliases.ja` for Notes in this slice.
- Do not localize `explain-background-settings` or any later controls-tour step in this slice.
- Do not change `control-map-notes` or any `meeting-control-map-demo` narration.
- Do not add direct Notes route handling, locator fallback, live state detection, confirmed-action workflow, acceptance evidence, manual-control changes, or Notes aliases.
- Do not click `Start notes`, click `Also record this meeting`, start notes, start recording, read notes/transcript content, inspect recording state, or imply that notes/recording actions are safe unattended tour actions.
