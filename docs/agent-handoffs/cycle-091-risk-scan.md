# Cycle 091 Risk Scan: RingCentral Video Control Map Share JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-share`.

Current baseline after cycle 090 is Japanese localization `41/51`, with `meeting-control-map-demo` at `12/22`; the first missing step is `control-map-share`. This slice is high risk because the Share control opens a picker that may expose screen names, application window titles, document names, browser tab titles, presentation names, chat windows, private apps, thumbnails, and the `Share system audio` option. The final `Share` button can start broadcasting private visual content and local computer audio into a live meeting.

The safe target is a narrow open-and-explain localization. It is acceptable to open the picker for orientation, describe categories at a generic level, and close it after the explanation. The implementation must preserve:

- the English and Chinese narration text
- `action.entrypointId: ringcentral.video.toolbar.share`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 400`
- the step position after `control-map-camera-menu` and before `control-map-reactions`

The core safety rule is: opening the picker is allowed for a control-map tour, but clicking the final `Share` button is not allowed unless the user explicitly confirms what should be shown. Do not read candidate window names, screen labels, thumbnails, or visible content aloud unless the user has clearly asked for that specific help and the source is allowed.

## Allowed behavior

- Open the Share picker with the existing `ringcentral.video.toolbar.share` entrypoint to show where screen or application sharing begins.
- Explain generic choice categories, such as screen sharing, window sharing, selected content, and system audio, without naming actual candidates.
- Say that AiPresenter can explain the picker but will not press the final `Share` button until the user confirms the exact content to show.
- Say that `Share system audio` shares computer audio from the device into the meeting when enabled, and should be treated as a separate consent boundary.
- Close the picker after the explanation with Escape, consistent with the entrypoint cleanup behavior.
- Use conditional and user-controlled wording: the user chooses what to share, the presenter waits for confirmation, and the tour only points out the route.

## Forbidden behavior

- Do not click the final `Share` button during this control-map step.
- Do not start sharing an entire screen, application window, browser tab, file, presentation, whiteboard, or any other content.
- Do not select, preselect, recommend, prioritize, or switch between share candidates unless the user explicitly asks and confirms the intended target.
- Do not read aloud, translate, summarize, log, screenshot, or store candidate screen names, monitor labels, window titles, tab titles, document names, thumbnails, or visible window content.
- Do not infer the contents of a screen or window from thumbnails, titles, icons, app names, recent files, or surrounding UI.
- Do not toggle `Share system audio`, imply audio is already being shared, or promise audio capture quality. Enabling system audio can expose notifications, media, browser sound, private calls, or other local playback.
- Do not describe private content as safe, clean, approved, confidentially hidden, ready to share, or free of sensitive information.
- Do not broaden this slice into shared-screen interpretation, presentation coaching on the shared content, remote-control handoff, recording, notes, transcript, participant identity, chat content, security settings, host controls, or later control-map steps.
- Do not keep the picker open after the explanation, because it can block the next toolbar step and leave private candidates visible.

## Japanese wording guardrails

Safe Japanese copy should be explicit about consent and should avoid reading candidate names. Prefer wording like:

- `Share は、画面やアプリケーションウィンドウを共有するための選択画面を開きます。`
- `候補の種類は説明できますが、候補名や画面内容は明確な許可なしに読み上げません。`
- `表示する内容をユーザーが確認するまで、最終的な Share ボタンは押しません。`
- `Share system audio は、端末のシステム音声を会議に共有するための項目です。ユーザーが明示的に求めるまで有効にしません。`
- `説明したら選択画面を閉じます。`

Useful terms to keep:

- `Share`
- `画面`
- `アプリケーションウィンドウ`
- `選択画面`
- `候補`
- `Share system audio`
- `システム音声`
- `最終的な Share ボタン`
- `明確な許可`
- `ユーザーが確認するまで`
- `押しません`
- `読み上げません`
- `閉じます`

Avoid wording that sounds like AiPresenter selects, verifies, reads, or starts sharing content:

- `共有を開始します`
- `画面を共有します`
- `この画面を共有します`
- `ウィンドウを選択します`
- `候補を選びます`
- `おすすめの画面を選びます`
- `安全な画面を選びます`
- `内容を確認します`
- `内容を読み上げます`
- `候補名を読み上げます`
- `ウィンドウ名を読み上げます`
- `画面内容を説明します`
- `プライベートな内容はありません`
- `問題ありません`
- `自動で共有します`
- `Share system audio をオンにします`
- `システム音声を共有します` when phrased as an action AiPresenter performs
- `録画します`
- `記録します`
- `解析します`

System-audio wording should be cautious and non-actional. Safer phrasing is `Share system audio は、端末のシステム音声を会議に共有するための項目です`; unsafe phrasing is `システム音声を共有します`, `音声も一緒に流します`, or `音も自動で共有します`.

## Test guardrails

- Localization coverage should advance exactly one Japanese demo step: overall demo coverage from `41/51` to `42/51`, and `meeting-control-map-demo` from `12/22` to `13/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-share` to `control-map-reactions`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached only to `meeting-control-map-demo` -> `control-map-share`, not to `meeting-controls-tour` -> `explain-share`, Q&A, aliases, presenter notes, Reactions, Raise hand, More, Recording, Notes, Background, Settings, Leave, or Summary.
- Assert `control-map-share.action.entrypoint_id` remains `ringcentral.video.toolbar.share`, `operation` remains `open`, `placement` remains `during`, and `action_offset_ms` remains `400`.
- Assert the Share entrypoint still targets the toolbar `Share` button with `controlType: button` and `cleanup: escape`.
- Assert adjacent steps remain unchanged: `control-map-camera-menu` stays an `open` step on `ringcentral.video.toolbar.video-menu`, and `control-map-reactions` stays separate from sharing behavior.
- Assert the Japanese copy includes a final-share boundary, such as `最終的な Share ボタン` and `押しません`, plus a private-candidate boundary such as `読み上げません` or equivalent wording.
- Assert the Japanese copy does not contain action-claim phrases such as `共有を開始します`, `共有します`, `選択します`, `選びます`, `確認します`, `読み上げます`, `オンにします`, `自動で`, `安全な画面`, or `問題ありません` when they refer to share candidates, screen/window content, or system audio.
- If live validation is used, fail review if the final `Share` button is clicked, a share target is selected, `Share system audio` is toggled, screen/window candidate names enter logs or narration, thumbnails or content are captured as evidence, or the picker remains open after the step.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Reviewer checklist

- Confirm the diff is limited to the assigned Japanese narration and directly necessary test/source-index expectation updates in the implementation cycle; this risk-scan handoff itself should be the only file created by cycle 091 risk scan.
- Confirm no YAML, code, tests, or other documents were changed by this risk-scan subagent.
- Confirm opening the picker is treated as allowed orientation behavior, while final sharing remains blocked without explicit user confirmation.
- Confirm the proposed Japanese narration does not read, name, summarize, or infer candidate windows, screens, thumbnails, documents, tabs, apps, or visible private content.
- Confirm `Share system audio` is described as an option with consent risk, not as something AiPresenter enables or verifies.
- Confirm the copy does not promise that a chosen screen is safe, private, clean, approved, or free of sensitive information.
- Confirm the implementation keeps Escape cleanup so the picker closes before `control-map-reactions`.
- Confirm no screenshots, logs, fixtures, snapshots, or review artifacts include private screen/window candidates, monitor names, window titles, document names, browser tabs, thumbnails, meeting identifiers, account details, or local audio state.
