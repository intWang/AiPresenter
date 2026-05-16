# Cycle 098 Risk Scan: RingCentral Video Control Map Settings JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-settings` only.

Current Japanese localization baseline is `48/51` demo steps overall, with `meeting-control-map-demo` at `19/22`; the first missing step is `control-map-settings`. This slice is sensitive because Settings is a broad configuration dialog. It can expose and change audio devices, video devices, background choices, translation behavior, join preferences, and general meeting behavior. A wording or route mistake could switch microphone or speaker devices, turn camera-related options on or off, alter background state, change translation preferences, change how the user joins future meetings, expose account/device details, or leave the Settings dialog open for the next `control-map-leave` step.

The safe target is a narrow open-and-explain localization. The implementation should preserve:

- `action.entrypointId: ringcentral.video.more.settings`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 400`
- the `ringcentral.video.more.settings` route through `More` occurrence `3`, then `Settings`
- `match.cleanup: settings`
- English and Chinese narration text
- the step position after `control-map-background` and before `control-map-leave`

The core safety rule is: Settings may be opened so the user can understand where configuration sections live, but the presenter must not change, select, toggle, test, connect, disconnect, upload, enable, disable, or infer from any setting or account/device state.

## Allowed behavior

- Add exactly one Japanese narration block for `meeting-control-map-demo` -> `control-map-settings`.
- Describe Settings as the full configuration center for `Audio`, `Video`, `Background`, `Translation`, `Join preferences`, and `General`.
- Explain that the tour is showing the location and role of the sections only.
- State that AiPresenter does not change audio, video, background, translation, join-preference, or general settings unless the user explicitly asks and the visible option is confirmed.
- Mention that device names, account details, meeting defaults, and preference state can be private.
- Close the Settings dialog after the explanation so `control-map-leave` starts from the normal meeting surface.

## Forbidden behavior

- Do not change microphone, speaker, camera, audio connection, video quality, gallery, background, translation, join-preference, notification, shortcut, or general meeting settings.
- Do not click toggles, checkboxes, radio buttons, menus, dropdown options, test buttons, device names, account links, sign-out controls, upload controls, reset controls, or save/apply-style controls.
- Do not select `Audio`, `Video`, `Background`, `Translation`, `Join preferences`, or `General` sub-options unless the existing route already lands there and the action remains explanation-only.
- Do not run audio tests, camera previews, speaker tests, translation setup, background changes, upload flows, sign-in/account flows, or join-preference changes.
- Do not read, summarize, classify, or record account identifiers, email addresses, tenant names, phone numbers, device names, camera previews, uploaded background filenames, custom images, meeting defaults, or language preferences.
- Do not imply Settings is safe to change automatically, that privacy is guaranteed, or that the app can judge whether the current configuration is correct.
- Do not broaden this slice into `control-map-leave`, `control-map-summary`, aliases, Q&A, operation-entrypoint changes, cleanup changes, source code, YAML structure beyond the one `localizedText.ja` value, tests, or source-index updates unless a separate implementation owner explicitly owns those files.

## Settings Change Risk

`ringcentral.video.more.settings` is an executable open route into a dialog that can contain many stateful controls. The implementation must keep it as an open-and-explain step:

- The step should continue to use `ringcentral.video.more.settings`, not a more specific audio, video, background, translation, or join-preference route.
- The route should still open `More` occurrence `3`, then select `Settings`.
- The Settings open step should keep `cleanup: settings`.
- No new open step should target any device dropdown, background tab, translation toggle, join-preference value, General toggle, save/apply control, account link, or sign-out action.
- Review should fail if any setting value changes, any device is selected, any test or preview starts, any account area opens, any upload/file picker appears, or any Settings dialog remains open.

If a future implementation wants to demonstrate a specific Settings subsection, that belongs to a separately approved slice with explicit state-change, privacy, and cleanup review.

## Device And Account Privacy

Settings can reveal private local and account-specific information. Treat visible Settings content as private by default.

Safe references:

- Section labels such as `Audio`, `Video`, `Background`, `Translation`, `Join preferences`, and `General`.
- Generic categories such as microphone, speaker, camera, background, language, and meeting defaults.
- The fact that Settings contains configuration areas.

Unsafe by default:

- Device model names, device serial-like labels, room camera names, Bluetooth headset names, phone audio details, account names, emails, tenant/workspace labels, profile images, meeting IDs, calendar-linked identity, custom background names, uploaded images, or saved preferences.
- Judging whether a selected device is correct, secure, professional, allowed, or compliant.
- Inferring language, location, role, employer, accessibility needs, or privacy posture from visible settings.

If validation captures live evidence, record sanitized section labels and cleanup status only. Do not capture or transcribe device names, account details, participant names, meeting identifiers, camera previews, background thumbnails, transcript/note content, or private messages.

## Settings Dialog Cleanup

The route's `cleanup: settings` is part of the safety boundary. The presenter note for `ringcentral.video.more.settings` says the Settings dialog should be closed with its top-right X before continuing.

Review should fail if:

- the Settings dialog remains open before `control-map-leave`
- the dialog remains on a sensitive section after explanation
- cleanup is moved into narration wording instead of staying on the route
- any setting value changes during open, explanation, or cleanup
- any nested modal, file picker, permission prompt, test prompt, account page, or unsaved-change prompt is left open

Because the following step is `control-map-leave`, a missed cleanup can create extra risk: the Leave explanation should begin from the normal meeting toolbar, not from inside Settings.

## Localization Overclaiming

The Japanese copy should be calm and operational. Avoid implying that AiPresenter can validate the user's configuration, protect privacy automatically, or safely alter settings without an explicit request.

Safer wording should be conditional and narrow:

- "Settings is the place to review configuration sections"
- "this tour only explains where these sections are"
- "changes require a clear user request and visible option confirmation"
- "device names and account details may be private"
- "the Settings dialog is closed after explanation"

Unsafe overclaims include:

- "settings are optimized"
- "privacy is protected"
- "the correct microphone/camera is selected"
- "we will adjust this automatically"
- "safe configuration"
- "recommended setting"
- "no private information is visible"
- "translation is ready"
- "join preferences are correct"
- "General settings are safe"

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Settings は、Audio、Video、Background、Translation、Join preferences、General など、会議全体の設定をまとめて確認するダイアログです。このコントロールマップでは各セクションの場所と役割だけを説明し、ユーザーが明確に求め、表示された選択肢を確認できるまで、マイクやスピーカー、カメラ、背景、翻訳、入会設定、General の項目は変更しません。デバイス名、アカウント情報、保存済みの参加設定などはプライベートな情報を含む可能性があるため、明確な依頼がない限り読み上げたり記録したりしません。説明後は Settings ダイアログを閉じます。
```

