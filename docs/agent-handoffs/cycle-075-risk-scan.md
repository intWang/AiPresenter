# Cycle 075 Risk Scan: explain-notes JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-notes`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing step and preserve:

- `entrypointId: ringcentral.video.more.notes`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 400`
- the existing `ringcentral.video.more.notes.openSteps` route through `More` occurrence `3` to `onconf.controls.NOTES`, with alternate target `Notes`
- `cleanup: sidePanel` on the Notes menu item route

Do not edit runtime behavior, locators, aliases, Q&A, tests, diagnostics, source-index counts, flow order, or neighboring steps as part of this risk scan.

Relevant current context:

- Cycle 074 localized `explain-recording`, leaving `explain-notes` as the first missing Japanese step in `meeting-controls-tour`.
- Current Japanese coverage is expected to be `25/51` demo steps and `18/22` `meeting-controls-tour` steps before this implementation slice.
- `explain-notes` currently says in English that Notes opens the Notes and Transcript panel, can start meeting notes, can also record the meeting, and those actions stay under user control.
- The existing Chinese narration preserves the same boundary: opening the panel is allowed for explanation, while starting notes or recording remains user-controlled.
- `ringcentral.video.more.notes` is observed as a nested More menu item in the current build, exposed to UI Automation as `onconf.controls.NOTES` with visible text `Notes`.
- Presenter notes say older layouts may expose Notes directly on the toolbar, but the current route should prefer the More menu when a direct Notes button is absent.
- Presenter notes also say the observed panel offers `Start notes` and `Also record this meeting`.
- Knowledge docs continue to mark the Notes route as needing live validation for direct-vs-nested variants and side-panel cleanup without reading notes or transcript content.

## Key Risks

1. **Notes and Transcript panel privacy**
   - Opening the panel can reveal sensitive meeting artifacts, including notes, transcript snippets, recording prompts, speaker labels, or meeting-state details.
   - Japanese narration must not imply AiPresenter is allowed to inspect, read aloud, summarize, capture, or store the panel contents by default.
   - Any future validation evidence must avoid screenshots or logs that expose private note, transcript, or speaker content.

2. **Transcript and note content exposure**
   - If notes or transcripts are already active, the panel may contain live or historical meeting text.
   - The safe tour behavior is panel discovery, not content review.
   - The Japanese line should describe the panel's purpose without saying AiPresenter reads, verifies, understands, extracts, translates, or summarizes the content.

3. **Starting notes changes meeting state**
   - `Start notes` is a state-changing action that can create meeting artifacts and participant expectations.
   - A localized line that sounds like "I start notes here" would be unsafe.
   - The wording must preserve that starting notes stays under explicit user control and should occur only when the meeting context allows it.

4. **Recording linkage inside the Notes panel**
   - The observed panel offers `Also record this meeting`, so the Notes panel can be recording-adjacent even though recording has its own `explain-recording` step.
   - Japanese text must not imply that opening Notes starts recording, that starting notes automatically records, or that AiPresenter can enable `Also record this meeting` without confirmation.
   - Keep recording action language conditional and user-controlled.

5. **Boundary with the dedicated Recording step**
   - `explain-recording` owns `Start recording` and remains `operation: explain`.
   - `explain-notes` owns Notes and Transcript panel discovery and remains `operation: open`.
   - Do not move recording consent, start/stop behavior, role checks, or live recording confidence from `explain-recording` into this localization slice.

6. **Participant names and speaker labels**
   - Notes/transcript panels can expose participant names, roles, initials, speaker labels, or attribution tied to transcript lines.
   - AiPresenter should not read participant names or speaker labels unless the user explicitly asks and visible context is verified.
   - Validation notes should mention only sanitized product-control labels, not people.

7. **Side-panel cleanup**
   - The route uses `cleanup: sidePanel`, and the panel should be closed before continuing.
   - Cleanup is still a live-operation confidence gap; a failed close can leave private notes or transcript content visible and can block later controls.
   - The future localization must not change cleanup mode, add new close assumptions, or treat an unclosed panel as harmless.

8. **Route and layout variants**
   - Current package route uses `More` occurrence `3` and `onconf.controls.NOTES`; older or localized layouts may expose Notes directly on the toolbar.
   - Japanese narration does not improve locator confidence.
   - Any future route validation must separately confirm direct-vs-nested Notes variants across participant counts, window sizes, and locale states.

9. **Boundary with captions/transcripts Q&A**
   - Existing Q&A says Notes and Transcript is the known discovery surface for transcript-related controls, while Settings may own translation preferences.
   - Q&A also says not to start notes, transcription, captions, or translation; not to read caption or transcript text; and not to promise post-meeting summaries unless explicitly asked and visible context is verified.
   - The new Japanese narration must align with that policy and must not introduce a broader permission to operate captions, live transcription, translation, summaries, or post-meeting artifacts.

10. **Live-operation confidence**
    - Adding `localizedText.ja` is package content work; it does not prove the Notes panel route is safe in live meetings.
    - No live acceptance should be inferred for opening Notes, closing the side panel, reading content, starting notes, enabling recording, or managing transcripts.
    - Live confidence still requires disposable-meeting validation with sanitized evidence and explicit checks that no content is read or retained.

11. **Localization meaning drift**
    - Japanese wording that is too short can lose the distinction between opening a panel and starting notes or recording.
    - Japanese wording that over-explains transcription, captions, or post-meeting summaries can drift beyond the source step and conflict with Q&A boundaries.
    - Preserve the source meaning: Notes opens the Notes and Transcript panel; the panel can start meeting notes and can also involve recording; those actions remain user-controlled.

12. **Persistent artifact and retention implications**
    - Notes, transcripts, recordings, summaries, and insights can persist after the meeting depending on enabled features and permissions.
    - The narration should not promise artifacts exist, are private, are local-only, are temporary, or can be deleted by AiPresenter.
    - It should avoid legal or compliance advice while preserving the product safety boundary of explicit user control.

## Mitigations

- Add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-notes`.
- Preserve `entrypointId: ringcentral.video.more.notes`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.
- Preserve the current `ringcentral.video.more.notes.openSteps` and `cleanup: sidePanel`.
- Keep the Japanese text centered on four ideas:
  - Notes opens the Notes and Transcript panel.
  - The panel may contain or lead to meeting notes and transcript-related controls.
  - Starting notes can change meeting state and create artifacts.
  - Recording-related options in this panel, including `Also record this meeting`, remain under explicit user control.
