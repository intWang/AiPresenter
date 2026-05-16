# Cycle 072 Risk Scan: explain-raise-hand JA Narration

Date: 2026-05-16

## Scope

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-raise-hand`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing step and preserve:

- `entrypointId: ringcentral.video.toolbar.raise-hand`
- `operation: toggle`
- `placement: during`
- `actionOffsetMs: 350`

Relevant current context:

- The raise-hand entrypoint purpose is "Raise or lower hand to request attention."
- Its executable step clicks `Raise hand`, has alternate target `onconf.reactions.REMOVE_RAISE_HAND`, and uses `cleanup: toggle`.
- Presenter notes say the active state shows a hand indicator and changes toolbar emphasis, then should be clicked again to lower the hand after demonstration.
- Existing Q&A already frames Reactions and Raise hand as visible meeting signals and says not to raise a hand or leave it raised unless the user explicitly asks.
- Cycle 071 left Japanese demo narration at `22/51`, `meeting-controls-tour` at `15/22`, and the first missing controls-tour step at `explain-raise-hand`.

## Key Risks

1. **Persistent visible meeting signal**
   - Raise hand is not a transient explanation surface. It creates a visible participant state that can remain active after the narration step.
   - Japanese wording must describe it as a meeting-visible signal, not as a private reminder, local annotation, or harmless pointer.

2. **Accidental raise or lower**
   - The same control raises and lowers the hand.
   - In a real meeting, clicking it when the hand is down may request attention; clicking it when the hand is already up may cancel an intentional request.
   - The localization slice must not change action routing, locators, cleanup, or state assumptions that could make the toggle fire in the wrong direction.

3. **Request-for-attention meaning**
   - Raising a hand usually means the participant wants attention, permission to speak, or a place in the conversation queue.
   - The Japanese narration should avoid language that sounds like casual agreement, applause, emoji feedback, voting, or a nonverbal reaction.

4. **Moderated meeting expectations**
   - Raise hand is especially meaningful in moderated calls, webinars, classrooms, and host-controlled discussions.
   - A visible raised hand may affect how hosts manage turn-taking, questions, or speaking order.
   - Narration should present it as a polite alternative to interrupting, while keeping actual use under explicit user control.

5. **Attribution and privacy**
   - The raised-hand state may be associated with the user's name, tile, participant list, or host controls.
   - It can reveal intent to speak, attention state, confusion, dissent, or need for help.
   - Do not imply the signal is anonymous, private, local-only, reversible without anyone noticing, or safe to leave up indefinitely.

6. **Cleanup and toggle behavior**
   - The modeled cleanup is `toggle`, not Escape or panel close.
   - A failed or skipped cleanup could leave the hand raised after the tour; an extra cleanup click could lower a hand that the user intentionally raised before the demo.
   - Implementation and tests should verify the cleanup policy without overclaiming live-state confidence.

7. **Boundary with reactions**
   - Cycle 071 localized Reactions as quick feedback such as heart, thumbs up, celebration, clap, smile, and Be right back.
   - Raise hand is a separate persistent attention request, not a reaction option and not a quick sentiment signal.
   - The Japanese line should not mention emoji reactions, Be right back, or reaction-strip cleanup.

8. **Live-operation confidence**
   - This change would add localized narration only; it should not be treated as acceptance that unattended live raise/lower operation is safe.
   - Do not expand live operation, confirmed-action policy, aliases, Q&A, state extraction, telemetry, or tests beyond the narrow localization slice unless separately scoped.

## Mitigations

- Add only `narration.localizedText.ja` under `meeting-controls-tour` -> `explain-raise-hand`.
- Preserve the existing `entrypointId`, `operation`, `placement`, and `actionOffsetMs`.
- Keep wording close to the English/Chinese intent: the hand asks for attention without speaking over someone, and because it is a toggle, AiPresenter lowers it again after showing it.
- Explicitly frame raise hand as a visible meeting signal or attention request.
- State that AiPresenter does not raise, lower, or leave the hand raised unless the user clearly asks for a demonstration or action.
- Include the cleanup expectation that any confirmed demonstration ends by lowering the hand again.
- Avoid claiming current state unless verified; do not say the hand is currently up or down based on narration alone.
- Keep reactions out of this step. Do not reuse reaction examples, reaction panel cleanup, or quick-feedback framing.
- Avoid participant names, host names, meeting IDs, attendee list details, screenshots, or attribution logs in any validation notes.
- Manual validation, if later required, should use a disposable meeting and record only generic state such as "hand lowered after demo" or "pre-existing raised hand was not disturbed."

## Must-Verify Checks

- YAML shape:
  - `localizedText.ja` is added only to `meeting-controls-tour` -> `explain-raise-hand` -> `narration`.
  - `entrypointId` remains `ringcentral.video.toolbar.raise-hand`.
  - `operation` remains `toggle`.
  - `placement: during` and `actionOffsetMs: 350` remain unchanged.
  - English text and existing Chinese `localizedText.zh` remain unchanged.
  - No entrypoint, locator, cleanup, alias, Q&A, runtime, telemetry, test, or unrelated YAML changes are bundled into the localization slice.

- Text safety:
  - Japanese text identifies Raise hand as a meeting-visible signal or request for attention.
  - Japanese text explains the user value: asking to speak or get attention without interrupting.
  - Japanese text says or clearly implies the control is a toggle and the hand is lowered again after any demonstration.
  - Japanese text does not call raise hand a reaction, emoji, applause, vote, private note, anonymous signal, or local-only marker.
  - Japanese text does not imply AiPresenter will raise, lower, or leave a hand raised without explicit user instruction.
  - Japanese text does not claim live host behavior, speaking order, or moderation outcome beyond the visible request-for-attention meaning.

- Behavior and cleanup:
  - A tour-only explanation does not leave the user's hand raised.
  - If a confirmed demonstration raises the hand, cleanup lowers it exactly once.
  - If the hand is already raised before validation starts, the runbook must avoid treating the cleanup click as safe without first deciding whether lowering it is user-approved.
  - Failed cleanup is treated as a blocking safety issue for live acceptance, not as a harmless leftover state.

- Boundary and coverage:
  - `explain-reactions` remains unchanged and continues to own quick emoji/status feedback.
  - `explain-more`, recording, notes, settings, leave, Q&A, aliases, and diagnostics remain out of scope.
  - Expected Japanese demo narration after implementation: `22/51` -> `23/51`.
  - Expected `meeting-controls-tour` Japanese narration after implementation: `15/22` -> `16/22`.
  - Expected first missing controls-tour step after implementation: `explain-more`.
  - Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
  - Japanese `--require-complete` should still fail because later demo narration remains incomplete.

## Recommendation

Proceed only as a narrow narration slice. The Japanese line should make the persistent visible attention signal and cleanup obligation unmistakable while preserving the existing toggle action shape. Do not bundle live raise/lower acceptance, reaction behavior, moderated-meeting workflow changes, privacy evidence, locator changes, aliases, Q&A, tests, or runtime behavior into this cycle.
