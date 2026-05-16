# Cycle 073 Risk Scan: explain-more JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-more`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing step and preserve:

- `entrypointId: ringcentral.video.toolbar.more`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`

Relevant current context:

- `ringcentral.video.toolbar.more` opens the third observed `More` button and uses `cleanup: escape`.
- Presenter notes describe More as the expansion point for less frequent meeting tools.
- In the current observed two-person meeting layout, Notes is direct on the toolbar, while More keeps `Start recording`, `Background`, and `Settings`.
- The control map still frames More as the overflow hub for secondary meeting actions such as recording, notes, background, settings, and leaving.
- Downstream steps already own recording, notes/transcript, background settings, settings, and leave behavior separately.
- Cycle 072 left Japanese demo narration at `23/51`, `meeting-controls-tour` at `16/22`, and the first missing controls-tour step at `explain-more`.

## Key Risks

1. **Overflow hub ambiguity**
   - More is a navigation hub, not one feature.
   - Japanese narration should explain that it gathers deeper or less frequent meeting tools without implying every listed action is safe to open or execute during the same step.
   - The wording should tolerate layout variants where Notes may be on the toolbar or under More.

2. **Accidental downstream action**
   - The open menu can expose `Start recording`, `Background`, and `Settings`, and may expose `Notes` depending on layout.
   - A localization-only pass must not add routing, timing, or wording that causes AiPresenter to select a child menu item while explaining More.
   - Recording, notes, background, settings, and leave must remain separately governed by their own steps.

3. **Recording state change**
   - `Start recording` changes the meeting state and may notify or affect participants.
   - Japanese narration must not sound like AiPresenter starts, stops, confirms, or validates recording from the More overview step.
   - Recording belongs to `explain-recording`, which is `operation: explain` and should remain a later boundary.

4. **Notes and transcript side effects**
   - Notes can open a panel with transcript or note controls, and starting notes can also involve recording-related behavior.
   - The More narration should not read notes, transcript content, meeting summaries, attendee names, or panel state.
   - It should not promise that notes are always under More, because the current observed layout says Notes is already on the toolbar.

5. **Background and settings side effects**
   - Background and Settings can reveal camera, room, device, translation, join preference, and general meeting preferences.
   - They can also change durable local or meeting preferences.
   - The More step should name these as examples of deeper tools, not enter the settings dialog or change background effects.

6. **Leave and destructive action boundary**
   - The control map includes leaving among secondary More-related actions, but the package has `ringcentral.video.toolbar.leave` as its own explain-only destructive control.
   - Japanese text must not imply that More is the place to click Leave in the current toolbar tour, or that leaving is safe to demonstrate.
   - Leave remains a separate confirmed action with no click during normal tours.

7. **Cleanup and open-menu behavior**
   - `ringcentral.video.toolbar.more` relies on `cleanup: escape`.
   - Failed cleanup can leave the More menu open, changing the next step's click target or causing a later Escape to close the wrong surface.
   - The localization slice should not change cleanup semantics, add click-away cleanup, or claim stronger cleanup confidence than the current repo evidence supports.

8. **Locator and occurrence confidence**
   - The More route uses `occurrence: '3'`, and the locator matrix marks it low repo confidence because multiple `More` buttons can exist.
   - Japanese narration must not be treated as validation that the correct overflow button is always found across RingCentral builds, locales, DPI settings, participant layouts, or meeting states.
   - Do not update locator confidence in this slice.

9. **Privacy and audit surface**
   - More-adjacent tools can expose meeting recording state, notes/transcript state, room background, devices, translations, and preferences.
   - Validation notes should avoid participant names, meeting IDs, chat or transcript text, recording indicators tied to real meetings, screenshots with sensitive UI, or room details.
   - Narration should avoid saying these tools are private, anonymous, local-only, or harmless.

10. **Boundary with downstream steps**
    - `explain-more` should be a table-of-contents step.
    - `explain-recording`, `explain-notes`, `explain-background-settings`, `explain-settings`, and `explain-leave` own the specific risk policies.
    - The Japanese text should not pre-localize those downstream behaviors, change their safety contract, or collapse them into one combined action.

11. **Live-operation confidence**
    - Adding Japanese narration only does not prove unattended live operation is safe.
    - The route remains an open-and-close menu explanation until a separate live validation pass proves correct targeting and cleanup on current RingCentral Video builds.
    - Do not expand aliases, Q&A, state extraction, telemetry, runtime routing, tests, evidence claims, or live acceptance in this cycle.

## Mitigations

- Add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-more`.
- Preserve the existing `entrypointId`, `operation`, `placement`, and `actionOffsetMs`.
- Describe More as an overflow or expansion menu for deeper meeting tools.
- Keep examples limited to the existing English intent: Notes may already be on the toolbar, while More keeps `Start recording`, `Background`, and `Settings` in the observed build.
- Make clear that opening More is for orientation only; selecting a child action requires its own explicit step or user confirmation.
- Do not click `Start recording`, start notes, open transcript content, change background, open settings, or click Leave from this step.
- Close the More menu with Escape before continuing, matching the existing route.
- Do not alter `ringcentral.video.toolbar.more` occurrence selection, cleanup policy, presenter notes, downstream entrypoints, or neighboring narration.
- Avoid privacy-sensitive validation artifacts. Use generic labels such as "More menu opened" and "menu closed" rather than real participant, meeting, recording, notes, transcript, or device details.
- Treat manual validation, if later required, as disposable-meeting only and record no sensitive UI contents.

