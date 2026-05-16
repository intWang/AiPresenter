# Cycle 066 Demand Analysis: meeting-controls-tour / explain-microphone JA narration

Date: 2026-05-16

## Demand Judgment

Proceed with the next single-step Japanese localization slice: `meeting-controls-tour` -> `explain-microphone`.

Cycle 065 advanced Japanese demo narration to `16/51` steps and `meeting-controls-tour: 9/22`, with the first missing step now `explain-microphone`. This is the right next slice because it continues the tour in order and starts the media-controls section with the highest-value local audio privacy control: microphone mute state.

Keep this as a narrow microphone-control narration pass. Do not batch `explain-audio-menu`, `explain-camera`, `explain-camera-menu`, share, reactions, notes, recording, leave, or any later step. Microphone mute/unmute, audio device routing, and camera visibility each have different state, privacy, cleanup, and side-effect profiles.

## User Value

- Japanese presenters can continue the main meeting-controls tour from Chat into media controls without falling back to English.
- Users learn that the microphone button is the first place to check before speaking.
- The localized wording can reinforce that mute is a local audio privacy control, not a general audio-settings menu.
- The slice creates a clean boundary before the next `explain-audio-menu` step, which covers microphone/speaker devices, computer audio, phone audio, and more audio settings.

## Strict Scope

- Add only Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-microphone`.
- Preserve the existing action: `entrypointId: ringcentral.video.toolbar.audio`, `operation: point`.
- Preserve existing English and Chinese text, flow order, timing, locators, cleanup behavior, Q&A, aliases, runtime behavior, and state extraction unless a separate owner explicitly expands scope.
- If implementation owns localization accounting, update only the expected JA coverage for this single step.
- If source-index maintenance is included, update the coverage note from the first nine `meeting-controls-tour` steps to the first ten through Microphone.

## Non-Goals

- Do not localize `explain-audio-menu`, `explain-camera`, `explain-camera-menu`, `explain-share`, or any later step.
- Do not add or widen Japanese `questionAliases`.
- Do not change the microphone entrypoint route, UIA locator strategy, adapter state extraction, operation permissions, or demo runtime behavior.
- Do not click or toggle microphone state as part of this narration slice; the current action is point-only.
- Do not describe speaker selection, microphone device switching, leave-computer-audio, phone audio, or more audio settings. Those belong to `explain-audio-menu`.
- Do not discuss camera visibility, room privacy, background, or video settings. Those belong to camera-specific slices.

## Privacy And State Boundaries

- Microphone is a local audio privacy surface. `Unmute microphone` means the local mic is currently muted; `Mute microphone` means the local mic is currently unmuted.
- The default behavior may explain mute/unmute state and the recovery path, but real-meeting microphone toggles require explicit user intent.
- Because the package step is `operation: point`, this slice should describe the control without changing live audio state.
- The Japanese narration should frame Mute as the main microphone privacy switch and the first control to check before speaking.
- Do not imply AiPresenter will listen to, capture, transcribe, or evaluate private meeting audio.
- Do not infer whether the user should speak from participant, chat, recording, transcript, or sharing state.
- Unknown or stale microphone state should not be invented. State extraction remains conservative; current confidence depends on recognized labels and still needs current UIA/localized-label evidence.

## Acceptance Criteria

- `explain-microphone` has `narration.localizedText.ja`.
- The Japanese text preserves the visible product/control term `Mute` or otherwise clearly maps to the microphone mute control.
- The text identifies mute as the main privacy switch for the user's microphone.
- The text says this is the first control to check before speaking.
- The text stays point/explain-only and does not instruct AiPresenter to toggle the microphone.
- The text does not mention audio device menus, speaker choice, computer audio, phone audio, camera, share, reactions, notes, recording, leave, or later steps.
- No Japanese text is added to `explain-audio-menu`, camera, share, notes, recording, leave, or later steps in the same slice.
- Expected localization movement after implementation: JA demo narration `16/51` -> `17/51`; `meeting-controls-tour` `9/22` -> `10/22`; first missing `meeting-controls-tour` step should advance from `explain-microphone` to `explain-audio-menu`.
- Q&A localization should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27 entrypoints (9 aliases)` unless a separate alias task is approved.

## Next-Step Recommendations

- Implementation should be narration-only and test-first: assert `explain-microphone` is the first missing JA step, add the JA line, then update focused coverage expectations.
- Use wording parallel to the English narration: media controls, Mute as the microphone privacy switch, and first check before speaking.
- Run the Japanese localization report after implementation and confirm the next missing step is `explain-audio-menu`.
- Prepare a separate risk/technical slice for `explain-audio-menu`; do not combine it with microphone because it opens device/routing controls and has different privacy and cleanup concerns.
- Keep camera and camera-menu localization separate from microphone/audio because camera state exposes local video, room/background, and visual privacy rather than audio privacy.

## Sources Reviewed

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/agent-handoffs/cycle-065-demand-analysis.md`
- `docs/agent-handoffs/cycle-065-summary.md`
- `docs/agent-handoffs/cycle-065-implementation.md`
- `docs/agent-handoffs/cycle-065-review.md`
- `docs/agent-handoffs/cycle-065-risk-scan.md`

## Changed Files

- `docs/agent-handoffs/cycle-066-demand-analysis.md`
