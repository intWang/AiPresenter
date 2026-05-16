# Cycle 073 Technical Scan: meeting-controls-tour / explain-more JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-more`
- Entrypoint: `ringcentral.video.toolbar.more`
- Operation: `open`

This is a narrow localization slice. Do not edit runtime behavior, locators, aliases, Q&A, diagnostics implementation, CLI implementation, flow order, or adjacent narration. Preserve the existing `open` semantics and cleanup expectations.

Current repository state already has `explain-raise-hand` localized and expects the next missing Japanese controls-tour step to be `explain-more`:

```text
- meeting-controls-tour: 16/22 narration localized
  missing: explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 23/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

## Exact Source Step

From `packages/ringcentral-video.yaml`, `meeting-controls-tour` currently has English and Chinese narration only for `explain-more`:

```yaml
  - id: explain-more
    title: More actions
    action:
      entrypointId: ringcentral.video.toolbar.more
      operation: open
    narration:
      text: Finally, More is the expansion menu for deeper meeting tools. In this build, Notes is already on the
        toolbar, while More keeps Start recording, Background, and Settings.
      localizedText:
        zh: 最后是 More，它是更深层会议工具的扩展菜单。当前版本里 Notes 已在工具栏上，More 主要保留 Start recording、Background 和 Settings。
      placement: during
      actionOffsetMs: 350
```

Related entrypoint details:

```yaml
- id: ringcentral.video.toolbar.more
  title: More actions
  area: Meeting toolbar
  purpose: Open additional meeting actions.
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '3'
      controlType: button
      cleanup: escape
  presenterNotes:
  - This is the expansion point for less frequent meeting tools.
```

Related source-index wording:

```yaml
  moreMenu:
    shortScript: More is the overflow hub for secondary meeting actions such as recording, notes, background,
      settings, and leaving.
    details:
    - Open it as a navigation step, then choose the specific action intentionally.
    - Treat destructive or state-changing actions inside More with confirmation.
    relatedEntrypointIds:
    - ringcentral.video.toolbar.more
```

Important source semantics:

- The step operation is `open`, not `select`, `toggle`, `explain`, or a recording/settings action.
- The route clicks the third `More` control on the meeting toolbar and uses `cleanup: escape`.
- `More` is an overflow/expansion menu for deeper or less frequent meeting tools.
- In this build, the step text says `Notes` is already on the toolbar, while `More` keeps `Start recording`, `Background`, and `Settings`.
- Opening `More` must stay a navigation step only. Do not start recording, open Background, open Settings, change meeting state, or imply any deeper tool is selected automatically.
- Destructive or state-changing actions inside `More` still require explicit confirmation if implemented later.

## Recommended Japanese Text

```yaml
        ja: 最後に More を開くと、より深い会議ツールへ進むための拡張メニューを確認できます。このビルドでは Notes はすでにツールバー上にあり、More には Start recording、Background、Settings がまとまっています。ここではメニューの場所を説明するだけで、録画の開始や背景・設定の変更は、ユーザーが明確に求めるまで実行しません。
```

Rationale:

- Preserves `More`, `Notes`, `Start recording`, `Background`, and `Settings` as source UI labels.
- Matches the source meaning that `More` is an expansion menu for deeper meeting tools.
- Keeps the current-build distinction that `Notes` is already on the toolbar.
- Reinforces open-only behavior: the narration explains the menu location without selecting a child action.
- Avoids runtime, locator, alias, Q&A, or operation changes.
- Avoids implying that recording, background changes, or settings changes are safe passive tour actions.

## Expected Count Changes

After adding only the Japanese narration for `explain-more`:

- Japanese demo narration: `23/51` -> `24/51`
- `meeting-controls-tour.localized_steps`: `16/22` -> `17/22`
- First missing `meeting-controls-tour` step: `explain-more` -> `explain-recording`
- Remaining missing `meeting-controls-tour` steps: `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, `explain-leave`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not use this slice to localize control-map narration.

## TDD Test Updates

Recommended red-first test work:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `23` -> `24`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `16` -> `17`
  - Add `test_meeting_controls_tour_has_japanese_more_narration`, adjacent to `test_meeting_controls_tour_has_japanese_raise_hand_narration`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests:
    - `Localization report: 23/51 demo steps` -> `24/51`
    - `- meeting-controls-tour: 16/22 narration localized` -> `17/22`
    - `missing: explain-more` -> `missing: explain-recording`
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `23/51 demo steps` -> `24/51 demo steps`

Focused material-package test assertions should cover:

- `step.id == "explain-more"` found from `meeting-controls-tour`
- `step.action.entrypoint_id == "ringcentral.video.toolbar.more"`
- `step.action.operation == "open"`
- `step.narration.placement == "during"`
- `step.narration.action_offset_ms == 350`
- Japanese text exists and `has_cjk(ja_text)` is true
- Includes `More`, `拡張メニュー`, `より深い会議ツール`, `Notes`, `ツールバー`, `Start recording`, `Background`, `Settings`, `説明するだけ`, `録画`, `背景`, `設定`, `ユーザー`, and `明確に求める`
- Does not include child-action wording that would imply execution, such as `録画を開始します`, `Background を開きます`, `Settings を開きます`, `変更します`, `選択します`, or `Leave`
- Does not change operation/open semantics or route cleanup expectations.

Focused verification command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_more_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

## Expected CLI Output

After implementation, `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` should include:

```text
Demo flows:
- vbg-blur-demo: 4/4 narration localized
- meeting-basics-demo: 3/3 narration localized
- meeting-controls-tour: 17/22 narration localized
  missing: explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- meeting-control-map-demo: 0/22 narration localized
  missing: control-map-overview, control-map-meeting-info, control-map-network, control-map-views, control-map-report, control-map-add-coworkers, control-map-participants, control-map-chat, control-map-microphone, control-map-audio-menu, control-map-camera, control-map-camera-menu, control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary

Q&A:
- localized questions: 12/12
- localized answers: 12/12

Entrypoint aliases:
- questionAliases.ja present on 3/27 entrypoints (9 aliases)

Localization report: 24/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` should still exit `1` and append:

```text
Localization coverage incomplete for ja.
```

The focused diagnostics detail should move to:

```text
[FAIL] localization: required ja localization incomplete: 24/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
```

Note: running `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization` in the current profile can also fail the voice check because `ringcentral-video-bind-speaker` uses `windows-sapi-en`; that is separate from the localization-count assertion.

## Guardrails

- Edit only the `localizedText.ja` entry for `meeting-controls-tour` -> `explain-more` during implementation.
- Preserve `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- Preserve the route's `cleanup: escape`, `occurrence: '3'`, locators, entrypoint IDs, flow order, aliases, Q&A, runtime behavior, CLI formatting, and diagnostics logic.
- Do not localize `explain-recording` or any later controls-tour step in this slice.
- Do not change `control-map-more` or any `meeting-control-map-demo` narration.
- Do not add live state detection, confirmed-action workflow, acceptance evidence, manual-control changes, or More aliases.
- Do not select child menu items from `More`; this step opens the menu only.