- Use wording that allows panel explanation but does not grant permission to read note or transcript content.
- Keep participant names, speaker labels, chat content, invite links, meeting IDs, recording filenames, and transcript text out of validation notes and screenshots.
- Do not add clicks on `Start notes`, `Also record this meeting`, caption controls, translation controls, recording controls, transcript text, participant names, or post-meeting artifacts.
- Do not change Q&A wording, aliases, runtime state extraction, consent automation, permission checks, telemetry, diagnostics, evidence docs, or live-acceptance status in this documentation-only task.
- If manual validation is ever required, use a disposable meeting with no sensitive content, informed participants, and sanitized evidence that records only route shape, panel open/close behavior, and whether cleanup restored the prior view.
- Treat any visible private content, failed cleanup, route ambiguity, or uncertain state-changing control as a blocker for live acceptance.

## Must-Verify Checks

- YAML shape:
  - `localizedText.ja` is added only to `meeting-controls-tour` -> `explain-notes` -> `narration`.
  - `entrypointId` remains `ringcentral.video.more.notes`.
  - `operation` remains `open`.
  - `placement` remains `during`.
  - `actionOffsetMs` remains `400`.
  - `ringcentral.video.more.notes.openSteps` remains routed through `More` occurrence `3` to `onconf.controls.NOTES` with alternate target `Notes`.
  - `cleanup: sidePanel` remains attached to the Notes menu item route.
  - English `text` and existing Chinese `localizedText.zh` remain unchanged.
  - No entrypoint, locator, cleanup, alias, Q&A, runtime, telemetry, diagnostics, test, evidence, or unrelated YAML changes are bundled into the localization slice.

