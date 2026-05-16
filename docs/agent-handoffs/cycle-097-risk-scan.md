# Cycle 097 Risk Scan: RingCentral Video Control Map Background JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-background`.

Current Japanese localization baseline is `47/51` demo steps overall, with `meeting-control-map-demo` at `18/22`; the first missing step is `control-map-background`. This slice is sensitive because the step opens the Settings dialog directly on the Background tab. That surface can show the user's real room, background thumbnails, built-in image or video choices, custom upload controls, and the current local background state. A wording or route mistake could select or apply a visual effect, expose private room imagery, upload a personal image, or leave the settings dialog open for the next step.

The safe target is a narrow open-and-explain localization. The implementation should preserve:

- `action.entrypointId: ringcentral.video.more.background`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 400`
- the `ringcentral.video.more.background` route through `More` occurrence `3`, then `Background`
- `match.cleanup: settings`
- English and Chinese narration text
- the step position after `control-map-notes` and before `control-map-settings`

The core safety rule is: the Background settings surface may be opened so the user can see where background controls live, but the presenter must not select, toggle, apply, upload, inspect, describe, or infer from background imagery beyond generic control labels.

## Allowed behavior

- Add exactly one Japanese narration block for `meeting-control-map-demo` -> `control-map-background`.
- Describe Background settings as a place for presentation quality and room privacy controls.
- Mention available categories at a high level: Off, Blur, built-in image backgrounds, video backgrounds, upload, and Mirror my video.
- Explain that the tour is showing the location and role of the panel only.
- Say AiPresenter does not choose, apply, or change any background effect in this control-map step.
- Say AiPresenter does not upload a custom image or inspect room/background imagery.
- Refer only to product-control labels and generic option categories unless the user explicitly asks for a visual inspection and the privacy boundary is confirmed.
- Close the Settings dialog after the explanation so `control-map-settings` starts from a neutral meeting surface.

## Forbidden behavior

- Do not click `Off`, `Blur`, a built-in image, a video background, the plus tile, upload, mirror, or any thumbnail.
- Do not imply the tour applies a background, protects the room automatically, hides private objects, or makes the current room safe to show.
- Do not upload, browse for, choose, preview, or describe a custom background asset.
- Do not read, summarize, classify, or infer from room details, personal objects, faces, documents, screens, artwork, custom images, or background thumbnails.
- Do not claim whether the currently visible background is real, blurred, virtual, private, safe, professional, or compliant.
- Do not add or change `openSteps`, cleanup behavior, action offsets, aliases, presenter notes, Q&A, source code, tests, source-index text, validation targets, or later demo steps as part of this risk scan.
- Do not broaden this slice into `control-map-settings`, `control-map-leave`, `control-map-summary`, actual blur selection, virtual-background upload, device configuration, or alias expansion.

## Background Effect Selection Risk

`ringcentral.video.more.background` is an executable open route, while `ringcentral.video.settings.background.blur` is the actual selection route for Blur. The implementation must keep those separate:

- `control-map-background` should continue to use `ringcentral.video.more.background`, not `ringcentral.video.settings.background.blur`.
- The route should still open `More` occurrence `3`, then select the `Background` menu item.
- The `Background` open step should keep `cleanup: settings`.
- No new open step should target `Blur`, `Off`, any thumbnail, `Upload`, the plus tile, or `Mirror my video`.
- Review should fail if any local background effect changes, any selection highlight moves as a result of the narration slice, or any upload/file picker appears.

If a future implementation wants to select Blur, that belongs to the existing `vbg-blur-demo` or a separately approved slice with explicit cleanup and privacy review.

## Privacy And Visual Boundary

Background settings can reveal the real room, custom uploaded images, organization-provided imagery, and personal preference state. This risk scan treats that visual content as private by default.

The Japanese narration should distinguish control labels from visual content:

- Safe: naming labels such as `Background`, `Off`, `Blur`, upload, built-in image/video background categories, and `Mirror my video`.
- Unsafe by default: describing what appears in the camera preview, room, thumbnails, uploaded images, or selected background.
- Unsafe by default: deciding whether an image is appropriate, identifying objects in the room, judging professionalism, or inferring location, employer, family, documents, health, politics, or other personal context.

If validation captures live evidence, record sanitized control labels and cleanup status only. Do not capture or transcribe room imagery, custom thumbnails, meeting IDs, participant names, account details, device names, or profile information.

## Settings Dialog Cleanup

The route's `cleanup: settings` is part of the safety boundary. The presenter note for the background route says to close the Settings dialog with the top-right X before continuing.

Review should fail if:

- the Settings dialog remains open before `control-map-settings`
- the dialog stays on the Background tab and causes the next step to skip its intended route
- the implementation changes cleanup ownership from the package route into narration wording only
- any settings value is changed as part of cleanup
- any modal, file picker, permission prompt, or unsaved-change prompt is left open

Because the following step also discusses Settings, a missed cleanup can be easy to overlook. The acceptance check should verify that `control-map-settings` still opens from the normal meeting surface, not from a carried-over Background dialog.

## Localization Overclaiming

The Japanese copy should be calm and practical, not stronger than the product behavior. Avoid claims that the Background tab itself guarantees privacy or that AiPresenter can judge the room safely.

Safer wording should be conditional and operational:

- "background settings help manage presentation quality and room privacy"
- "this tour only explains where the controls are"
- "background effects are changed only after an explicit user request"
- "uploaded or visible images may contain private information"
- "AiPresenter handles only control labels here"

Unsafe overclaims include:

- "privacy is protected"
- "the room is hidden"
- "safe background"
- "approved background"
- "professional background"
- "we will blur/apply/select it"
- "this image is acceptable"
- "nothing private is visible"

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Background settings は、見え方の品質と部屋のプライバシーに関わる設定場所です。ここではエフェクトなし、ぼかし、内蔵の画像やビデオ背景、独自背景のアップロード、Mirror my video などの選択肢を確認できます。このコントロールマップでは場所と役割だけを説明し、背景効果を選んだり適用したり、画像をアップロードしたりはしません。表示される部屋や背景サムネイルはプライベートな情報を含む可能性があるため、明確な依頼がない限り、操作ラベル以外の視覚内容は読み取ったり説明したりしません。説明後は Settings ダイアログを閉じます。
```

