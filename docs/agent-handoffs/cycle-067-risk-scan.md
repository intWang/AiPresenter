# Cycle 067 Risk Scan: `explain-audio-menu` JA Narration

Date: 2026-05-16

## Scope

Assess risks for adding Japanese `localizedText.ja` narration to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-audio-menu`.

Owned change for the implementation pass should remain narration-only unless a separate technical scan explicitly authorizes tests or package behavior changes.

Local context reviewed:

- `packages/ringcentral-video.yaml`
  - `ringcentral.video.toolbar.audio-menu`
  - `meeting-controls-tour` steps `explain-microphone`, `explain-audio-menu`, and `explain-camera`
- `presenter/skills/ringcentral-safety.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/agent-handoffs/cycle-066-summary.md`

## Current Behavior

- `explain-audio-menu` uses `entrypointId: ringcentral.video.toolbar.audio-menu`.
- The action is `operation: open`, not `point`.
- The entrypoint opens the first visible toolbar `More` button, currently modeled as the microphone/speaker menu.
- Cleanup is `escape`.
- The package says observed menu sections include `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio settings`.
- The step's English narration says the microphone arrow opens audio devices and names microphone switching, speaker switching, leaving computer audio, phone audio, and more audio settings.
- Cycle 066 advanced Japanese coverage through `explain-microphone`; `explain-audio-menu` is the next missing Japanese controls-tour step.

## Risk List

1. **Private device names**
   - Microphone and speaker lists can expose hardware names, virtual audio routes, headset names, room systems, driver labels, or organization-specific device names.
   - Japanese narration should not read specific device names aloud or imply that device labels are safe to log.
   - Manual evidence should record generic labels such as "microphone list visible" or "speaker list visible", not exact device names.

2. **Audio level indicators**
   - Live input/output meters can reveal whether local speech, room noise, or meeting audio is active.
   - The narration may describe that level indicators help diagnose audio, but must not infer what is being said, who is speaking, or whether private sound is present.
   - Screenshots or raw UI dumps around this menu should be avoided unless there is a clear privacy review path.

3. **Unintentional microphone or speaker switching**
   - Selecting a microphone can expose local audio from a different source.
   - Selecting a speaker can route meeting audio to speakers, headphones, virtual cables, or room devices.
   - The demo may open the menu for explanation, but should not choose a different device unless the user explicitly asks and a recovery path is known.

4. **Leave computer audio side effect**
   - `Leave computer audio` can disconnect the local computer audio path and disrupt the presenter or meeting.
   - Japanese narration may name the option as an available recovery path, but must not suggest AiPresenter will click it during the tour.
   - This control should remain confirmation-required in real meetings.

5. **Phone audio side effect and private dial-in data**
   - `Use phone audio` can expose dial-in instructions, phone numbers, pairing details, or meeting identifiers.
   - Narration should say phone audio is an option without reading or opening any phone-audio details beyond the already-open menu surface.
   - Do not capture dial-in numbers or meeting IDs in handoff evidence.

6. **System-default-audio-devices toast**
   - The package notes that a system-default audio devices toast may appear and should be closed only when visible.
   - Its close coordinate overlaps `Add coworkers` on the clean main screen, so blind cleanup can accidentally open an invite/add-coworkers path.
   - Any implementation or manual validation must keep this as conditional cleanup only, not a generic click.

7. **More audio settings and durable preferences**
   - `More audio settings` can lead to persistent device preferences or account/environment settings.
   - The Japanese line may mention it as a deeper settings path, but must not imply the tour changes settings.
   - Opening settings belongs to a separate accepted route, not this narration slice.

8. **Boundary with microphone privacy step**
   - `explain-microphone` owns the main `Mute` privacy switch and state check before speaking.
   - `explain-audio-menu` should not reframe the arrow as a mute/unmute control or claim current mute state.
   - Avoid language that blurs device recovery with changing microphone mute state.

9. **Boundary with camera step**
   - The next step, `explain-camera`, owns local camera state.
   - Audio-menu narration should not mention camera selection, video settings, background, or camera privacy.
   - This keeps the audience from hearing one media menu as permission to alter all media controls.

10. **Low live-operation confidence**
    - The locator matrix marks `ringcentral.video.toolbar.audio-menu` as low repo confidence.
    - Cycle 003 observed the first `More` order only in RingCentral Video `26.2.20.355`, `en-US`, 100% DPI, empty-room state, with no clicks or cleanup validation.
    - The route can be described in a localized script, but should not be treated as accepted for unattended live operation.

11. **Japanese wording could over-promise automation**
    - A direct translation of "You can switch..." may sound like AiPresenter is about to switch devices.
    - The Japanese narration should frame these as menu capabilities for the user, and explicitly preserve the safety boundary that devices and routing are not changed without instruction.

## Mitigations

- Keep the implementation narration-only: add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-audio-menu`.
- Preserve `operation: open`, `actionOffsetMs: 350`, and existing cleanup semantics.
- Do not modify locators, open steps, aliases, Q&A routing, runtime safety gates, settings routes, or tests unless separately assigned.
- Use generic capability language:
  - The microphone arrow opens audio device choices.
  - The menu is for checking or recovering microphone and speaker setup.
  - It also contains leave-computer-audio, phone-audio, and more-audio-settings paths.
  - AiPresenter will not select devices, change routing, leave computer audio, use phone audio, or open deeper settings without clear instruction.
