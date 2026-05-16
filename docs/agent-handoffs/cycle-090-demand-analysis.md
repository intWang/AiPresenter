# Cycle 090 Demand Analysis: RingCentral Video Control Map Camera Menu JA

## User need

Japanese users need the control map to explain where camera-related setup lives without making the presenter change live meeting state for them.

The camera menu is valuable because it is the practical route from the meeting toolbar to camera device choice and `More video settings`. In a RingCentral Video meeting, users often need this entrance when the wrong camera is selected, an external camera or virtual camera should be chosen, the visual presentation needs adjustment, or they need to find the settings route that eventually leads to background, quality, gallery, or camera configuration.

This step should answer: "Where do I go when the camera button itself is not enough?" It should not answer: "Is my video safe right now?" or "Please change my camera/background for me." The previous `control-map-camera` step already covers the main `Start video` / `Stop video` state cue. This slice should explain the adjacent menu as a route and decision point.

Important boundaries:

- The camera toggle controls whether local video is on or off. The camera menu is adjacent but different: it opens choices and settings.
- `More video settings` is a deeper configuration route. The camera menu may mention it as a shortcut, but this step should not drill into the settings dialog.
- Background is related to video appearance and privacy, but it already has separate Background routes. This step may say that appearance/background setup can be reached from video settings, but it should not describe or apply blur, virtual backgrounds, uploads, or mirror controls in detail.
- Camera device names and selected devices may reveal hardware, workplace setup, virtual camera software, capture cards, or personal devices. The narration should keep device references generic.

## Presenter behavior

The existing step is `meeting-control-map-demo` -> `control-map-camera-menu`, using `entrypointId: ringcentral.video.toolbar.video-menu`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. The presenter may open the menu to show where camera choice and video settings are located, then should close it according to the entrypoint cleanup behavior.

Expected behavior for this narration:

- Explain that the menu is for choosing a camera and reaching `More video settings`.
- Treat the menu as orientation, not consent to change devices or appearance.
- Keep the action limited to opening the menu during the tour.
- Avoid reading camera names aloud by default.
- Avoid saying the currently selected camera is correct, safe, broken, private, or recommended.
- Avoid switching cameras, opening `More video settings`, changing backgrounds, verifying the local camera feed, taking screenshots, or interpreting preview content unless a later explicit user request and visible UI verification justify it.
- Close the menu after explanation so it does not block later toolbar steps such as Share.

## Localization tone

Use natural Japanese product-demo language: calm, direct, and a little protective. The copy should sound like live guidance from a careful presenter, not like a literal translation of a settings manual.

Recommended tone:

- Keep RingCentral UI labels in English where they are likely visible in the product, especially `More video settings`, `Start video`, and `Stop video` when referenced.
- Prefer generic terms such as "カメラの選択", "ビデオ設定", "見え方の調整", and "背景まわりの設定" over detailed option lists.
- Use explicit consent language: "ユーザーが明確に求めるまで..." or an equivalent natural phrase.
- Make privacy wording precise. Say the menu may expose camera/device choices and visual setup; do not say AiPresenter can determine whether the room is private or who can see the user.
- Keep the narration concise enough for an in-meeting control map. One compact paragraph is better than a long compliance disclaimer.

Good semantic target for the Japanese text:

The camera menu opens camera selection and a shortcut to `More video settings`. It is the route for changing devices and adjusting appearance, including background-related setup, but in this tour the presenter only shows the location. It does not switch cameras, read device names, open deeper settings, or change background/video appearance unless the user explicitly asks.

## Out of scope

- Do not modify YAML, tests, runtime code, source index, profiles, Q&A, aliases, diagnostics, CLI output, or any other documentation in this demand-analysis turn.
- Do not localize later `meeting-control-map-demo` steps such as Share, Reactions, More, Notes, Recording, Background, Settings, or Leave.
- Do not change the existing camera-menu action semantics, locator, occurrence, timing, placement, cleanup, or flow order.
- Do not add Japanese question aliases for camera menu in this slice unless a separate implementation task explicitly assigns alias work.
- Do not change the previous `control-map-camera` narration or blur-demo/video-settings flows.
- Do not introduce behavior that selects a camera, opens `More video settings`, changes HD/quality/gallery settings, applies blur, selects a virtual background, uploads a background, toggles mirror video, or verifies the local preview.
- Do not capture or preserve evidence containing participant names, meeting identifiers, device names, video thumbnails, local camera preview, room details, or background images unless a later validation task explicitly requires sanitized evidence.

## Acceptance criteria

- This handoff exists as `docs/agent-handoffs/cycle-090-demand-analysis.md`.
- No YAML, code, tests, source-index files, profiles, or other docs are modified by this demand-analysis subagent.
- The future implementation target is only `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-camera-menu` -> `narration.localizedText.ja`.
- Current baseline is treated as `40/51` Japanese demo steps, `meeting-control-map-demo: 11/22`, first missing `control-map-camera-menu`.
- The future localized narration should advance Japanese demo coverage to `41/51` and `meeting-control-map-demo` to `12/22`.
- After implementation, the first remaining missing `meeting-control-map-demo` Japanese step should become `control-map-share`.
- Existing camera-menu behavior remains:
  - `entrypointId: ringcentral.video.toolbar.video-menu`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
  - underlying entrypoint target `More`, occurrence `2`, control type `button`, cleanup `escape`
- The Japanese narration explains the camera menu as a route for camera selection and `More video settings`.
- The Japanese narration distinguishes this menu from the camera on/off toggle.
- The Japanese narration mentions device/appearance/background setup only at route level and does not describe applying any specific setting.
- The Japanese narration includes explicit-user-request boundaries before camera switching, device-name reading, opening deeper settings, or changing background/video appearance.
- Japanese `--require-complete` should still fail after this future slice because later control-map steps remain untranslated.
- Q&A localization and `questionAliases.ja` coverage should remain unchanged unless separately assigned.

## Next handoff notes

Implementation should be a narrow narration-only package-content slice. Reuse the safety posture already established in cycle 089, but adapt it to the higher-risk menu surface: this step can open a menu that may expose camera device names and routes into settings, so the narration must emphasize orientation and consent.

Suggested implementation wording should stay close to the existing `meeting-controls-tour` Japanese `explain-camera-menu` copy, but tighten it for the control-map context by adding the menu cleanup/route boundary and the "do not read device names or change settings" privacy constraint.

Recommended next artifacts after implementation:

- A technical scan confirming the exact YAML location, count changes, first missing step, and tests to update.
- A risk scan focused on camera device names, `More video settings`, background appearance, and menu cleanup.
- A focused implementation handoff documenting changed files and verification commands.