Useful positive assertions can include:

- `Settings`
- `Audio`
- `Video`
- `Background`
- `Translation`
- `Join preferences`
- `General`
- `場所と役割だけ`
- `変更しません`
- `表示された選択肢を確認`
- `デバイス名`
- `アカウント情報`
- `保存済みの参加設定`
- `プライベート`
- `読み上げたり記録したりしません`
- `Settings ダイアログを閉じます`

Unsafe or overclaiming phrases should be rejected when they imply action, optimization, or privacy guarantees:

- `設定を変更します`
- `マイクを切り替えます`
- `スピーカーを選択します`
- `カメラを変更します`
- `背景を変更します`
- `翻訳を有効にします`
- `入会設定を調整します`
- `General を最適化します`
- `正しい設定です`
- `安全な設定です`
- `プライバシーを保護します`
- `自動`
- `クリックします`
- `テストします`
- `保存します`

## Localization Boundary

Expected coverage movement after implementation:

- Overall Japanese demo narration: `48/51` -> `49/51`
- `meeting-control-map-demo`: `19/22` -> `20/22`
- First missing Japanese step: `control-map-settings` -> `control-map-leave`
- Remaining missing steps should be `control-map-leave` and `control-map-summary`

Do not imply full Japanese coverage for `meeting-control-map-demo` until all 22 steps are localized. Japanese `--require-complete` should still fail after this slice because later control-map steps remain untranslated.

