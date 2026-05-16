# Cycle 077 Risk Scan: explain-settings JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-settings`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `explain-settings` step and preserve:

- `entrypointId: ringcentral.video.more.settings`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 400`
- the existing `ringcentral.video.more.settings.openSteps` route through `More` occurrence `3` to `Settings`
- `cleanup: settings` on the Settings route

The current step opens the general Settings dialog and explains the complete configuration area: audio, video, background, translation, join preferences, and general meeting preferences. This is broader and riskier than the preceding `explain-background-settings` step because Settings may open to the current or last selected section and can expose durable user preferences, device names, media controls, privacy-related translation or transcript settings, and join behavior.

The main risk is turning a neutral settings overview into a state-changing configuration flow. This cycle should not select audio devices, toggle microphone or camera behavior, change background effects, start translation or captions, alter join preferences, modify general meeting preferences, or navigate into background-specific behavior beyond naming it as one Settings area.

## Behavior Boundaries

- Keep `explain-settings` as a route-and-explain step. It may open Settings and describe the categories at a high level.
- Do not change microphone, speaker, camera, HD video, gallery, background, translation, caption, join, or general meeting preference values.
- Do not click into nested controls after opening Settings unless a separate flow explicitly owns that behavior.
- Do not reuse `explain-background-settings` or `vbg-blur-demo` semantics. Background-specific explanation belongs to `explain-background-settings`; actual Blur selection belongs to `vbg-blur-demo` through `ringcentral.video.settings.background.blur`.
- Do not imply Settings is only for Background. The Japanese copy must cover the same complete category list as English and Chinese: audio, video, background, translation, join preferences, and general meeting preferences.
- Do not frame Settings as a troubleshooting action that automatically fixes device problems. Device recovery belongs to audio/video menus and explicit user intent.
- Do not combine this step with `explain-leave`. Leave remains destructive and explain-only, with no click unless explicitly confirmed.
- Close the Settings dialog before continuing the tour; the cleanup expectation remains Settings-window cleanup only.

## Privacy Notes

- Settings can expose microphone, speaker, and camera device names. Narration and test logs should avoid reading specific device labels unless the user explicitly asks and the UI text is verified.
- Settings can expose camera preview, current background effect, custom background thumbnails, and room details. The general settings overview should not inspect or describe personal visual content.
- Translation, captions, notes, and transcript-related preferences may imply language use, accessibility needs, or meeting content processing. Do not start or promise translation, transcription, captions, notes, summaries, or post-meeting artifacts from this step.
- Join preferences and general meeting preferences can reveal durable behavior such as how the user joins meetings, audio/video defaults, and meeting readiness choices. Do not change or announce exact preference values during a tour.
- Background upload or custom media controls are privacy-sensitive because they may open file pickers or show personal/company images. This step must not activate upload controls.
- Test artifacts should avoid screenshots or logs that include account details, participant names, meeting IDs, invite links, private chat/transcript content, device labels, room previews, or custom media thumbnails.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-controls-tour`; the first missing controls-tour step should move from `explain-settings` to `explain-leave`.
- Assert the new Japanese text is attached to `meeting-controls-tour` -> `explain-settings`, not to `meeting-control-map-demo` -> `control-map-settings`, Q&A, entrypoint presenter notes, or aliases.
- Assert the step still uses `entrypointId: ringcentral.video.more.settings` and `operation: open`.
- Assert the route still uses `More` occurrence `3`, target `Settings`, and `cleanup: settings`.
- Assert the Japanese copy includes the same six categories as the source meaning: audio, video, background, translation, join preferences, and general meeting preferences.
- Assert the Japanese copy does not say or imply that AiPresenter changes devices, toggles microphone/camera, applies a background, opens upload, starts translation/captions/transcripts/notes, changes join defaults, changes general preferences, or reads private values.
- Assert neighboring steps remain unchanged: `explain-background-settings` stays the Background-specific step, and `explain-leave` remains `operation: explain` with no click/open behavior.
- If implementation updates CLI coverage tests, expected totals should reflect one additional Japanese-localized demo step and no broader package-content changes.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-controls-tour` -> `explain-settings`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-077-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral settings tour step." Keep device-control behavior, background selection, translation activation, join preference changes, general preference changes, cleanup mechanics, locator updates, and Leave behavior for separate cycles.
