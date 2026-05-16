# Cycle 071 Risk Scan: explain-reactions JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-reactions`.

The owned implementation should remain narration-only and preserve `operation: open`.

## Key Risks

1. **Visible meeting signals**
   - Reactions are visible meeting feedback, not private notes or local-only UI.
   - Japanese narration should make the feature sound like a public meeting signal, not a private way to annotate the call.

2. **Accidental reaction sending**
   - The reaction strip includes direct-send options such as heart, thumbs up, celebration, clap, smile, and Be right back.
   - Opening the strip for explanation must not select an emoji or status unless the user explicitly asks.

3. **Be right back status implications**
   - Be right back can imply temporary absence, availability, or attention state to other participants.
   - The Japanese line should describe it as an available quick signal, not suggest AiPresenter sets status automatically.

4. **Cleanup confidence**
   - `ringcentral.video.toolbar.react` uses Escape cleanup.
   - This localization pass should not change cleanup behavior, add click-away cleanup, or claim a live cleanup path is stronger than observed.

5. **Privacy and attribution**
   - A reaction may reveal sentiment, attendance, or availability and can be attributed to the user in the meeting.
   - Narration should avoid saying reactions are anonymous, private, reversible, or harmless in all contexts.

6. **Boundary with Raise hand**
   - `explain-raise-hand` owns the moderated attention signal and uses a toggle flow.
   - Reaction narration should not blur quick emoji feedback with raising/lowering a hand or requesting the floor.

7. **Live-operation confidence**
   - This change adds Japanese narration only; it should not be treated as acceptance for unattended live operation.
   - Do not expand locators, action routing, aliases, Q&A, state extraction, or tests in this slice.

## Mitigations

- Keep `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- Add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-reactions`.
- Frame reactions as lightweight visible meeting feedback.
- Mention Be right back only as one of the quick signals and avoid implying status will be changed automatically.
- Explicitly preserve the boundary that AiPresenter does not send a reaction or set Be right back unless the user clearly asks.
- Close the reaction strip with Escape after explanation.
- Do not modify the neighboring `explain-raise-hand` step or any raise-hand toggle behavior.
- Do not add privacy-sensitive evidence such as participant names, meeting IDs, chat content, or reaction attribution logs.

## Must-Verify Checks

- `localizedText.ja` is added only to `meeting-controls-tour` -> `explain-reactions` -> `narration`.
- `entrypointId` remains `ringcentral.video.toolbar.react`.
- `operation` remains `open`.
- `placement: during` and `actionOffsetMs: 350` remain unchanged.
- The Japanese narration covers quick feedback such as heart, thumbs up, celebration, clap, smile, and Be right back.
- The Japanese narration says or clearly implies reactions are visible meeting signals.
- The Japanese narration does not claim reactions are private, anonymous, or local-only.
- The Japanese narration does not say AiPresenter sends a reaction, sets Be right back, or changes status without explicit user request.
- The reaction strip can be closed without sending anything.
- `explain-raise-hand` remains unchanged and still owns hand raise/lower behavior.
- Q&A, aliases, locators, cleanup, runtime routing, state extraction, tests, and `.coverage` remain unchanged.
- Assuming the cycle 070 baseline, Japanese coverage advances to `22/51`.
- Assuming the cycle 070 baseline, `meeting-controls-tour` advances to `15/22`.
- First missing `meeting-controls-tour` step advances to `explain-raise-hand`.

## Recommendation

Proceed as a narrow narration slice. Do not bundle reaction sending, Be right back status changes, raise-hand localization, cleanup changes, locator confidence updates, or live-operation acceptance into this commit.
