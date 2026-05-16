# Cycle 085 Risk Scan: control-map-participants JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-participants`.

This should be a narrow narration-only slice. The future implementation should add only Japanese narration under the existing `control-map-participants` step and preserve:

- `entrypointId: ringcentral.video.toolbar.participants`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- the step position after `control-map-add-coworkers` and before `control-map-chat`
- the entrypoint route: `clickWindowControl`, target `Participants`, `controlType: button`, `cleanup: toggle`

The Participants panel is privacy-sensitive because it can expose the live roster, names, roles, attendee count, search, invite, lock meeting, mute, raise hand, more options, and host/moderator controls. Safe Japanese copy may explain that this is the roster and people-control panel, but it must not read or imply access to participant identities, exact count, roles, host powers, or active attendee management unless explicitly requested and visibly verified.

Adjacent context matters. The preceding Add coworkers step opens an invite modal and must be closed before Participants is opened. The following Chat step opens another side panel with public/private messages. Participants narration must not blur into invite sending, contact search, chat reading, or active host control behavior.

## Behavior Boundaries

- Keep this as an open-and-explain step. Opening the Participants panel for the tour is acceptable only with toggle/side-panel cleanup.
- Mention participant count only when it is verified from visible UI text or approved state extraction. Do not invent an exact count from the presence of tiles, labels, or assumptions.
- Do not read participant names, roles, email addresses, profile details, private tabs, or roster rows unless the user explicitly asks and visible content is verified.
- Do not use the Participants search field, type a name, select a person, expand a participant row, open a more-options menu for a specific attendee, or inspect host/moderator controls during this localization slice.
- Do not mute others, ask all to unmute, lower hands, remove participants, promote/demote roles, lock the meeting, change security settings, or perform any active attendee-management action.
- Raise hand is a meeting-visible signal. The Participants narration may mention where raise-hand related controls live, but it should not raise, lower, or manage hands unless a separate confirmed demo owns cleanup.
- Invite inside Participants has the same privacy boundary as Add coworkers/toolbar Invite: do not search contacts, click Invite, copy links, or read suggestions/links by default.
- Preserve cleanup. Toggle `Participants` or close the side panel before opening Chat or moving to later toolbar controls.
- Treat cleanup failure as blocking. If the panel remains open, later Chat or toolbar interactions can land on roster, invite, search, or host-control surfaces.
- Keep Participants and Chat separate. Participants copy should not describe chat message contents, private chat tabs, or Chat behavior beyond the need to close the panel before Chat opens.

## Privacy Notes

- Participants can expose names, roles, participant count, active attendee state, raised hands, host/moderator controls, search results, invite affordances, and account/profile details.
- Exact count is less sensitive than identity, but it still must be verified. If the badge or panel count is absent, stale, ambiguous, or not parsed by the adapter, use general wording such as "who is present" or "attendee context" instead of a number.
- Manual validation should prefer sanitized UIA/window metadata. Avoid screenshots or logs that include roster names, roles, profile details, emails, invite suggestions, meeting identifiers, chat text, or account context.
- Host/security controls are higher risk than ordinary panel explanation. Lock meeting, mute others, remove attendee, moderator assignment, and similar controls should remain explain-only until role, confirmation, consent, and rollback policy are defined.
- The panel has observed overlap with Chat tabs and invite controls. Evidence should record only generic labels needed for route and cleanup confidence, not private message or roster content.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `6/22` to `7/22`, with the first remaining missing step moving from `control-map-participants` to `control-map-chat`.
- Overall Japanese demo localization totals should advance by exactly one step from the Cycle 084 baseline: from `35/51` to `36/51`, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-participants`, not to `meeting-controls-tour` -> `explain-participants`, Q&A, aliases, presenter notes, Add coworkers, Invite, or Chat.
- Assert `control-map-participants.action.entrypointId` remains `ringcentral.video.toolbar.participants`.
- Assert `control-map-participants.action.operation` remains `open`.
- Assert `control-map-participants.narration.placement` remains `during`.
- Assert `control-map-participants.narration.actionOffsetMs` remains `350`.
- Assert the entrypoint `ringcentral.video.toolbar.participants` still has `cleanup: toggle` and presenter notes covering attendee count, no participant identification unless verified and allowed, observed Participant/Chat tabs, search, invite, lock, mute, raise-hand, more controls, and closing before Chat.
- Assert the Japanese copy clearly says Participants is the roster/people-control panel and remains explanatory.
- Assert the Japanese copy includes or preserves privacy boundaries for names, roles, exact count verification, and explicit user request before reading or managing people.
- Assert the Japanese copy does not imply automatic participant identification, exact unverified count reading, search, invite sending, meeting lock, muting others, hand management, removal, role changes, or other host/moderator action.
- Assert neighboring steps remain unchanged, especially `control-map-add-coworkers`, `control-map-chat`, and the existing `meeting-controls-tour` Participants and Chat explainers.
- Assert adaptive behavior still keeps unrelated Participants steps unchanged when participant count is present; `tests/unit/test_adaptive_demo.py::test_keeps_unrelated_steps_unchanged` is the current guard.
- If live or screenshot-based validation is used, fail review when the Participants panel remains open before Chat, when search or attendee menus are opened, when host controls are executed, or when evidence captures roster names, roles, emails, chat text, invite links, or meeting identifiers.
- If implementation updates CLI localization diagnostics, Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-participants`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-085-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map Participants." Keep roster identity reading, exact unverified counts, participant search, invite sending, meeting lock, muting others, hand management, attendee removal, role/security changes, Chat behavior, locator changes, Q&A edits, aliases, and broader control-map localization for separate cycles unless explicitly assigned.
