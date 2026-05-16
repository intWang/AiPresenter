# Cycle 098 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-settings` -> `narration.localizedText.ja`.

The user need is a Japanese control-map explanation for `Settings` that helps presenters understand the full RingCentral Video configuration center without changing broad meeting preferences automatically. Japanese users should hear that Settings is where audio, video, background, translation, join preferences, and general meeting behavior are configured, while also understanding that AiPresenter only explains the route in this tour.

Current Japanese localization baseline after cycle 097:

- Overall Japanese demo narration: `48/51`.
- `meeting-control-map-demo`: `19/22`.
- First missing `meeting-control-map-demo` Japanese step: `control-map-settings`.
- Remaining missing control-map steps: `control-map-settings`, `control-map-leave`, `control-map-summary`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.

This cycle should let Japanese users understand that `Settings` is a broad configuration surface. The narration should be useful as a map, not as an instruction to alter devices, camera behavior, background effects, translation, join defaults, or general meeting preferences.

## Presenter behavior

The presenter should treat `control-map-settings` as a Settings-dialog explanation step on `ringcentral.video.more.settings`.

Required behavior in real meeting context:

- Preserve `entrypointId: ringcentral.video.more.settings`.
- Preserve `operation: open`.
- Preserve `placement: during`.
- Preserve `actionOffsetMs: 400`.
- Preserve the existing route: open `More`, select `Settings`, and keep `cleanup: settings`.
- Explain that `Settings` is the full configuration center for audio, video, background, translation, join preferences, and general meeting behavior.
- Mention that the Settings dialog may open to the current or last selected section, so the point of the step is the dialog and its configuration scope, not a guaranteed initial tab.
- Keep the dialog visible only long enough to explain the location and role.
- Close the Settings dialog after the explanation before continuing the control-map flow.
- Do not switch microphones, speakers, cameras, camera effects, background options, translation settings, caption/language settings, join preferences, or general meeting behavior.
- Do not test audio, test video, preview devices, change defaults, toggle persistent preferences, or infer whether current settings are correct.
- Do not inspect or describe device names, account details, organization policy, room imagery, background thumbnails, participant content, translation output, captions, meeting IDs, invite links, or any private meeting context.

Good semantics: "`Settings` is the central place for meeting configuration: audio, video, background, translation, join preferences, and general behavior. In this control map, AiPresenter explains where the configuration center is and what it is for. It does not change devices, camera/background appearance, translation, join defaults, or general settings unless the user explicitly asks and the visible setting plus likely effect are confirmed."

## Broad configuration-change boundaries

The Japanese narration should make Settings feel powerful but deliberately non-operational in this slice. It should communicate these separate boundaries:

- Device boundary: audio and video settings can change microphone, speaker, camera, test, and preview behavior, so the tour must not switch or test devices automatically.
- Appearance boundary: background and video settings can alter how the user appears to others, so this step must not change camera effects, blur, virtual backgrounds, mirror behavior, or video preferences.
- Language boundary: translation, captions, and language settings can affect meeting comprehension and may expose or transform meeting content, so AiPresenter must not enable, disable, or change language behavior from this general Settings pass.
- Preference boundary: join preferences and general settings may persist beyond the current moment or affect future meetings, so the tour must not toggle defaults or imply account-level approval.
- Confirmation boundary: any real configuration change requires a specific user request, visible setting identification, likely-effect confirmation, and a chance for the user to cancel before AiPresenter acts.

Any real Settings action should be conditional on all of the following:

- The user explicitly asks for the specific setting change.
- The visible UI makes the target setting and current value clear.
- AiPresenter can explain the likely local or meeting-level effect without guessing about policy, account permissions, or hidden state.
- The user confirms the intended change after seeing the setting.
- The action does not require AiPresenter to inspect or describe private device names, room imagery, meeting content, participant details, or account information beyond what the user asks.

