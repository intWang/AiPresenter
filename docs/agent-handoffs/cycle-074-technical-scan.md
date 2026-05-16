# Cycle 074 Technical Scan: meeting-controls-tour / explain-recording JA narration

Date: 2026-05-16

## Scope

Add Japanese `localizedText.ja` for:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-recording`
- Entrypoint: `ringcentral.video.more.recording`
- Operation: `explain`

This is a narrow localization slice. Do not edit runtime behavior, locators, aliases, Q&A, diagnostics implementation, CLI implementation, flow order, or adjacent narration. Preserve the existing `explain` semantics: this step describes the recording entry only and must not click, start, stop, or otherwise change recording state.

Current repository state already has `explain-more` localized and expects the next missing Japanese controls-tour step to be `explain-recording`:

```text
- meeting-controls-tour: 17/22 narration localized
  missing: explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
Localization report: 24/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

## Exact Source Step

From `packages/ringcentral-video.yaml`, `meeting-controls-tour` currently has English and Chinese narration only for `explain-recording`:

```yaml
  - id: explain-recording
    title: Recording
    action:
      entrypointId: ringcentral.video.more.recording
      operation: explain
    narration:
      text: Start recording changes the meeting state, so I only explain it in a tour. I would ask before starting
        or stopping recording.
      localizedText:
        zh: Start recording 会改变会议状态，所以在导览里只解释入口；开始或停止录制前都需要先询问并确认。
      placement: before
```

Related entrypoint details:

```yaml
- id: ringcentral.video.more.recording
  title: Start recording
  area: More menu
  purpose: Start recording the meeting.
  questionAliases:
    zh:
    - 录制
    - 录像
    - 记录会议
  openSteps: []
  presenterNotes:
  - Observed under More as Start recording.
  - Treat this as a state-changing action during a tour.
  - AiPresenter should explain this entry without clicking it unless the user explicitly asks to start recording.
```

Related source-index wording:

```yaml
  recording:
    shortScript: Start recording is available from More and should be treated as a confirmed action, not a passive
      tour step.
    details:
    - Explain it without clicking during normal demos.
    - Ask for confirmation before starting or stopping recording.
    relatedEntrypointIds:
    - ringcentral.video.more.recording
```

Important source semantics:

- The step operation is `explain`, not `open`, `select`, `toggle`, or a recording action.
- The entrypoint has `openSteps: []`; do not add a locator, route, click action, cleanup, or alias in this slice.
- `placement: before` means the narration is a pre-action explanation. There is no `actionOffsetMs` on this step.
- `Start recording` changes meeting state and can affect or notify meeting participants.
- The tour must describe the entry without clicking it unless the user explicitly asks to start recording.
- Starting or stopping recording remains a confirmed action boundary and must stay separate from this localization-only pass.

## Recommended Japanese Text

```yaml
        ja: Start recording は会議状態を変更する操作なので、ツアーでは入口を説明するだけにします。録画を開始または停止する前には、必ず先にユーザーへ確認します。
```

Rationale:

- Preserves `Start recording` as the source UI label.
- Directly mirrors the English source: recording changes meeting state, so the tour only explains it.
- Keeps start and stop recording behind prior user confirmation.
- Avoids implying AiPresenter clicks `Start recording`, starts recording, stops recording, validates permission, checks consent, or reads recording state.
- Avoids runtime, locator, alias, Q&A, operation, or diagnostics changes.

## Expected Count Changes

After adding only the Japanese narration for `explain-recording`:

- Japanese demo narration: `24/51` -> `25/51`
- `meeting-controls-tour.localized_steps`: `17/22` -> `18/22`
- First missing `meeting-controls-tour` step: `explain-recording` -> `explain-notes`
- Remaining missing `meeting-controls-tour` steps: `explain-notes`, `explain-background-settings`, `explain-settings`, `explain-leave`
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- Japanese aliases remain `3/27` entrypoints and `9` aliases.
- Japanese `--require-complete` remains intentionally incomplete and should still exit `1`.
- `meeting-control-map-demo` remains `0/22`; do not use this slice to localize control-map narration.

