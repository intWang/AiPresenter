# Cycle 078 Risk Scan: explain-leave JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-leave`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `explain-leave` step and preserve:

- `entrypointId: ringcentral.video.toolbar.leave`
- `operation: explain`
- `placement: before`
- `ringcentral.video.toolbar.leave.openSteps: []`
- the existing destructive-control framing in the Leave entrypoint notes

The current Leave entrypoint is deliberately modeled with no UI open steps. That is the key safety boundary: `explain-leave` is a closeout explanation, not a route that clicks the Leave button or opens a leave/end confirmation dialog.

The main risk is accidentally turning a passive tour step into a real meeting exit. In the observed test build, clicking Leave can immediately show the left-meeting state. Depending on role, meeting state, product version, and whether the current user is host/cohost/participant, the Leave path may also expose choices that differ in blast radius, such as leaving only the current user versus ending the meeting for everyone. A localization update must not imply AiPresenter can safely click Leave during a normal tour, must not collapse "leave meeting" and "end meeting for all" into one harmless action, and must not promise a confirmation dialog will always protect the user.

Neighboring context matters. `explain-settings` opens Settings through More and then cleans up the Settings dialog, while `explain-leave` is immediately after that and uses `operation: explain`. Any Japanese copy should make the transition clear: after the settings overview, Leave is only identified as the exit control and remains untouched unless the user explicitly confirms an exit/end action.

## Behavior Boundaries

- Keep `explain-leave` as explain-only. Do not add an `open`, `click`, `toggle`, `select`, or route operation.
- Do not add `openSteps` to `ringcentral.video.toolbar.leave`.
- Do not click the toolbar Leave control during `meeting-controls-tour`.
- Do not open, depend on, or script through a confirmation dialog during this tour step.
- Do not choose between `Leave meeting`, `End meeting for all`, transfer-host, assign-host, cancel, or similar role-dependent choices.
- Do not state that clicking Leave is always reversible or always protected by a confirmation prompt.
- Do not state that leaving affects only the local user unless the visible UI explicitly confirms the available choice.
- Do not state that ending the meeting affects only the current user. Host-level end actions can affect all participants.
- Do not instruct AiPresenter to perform Leave, End, close-window, or equivalent exit actions from generic tour language.
- Do not mix this step with recording, notes, settings, background, participants, or host controls behavior.
- The Japanese text should mirror the current English meaning: Leave exits the meeting; it is destructive; the presenter explains it but does not click it without explicit confirmation.
- Stronger safe wording is acceptable if it preserves meaning, for example mentioning that host/end-for-all choices require separate explicit confirmation when shown by the UI.

## Privacy Notes

- Leave/end dialogs may reveal participant counts, host identity, meeting ownership, meeting title, role labels, or names of remaining participants. The tour should not read those values aloud by default.
- Host or moderator variants may expose controls for ending the meeting for all participants, assigning a new host, or managing meeting continuity. These reveal role/permission status and should be treated as contextual, not assumed.
- If the user requests an actual leave/end action, AiPresenter should verify visible UI text before describing choices and should avoid logging or narrating private participant names unless explicitly requested.
- Leaving a live meeting can interrupt ongoing conversation and can signal availability/status to other people. Treat the action as user-visible and socially consequential, not merely local navigation.
- Test artifacts should avoid screenshots or logs that include meeting IDs, invite links, participant names, host labels, private chat/transcript content, account details, or role-sensitive leave/end dialogs unless those artifacts are intentionally sanitized.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-controls-tour`; no other flow should gain or lose localization coverage as part of this change.
- Assert the new Japanese text is attached to `meeting-controls-tour` -> `explain-leave`, not to `meeting-control-map-demo`, Q&A, entrypoint presenter notes, aliases, or manual controls.
- Assert `explain-leave.action.entrypointId` remains `ringcentral.video.toolbar.leave`.
- Assert `explain-leave.action.operation` remains `explain`.
- Assert `explain-leave.narration.placement` remains `before`.
- Assert `ringcentral.video.toolbar.leave.openSteps` remains an empty list.
- Assert the Japanese copy includes the destructive/safety boundary: AiPresenter explains Leave and does not click it without explicit confirmation.
- Assert the Japanese copy distinguishes, or at least does not conflate, leaving the meeting with ending the meeting for everyone.
- Assert the Japanese copy does not promise a confirmation dialog, cancel path, undo path, host transfer path, or role-specific option that may not exist in every UI state.
- Assert the Japanese copy does not instruct the presenter to press Leave, End meeting, close the meeting window, or choose any confirmation-dialog option.
- Assert neighboring steps remain unchanged: `explain-settings` stays `operation: open` with `cleanup: settings` on its entrypoint route, while `explain-leave` stays explain-only and has no cleanup expectation.
- If implementation updates CLI coverage tests, expected totals should reflect one additional Japanese-localized demo step and no broader package-content changes.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-controls-tour` -> `explain-leave`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-078-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral Leave tour step." Keep Leave click behavior, host end-for-all handling, confirmation-dialog automation, role/permission branching, cleanup mechanics, locator changes, and Settings behavior for separate cycles.