Use cautious product language, not policy guarantees. Prefer Japanese equivalents of `場所と役割だけを説明します`, `ユーザーが明確に求めた場合`, `表示された項目と影響を確認してから`, and `設定は変更しません`. Avoid claiming that the current configuration is correct, safe, compliant, private, organization-approved, or persistent in a specific way.

Suggested semantic shape, not a required final string:

```text
Settings は、Audio、Video、Background、Translation、Join preferences、General など、会議中の設定をまとめて確認する中心的なダイアログです。開いたときに現在または最後に選ばれていたセクションが表示される場合がありますが、このコントロールマップでは Settings の場所と役割だけを説明します。音声デバイス、カメラ、背景、翻訳、入会時の動作、一般的な会議のふるまいに関わるため、ユーザーが明確に求め、表示された項目と影響を確認できるまで、AiPresenter はデバイスの切り替え、ビデオや背景の変更、翻訳や参加設定のオン・オフ、General の設定変更は行いません。説明後は Settings ダイアログを閉じます。
```

## Tone constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` voice: calm, concise, safety-aware, and practical. The line should sound like a meeting coach explaining a configuration center, not an IT policy notice.

Recommended tone points:

- Keep source UI labels in English when naming sections: `Settings`, `Audio`, `Video`, `Background`, `Translation`, `Join preferences`, and `General`.
- Use direct Japanese around the labels: `設定`, `設定ダイアログ`, `中心的なダイアログ`, `場所と役割`, `設定は変更しません`, `表示された項目と影響`.
- Include explicit non-execution wording such as `変更しません`, `切り替えません`, `オン・オフしません`, or `場所と役割だけを説明します`.
- Make the breadth of Settings clear without listing every possible sub-control.
- Mention explicit user request and visible confirmation before any future setting change.
- Stay focused on Settings. Do not teach Leave, Summary, Notes, recording, transcript, Q&A, source-index coverage, or deeper Background workflow behavior in this step.
- Avoid dramatic, legal, or fear-based wording. Settings is broad, but the narration should remain short enough for a live product tour.

Avoid wording that says or implies:

