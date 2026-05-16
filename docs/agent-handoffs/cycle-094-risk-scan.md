# Cycle 094 Risk Scan: RingCentral Video Control Map More JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-more`.

Current baseline after cycle 093 is Japanese localization `44/51`, with `meeting-control-map-demo` at `15/22`; the first missing step is `control-map-more`. This slice is safety-sensitive because `More` is an overflow hub for deeper or less frequent meeting controls. Opening the menu is low risk, but the menu exposes actions that can change meeting state, reveal or affect private context, open blocking dialogs, or exit the meeting.

The safe target is a narrow open-and-explain localization. It is acceptable to open the `More` menu to show where advanced controls live, describe the visible categories generically, and close the menu after the explanation. The implementation must preserve:

- `action.entrypointId: ringcentral.video.toolbar.more`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 350`
- the step position after `control-map-raise-hand` and before `control-map-recording`
- English and Chinese narration text

The core safety rule is: `More` can be opened for orientation, but secondary actions inside it must not be clicked during `control-map-more`. Recording, Notes, Background, Settings, and Leave each need their own safer boundary and must not be smuggled into this slice.

## Allowed behavior

- Open the `More` menu with the existing `ringcentral.video.toolbar.more` entrypoint to show the overflow hub.
- Explain that `More` gathers advanced, less frequent, or more cautious meeting tools.
- Mention secondary controls as locations or categories only: `Start recording`, `Notes`, `Background`, `Settings`, and possibly `Leave` if visible in the current layout.
- Say that recording and leaving are state-changing controls that require explicit user confirmation before execution.
- Say that Background and Settings may be opened in their own steps for explanation, but the `More` step itself should not change settings.
- Say that Notes may open a panel with meeting notes, transcript, and recording-adjacent controls, so the `More` step should not start notes, read notes, summarize transcripts, or start recording.
- Close the `More` menu after explaining it, so the next step does not inherit an active overflow surface.
- Keep `control-map-more` distinct from the later dedicated steps: `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`.

## Forbidden behavior

- Do not click `Start recording` from `control-map-more`.
- Do not click `Notes`, `Background`, `Settings`, or `Leave` from `control-map-more`.
- Do not start, stop, pause, resume, or promise recording.
- Do not open Notes and then start notes, start transcript, read note content, read transcript content, summarize meeting content, or click `Also record this meeting`.
- Do not change Background effects, select Blur, choose a virtual background, upload a background, toggle Mirror my video, or expose the user's room unnecessarily.
- Do not change Settings for audio, video, background, translation, join preferences, General, device selection, or meeting behavior.
- Do not click Leave, End meeting, End for all, or any confirmation related to leaving.
- Do not imply that `More` is harmless just because it is an overflow menu; it contains risky controls.
- Do not broaden this slice into the later recording, notes, background, settings, leave, summary, Q&A, alias, presenter-note, source-index, or test-content changes unless a separate implementation task explicitly assigns them.

## Japanese wording guardrails

Safe Japanese copy should use orientation language and avoid execution verbs for secondary actions. Prefer wording like:

- `最後に More を開くと、録画、Notes、Background、Settings など、より慎重に扱う会議ツールの入口を確認できます。`
- `ここではメニューの場所と分類だけを説明し、Start recording、Notes、Background、Settings、Leave はクリックしません。`
- `録画や退出のように会議状態を変える操作は、ユーザーが明確に確認した場合だけ扱います。`
- `Background や Settings は表示やプライバシーに関わるため、この More の説明では変更しません。`
- `Notes はメモ、文字起こし、録画に関係する可能性があるため、内容を読み上げたり開始したりせず、入口としてだけ説明します。`
- `説明後は More メニューを閉じて、次の操作に影響しない状態に戻します。`

Useful terms to keep:

- `More`
- `拡張メニュー`
- `入口`
- `場所`
- `分類`
- `より慎重に扱う`
- `低頻度`
- `会議状態を変える`
- `ユーザーが明確に確認した場合だけ`
- `クリックしません`
- `変更しません`
- `開始しません`
- `閉じます`

Avoid wording that sounds like AiPresenter executes the secondary action or makes a decision for the user:

- `Start recording を開始します`
- `録画します`
- `録画を始めます`
- `録画を止めます`
- `Notes を開始します`
- `メモを取ります`
- `文字起こしします`
- `内容を読み上げます`
- `要約します`
- `Background を変更します`
- `Blur にします`
- `背景を選びます`
- `アップロードします`
- `Settings を調整します`
- `設定を変更します`
- `翻訳をオンにします`
- `デバイスを切り替えます`
- `Leave をクリックします`
- `退出します`
- `会議を終了します`
- `自動で`
- `必要なら`
- `安全なので`
- `すぐに`

Preferred distinction among secondary actions:

- `Start recording は録画の入口であり、会議状態と同意に関わるため説明だけにします。`
- `Notes はメモと文字起こしの入口ですが、開始や内容の読み上げはしません。`
- `Background と Settings は開ける場所を示すだけで、見え方や設定は変更しません。`
- `Leave は退出の入口なので、ツアーではクリックしません。`

## Test guardrails

- Localization coverage should advance exactly one Japanese demo step: overall demo coverage from `44/51` to `45/51`, and `meeting-control-map-demo` from `15/22` to `16/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-more` to `control-map-recording`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached only to `meeting-control-map-demo` -> `control-map-more`, not to `meeting-controls-tour`, Q&A, aliases, presenter notes, Reactions, Raise hand, Recording, Notes, Background, Settings, Leave, Summary, or source-index content.
- Assert `control-map-more.action.entrypoint_id` remains `ringcentral.video.toolbar.more`, `operation` remains `open`, `placement` remains `during`, and `action_offset_ms` remains `350`.
- Assert adjacent steps remain unchanged: `control-map-raise-hand` stays the previous localized step, and `control-map-recording` remains the next unlocalized control-map step.
- Assert the Japanese copy includes `More`, an orientation term such as `入口` or `場所`, and a no-secondary-click boundary such as `クリックしません`.
- Assert the Japanese copy identifies risky or careful secondary actions without executing them, using safe nouns such as `録画`, `Notes`, `Background`, `Settings`, and `Leave`.
- Assert the Japanese copy does not contain execution phrases such as `録画します`, `録画を始めます`, `Notes を開始します`, `文字起こしします`, `Background を変更します`, `Settings を調整します`, `Leave をクリックします`, `退出します`, or `会議を終了します`.
- Assert live validation, if used, opens only the `More` menu for this step and does not click any menu item inside it.
- Fail review if recording starts, a notes/transcript panel starts capture, a background or settings value changes, a settings dialog remains blocking unintentionally, the user leaves the meeting, or screenshots/logs capture participant-identifying content beyond sanitized control labels.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Reviewer checklist

- Confirm this risk-scan subagent created only `docs/agent-handoffs/cycle-094-risk-scan.md`.
- Confirm no YAML, code, tests, or other documents were changed by this risk-scan subagent.
- Confirm the implementation slice adds only one Japanese narration block for `control-map-more`.
- Confirm opening the `More` menu is allowed for orientation, while clicking secondary actions from `More` is not allowed in this slice.
- Confirm `Start recording` is described as a recording entrypoint, not executed or promised.
- Confirm `Notes` is described as a notes/transcript entrypoint, without starting notes, recording, transcript, reading, or summarizing content.
- Confirm `Background` and `Settings` are described as locations, without changing visual, privacy, device, translation, join, or general settings.
- Confirm `Leave` is described as destructive or exit-related and is not clicked.
- Confirm tests lock both localization counts and the action boundary: `open` on `ringcentral.video.toolbar.more` with no secondary menu-item click.
- Confirm no screenshots, logs, fixtures, snapshots, or review artifacts include unnecessary participant names, meeting identifiers, account details, room imagery, note/transcript content, recording evidence, or live meeting context.
