# Cycle 097 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-background` -> `narration.localizedText.ja`.

The user need is a Japanese control-map explanation for `Background settings` that helps presenters understand where appearance and privacy controls live without changing their live camera appearance automatically. Japanese users should hear that this panel can turn effects off, blur the real room, choose built-in image or video backgrounds, or upload a custom background, while also understanding that AiPresenter is only explaining the panel in this tour.

Current Japanese localization baseline after cycle 096:

- Overall Japanese demo narration: `47/51`.
- `meeting-control-map-demo`: `18/22`.
- First missing `meeting-control-map-demo` Japanese step: `control-map-background`.
- Remaining missing control-map steps: `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.

This cycle should let Japanese users understand that Background settings are useful for presentation quality and room privacy, but that changing or uploading a background can expose, hide, or alter the meeting video appearance and must remain under explicit user control.

## Presenter behavior

The presenter should treat `control-map-background` as a panel-opening explanation step on `ringcentral.video.more.background`.

Required behavior in real meeting context:

- Preserve `entrypointId: ringcentral.video.more.background`.
- Preserve `operation: open`.
- Preserve `placement: during`.
- Preserve `actionOffsetMs: 400`.
- Preserve the existing Background route and cleanup behavior.
- Explain that Background settings control visual appearance and privacy.
- Explain the available categories: no effect or off, blur, built-in image backgrounds, built-in video backgrounds, and custom upload.
- Keep the panel visible only long enough to explain the location and role.
- Do not choose a built-in background, choose a video background, select blur, turn effects off, upload a file, remove a custom asset, mirror video, or otherwise change the user's camera appearance.
- Do not inspect or describe the user's room, personal objects, faces, coworkers, family members, confidential material, screen content, or uploaded image/video filenames.
- Do not claim that blur fully protects privacy or that a virtual background is guaranteed to hide sensitive details.
- Do not infer camera permission, visual quality, privacy status, room contents, organization policy, or meeting appropriateness from the panel opening successfully.

Good semantics: "Background settings are where you adjust meeting appearance and privacy: off, blur, built-in image or video backgrounds, and custom upload. In this control map, AiPresenter only explains where the options are. It does not select, upload, remove, or preview a background unless the user explicitly asks and the visible choice is confirmed."

## Privacy and appearance boundaries

The Japanese narration should keep Background settings in the appearance-and-privacy lane. It should communicate three separate boundaries:

- Appearance boundary: any background effect changes how the user's camera tile appears to other participants, so the tour must not apply an effect automatically.
- Privacy boundary: blur and virtual backgrounds can reduce room exposure, but they are not a promise that sensitive details are fully hidden.
- Upload boundary: custom uploads may contain personal, branded, copyrighted, confidential, or otherwise sensitive media, so AiPresenter should not upload, select, delete, describe, or reuse custom assets without explicit user direction and visible confirmation.

Any real background action should be conditional on all of the following:

- The user explicitly asks for the specific background action.
- The current visible UI makes the selected option and its likely effect clear.
- The user confirms the intended appearance before AiPresenter applies or uploads anything.
- The action does not require AiPresenter to inspect or describe private room details or personal media beyond what the user asks.

Use cautious product language, not security guarantees. Prefer Japanese equivalents of `場所と役割だけを説明します`, `ユーザーが明確に求めた場合`, `表示された選択肢を確認してから`, and `プライバシー保護を保証するものではありません`. Avoid claiming that a background is safe, fully private, policy-approved, or already selected.

Suggested semantic shape, not a required final string:

```text
Background settings は、会議中の見た目とプライバシーを調整する場所です。効果をオフにする、部屋をぼかす、内蔵の画像や動画背景を選ぶ、または自分の背景をアップロードする選択肢があります。このコントロールマップでは場所と役割だけを説明し、ユーザーが明確に求めて表示された選択肢を確認するまでは、背景の選択、ぼかしの適用、アップロード、削除は行いません。ぼかしや仮想背景は部屋の見え方を抑える助けになりますが、プライバシー保護を保証するものではありません。
```

## Tone constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` voice: calm, concise, safety-aware, and practical. The line should sound like a meeting coach explaining an appearance panel, not a warning banner.

Recommended tone points:

- Keep the source UI label in English when naming the panel: `Background settings`.
- Use direct Japanese around the label: `見た目`, `プライバシー`, `ぼかし`, `内蔵の画像や動画背景`, `自分の背景`, `場所と役割`.
- Include explicit non-execution wording such as `選択しません`, `適用しません`, `アップロードしません`, or `場所と役割だけを説明します`.
- Mention privacy as an important consideration without promising that blur or a virtual background fully hides the room.
- Stay focused on Background settings. Do not teach Settings, Leave, Summary, Notes, recording, transcript, or other More-menu behavior in this step.
- Avoid dramatic or fear-based wording. The point is controlled appearance management, not alarm.

Avoid wording that says or implies:

