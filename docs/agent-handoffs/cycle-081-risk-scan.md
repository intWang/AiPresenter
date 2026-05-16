# Cycle 081 Risk Scan: control-map-network JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-network`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `control-map-network` step and preserve:

- `entrypointId: ringcentral.video.top.network-quality`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- the step position after `control-map-meeting-info` and before `control-map-views`
- the existing entrypoint cleanup behavior: `cleanup: escape`

`control-map-network` opens the top-bar Network quality popover. The entrypoint purpose is diagnostic: it shows network quality for sharing, video, and audio, including packet loss, jitter, and latency. The adjacent `control-map-meeting-info` step is identity/privacy-sensitive and must close before this step. The adjacent `control-map-views` step is a local layout control. `control-map-report` is a separate support escalation path and opens a blocking dialog.

The main risk in this localization slice is overstating what the diagnostic popover can prove. Japanese copy should explain that Network quality is where the user can check meeting health indicators when audio, video, or sharing feels unstable. It must not claim AiPresenter has diagnosed the cause, confirmed the user's network is bad, identified a provider or route issue, or fixed anything. It should keep the same control-map framing as the English source while softening causal language from "are coming from" into "may help check whether packet loss, jitter, or latency is related."

## Behavior Boundaries

- Keep this as an open-and-explain step. Do not change the action into repair, settings changes, issue submission, export, copy, or secondary clicks inside the popover.
- Do not say AiPresenter can fix packet loss, jitter, latency, Wi-Fi, VPN, firewall, bandwidth, ISP, provider, device, or server problems from this popover.
- Do not diagnose a root cause without observed values. Safe language: "check indicators," "look for possible packet loss, jitter, or latency," or "use this for troubleshooting context."
- Do not promise certainty such as "this tells you exactly why the call is choppy" or "this proves the network is the problem."
- Do not provide medical-style or support-style determinations such as "your connection is unhealthy," "the provider is at fault," "RingCentral is down," or "the issue is on your side" unless a separate verified support workflow exists.
- Do not click `Report issue` or choose a report category from this step. Reporting belongs to `control-map-report` and should remain an escalation path, not an automatic continuation.
- Do not introduce remediation instructions that change meeting state or system state, such as disabling video, stopping sharing, switching networks, leaving the meeting, restarting the app, changing devices, or opening system settings.
- Preserve cleanup. The Network quality popover should be closed with Escape before `control-map-views` or any later top-bar/toolbar control runs.
- Do not alter the neighboring meeting-info privacy boundary. The network step should not repeat or expose meeting ID, links, dial-in information, host, encryption details, or any private value from the previous popover.
- Do not alter Q&A, question aliases, presenter notes, openSteps, locator coordinates, report-issue behavior, or view-layout behavior as part of this localization slice.

## Privacy Notes

- Packet loss, jitter, latency, media direction, region, transport, IP address, server, provider, device labels, network names, VPN status, account or tenant names, and participant/media identifiers can reveal environment or infrastructure details. Treat exact values and labels as sensitive by default.
- The narration may name metric categories: packet loss, jitter, latency, audio, video, and sharing. It should not read exact metric values aloud unless the user explicitly asks and the runtime has verified visible context.
- Avoid adding Japanese examples with concrete numbers such as percentages, milliseconds, IP addresses, hostnames, carrier names, Wi-Fi names, domains, or meeting/server locations.
- Avoid phrasing that implies AiPresenter stores, logs, uploads, or shares network diagnostics.
- Test output, snapshots, screenshots, logs, and review notes should not include real packet loss percentages, latency values, jitter values, IP addresses, network names, providers, device labels, meeting IDs, links, participant names, or tenant/account identifiers.
- Cleanup failure is a privacy issue. Leaving the Network quality popover open can expose live diagnostics during later screenshots or steps.
- Support/report issue boundaries remain separate. The Network quality step can help locate diagnostics, but it should not auto-file an issue or imply support will receive diagnostics unless the user explicitly enters that workflow.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `2/22` to `3/22`, with first remaining missing step moving from `control-map-network` to `control-map-views`.
- Overall Japanese demo localization totals should advance by exactly one step from the cycle 080 baseline, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-network`, not to `meeting-controls-tour` -> `explain-network-quality`, Q&A, entrypoint presenter notes, aliases, meeting info, views, or report issue.
- Assert `control-map-network.action.entrypointId` remains `ringcentral.video.top.network-quality`.
- Assert `control-map-network.action.operation` remains `open`.
- Assert `control-map-network.narration.placement` remains `during`.
- Assert `control-map-network.narration.actionOffsetMs` remains `350`.
- Assert the entrypoint `ringcentral.video.top.network-quality` still has `cleanup: escape` in its open step.
- Assert the Japanese copy preserves safe metric categories: audio, video, or sharing health; packet loss; jitter; latency.
- Assert the Japanese copy frames the popover as a place to check or troubleshoot indicators, not as proof of root cause.
- Assert the Japanese copy does not promise repair, optimization, escalation, report filing, provider diagnosis, system diagnosis, or guaranteed cause identification.
- Assert the Japanese copy does not include concrete sample values, IP addresses, network/provider names, server regions, hostnames, domains, account names, participant names, device labels, meeting IDs, meeting links, or dial-in details.
- Assert the Japanese copy does not say AiPresenter will read exact diagnostics aloud by default.
- Assert neighboring steps remain unchanged, especially `control-map-meeting-info`, `control-map-views`, `control-map-report`, the `meeting-controls-tour` network step, and the Q&A answer for choppy audio/video.
- If live or screenshot-based validation is used, sanitize or avoid artifacts that show exact network diagnostics. A cleanup failure or visible real diagnostic value in committed evidence should fail review.
- If implementation updates CLI localization diagnostics, `--require-complete` for Japanese should still fail after this slice because the remaining `meeting-control-map-demo` steps are still untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-network`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-081-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map network quality." Keep exact diagnostic value reading, provider/IP/environment disclosure, report submission, remediation behavior, locator changes, cleanup behavior changes, Q&A edits, and broader control-map localization for separate cycles unless explicitly assigned.
