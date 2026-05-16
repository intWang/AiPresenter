# Cycle 084 Risk Scan: control-map-add-coworkers JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-add-coworkers`.

This handoff is documentation-only. The future implementation should add only Japanese narration under the existing `control-map-add-coworkers` step and preserve:

- `entrypointId: ringcentral.video.main.add-coworkers`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- the step position after `control-map-report` and before `control-map-participants`
- the entrypoint route: `clickWindowControl`, target `Add coworkers`, `controlType: button`, `cleanup: modal`

`Add coworkers` opens the same Invite others dialog as the toolbar `Invite` control. The dialog may include a name/email search field, contact suggestions, `Copy meeting link`, `Cancel`, and `Invite`. The main risk is Japanese copy that makes this sound like AiPresenter will invite people, search contacts, select suggestions, copy or read a meeting link, or otherwise change membership. The narration must be explanation-only: it may describe the invite entry point and the empty-room use case, but must not promise or perform invite actions.

Adjacent context matters. The preceding `control-map-report` step opens a blocking modal and must be closed before this invite modal opens. The following `control-map-participants` and `control-map-chat` steps expose people and message surfaces; Add coworkers must not blur into roster reading, chat reading, host controls, or active participant-management behavior.

## Behavior Boundaries

- Keep this as an open-and-explain step. Opening the Invite others dialog for the tour is acceptable only with modal cleanup; sending invites is not.
- Do not type into the name/email field, search contacts, select a suggestion, expand a contact card, or validate an email address during the tour.
- Do not click `Invite`, `Send`, or any equivalent final action unless the user explicitly asks to invite someone and the workflow has a confirmation boundary.
- Do not click `Copy meeting link` or copy meeting details during this localization slice. Copying is a privacy-affecting action even when no invite is sent.
- Do not read meeting links, meeting IDs, dial-in details, contact names, email addresses, or suggestion lists aloud unless the user explicitly asks and the visible content is verified.
- Preserve empty-room semantics. The main `Add coworkers` callout only applies when the user is first in the room; when other participants are present, existing adaptive behavior should rewrite to the toolbar `Invite` path.
- Do not imply membership changed. Safe wording should describe "opens the invite dialog" or "entry point for inviting/copying details," not "adds coworkers" as a completed action.
- Preserve cleanup. Close the Invite others dialog with the dialog X or `Cancel` before touching `Participants`, `Chat`, toolbar controls, or any later step.
- Treat cleanup failure as blocking. If the modal remains open, later clicks can land in invite search, copy-link, or invite controls instead of the intended meeting surface.
- Keep Participants and Chat separate. Add coworkers narration should not identify attendees, read participant names/roles, read chat messages, or describe private chat tabs.

## Privacy Notes

- Invite/Add coworkers can expose private names, email addresses, contact suggestions, meeting links, meeting IDs, dial-in details, and organization/account context.
- Contact suggestions are sensitive even before selection. Evidence and narration should summarize the surface without capturing or reading suggestion rows.
- Meeting links should not be read aloud, copied, logged, or included in screenshots unless the user explicitly requests it and the content is safe to disclose.
- Manual validation should prefer UIA/window metadata and sanitized labels. Avoid screenshots that include invite links, emails, participant names, meeting identifiers, or account/profile details.
- If the room is not empty, the empty-room Add coworkers callout may be absent; do not force the locator or infer that adding people is still the right entry point. Use the toolbar Invite explanation boundary instead.
- The nearby Participants panel may show attendee counts, names, roles, search, invite, lock, mute, raise-hand, and more controls. Default narration may describe the panel purpose or verified count, but not names or host actions.
- The nearby Chat panel may show public/private messages and tabs. It should remain private by default and must not be read as part of invite narration.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `5/22` to `6/22`, with the first remaining missing step moving from `control-map-add-coworkers` to `control-map-participants`.
- Overall Japanese demo localization totals should advance by exactly one step from the Cycle 083 baseline: from `34/51` to `35/51`, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-add-coworkers`, not to `meeting-controls-tour` -> `explain-add-coworkers`, toolbar `Invite`, Q&A, aliases, presenter notes, Participants, or Chat.
- Assert `control-map-add-coworkers.action.entrypointId` remains `ringcentral.video.main.add-coworkers`.
- Assert `control-map-add-coworkers.action.operation` remains `open`.
- Assert `control-map-add-coworkers.narration.placement` remains `during`.
- Assert `control-map-add-coworkers.narration.actionOffsetMs` remains `350`.
- Assert the entrypoint `ringcentral.video.main.add-coworkers` still has `cleanup: modal` and the existing notes about search field, suggestions, Copy meeting link, Cancel, Invite, empty-room applicability, and closing before other controls.
- Assert the Japanese copy clearly says this opens the invite dialog from the empty-room view and remains explanatory.
- Assert the Japanese copy includes or preserves privacy boundaries for names, emails, suggestions, invite links, and explicit user request before reading/copying/sending.
- Assert the Japanese copy does not imply automatic invite sending, contact search, suggestion selection, link copying, link reading, participant identification, membership changes, or chat/participant content reading.
- Assert adaptive tests continue to rewrite `control-map-add-coworkers` from `ringcentral.video.main.add-coworkers` to `ringcentral.video.toolbar.invite` when multiple participants are present, including localized narration replacement behavior.
- Assert neighboring steps remain unchanged, especially `control-map-report`, `control-map-participants`, `control-map-chat`, and the existing `meeting-controls-tour` Add coworkers and Invite explainers.
- If live or screenshot-based validation is used, fail review when the invite dialog remains open after the step, when text is typed into search, when a suggestion is selected, when `Copy meeting link` or `Invite` is clicked, or when evidence captures private names, emails, suggestions, links, or meeting identifiers.
- If implementation updates CLI localization diagnostics, Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-add-coworkers`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-084-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map Add coworkers." Keep invite sending, contact search, suggestion selection, copy-link behavior, meeting-link reading, modal cleanup changes, locator changes, Participants/Chat behavior, Q&A edits, aliases, and broader control-map localization for separate cycles unless explicitly assigned.
