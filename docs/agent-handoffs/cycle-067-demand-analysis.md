# Cycle 067 Demand Analysis: meeting-controls-tour / explain-audio-menu JA narration

Date: 2026-05-16

## Demand Judgment

Proceed with the next single-step Japanese localization slice: `meeting-controls-tour` -> `explain-audio-menu`.

Cycle 066 advanced Japanese demo narration to `17/51` steps and `meeting-controls-tour: 10/22`, with the first missing step now `explain-audio-menu`. This is the right next slice because it continues the tour in order and completes the immediate audio-readiness pair after `explain-microphone`: the main microphone button covers privacy/readiness, while the microphone arrow covers device and routing recovery.

Keep this as a narrow audio-menu narration pass. Do not batch `explain-camera`, `explain-camera-menu`, share, reactions, notes, recording, leave, or any later step. Audio device routing, camera visibility, screen sharing, and meeting-visible actions have different privacy and state consequences.

## User Value

- Japanese presenters can continue the main meeting-controls tour from microphone privacy into audio device recovery without falling back to English.
- Users learn where to switch microphone or speaker when the wrong device is selected.
- Users learn that the same menu exposes leave-computer-audio, phone-audio, and more audio settings.
- The slice keeps audio recovery distinct from camera/video readiness, reducing the chance that a localization update becomes a broader media-state change.

## Strict Scope

- Add only Japanese narration for `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-audio-menu`.
- Preserve the existing action: `entrypointId: ringcentral.video.toolbar.audio-menu`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- Preserve existing English and Chinese text, flow order, entrypoint locators, cleanup behavior, Q&A, aliases, runtime behavior, and state extraction unless a separate owner explicitly expands scope.
- If implementation owns localization accounting, update only the expected JA coverage for this single step.
- If source-index maintenance is included, update the coverage note from the first ten `meeting-controls-tour` steps to the first eleven through Audio menu.

## Non-Goals

- Do not localize `explain-camera`, `explain-camera-menu`, `explain-share`, or any later step.
- Do not add or widen Japanese `questionAliases`; the audio-menu entrypoint currently has Chinese aliases only, and alias expansion is a separate routing/privacy task.
- Do not change `ringcentral.video.toolbar.audio-menu` locator strategy, `More` occurrence selection, cleanup, or toast handling.
- Do not click a microphone device, speaker device, phone-audio option, leave-computer-audio option, or more-audio-settings item during this localization slice.
- Do not toggle the main microphone mute/unmute control; Cycle 066 already localized the point-only microphone privacy step.
- Do not discuss camera state, camera device selection, room/background privacy, or video settings. Those belong to camera-specific slices.

## Privacy And State Boundaries

- The audio menu is a local audio routing surface. It can expose microphone names, speaker names, device availability, audio level indicators, phone-audio options, leave-computer-audio, and more audio settings.
- Opening the menu for explanation is acceptable in the scripted tour only if cleanup remains `escape` and no menu item is selected.
- Real-meeting audio route changes require explicit user intent because they can change what the meeting hears or what the user hears.
- Device names may reveal private hardware, room setup, virtual audio tools, or phone-routing context. Do not read detailed device names aloud unless the user explicitly asks and the visible content is verified.
- Do not claim a specific current microphone, speaker, phone-audio, or computer-audio state unless it is observed through an approved source.
- If the system-default-audio-devices toast appears, follow the existing package note: close it only when visible because its close coordinate can overlap Add coworkers on the clean main screen.
- Keep the boundary with `explain-microphone`: microphone mute/unmute is the primary privacy state; the arrow menu is for recovery and routing.

## Acceptance Criteria

- `explain-audio-menu` has `narration.localizedText.ja`.
- The Japanese text clearly maps the microphone arrow/menu to audio device controls.
- The text covers microphone switching, speaker switching, leave computer audio, phone audio, and more audio settings at a high level.
- The text frames the menu as device/routing recovery, not as permission to change devices automatically.
- The step remains `operation: open` on `ringcentral.video.toolbar.audio-menu`, with existing timing and cleanup behavior unchanged.
- The Japanese text does not mention camera, camera menu, share, reactions, notes, recording, leave, or later tour steps.
- No Japanese text is added to `explain-camera`, `explain-camera-menu`, or any later step in the same slice.
- Expected localization movement after implementation: JA demo narration `17/51` -> `18/51`; `meeting-controls-tour` `10/22` -> `11/22`; first missing `meeting-controls-tour` step should advance from `explain-audio-menu` to `explain-camera`.
- Q&A localization should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27 entrypoints (9 aliases)` unless a separate alias task is approved.

## Next-Step Recommendations

- Implementation should be narration-only and test-first: assert `explain-audio-menu` is the first missing JA step, add the JA line, then update focused coverage expectations.
- Use wording parallel to the English narration: the microphone arrow opens audio devices, where the user can switch microphone and speaker, leave computer audio, use phone audio, or open more audio settings.
- Add safety wording only if it stays concise: AiPresenter explains the menu and does not change routing without a clear user request.
- Run the Japanese localization report after implementation and confirm the next missing step is `explain-camera`.
- Prepare separate demand/risk/technical slices for `explain-camera` and `explain-camera-menu`; do not combine them with this audio-menu slice.

## Sources Reviewed

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/agent-handoffs/cycle-066-demand-analysis.md`
- `docs/agent-handoffs/cycle-066-risk-scan.md`
- `docs/agent-handoffs/cycle-066-summary.md`

## Changed Files

- `docs/agent-handoffs/cycle-067-demand-analysis.md`