## TDD Test Updates

Recommended red-first test work:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
    - `report.demo_localized_steps`: `24` -> `25`
    - `report.flow_by_id["meeting-controls-tour"].localized_steps`: `17` -> `18`
  - Add `test_meeting_controls_tour_has_japanese_recording_narration`, adjacent to `test_meeting_controls_tour_has_japanese_more_narration`.
- `tests/unit/test_cli.py`
  - In both Japanese localization-report tests:
    - `Localization report: 24/51 demo steps` -> `25/51`
    - `- meeting-controls-tour: 17/22 narration localized` -> `18/22`
    - `missing: explain-recording` -> `missing: explain-notes`
- `tests/unit/test_diagnostics.py`
  - In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:
    - diagnostic detail `24/51 demo steps` -> `25/51 demo steps`

Focused material-package test assertions should cover:

- `step.id == "explain-recording"` found from `meeting-controls-tour`
- `step.action.entrypoint_id == "ringcentral.video.more.recording"`
- `step.action.operation == "explain"`
- `step.narration.placement == "before"`
- Japanese text exists and `has_cjk(ja_text)` is true
- Includes `Start recording`, `会議状態`, `変更`, `操作`, `ツアー`, `入口`, `説明するだけ`, `録画`, `開始`, `停止`, `先に`, `ユーザー`, and `確認`
- Does not include action wording that would imply execution, such as `録画を開始します`, `録画を停止します`, `クリック`, `押します`, `選択します`, `許可されています`, `同意済み`, or `録画中`
- Does not add or require `questionAliases.ja`, `openSteps`, locators, cleanup behavior, runtime routing, or operation changes.

Focused verification command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_recording_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
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
- meeting-controls-tour: 18/22 narration localized
  missing: explain-notes, explain-background-settings, explain-settings, explain-leave
- meeting-control-map-demo: 0/22 narration localized
  missing: control-map-overview, control-map-meeting-info, control-map-network, control-map-views, control-map-report, control-map-add-coworkers, control-map-participants, control-map-chat, control-map-microphone, control-map-audio-menu, control-map-camera, control-map-camera-menu, control-map-share, control-map-reactions, control-map-raise-hand, control-map-more, control-map-recording, control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary

Q&A:
- localized questions: 12/12
- localized answers: 12/12

Entrypoint aliases:
- questionAliases.ja present on 3/27 entrypoints (9 aliases)

Localization report: 25/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

`.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` should still exit `1` and append:

```text
Localization coverage incomplete for ja.
```

The focused diagnostics detail should move to:

```text
[FAIL] localization: required ja localization incomplete: 25/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers
```

Note: running `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization` in the current profile can also fail the voice check because `ringcentral-video-bind-speaker` uses `windows-sapi-en`; that is separate from the localization-count assertion.

## Guardrails

- Edit only the `localizedText.ja` entry for `meeting-controls-tour` -> `explain-recording` during implementation.
- Preserve `operation: explain`, `placement: before`, and the absence of `actionOffsetMs`.
- Preserve `ringcentral.video.more.recording` entrypoint details, including `openSteps: []`.
- Preserve locators, entrypoint IDs, flow order, aliases, Q&A, runtime behavior, CLI formatting, diagnostics logic, and More menu behavior.
- Do not add `questionAliases.ja` for recording in this slice.
- Do not localize `explain-notes` or any later controls-tour step in this slice.
- Do not change `control-map-recording` or any `meeting-control-map-demo` narration.
- Do not add live state detection, confirmed-action workflow, consent policy, host-permission checks, acceptance evidence, manual-control changes, or recording aliases.
- Do not click `Start recording`, start recording, stop recording, inspect recording state, or imply that recording is safe as an unattended passive tour action.
