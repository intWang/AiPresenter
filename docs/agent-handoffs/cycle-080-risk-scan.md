# Cycle 080 Risk Scan: control-map-meeting-info JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-meeting-info`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `control-map-meeting-info` step and preserve:

- `entrypointId: ringcentral.video.top.meeting-info`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- the step position after `control-map-overview` and before `control-map-network`
- the existing entrypoint cleanup behavior: `cleanup: escape`

`control-map-meeting-info` opens the meeting information popover from the top bar. That popover is explicitly privacy-sensitive because the entrypoint purpose includes meeting title, host, meeting ID, copy link, dial-in info, encryption, and the end-to-end encryption option. The English narration already keeps the right posture: it explains that meeting information answers the identity question and says AiPresenter summarizes it without reading private values aloud.

The primary risk in this localization slice is weakening that boundary. Japanese copy must not turn "summarize without reading private values aloud" into a promise to identify, verify, copy, share, announce, or inspect the private meeting values. The step may open the popover for orientation, but it should treat visible values as sensitive unless the user explicitly asks for exact values and the runtime has an approved observation path.

Neighboring context matters. `control-map-overview` is explain-only and provides the high-level top/center/bottom map. `control-map-network` opens diagnostic health metrics after meeting info. The meeting info step should remain the only place in this demo slice that mentions identity, link, dial-in, and encryption details; it should not borrow network troubleshooting language, invite workflow wording, chat content boundaries, or destructive-control confirmation language except where privacy principles overlap.

## Behavior Boundaries

- Keep this as an open-and-explain step. Do not change the action into copy, share, invite, toggle, click secondary controls, or extract text from the popover.
- Do not click `Copy link`, copy meeting details, open an invite flow, send a chat message, or share a meeting URL as part of this step.
- Do not read, spell, translate, summarize by value, or log the meeting ID, meeting link, dial-in number, access code, password, host name, account name, tenant/company identity, or encryption-specific value.
- It is acceptable to name categories such as meeting details, link, dial-in options, and encryption information. It is not acceptable to reveal the actual values inside those categories.
- Preserve the cleanup contract. The meeting information popover should be closed with Escape before `control-map-network` or any later toolbar control runs.
- Do not imply the assistant verifies the user's encryption posture, compliance status, host privileges, account security, or meeting ownership from the displayed values.
- Do not claim end-to-end encryption is enabled, disabled, recommended, required, or changed unless a separate verified and authorized flow is introduced.
- Do not ask the user to copy or share the link from the narration. If the user asks how to invite people, that belongs to the Invite/Add coworkers Q&A or related entrypoints, still with private-link safeguards.
- Do not collapse this step into the broader `meeting-controls-tour` wording if that loses the control-map framing. The control-map version should explain where identity information lives in the map.
- Do not alter Q&A, question aliases, presenter notes, openSteps, locator coordinates, or adjacent overview/network steps as part of this localization slice.

## Privacy Notes

- Meeting ID, meeting URL, dial-in numbers, access codes, passwords, host names, account or company names, and encryption indicators can all identify a real meeting or organization. Treat them as private by default.
- "Private values" should cover both obvious identifiers and secondary details that can be used to join, enumerate, contact, or profile a meeting.
- The Japanese narration should say the assistant explains the location and purpose, or summarizes the categories, without reading private values aloud.
- If a user explicitly asks for exact values in a real session, the runtime should require visible context verification and the existing privacy policy should govern what can be read or copied. This localization task should not introduce that behavior.
- Test output, snapshots, screenshots, logs, and review notes should avoid real meeting IDs, URLs, dial-in numbers, host/account names, participant names, chat text, transcript text, device labels, or encryption-specific meeting metadata.
- Cleanup failure is a privacy issue. Leaving the meeting info popover open can expose identifiers during later steps or screenshots, so validation should treat failure to close as a blocker.
- Q&A boundaries remain separate: Invite/Add coworkers can explain how to bring people in without reading private invite links; Chat/Participants Q&A can explain locations and counts without reading names or messages. The meeting info step should not expand those behaviors.
- The network step is adjacent but lower privacy risk. It can discuss packet loss, jitter, and latency, but should not inherit or display meeting identity details from an uncleared meeting information popover.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `1/22` to `2/22`, with first remaining missing step moving from `control-map-meeting-info` to `control-map-network`.
- Overall Japanese demo localization totals should advance by exactly one step from the cycle 079 baseline, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-meeting-info`, not to `meeting-controls-tour` -> `explain-meeting-info`, Q&A, entrypoint presenter notes, aliases, overview, or network.
- Assert `control-map-meeting-info.action.entrypointId` remains `ringcentral.video.top.meeting-info`.
- Assert `control-map-meeting-info.action.operation` remains `open`.
- Assert `control-map-meeting-info.narration.placement` remains `during`.
- Assert `control-map-meeting-info.narration.actionOffsetMs` remains `350`.
- Assert the entrypoint `ringcentral.video.top.meeting-info` still has `cleanup: escape` in its open step.
- Assert the Japanese copy names the same safe categories as the English source: meeting identity/details, link, dial-in options, and encryption information.
- Assert the Japanese copy states or clearly preserves the privacy boundary: summarize or explain without reading private values aloud.
- Assert the Japanese copy does not include placeholders or examples that resemble a real meeting ID, meeting URL, phone number, dial-in code, password, host name, email, account name, or encryption token.
- Assert the Japanese copy does not say AiPresenter will copy, share, send, paste, invite, verify, expose, announce, inspect exact values, or change encryption.
- Assert the Japanese copy does not imply private values are safe to read by default or only sensitive in public meetings.
- Assert neighboring steps remain unchanged, especially `control-map-overview`, `control-map-network`, the `meeting-controls-tour` meeting information step, Invite/Add coworkers steps, Q&A privacy answers, and recording/leave boundaries.
- If live or screenshot-based validation is used, sanitize or avoid artifacts that show the meeting information popover values. A cleanup failure or visible private value in committed evidence should fail review.
- If implementation updates CLI localization diagnostics, `--require-complete` for Japanese should still fail after this slice because the remaining `meeting-control-map-demo` steps are still untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-meeting-info`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-080-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map meeting info." Keep privacy-sensitive value reading/copying, invite/share behavior, encryption interpretation, locator changes, cleanup behavior changes, Q&A edits, and broader control-map localization for separate cycles unless explicitly assigned.