Japanese Q&A coverage and alias coverage should remain unchanged unless a separate task owns them. In the current baseline, Japanese Q&A is complete and `questionAliases.ja` coverage is not part of this slice.

## Suggested Test Guardrails

Implementation tests should confirm:

- `control-map-settings` has `localizedText.ja`.
- `control-map-leave` remains without Japanese narration and becomes the first missing step.
- Coverage updates exactly to `49/51` overall and `20/22` for `meeting-control-map-demo`.
- `control-map-settings.action.entrypoint_id == "ringcentral.video.more.settings"`.
- `control-map-settings.action.operation == "open"`.
- `control-map-settings.narration.placement == "during"`.
- `control-map-settings.narration.action_offset_ms == 400`.
- `ringcentral.video.more.settings` keeps open-step targets `More` and `Settings`.
- The first Settings open step keeps `occurrence == "3"` and `controlType == "button"`.
- The second Settings open step keeps `cleanup == "settings"`.
- No Japanese aliases are added for Settings.
- The previous `control-map-background` step remains localized and keeps the Background privacy/no-change boundary.
- The next `control-map-leave` step remains a separate unlocalized explain step.
- The Japanese copy explains sections, no setting changes, explicit user request plus visible option confirmation, device/account privacy, and Settings cleanup.

Review should update CLI and diagnostics localization-report expectations only if the implementation owner scope includes those test files. This risk-scan handoff itself does not edit tests.

## Commit Hygiene

This risk-scan agent should create only `docs/agent-handoffs/cycle-098-risk-scan.md`.

At initial scan time, `git status --short` showed `.coverage` modified and `tests/unit/test_material_packages.py` modified before this document was created. Final verification also showed parallel modifications in `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py`, plus an untracked `docs/agent-handoffs/cycle-098-demand-analysis.md`. Treat all of those as existing or parallel-agent work:

- Do not stage `.coverage`.
- Do not overwrite, revert, normalize, or format `tests/unit/test_material_packages.py`, `tests/unit/test_cli.py`, or `tests/unit/test_diagnostics.py` unless the implementation owner deliberately takes over those files.
- Do not stage `docs/agent-handoffs/cycle-098-demand-analysis.md` from this risk-scan slice.
- Re-check `git status --short` immediately before staging because other agents may be working in parallel.
- Keep any later implementation commit narrow: one YAML localization block and only directly necessary test/source-index expectation updates if assigned.
- Do not stage unrelated handoff docs, generated artifacts, screenshots, logs, `.coverage`, or other agents' WIP.
- If tests are run, prefer commands that avoid creating or refreshing coverage artifacts, and verify `.coverage` remains unstaged.

No commit should be made by this risk-scan agent.

## Reviewer Checklist

- Confirm this risk-scan subagent changed only `docs/agent-handoffs/cycle-098-risk-scan.md`.
- Confirm no YAML, code, tests, `.coverage`, screenshots, logs, or generated files were changed by this risk-scan subagent.
- Confirm the implementation adds only `meeting-control-map-demo` -> `control-map-settings` -> `narration.localizedText.ja`.
- Confirm the Settings route remains an open-and-explain route with `cleanup: settings`.
- Confirm no audio, video, background, translation, join-preference, General, device, account, upload, test, save, or sign-out control is changed by this slice.
- Confirm no device name, account detail, meeting identifier, camera preview, background image, saved preference, participant data, note content, transcript content, or chat content is read or recorded beyond generic control labels.
- Confirm the Japanese narration avoids claims that Settings is optimized, safe, privacy-protecting, or automatically correct.
- Confirm the Settings dialog closes before the next `control-map-leave` step.
- Confirm Japanese coverage advances one step only and the next missing control-map step is `control-map-leave`.