Useful positive assertions can include:

- `Background settings`
- `部屋のプライバシー`
- `エフェクトなし`
- `ぼかし`
- `内蔵の画像やビデオ背景`
- `独自背景のアップロード`
- `Mirror my video`
- `場所と役割だけ`
- `選んだり適用したり`
- `画像をアップロード`
- `背景サムネイル`
- `操作ラベル以外`
- `読み取ったり説明したりしません`
- `Settings ダイアログを閉じます`

Unsafe or overclaiming phrases should be rejected when they imply action, visual inspection, or guaranteed privacy:

- `ぼかしを選択します`
- `背景を適用します`
- `背景を変更します`
- `アップロードします`
- `画像を選びます`
- `この部屋を隠します`
- `プライバシーを保護します`
- `安全な背景です`
- `プロフェッショナルです`
- `部屋を確認します`
- `サムネイルを説明します`
- `自動`
- `すぐに`
- `問題ありません`

## Localization Boundary

Expected coverage movement after implementation:

- Overall Japanese demo narration: `47/51` -> `48/51`
- `meeting-control-map-demo`: `18/22` -> `19/22`
- First missing Japanese step: `control-map-background` -> `control-map-settings`
- Remaining missing steps should start with `control-map-settings`, then `control-map-leave`, and `control-map-summary`

Do not imply full Japanese coverage for `meeting-control-map-demo` until all 22 steps are localized. Japanese `--require-complete` should still fail after this slice because later control-map steps remain untranslated.

## Suggested Test Guardrails

Implementation tests should confirm:

- `control-map-background` has `localizedText.ja`.
- `control-map-settings` remains without Japanese narration and becomes the first missing step.
- Coverage updates exactly to `48/51` overall and `19/22` for `meeting-control-map-demo`.
- `control-map-background.action.entrypoint_id == "ringcentral.video.more.background"`.
- `control-map-background.action.operation == "open"`.
- `control-map-background.narration.placement == "during"`.
- `control-map-background.narration.action_offset_ms == 400`.
- `ringcentral.video.more.background` keeps open-step targets `More` and `Background`.
- The first Background open step keeps `occurrence == "3"` and `controlType == "button"`.
- The second Background open step keeps `cleanup == "settings"`.
- No Japanese aliases are added for Background; global Japanese alias coverage remains unchanged unless a separate alias task owns it.
- The previous `control-map-notes` step remains localized with side-panel cleanup.
- The next `control-map-settings` step remains a separate unlocalized open step.
- The Japanese copy explains the panel, privacy sensitivity, no selection/application/upload, no visual-content reading beyond control labels, and Settings cleanup.

Review should update CLI and diagnostics localization-report expectations only if the implementation owner scope includes those test files. This risk-scan handoff itself does not edit tests.

## Commit Hygiene

This risk-scan agent should create only `docs/agent-handoffs/cycle-097-risk-scan.md`.

At scan time, `git status --short` showed `.coverage` modified and `tests/unit/test_material_packages.py` modified before this document was created. Treat those as existing or parallel-agent work:

- Do not stage `.coverage`.
- Do not overwrite, revert, normalize, or format `tests/unit/test_material_packages.py` unless the implementation owner deliberately takes over that file.
- Re-check `git status --short` immediately before staging because other agents may be working in parallel.
- Keep any later implementation commit narrow: one YAML localization block and only directly necessary test/source-index expectation updates if assigned.
- Do not stage unrelated handoff docs, generated artifacts, screenshots, logs, `.coverage`, or other agents' WIP.
- If tests are run, prefer commands that avoid creating or refreshing coverage artifacts, and verify `.coverage` remains unstaged.

No commit should be made by this risk-scan agent.

## Reviewer Checklist

- Confirm this risk-scan subagent changed only `docs/agent-handoffs/cycle-097-risk-scan.md`.
- Confirm no YAML, code, tests, `.coverage`, screenshots, logs, or generated files were changed by this risk-scan subagent.
- Confirm the implementation adds only `meeting-control-map-demo` -> `control-map-background` -> `narration.localizedText.ja`.
- Confirm the Background route remains an open-and-explain Settings route with `cleanup: settings`.
- Confirm no background effect is selected, applied, changed, uploaded, or previewed by this slice.
- Confirm no room image, custom thumbnail, uploaded asset, participant image, device name, account detail, or other private visual content is read or described beyond control labels.
- Confirm the Japanese narration mentions privacy conditionally without claiming that the room is protected, safe, or inspected.
- Confirm the Settings dialog closes before the next `control-map-settings` step.
- Confirm Japanese coverage advances one step only and the next missing control-map step is `control-map-settings`.