## Must-Verify Checks

- YAML shape:
  - `localizedText.ja` is added only to `meeting-controls-tour` -> `explain-more` -> `narration`.
  - `entrypointId` remains `ringcentral.video.toolbar.more`.
  - `operation` remains `open`.
  - `placement: during` and `actionOffsetMs: 350` remain unchanged.
  - English text and existing Chinese `localizedText.zh` remain unchanged.
  - No entrypoint, locator, cleanup, alias, Q&A, runtime, telemetry, test, evidence, or unrelated YAML changes are bundled into the localization slice.

- Text safety:
  - Japanese text frames More as an overflow or expansion hub for deeper meeting tools.
  - Japanese text reflects the observed layout nuance: Notes may already be on the toolbar while More keeps `Start recording`, `Background`, and `Settings`.
  - Japanese text does not say AiPresenter starts or stops recording from this step.
  - Japanese text does not say AiPresenter starts notes, reads notes/transcripts, changes background, changes settings, or leaves the meeting from this step.
  - Japanese text does not imply More actions are private, anonymous, local-only, risk-free, or automatically reversible.
  - Japanese text does not promise a specific Notes placement across all RingCentral layouts.

- Behavior and cleanup:
  - The More overview step opens the menu only and does not select any child item.
  - The menu closes with Escape before the tour proceeds.
  - Failed menu cleanup is treated as a blocking issue for live acceptance, not as harmless leftover UI.
  - The step does not leave a Settings dialog, side panel, recording state, background change, notes state, or left-meeting state behind.

- Boundary and coverage:
  - `explain-recording` remains unchanged and continues to own recording confirmation language.
  - `explain-notes` remains unchanged and continues to own Notes and Transcript panel boundaries.
  - `explain-background-settings` and `explain-settings` remain unchanged and continue to own settings cleanup.
  - `explain-leave` remains unchanged and continues to be explain-only/destructive.
  - Expected Japanese demo narration after implementation: `23/51` -> `24/51`.
  - Expected `meeting-controls-tour` Japanese narration after implementation: `16/22` -> `17/22`.
  - Expected first missing controls-tour step after implementation: `explain-recording`.
  - Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
  - Japanese `--require-complete` should still fail because later demo narration remains incomplete.

## Recommendation

Proceed only as a narrow narration slice. The Japanese line should make More feel like an orientation point for deeper, riskier meeting tools while preserving the current open-menu action shape and Escape cleanup. Do not bundle recording, notes/transcript, background, settings, leave, locator confidence, cleanup changes, aliases, Q&A, tests, telemetry, evidence updates, or live-operation acceptance into this cycle.
