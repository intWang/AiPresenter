# Cycle 087 Risk Scan: RingCentral Video Control Map Microphone JA

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-microphone`.

This should be a narrow narration-only slice. The future implementation should add only Japanese narration under the existing `control-map-microphone` step and preserve:

- the English and Chinese narration text
- `action.entrypointId: ringcentral.video.toolbar.audio`
- `action.operation: point`
- `narration.placement: before`
- the step position after `control-map-chat` and before `control-map-audio-menu`

Microphone is a high-risk control because the underlying entrypoint is a real meeting-state toggle. `ringcentral.video.toolbar.audio` targets `Mute` with alternate target `Unmute`; clicking it can expose the user's audio or silence them. Safe Japanese copy may explain the microphone button as the main privacy and speaking-readiness control, but it must not imply that AiPresenter mutes, unmutes, tests, records, transcribes, monitors, or verifies audible speech unless the user explicitly asks and the visible UI state is checked.

Adjacent context matters. The previous Chat step must be closed before microphone orientation. The next Audio menu step is for microphone/speaker device recovery and should stay separate: this slice should not open device menus, name devices, change audio routes, leave computer audio, use phone audio, or open deeper audio settings.

## Behavior Boundaries

- Keep this as a point-and-explain step. Do not change `operation: point` to `open`, `toggle`, or any action that executes the `Mute` / `Unmute` button.
- Do not click the microphone button during the control-map tour. Muting and unmuting are live meeting-state changes.
- Do not infer the current mic state from generic labels such as `Mute`, `Unmute`, icon appearance, toolbar position, or prior assumptions. State should be treated as verified only when the UI exposes the self-mic label clearly, such as `Mute microphone` or `Unmute microphone`.
- Do not claim the user is ready to speak, muted, audible, or unheard unless the visible state supports that exact claim.
- Do not perform a "mic test", listen for audio, capture microphone input, inspect audio levels, or ask the user to speak as part of this localization slice.
- Do not mention recording, transcription, notes, captions, summaries, or post-meeting artifacts as consequences of this microphone step. Those are separate controls with separate consent boundaries.
- Do not name or expose microphone/speaker device names here. Device selection belongs to `control-map-audio-menu` and should remain explain-only unless explicitly requested.
- Do not leave Chat or any side panel open before this step; open panels can obscure toolbar evidence and create false confidence about mic state.

## Privacy Notes

- The microphone button is a privacy boundary: unmuting can immediately transmit local room audio to meeting participants.
- Audio capture, device names, audio level indicators, and system-default-device toasts can reveal sensitive environment, hardware, or account context. Avoid collecting or logging them unless required for an explicit troubleshooting task.
- Manual validation should prefer sanitized package and UIA metadata. Avoid screenshots, logs, or transcripts that include participant names, meeting identifiers, device names, chat content, audio levels, or spoken content.
- Do not conflate microphone readiness with recording or transcription. A muted/unmuted state is not consent to record, transcribe, summarize, or monitor speech.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `8/22` to `9/22`, with the first remaining missing step moving from `control-map-microphone` to `control-map-audio-menu`.
- Overall Japanese demo localization totals should advance by exactly one step: from `37/51` to `38/51`, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-microphone`, not to `meeting-controls-tour` -> `explain-microphone`, Q&A, aliases, presenter notes, Chat, Audio menu, or later control-map steps.
- Assert `control-map-microphone.action.operation` remains `point`, `action.entrypointId` remains `ringcentral.video.toolbar.audio`, and `narration.placement` remains `before`.
- Assert the audio entrypoint still has one `clickWindowControl` open step targeting `Mute`, `alternateTargets: Unmute`, and `controlType: button`; tests should document that this route is a real toggle and must not be executed by the control-map microphone step.
- Assert presenter notes still say the button text alternates between `Unmute` and `Mute` and that the entrypoint is for audio privacy and meeting readiness.
- Preserve adapter guards that self-mic state is extracted only from precise self labels and not from `Mute participants`, bare `Mute`, or bare `Unmute`.
- Assert the Japanese copy describes microphone privacy and speaking readiness without claiming AiPresenter will mute, unmute, toggle, test, record, transcribe, capture audio, verify audibility, name devices, or change device routes.
- Assert neighboring steps remain unchanged, especially `control-map-chat`, `control-map-audio-menu`, and the existing `meeting-controls-tour` Microphone explainer.
- If live validation is used, fail review if the mic button is clicked, local mic state changes, Chat remains open, the audio menu opens during this step, device names are captured in evidence, or recording/transcription controls are opened.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-microphone`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-087-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map Microphone." Keep mute/unmute behavior changes, audio-menu behavior, device selection, audio capture, recording/transcription, Q&A edits, aliases, locator changes, and broader control-map localization for separate cycles unless explicitly assigned.
