# Cycle 083 Risk Scan: control-map-report JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-report`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `control-map-report` step and preserve:

- `entrypointId: ringcentral.video.top.report-issue`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 400`
- the step position after `control-map-views` and before `control-map-add-coworkers`
- the existing entrypoint cleanup behavior: `cleanup: modal`

`ringcentral.video.top.report-issue` opens a foreground Report issue dialog for Audio, Video, Screen sharing, Meeting join, Notes and transcript, or Other. The entrypoint notes already define it as a blocking support workflow: it blocks other meeting controls, should not pick a category during a feature tour, and should be closed with the dialog X because Escape was not reliable in testing.

The main risk in this localization slice is making the Report issue entry sound like an action that files a report, selects a problem category, uploads logs, or sends diagnostics. Japanese copy must frame it as an escalation entry point that opens a dialog and is closed after explanation. It must not imply AiPresenter will submit the form, attach logs, diagnose root cause, or expose meeting/device/network details without explicit user intent.

Adjacent context matters. `control-map-network` is the safe first stop for checking packet loss, jitter, and latency; `control-map-report` is escalation after something is wrong, not a replacement for observed diagnostics. `control-map-add-coworkers` opens another blocking modal with invite/search/link privacy risks; cleanup from Report issue must finish before moving into that people/invite flow.

## Behavior Boundaries

- Keep this as an open-and-explain step. The demo may open the Report issue dialog, but must not choose Audio, Video, Screen sharing, Meeting join, Notes and transcript, Other, or any runtime-specific issue category.
- Do not click Submit, Send, Report, Upload, Attach, Include logs, Include diagnostics, or any similar control unless the user explicitly asks to file a report and the workflow has a confirmation boundary.
- Do not enter free-form issue descriptions, meeting names, participant names, email addresses, device names, network details, or reproduction notes during the tour.
- Do not imply report submission is automatic. Safe wording: "opens the report/troubleshooting dialog," "escalation path," "close it before continuing."
- Do not promise that opening Report issue fixes audio/video/sharing/joining/notes/transcript problems or identifies the exact cause.
- Do not infer root cause from the Report issue entry. For media quality, use Network quality for observable packet loss, jitter, latency, or related diagnostics before escalating.
- Do not merge the Network quality boundary into Report issue. Network quality is diagnostic and read-only; Report issue is a support/reporting workflow that can become write/send behavior if advanced.
- Preserve cleanup. The Report issue dialog should be closed via the dialog X or other safe cancel/close affordance before touching Views, Add coworkers, Invite, Participants, toolbar controls, or any later step.
- Treat cleanup failure as blocking. If the modal remains open, subsequent clicks can land inside the report form or be blocked by the dialog instead of reaching the intended meeting control.
- Keep Add coworkers separate. Do not let the Report issue narration mention inviting people, copying meeting links, searching coworkers, or sending invites.

## Privacy Notes

- Report issue may expose or request sensitive troubleshooting data, including meeting identity, timestamps, account context, app version, device model, camera/microphone/speaker names, OS/browser details, network diagnostics, logs, screenshots, or user-entered descriptions.
- Japanese narration should not say that logs or diagnostic data are uploaded, included, attached, or sent unless the UI explicitly shows that state and the user has requested report filing.
- Do not read exact diagnostic values, meeting IDs, meeting links, dial-in details, participant names, email addresses, device labels, IP/network identifiers, screenshots, transcript text, notes, or issue descriptions aloud unless the user explicitly asks and the visible content is safe to disclose.
- If the dialog exposes category names, summarize the category set rather than treating any one category as selected. Safe examples are audio, video, sharing, joining, notes/transcript, or other issues.
- The preceding Network quality step can expose packet loss, jitter, latency, and media health values. Those values should be summarized unless requested, and should not be copied into Report issue text during a tour.
- The following Add coworkers step may expose suggestions, names, emails, and meeting links. Report issue cleanup must complete before opening that invite dialog so private support and invite surfaces are not visually stacked or confused.
- Screenshot or live validation evidence should avoid sensitive report-form contents, visible meeting identifiers, participant names, invite suggestions, copied links, device lists, network values, logs, or diagnostics.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `4/22` to `5/22`, with the first remaining missing step moving from `control-map-report` to `control-map-add-coworkers`.
- Overall Japanese demo localization totals should advance by exactly one step from the cycle 082 baseline, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-report`, not to `meeting-controls-tour` -> `explain-report-issue`, Q&A, entrypoint presenter notes, aliases, network, views, invite, or add-coworkers.
- Assert `control-map-report.action.entrypointId` remains `ringcentral.video.top.report-issue`.
- Assert `control-map-report.action.operation` remains `open`.
- Assert `control-map-report.narration.placement` remains `during`.
- Assert `control-map-report.narration.actionOffsetMs` remains `400`.
- Assert the entrypoint `ringcentral.video.top.report-issue` still has `cleanup: modal`.
- Assert the Report issue presenter notes still preserve the safety rules: foreground blocking dialog, do not pick a category during a tour, close with dialog X because Escape alone was unreliable.
- Assert the Japanese copy clearly describes opening a troubleshooting/reporting dialog as an escalation path, not submitting a report.
- Assert the Japanese copy names the problem scope safely: audio, video, sharing, joining, notes/transcript, or other issues. It should not make one category sound selected.
- Assert the Japanese copy includes or preserves the blocking-dialog cleanup boundary: close it before continuing.
- Assert the Japanese copy does not mention or imply automatic submission, category selection, log upload, diagnostic upload, attachment, screenshot capture, form entry, support-ticket creation, root-cause certainty, or guaranteed remediation.
- Assert neighboring steps remain unchanged, especially `control-map-network`, `control-map-views`, `control-map-add-coworkers`, and the `meeting-controls-tour` Report issue step.
- Assert the Network quality Q&A boundary remains intact: Network quality is used to inspect packet loss, jitter, latency, or related diagnostics; Report issue is only escalation, and exact causes are not guessed without observed values.
- If live or screenshot-based validation is used, fail review when the Report issue dialog remains open after the step, when a category is visibly selected by the automation, when form fields contain generated text, or when evidence captures private meeting/device/network/log data.
- If implementation updates CLI localization diagnostics, `--require-complete` for Japanese should still fail after this slice because the remaining `meeting-control-map-demo` steps are still untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-report`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-083-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map report issue." Keep category selection, report submission, log or diagnostic upload, screenshots, form-fill behavior, modal cleanup changes, locator changes, Network quality behavior, Add coworkers behavior, Q&A edits, and broader control-map localization for separate cycles unless explicitly assigned.