- AiPresenter selects, applies, previews, uploads, removes, or tests any background effect.
- Blur or virtual background guarantees privacy, safety, compliance, confidentiality, or full room concealment.
- The user's room, personal items, uploaded media, or camera image has been inspected.
- A custom background is appropriate, policy-approved, copyright-cleared, or safe to use.
- The current background should be changed without an explicit user request and visible confirmation.

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not edit tests, runtime code, source-index docs, profiles, fixtures, lockfiles, coverage files, or other handoff files in this demand-analysis handoff.
- Do not commit.
- Do not add Japanese narration for `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change already-localized `control-map-recording` or `control-map-notes` narration.
- Do not change `meeting-controls-tour` narration or the existing `vbg-blur-demo` Japanese narration.
- Do not change English or Chinese narration.
- Do not add Japanese aliases, Q&A entries, presenter notes, locators, open steps, cleanup behavior, operation types, manual-control behavior, diagnostics behavior, CLI formatting, telemetry, or source-index coverage wording unless the implementation assignment explicitly expands scope.
- Do not add a background-selection workflow, media-upload workflow, privacy checker, room scanner, image classifier, policy checker, copyright checker, camera-quality detector, or custom background manager.
- Do not select Off, Blur, any built-in image, any built-in video, Upload, Mirror my video, delete/remove, preview, or apply controls.
- Do not inspect, describe, summarize, screenshot, store, or log participant faces, room imagery, personal items, confidential materials, uploaded media, filenames, meeting IDs, invite links, or other sensitive meeting context.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-background` -> `narration.localizedText.ja`.
- Japanese localization advances from `47/51` to `48/51` overall.
- `meeting-control-map-demo` advances from `18/22` to `19/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-settings`.
- Remaining missing control-map steps become `control-map-settings`, `control-map-leave`, and `control-map-summary`.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.
- `control-map-background.action.entrypointId` remains `ringcentral.video.more.background`.
- `control-map-background.action.operation` remains `open`.
- `control-map-background.narration.placement` remains `during`.
- `control-map-background.narration.actionOffsetMs` remains `400`.
- The Japanese text is authored Japanese and mentions `Background settings` or an unambiguous background settings panel reference.
- The Japanese text mentions appearance or presentation quality.
- The Japanese text mentions privacy or room exposure.
- The Japanese text mentions at least two option categories, preferably off/no effect, blur, built-in image or video background, and custom upload.
- The Japanese text says this control-map pass explains the panel location/role only.
- The Japanese text says AiPresenter does not select, apply, upload, remove, or preview a background automatically.
- The Japanese text requires explicit user request and visible option confirmation before any real background change.
- The Japanese text does not guarantee that blur or virtual background fully protects privacy.
- The Japanese text stays focused on Background settings and does not pull in Settings, Leave, Summary, Notes, recording, transcript, Q&A, aliases, or legal advice.
- Japanese `--require-complete` remains incomplete because later `meeting-control-map-demo` steps remain untranslated.

Useful negative assertions for implementation tests:

```python
assert "ja" in background_step.narration.localized_text
assert "ja" not in settings_step.narration.localized_text
assert background_step.action.entrypoint_id == "ringcentral.video.more.background"
assert background_step.action.operation == "open"
assert background_step.narration.placement == "during"
assert background_step.narration.action_offset_ms == 400
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-settings"
)
assert "Background settings" in ja_text or "背景" in ja_text
assert "プライバシー" in ja_text or "見え方" in ja_text
assert "ぼかし" in ja_text or "Blur" in ja_text
assert "アップロード" in ja_text or "upload" in ja_text
assert "説明" in ja_text
assert "選択しません" in ja_text or "適用しません" in ja_text or "アップロードしません" in ja_text
assert "選択します" not in ja_text
assert "適用します" not in ja_text
assert "アップロードします" not in ja_text
assert "削除します" not in ja_text
assert "保証します" not in ja_text
assert "完全に隠します" not in ja_text
assert "安全です" not in ja_text
```

## Handoff notes for implementation

Implementation should be a narrow localization update only. Start from the current baseline after cycle 096: Japanese demo coverage `47/51`, `meeting-control-map-demo: 18/22`, first missing `control-map-background`.

The closest references are:

- `meeting-control-map-demo` -> `control-map-background`, which currently has English and Chinese narration only and is already an `open` step.
- `ringcentral.video.more.background`, whose presenter notes describe Background under More, covering Off, Blur, built-in static backgrounds, video backgrounds, upload, and Mirror my video.
- `vbg-blur-demo`, already localized in Japanese, which owns the deeper blur workflow. Do not copy its action-oriented wording in a way that applies blur during this control-map step.
- `meeting-control-map-demo` -> `control-map-notes`, localized in cycle 096, as the nearest example of an open-and-explain step with explicit no-action boundaries.

Keep this step separate from the following control-map slices. `control-map-background` teaches appearance, privacy, and no automatic background changes; `control-map-settings` should separately teach the full configuration center; `control-map-leave` should separately teach exit confirmation; `control-map-summary` should separately close the tour.

After implementation, expected localization report key lines should be:

```text
Localization report: 48/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 19/22 narration localized
  missing: control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

This demand-analysis handoff intentionally creates only `docs/agent-handoffs/cycle-097-demand-analysis.md`. It does not modify package YAML, code, tests, source-index files, other docs, coverage artifacts, or git history.