- AiPresenter changes, fixes, optimizes, validates, tests, previews, or recommends current settings.
- AiPresenter switches audio/video devices, changes camera state, changes background effects, enables translation, changes captions, toggles join defaults, or updates general preferences.
- The visible settings are safe, policy-approved, correct, persistent, private, or appropriate for every participant.
- The user has already consented to, authorized, or requested configuration changes.
- The current UI section is guaranteed to be the first Settings tab.

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not edit tests, runtime code, source-index docs, profiles, fixtures, lockfiles, coverage files, or other handoff files in this demand-analysis handoff.
- Do not commit.
- Do not add Japanese narration for `control-map-leave` or `control-map-summary`.
- Do not change the already-localized `control-map-background`, `control-map-notes`, `control-map-recording`, or earlier control-map narration.
- Do not change `meeting-controls-tour` narration, including the already-localized `explain-settings` step.
- Do not change English or Chinese narration.
- Do not add Japanese aliases, Q&A entries, presenter notes, locators, open steps, cleanup behavior, operation types, manual-control behavior, diagnostics behavior, CLI formatting, telemetry, or source-index coverage wording unless the implementation assignment explicitly expands scope.
- Do not add a settings editor, device picker, audio/video test workflow, background workflow, translation workflow, caption workflow, join-preference manager, policy checker, account-preference detector, or persistent-preference sync.
- Do not click or toggle any specific Settings sub-control after opening the dialog.
- Do not inspect, describe, summarize, screenshot, store, or log device names, account information, participant names, meeting identifiers, invite links, room imagery, background thumbnails, captions, translated text, private messages, or other sensitive meeting context.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-settings` -> `narration.localizedText.ja`.
- Japanese localization advances from `48/51` to `49/51` overall.
- `meeting-control-map-demo` advances from `19/22` to `20/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-leave`.
- Remaining missing control-map steps become `control-map-leave` and `control-map-summary`.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.
- `control-map-settings.action.entrypointId` remains `ringcentral.video.more.settings`.
- `control-map-settings.action.operation` remains `open`.
- `control-map-settings.narration.placement` remains `during`.
- `control-map-settings.narration.actionOffsetMs` remains `400`.
- `ringcentral.video.more.settings.openSteps` still opens `More`, then `Settings`, and keeps `cleanup: settings`.
- The Japanese text is authored Japanese and mentions `Settings`.
- The Japanese text explains Settings as a full or central configuration area.
- The Japanese text mentions the major configuration areas: audio, video, background, translation, join preferences, and general meeting behavior, or an equivalent concise grouping.
- The Japanese text says this control-map pass explains the Settings location/role only.
- The Japanese text says AiPresenter does not change settings automatically.
- The Japanese text requires explicit user request and visible setting/effect confirmation before any real configuration change.
- The Japanese text does not imply device switching, camera/background changes, translation/caption changes, join-preference changes, or general-setting changes are performed.
- The Japanese text does not infer policy, account permission, current setting correctness, device quality, privacy status, or persistence.
- Japanese `--require-complete` remains incomplete because `control-map-leave` and `control-map-summary` remain untranslated.

Useful negative assertions for implementation tests:

```python
assert "ja" in settings_step.narration.localized_text
assert "ja" not in leave_step.narration.localized_text
assert settings_step.action.entrypoint_id == "ringcentral.video.more.settings"
assert settings_step.action.operation == "open"
assert settings_step.narration.placement == "during"
assert settings_step.narration.action_offset_ms == 400
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-leave"
)
assert "Settings" in ja_text
assert "Audio" in ja_text or "音声" in ja_text
assert "Video" in ja_text or "ビデオ" in ja_text or "カメラ" in ja_text
assert "Background" in ja_text or "背景" in ja_text
assert "Translation" in ja_text or "翻訳" in ja_text
assert "Join preferences" in ja_text or "入会" in ja_text or "参加" in ja_text
assert "General" in ja_text or "一般" in ja_text
assert "説明" in ja_text
assert "変更しません" in ja_text or "切り替えません" in ja_text
assert "確認" in ja_text
assert "変更します" not in ja_text
assert "切り替えます" not in ja_text
assert "オンにします" not in ja_text
assert "オフにします" not in ja_text
assert "テストします" not in ja_text
assert "最適化します" not in ja_text
assert "安全です" not in ja_text
assert "承認されています" not in ja_text
```

## Handoff notes for implementation

Implementation should be a narrow localization update only. Start from the current baseline after cycle 097: Japanese demo coverage `48/51`, `meeting-control-map-demo: 19/22`, first missing `control-map-settings`.

The closest references are:

- `meeting-controls-tour` -> `explain-settings`, already localized in Japanese and very close semantically. Reuse its calm "explain only, do not change settings" posture, but adapt it to the control-map step and current baseline.
- `meeting-control-map-demo` -> `control-map-settings`, which currently has English and Chinese narration only and already opens `ringcentral.video.more.settings`.
- `ringcentral.video.more.settings`, whose presenter notes say Settings opens to the current or last selected section, should be used as the general route for audio, video, background, translation, join preferences, and general settings, and should be closed with the top-right X before continuing.
- `meeting-control-map-demo` -> `control-map-background`, localized in cycle 097, owns the deeper background-specific privacy and appearance explanation. Do not repeat that full boundary inside the Settings line.

Keep this step separate from the following control-map slices. `control-map-settings` teaches the broad configuration center and no automatic setting changes; `control-map-leave` should separately teach exit confirmation; `control-map-summary` should separately close the tour.

Parallel-agent note: the worktree may contain unrelated or preparatory edits from other agents, especially around localization expectations. Reconcile with current files at implementation time, but do not revert or overwrite unrelated dirty work.

After implementation, expected localization report key lines should be:

```text
Localization report: 49/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 20/22 narration localized
  missing: control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

This demand-analysis handoff intentionally creates only `docs/agent-handoffs/cycle-098-demand-analysis.md`. It does not modify package YAML, code, tests, source-index files, other docs, coverage artifacts, or git history.
