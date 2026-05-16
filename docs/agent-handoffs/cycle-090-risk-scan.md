# Cycle 090 Risk Scan: RingCentral Video Control Map Camera Menu JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-camera-menu`.

Current baseline after cycle 089 is Japanese localization `40/51`, with `meeting-control-map-demo` at `11/22`; the first missing step is `control-map-camera-menu`. This slice is more sensitive than the prior Camera point step because the existing action intentionally opens `ringcentral.video.toolbar.video-menu`, whose menu can expose camera device selection and `More video settings`. The related settings route can lead to camera choice, quality, gallery, background, blur, virtual background, video background, upload, mirror, and other appearance controls.

The safe target is a narrow open-and-explain localization. It is acceptable for the tour step to open the camera menu and explain that the menu is the route to camera choice and video settings. It must not select a camera, switch devices, read or narrate device names, enter `More video settings`, change background or appearance, or imply that AiPresenter has verified camera output. The implementation should preserve:

- the English and Chinese narration text
- `action.entrypointId: ringcentral.video.toolbar.video-menu`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 350`
- the step position after `control-map-camera` and before `control-map-sharing`

## Allowed behavior

- Open the camera menu using the existing `ringcentral.video.toolbar.video-menu` entrypoint and then explain the visible menu at a high level.
- Say that this menu is where camera selection and `More video settings` can be found.
- Mention background only as a downstream settings area, for example that video settings may include background or appearance-related options.
- Use generic language such as camera choice, video settings, appearance setup, and background options without naming actual devices, current selections, personal backgrounds, or setting values.
- Close the menu with Escape after explaining the entry point, consistent with the existing `cleanup: escape` presenter note.
- Treat `More video settings` as a referenced shortcut only; opening it belongs to a separate explicit settings slice or user request.

## Forbidden behavior

- Do not select, switch, enable, disable, prefer, test, or troubleshoot any camera device during this control-map step.
- Do not read, log, screenshot, translate, summarize, or narrate actual camera device names or selected-device labels.
- Do not click `More video settings`, open Settings, open the Video panel, or inspect deeper camera, quality, gallery, mirror, HD, or appearance controls.
- Do not open Background settings, select Blur, choose virtual backgrounds, choose video backgrounds, upload backgrounds, mirror video, or change any local appearance setting.
- Do not imply that AiPresenter will fix camera quality, optimize the picture, apply a safer background, hide the room, or make the user look better.
- Do not claim the camera is on, off, ready, wrong, blocked, private, or visible based only on the menu being open.
- Do not capture or store screenshots, local video previews, participant tiles, device lists, meeting identifiers, account details, custom backgrounds, or settings values as evidence for this slice.
- Do not broaden this slice into Q&A aliases, `ringcentral.video.settings.video`, `ringcentral.video.settings.background`, the Background control-map step, the general Settings step, recording, sharing, reactions, notes, security, host controls, or leave behavior.

## Japanese wording guardrails

Safe Japanese copy should sound explanatory and conditional. Prefer wording like:

- `カメラメニューは、カメラ選択と More video settings への入口です。`
- `ここでは場所と選択肢の種類を説明するだけです。`
- `背景や表示に関する設定へ進める場合がありますが、ユーザーが明示的に求めるまで設定は変更しません。`

Useful terms to keep:

- `カメラメニュー`
- `カメラ選択`
- `More video settings`
- `ビデオ設定`
- `背景`
- `表示`
- `入口`
- `ユーザーが明示的に求めるまで`
- `変更しません`

Avoid wording that sounds like AiPresenter performs a change or validates private state:

- `カメラを切り替えます`
- `カメラを選択します`
- `デバイスを変更します`
- `選択中のカメラを確認します`
- `More video settings を開きます`
- `ビデオ設定を開きます`
- `背景を変更します`
- `ぼかしを適用します`
- `仮想背景を選択します`
- `映像を調整します`
- `画質を改善します`
- `カメラを確認します`
- `プレビューを確認します`
- `安全な背景にします`
- `自動で`
- `必ず`

Background can be mentioned, but only as a cautious downstream category. Safer phrasing is `背景や表示に関する設定へ進める場合があります`; unsafe phrasing is `背景を変更します`, `背景を設定します`, or `部屋を隠します`.

## Test guardrails

- Localization coverage should advance exactly one Japanese demo step: overall demo coverage from `40/51` to `41/51`, and `meeting-control-map-demo` from `11/22` to `12/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-camera-menu` to `control-map-sharing`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached only to `meeting-control-map-demo` -> `control-map-camera-menu`, not to `meeting-controls-tour` -> `explain-camera-menu`, Q&A, aliases, presenter notes, Video settings, Background, Settings, or later control-map steps.
- Assert `control-map-camera-menu.action.entrypoint_id` remains `ringcentral.video.toolbar.video-menu`, `operation` remains `open`, `placement` remains `during`, and `action_offset_ms` remains `350`.
- Assert the camera-menu entrypoint still targets `More` with `occurrence: '2'`, `controlType: button`, and `cleanup: escape`; this must remain distinct from the audio menu `occurrence: '1'` and overflow More `occurrence: '3'`.
- Assert adjacent steps remain unchanged: `control-map-camera` stays a `point` step on `ringcentral.video.toolbar.video`, and `control-map-sharing` stays separate from camera/menu behavior.
- Assert the Japanese copy includes camera-menu/video-settings concepts such as `カメラ`, `メニュー`, `More video settings` or `ビデオ設定`, and an explicit no-change boundary.
- Assert the Japanese copy does not contain action-claim phrases such as `切り替えます`, `選択します`, `変更します`, `開きます`, `適用します`, `改善します`, `確認します` when they refer to devices, settings, previews, background, or camera output.
- If live validation is used, fail review if a camera device is selected, `More video settings` opens, Settings opens, background or appearance changes, local video state changes, device names or selected labels enter evidence, or the camera menu remains open after the step.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Reviewer checklist

- Confirm the diff is limited to the assigned Japanese narration and directly necessary test/source-index expectation updates in the implementation cycle; this risk-scan handoff itself should be the only file created by cycle 090 risk scan.
- Confirm no YAML, code, tests, or other documents were changed by this risk-scan subagent.
- Confirm the proposed Japanese narration explains the menu as an entry point, not as an instruction to select a device or open deeper settings.
- Confirm background is either omitted or mentioned only as a downstream option/category, with an explicit no-change boundary.
- Confirm there is no wording that promises privacy protection, camera readiness, quality improvement, device correctness, preview inspection, or automatic remediation.
- Confirm no actual camera names, background assets, screenshots, participant information, meeting identifiers, account details, or settings values are introduced into tests, docs, or review artifacts.
- Confirm `More video settings` remains referenced but not entered during this control-map menu slice.
- Confirm cleanup returns the UI to a neutral toolbar state before the next `control-map-sharing` step.
