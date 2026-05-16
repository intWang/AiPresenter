# Cycle 074 Risk Scan: explain-recording JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-recording`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing step and preserve:

- `entrypointId: ringcentral.video.more.recording`
- `operation: explain`
- `placement: before`
- empty `openSteps` on `ringcentral.video.more.recording`

Do not edit runtime behavior, locators, aliases, Q&A, tests, diagnostics, source-index counts, flow order, or neighboring steps as part of this risk scan.

Relevant current context:

- Cycle 073 localized `explain-more`, leaving `explain-recording` as the first missing Japanese step in `meeting-controls-tour`.
- Current Japanese coverage is expected to be `24/51` demo steps and `17/22` `meeting-controls-tour` steps before this implementation slice.
- `explain-recording` says in English that `Start recording` changes meeting state, so AiPresenter only explains it in a tour and would ask before starting or stopping recording.
- The existing Chinese narration has the same explain-only and ask-before-start/stop boundary.
- `ringcentral.video.more.recording` is observed under More as `Start recording`, but has no executable `openSteps`.
- Presenter notes say recording is state-changing and AiPresenter should explain this entry without clicking it unless the user explicitly asks to start recording.
- The source index treats recording as a confirmed action, not a passive tour step.
- The neighboring `explain-more` step may open the More menu, while `explain-recording` itself is not an open or select action.
- The neighboring `explain-notes` step is separate and covers Notes and Transcript, where notes and recording-related controls can also appear.

## Key Risks

1. **Recording is state-changing and participant-affecting**
   - Starting or stopping recording changes the live meeting state and can affect everyone in the room.
   - It can create persistent meeting artifacts and alter participant expectations.
   - Japanese text must not sound like AiPresenter starts, stops, toggles, previews, validates, or demonstrates recording during the tour.

2. **Consent boundary**
   - Recording may require participant awareness or consent depending on meeting policy, organization rules, and jurisdiction.
   - A localized line that says only "I can start recording" would understate consent risk.
   - The Japanese narration should preserve the ask-before-starting-or-stopping language and should not imply consent is automatic.

3. **Permissions and host role**
   - Recording availability can depend on host, cohost, organizer, account, or policy permissions.
   - The text must not promise that every user can start or stop recording.
   - If execution is ever added later, role and permission checks must be separate from this localization slice.

4. **Privacy and post-meeting artifacts**
   - Recording can capture voice, video, screen share, participant names, chat-adjacent context, transcript-adjacent context, and room details.
   - It can also create post-meeting recordings, transcripts, summaries, or insights depending on enabled features.
   - Validation notes should not include participant names, meeting IDs, invite links, transcript text, recording filenames, screenshots of sensitive UI, or real room contents.

5. **Accidental start or stop**
   - The label `Start recording` sits inside More, near other secondary controls.
   - Any route, timing, or operation drift from `explain` to `open`, `select`, or `toggle` could accidentally affect the meeting.
   - A Japanese wording pass must not add child-click instructions, new open steps, "try it now" language, or test acceptance that requires clicking the control.

6. **Notification and legal implications**
   - Recording may trigger participant notifications, visible indicators, compliance banners, retention rules, or audit trails.
   - The narration should not describe recording as private, local-only, invisible, reversible, harmless, or a simple UI preference.
   - It should avoid legal advice; the safe product behavior is to require explicit user confirmation and clear participant consent.

7. **Boundary with More**
   - `explain-more` owns the menu-opening orientation step; `explain-recording` owns the recording-specific safety warning.
   - The Japanese line for recording may name `Start recording`, but should not imply that AiPresenter opens More again or selects the item.
   - Do not change the More locator, occurrence, cleanup behavior, or live-operation confidence while localizing the recording narration.

8. **Boundary with Notes**
   - Notes and Transcript can expose note and recording-related controls, but it is a separate step with its own safety language.
   - Recording narration should not say that Notes is the recording path, start notes, start transcript, read transcript content, or summarize meeting artifacts.
   - Keep recording consent and start/stop confirmation separate from Notes panel discovery.

9. **Explain-only operation**
   - The current action is `operation: explain`, and the recording entrypoint has empty `openSteps`.
   - This is the primary safety control for the tour.
   - The future implementation must not treat localized Japanese text as permission to add automation or to promote the step to an executable action.

10. **Live-operation confidence**
    - Adding Japanese narration does not prove that live operation is safe.
    - No live start/stop recording acceptance should be inferred from this cycle.
    - Any future confirmed recording workflow would need disposable-meeting validation, explicit confirmation UX, permission checks, consent checks, state detection, notifications review, and recovery handling.