- Text safety:
  - Japanese text is authored Japanese, not English or Chinese fallback.
  - Japanese text preserves the `Notes` and `Notes and Transcript` UI references or otherwise keeps the panel unambiguous.
  - Japanese text clearly says the panel is opened for explanation or discovery.
  - Japanese text clearly says starting notes remains user-controlled.
  - Japanese text clearly says recording-related action remains user-controlled.
  - Japanese text does not say AiPresenter starts notes, starts transcription, starts captions, starts translation, starts recording, clicks `Also record this meeting`, or creates meeting artifacts.
  - Japanese text does not say AiPresenter reads, summarizes, translates, validates, stores, or exports notes or transcript content.
  - Japanese text does not imply participant names, speaker labels, caption text, transcript text, or post-meeting artifacts can be read by default.
  - Japanese text does not claim artifacts always exist, are private, are local-only, are invisible, are temporary, or are automatically reversible.

- Behavior boundary:
  - The Notes step remains a panel-opening discovery step, not a note-starting or recording-starting step.
  - The step may open the Notes and Transcript panel but must not click `Start notes`, `Also record this meeting`, any transcript row, any caption/transcription/translation start control, or any post-meeting artifact.
  - The step does not start, stop, pause, resume, preview, locate, download, read, summarize, or validate recordings.
  - The step does not identify participant names, speaker labels, or roles.
  - The step closes the side panel before continuing, and failed cleanup is treated as a blocking issue for live acceptance.

- Boundary with related policy surfaces:
  - `explain-recording` remains the only `meeting-controls-tour` step for the `Start recording` entry.
  - `explain-notes` does not inherit recording start/stop behavior or recording live-operation confidence.
  - Existing captions/transcripts Q&A remains stricter than the tour: no starting notes, transcription, captions, translation, reading content, or promising summaries without explicit user request and verified visible context.
  - Post-meeting recordings, transcripts, summaries, and insights remain out of scope for this tour step.
  - `explain-background-settings`, `explain-settings`, and `explain-leave` remain unchanged.
  - The implementation does not localize later controls-tour steps in the same slice.

- Live-operation confidence:
  - This localization does not upgrade `ringcentral.video.more.notes` beyond its current evidence state.
  - Direct Notes button vs nested More menu variants remain unresolved until separately validated.
  - Side-panel close behavior remains unresolved until separately validated.
  - Any future live validation uses a disposable meeting, no sensitive content, and sanitized evidence only.
  - Validation evidence confirms only panel open/close and route shape; it does not capture notes, transcripts, captions, participant names, recordings, links, or post-meeting artifact content.

- Coverage expectations after the future implementation:
  - Japanese demo narration should move from `25/51` to `26/51`.
  - `meeting-controls-tour` Japanese narration should move from `18/22` to `19/22`.
  - The first missing `meeting-controls-tour` step should move from `explain-notes` to `explain-background-settings`.
  - Remaining missing `meeting-controls-tour` steps should be `explain-background-settings`, `explain-settings`, and `explain-leave`.
  - Japanese Q&A should remain complete at `12/12` questions and `12/12` answers.
  - Japanese `--require-complete` should still fail because later demo narration remains incomplete.

## Recommendation

Proceed only as a narrow narration localization slice. The Japanese line should preserve the current safety boundary: Notes opens the Notes and Transcript panel for discovery, but starting notes, interacting with transcript content, identifying participants, and enabling any recording-related option remain under explicit user control. Do not bundle executable Notes behavior, transcript/caption operation, recording behavior, side-panel cleanup changes, live-operation acceptance, Q&A edits, tests, or evidence updates into this risk-scan task.
