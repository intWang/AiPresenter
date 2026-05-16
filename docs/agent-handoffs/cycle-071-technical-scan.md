# Cycle 071 Technical Scan: meeting-controls-tour / explain-reactions JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-reactions`
- Entrypoint: `ringcentral.video.toolbar.react`
- Operation: `open`

No runtime, locator, alias, Q&A, diagnostics implementation, CLI implementation, or flow-order changes are needed. Keep this as a narrow narration slice. Do not localize `explain-raise-hand` or later controls in the same implementation pass.

Current repository state already expects the next missing Japanese controls-tour step to be `explain-reactions`:

```text
- meeting-controls-tour: 14/22 narration localized
  missing: explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 21/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

## Exact Source Step

From `packages/ringcentral-video.yaml`, `meeting-controls-tour` currently has English and Chinese narration only for `explain-reactions`:

```yaml
  - id: explain-reactions
    title: Reactions
    action:
      entrypointId: ringcentral.video.toolbar.react
      operation: open
    narration:
      text: For lightweight interaction, React opens quick feedback such as heart, thumbs up, celebration, clap,
        smile, and Be right back.
      localizedText:
        zh: React 适合轻量反馈，比如爱心、点赞、庆祝、鼓掌、微笑和 Be right back，不需要打断正在说话的人。
      placement: during
      actionOffsetMs: 350
```

Related entrypoint details:

```yaml
- id: ringcentral.video.toolbar.react
  title: Reactions
  area: Meeting toolbar
  purpose: Send meeting reactions without interrupting speech.
  openSteps:
  - action: clickWindowControl
    target: React
    match:
      controlType: button
      cleanup: escape
  presenterNotes:
  - Reactions are lightweight feedback signals.
  - This is a good fallback when the presenter wants to acknowledge without opening a panel.
  - Observed reactions include heart, thumbs up, celebration, clap, smile, and Be right back.
  - Close the reaction strip with Escape if no reaction should be sent.
```

Important source semantics:

- The step operation is `open`, not `toggle`.
- The route opens the React strip and uses `cleanup: escape`.
- The narration should explain visible meeting feedback without sending a reaction.
- Keep this separate from `ringcentral.video.toolbar.raise-hand`, whose next step uses `operation: toggle`.

## Recommended Japanese Text

```yaml
        ja: React は、発話を遮らずに気持ちや反応を示すためのリアクション欄を開きます。ハート、いいね、祝福、拍手、スマイル、Be right back などのクイックフィードバックがあります。リアクションは会議中に見えるシグナルなので、ユーザーの明確な指示なしに送信しません。説明だけの場合は送信せずに閉じます。
```

Rationale:

- Preserves `React`, lightweight feedback, and the observed reaction examples.
- States reactions are visible meeting signals, not private notes.
- Keeps the operation as explain/open only by saying no reaction is sent without clear user instruction.
- Mentions closing the reaction strip after explanation, matching `cleanup: escape`.
- Avoids raise-hand behavior, reaction selection, or any automatic visible signal.

## Expected Count Changes

After adding only the Japanese narration for `explain-reactions`:

- Japanese demo narration: `21/51` -> `22/51`
- `meeting-controls-tour.localized_steps`: `14/22` -> `15/22`
- First missing `meeting-controls-tour` step: `explain-reactions` -> `explain-raise-hand`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not use this slice to localize control-map narration.

## TDD Test Updates

Recommended red-first test work:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `21` -> `22`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `14` -> `15`
  - Add `test_meeting_controls_tour_has_japanese_reactions_narration`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests:
    - `Localization report: 21/51 demo steps` -> `22/51`
    - `- meeting-controls-tour: 14/22 narration localized` -> `15/22`
    - `missing: explain-reactions` -> `missing: explain-raise-hand`
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `21/51 demo steps` -> `22/51 demo steps`

Focused material-package test assertions should cover:

- `step.id == "explain-reactions"` found from `meeting-controls-tour`
- `step.action.entrypoint_id == "ringcentral.video.toolbar.react"`
- `step.action.operation == "open"`
- Japanese text exists and `has_cjk(ja_text)` is true
- Includes `React`, `リアクション`, `ハート`, `いいね`, `祝福`, `拍手`, `スマイル`, `Be right back`, `会議中に見える`, `ユーザー`, `明確な指示`, `送信しません`, and `閉じます`
- Does not include `Raise hand`, `手を上げ`, or language implying an automatic send such as `送信します`

Focused verification command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_reactions_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

## Expected CLI Output

After implementation, `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` should include:

```text
Demo flows:
- vbg-blur-demo: 4/4 narration localized
- meeting-basics-demo: 3/3 narration localized
- meeting-controls-tour: 15/22 narration localized
  missing: explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- meeting-control-map-demo: 0/22 narration localized
  missing: control-map-overview, control-map-meeting-info, control-map-network, control-map-views, control-map-report, control-map-add-coworkers, control-map-participants, control-map-chat, control-map-microphone, control-map-audio-menu, control-map-camera, control-map-camera-menu, control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary

Q&A:
- localized questions: 12/12
- localized answers: 12/12

Entrypoint aliases:
- questionAliases.ja present on 3/27 entrypoints (9 aliases)

Localization report: 22/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` should still exit `1` and append:

```text
Localization coverage incomplete for ja.
```

The focused diagnostics detail should move to:

```text
[FAIL] localization: required ja localization incomplete: 22/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
```

Note: running `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization` in the current profile can also fail the voice check because `ringcentral-video-bind-speaker` uses `windows-sapi-en`; that is separate from the localization-count assertion.

## Guardrails

- Edit only the `localizedText.ja` entry for `meeting-controls-tour` -> `explain-reactions` during implementation.
- Preserve `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- Do not change `openSteps`, locators, cleanup semantics, entrypoint IDs, aliases, Q&A, runtime behavior, CLI formatting, or diagnostics logic.
- Do not send a reaction, select a reaction, raise a hand, or modify `explain-raise-hand` in this slice.