11. **Localization meaning drift**
    - Japanese wording that is too terse could lose the distinction between explaining the entry and operating it.
    - Japanese wording that over-explains legal/compliance details could sound like policy advice beyond the package evidence.
    - Preserve the source meaning: recording changes meeting state; the tour explains only; start or stop requires asking and confirmation.

## Mitigations

- Add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-recording`.
- Preserve `entrypointId: ringcentral.video.more.recording`, `operation: explain`, and `placement: before`.
- Preserve empty `openSteps` on `ringcentral.video.more.recording`.
- Keep the Japanese text centered on three ideas:
  - `Start recording` changes meeting state.
  - Recording can affect all participants.
  - AiPresenter only explains the entry during the tour.
  - Starting or stopping recording requires asking, explicit confirmation, an allowed role, and clear participant-consent context first.
- Prefer wording that also leaves room for role, policy, and participant-consent requirements without claiming AiPresenter can verify them in this slice.
- Do not add clicks, menu navigation, locators, cleanup, delays, aliases, Q&A, runtime state extraction, telemetry, diagnostics, evidence updates, or tests in this documentation-only task.
- Do not use this slice to start, stop, pause, resume, preview, locate, download, read, summarize, or validate recordings.
- Keep `explain-more`, `explain-notes`, `explain-background-settings`, `explain-settings`, and `explain-leave` unchanged.
- Use only generic validation language later, such as "recording step remains explain-only"; avoid real meeting details or sensitive screenshots.
- If manual validation is ever required, use a disposable test meeting with informed participants, no sensitive content, and an account/role where recording permissions and notifications can be observed safely.

## Must-Verify Checks

- YAML shape:
  - `localizedText.ja` is added only to `meeting-controls-tour` -> `explain-recording` -> `narration`.
  - `entrypointId` remains `ringcentral.video.more.recording`.
  - `operation` remains `explain`.
  - `placement` remains `before`.
  - `ringcentral.video.more.recording.openSteps` remains an empty list.
  - English `text` and existing Chinese `localizedText.zh` remain unchanged.
  - No entrypoint, locator, cleanup, alias, Q&A, runtime, telemetry, diagnostics, test, evidence, or unrelated YAML changes are bundled into the localization slice.

- Text safety:
  - Japanese text is authored Japanese, not English or Chinese fallback.
  - Japanese text preserves the `Start recording` UI label or otherwise keeps the UI reference unambiguous.
  - Japanese text clearly says recording changes meeting state.
  - Japanese text clearly says recording can affect participants.
  - Japanese text clearly says the tour only explains the entry.
  - Japanese text clearly says AiPresenter asks and confirms before starting or stopping recording.
  - Japanese text clearly keeps real recording action conditional on an allowed role or permission context.
  - Japanese text clearly keeps real recording action conditional on participant consent or clear meeting-context permission.
  - Japanese text does not say AiPresenter starts, stops, toggles, tests, previews, validates, or demonstrates recording.
  - Japanese text does not imply all users have permission to record.
  - Japanese text does not imply participant consent, notification, retention, compliance, or legal requirements are automatically satisfied.
  - Japanese text does not describe recording as private, local-only, anonymous, invisible, harmless, or automatically reversible.

- Behavior boundary:
  - The recording step remains non-clicking and explain-only.
  - The step does not open More, select `Start recording`, stop an active recording, start notes, open transcript content, change settings, or leave the meeting.
  - Any previous More menu cleanup remains owned by `explain-more`; this step should not rely on a menu being open.
  - Failed cleanup, visible recording state, or uncertain targeting is treated as a blocking issue for live acceptance, not as a harmless tour artifact.

- Boundary with neighboring steps:
  - `explain-more` remains the only More menu orientation step in this portion of the tour.
  - `explain-notes` remains the Notes and Transcript panel step and does not inherit recording start/stop behavior.
  - `explain-background-settings`, `explain-settings`, and `explain-leave` remain unchanged.
  - The implementation does not localize later controls-tour steps in the same slice.

- Coverage expectations after the future implementation:
  - Japanese demo narration should move from `24/51` to `25/51`.
  - `meeting-controls-tour` Japanese narration should move from `17/22` to `18/22`.
  - The first missing `meeting-controls-tour` step should move from `explain-recording` to `explain-notes`.
  - Japanese Q&A should remain complete at `12/12` questions and `12/12` answers.
  - Japanese `--require-complete` should still fail because later demo narration remains incomplete.

## Recommendation

Proceed only as a narrow narration localization slice. The Japanese line should strengthen the existing recording safety boundary: `Start recording` is a participant-affecting state change, so this tour explains the entry only and requires explicit confirmation before any future start or stop action. Do not bundle executable recording behavior, More menu changes, Notes behavior, consent automation, permission checks, live-operation acceptance, tests, Q&A, or evidence updates into this cycle.