- Do not include exact microphone/speaker device names in narration, tests, or handoff evidence.
- Keep level indicators as diagnostic UI only; do not infer or describe private audio content.
- Treat phone-audio and more-settings paths as mention-only in this slice.
- If validating manually, use a disposable meeting and safe test devices; record generic state only.
- Close the audio menu with Escape after the step. Close a system-default toast only when it is visibly present and positively identified.

## Must-Verify Checks

Content checks:

- `localizedText.ja` is added only to `meeting-controls-tour` -> `explain-audio-menu` -> `narration`.
- The Japanese line mentions the audio-device menu and covers microphone, speaker, leave computer audio, phone audio, and more audio settings.
- The Japanese line does not include actual local device names.
- The Japanese line does not claim that AiPresenter will switch microphone, switch speaker, leave computer audio, use phone audio, open settings, or change routing by default.
- The Japanese line does not claim the microphone is muted or unmuted.
- The Japanese line does not introduce camera/video/background behavior.

Behavior checks:

- The step remains `operation: open`.
- The entrypoint remains `ringcentral.video.toolbar.audio-menu`.
- Opening the step does not select a microphone or speaker.
- Opening the step does not toggle `Mute` / `Unmute`.
- Opening the step does not click `Leave computer audio`.
- Opening the step does not open phone-audio details.
- Opening the step does not open `More audio settings`.
- Escape returns to the stable meeting toolbar.
- Any system-default-audio-devices toast is closed only if visible and positively identified; no blind click is used near `Add coworkers`.

Coverage checks:

- Japanese demo narration should advance from `17/51` to `18/51`.
- `meeting-controls-tour` Japanese narration should advance from `10/22` to `11/22`.
- First missing `meeting-controls-tour` step should advance from `explain-audio-menu` to `explain-camera`.
- Q&A question/answer coverage and Japanese alias counts should remain unchanged unless separately assigned.

Manual evidence checks, if performed:

- Use a disposable RingCentral meeting.
- Record build, locale, DPI, window bounds, and generic result.
- Do not record participant names, chat content, meeting IDs, invite links, phone numbers, account labels, or exact device names.
- Prefer text evidence over screenshots. If a screenshot is necessary, review it for device names and meeting/private content before preserving it.

## Recommendation

Proceed as a narrow Japanese narration slice only if the wording preserves the audio-routing boundary: the menu can be explained as the place to check or recover microphone and speaker setup, leave computer audio, use phone audio, or reach more audio settings, but AiPresenter must not select devices, change routing, leave audio, open phone details, or enter settings without explicit user intent.

Do not bundle this with live-operation acceptance, locator updates, settings work, aliases, Q&A changes, microphone mute behavior, or camera narration. The route remains low-confidence for unattended live operation until a separate validation pass proves open/cleanup behavior across current RingCentral builds and states.
