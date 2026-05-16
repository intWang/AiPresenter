# RingCentral Video Privacy And Safety Matrix

Date: 2026-05-16

## Default Policy

AiPresenter may explain controls and visible UI structure. It must not read, infer, or act on private meeting content unless the user explicitly asks and the content is verified from an approved observation source.

## Operation Modes

- `Scripted demo`: an action explicitly encoded in a reviewed demo flow, with cleanup and recovery notes. It may operate low-risk controls only when the flow's purpose requires it.
- `Explain-only`: the presenter describes the control or surface and does not click, toggle, submit, send, start, stop, or read sensitive values.
- `Real-meeting confirmed action`: the user gives explicit instruction for the current meeting context. This still requires a safe locator, clear side effects, and a recovery path.

When a control is safe in a scripted demo, that does not automatically make it safe in a real meeting. Real meetings add participant impact, privacy impact, and meeting-state consequences.

## Surface Matrix

| Surface | Sensitive Data | Allowed By Default | Disallowed By Default | Confirmation Required |
| --- | --- | --- | --- | --- |
| Meeting information | Meeting ID, link, dial-in, host identity, encryption details | Explain where details live and why they matter. | Reading IDs, links, dial-in numbers aloud. | Yes, before reading exact values or copying details. |
| Network quality | Packet loss, jitter, latency, CPU or connection health | Summarize that the panel is for troubleshooting. | Overstating root cause without observed values. | No for summary; yes for exact diagnostics if sensitive. |
| Invite/Add coworkers | Names, emails, meeting invite link | Explain invite workflow. | Sending invites, reading private suggestions/links. | Yes before inviting or reading/copying private details. |
| Participants | Names, roles, attendee count, controls | Mention verified count or panel purpose. | Reading participant names/roles by default. | Yes before identifying people or host controls. |
| Chat | Public/private messages | Explain chat purpose and tabs. | Reading message contents by default. | Yes before reading visible chat text. |
| Screen share | Shared applications, documents, desktop content | Explain share picker and safety boundary. | Describing shared content unless approved and verified. | Yes before final Share or content description. |
| Microphone | Local audio state | Explain mute/unmute state and recovery path. | Toggling mute in real meetings without user intent. | Yes for real meetings; scripted demos may operate only if the flow explicitly owns cleanup and side effects. |
| Camera | Local video state, room/background | Explain camera and video menu. | Turning camera on/off in real meetings without user intent. | Yes for real meetings; scripted demos may operate only if the flow explicitly owns cleanup and side effects. |
| Background | Room privacy, custom images | Explain blur/background choices; select blur in approved demo flow. | Uploading or exposing private images. | Yes before custom upload or non-demo changes. |
| Reactions | Meeting-visible feedback | Explain reaction strip. | Sending a reaction unless the flow intentionally sends and records cleanup. | Yes before sending visible feedback in a real meeting. |
| Raise hand | Meeting-visible attention signal | Explain raise/lower behavior. | Leaving hand raised unintentionally. | Yes in real meetings; scripted demo must lower it and verify cleanup. |
| Notes and transcript | Meeting notes, transcription, recording linkage | Explain panel and start controls. | Starting notes/transcript or reading content. | Yes before starting or reading. |
| Recording | Audio/video recording, consent implications | Explain location and policy. | Starting/stopping recording, reading recording contents. | Always. |
| Settings | Devices, preferences, account/environment details | Explain settings categories. | Changing persistent preferences without instruction. | Yes before durable changes. |
| Security/waiting room | Lock, admit/remove, permissions | Explain host-only controls. | Locking meeting, removing/admitting people, changing security. | Always. |
| Leave/end | Meeting presence, possible end for all | Explain exit path. | Clicking Leave/End automatically. | Always. |
| Post-meeting artifacts | Recordings, summaries, transcripts, insights | Explain where artifacts may live. | Reading artifact content or making availability claims not verified. | Yes before reading content. |

## Safety In Runtime

- `runtime.questions` can match risky intent, but `can_operate` must stay false for risky controls.
- `PackageActionExecutor` should only execute package `openSteps`; explain-only entrypoints have no executable steps.
- Controller queued interrupts must respect the same `can_operate` gate as idle demos.
- Future semantic matching must identify intent only; operation permission remains a separate policy decision.

## Observation Capture Policy

- Prefer `WINDOWS_UI_AUTOMATION` and `WINDOW_METADATA` for first-pass live evidence.
- Request screenshots only when there is a clear verification need and a privacy review path.
- Record product-control labels and generic state labels; redact or omit chat messages, participant names, invite links, meeting IDs, emails, and account/profile content.
- If a raw UIA dump contains unrelated browser/profile labels, summarize only the allowlisted RingCentral controls needed for locator or state evidence.

## Open Policy Questions

- Should the product ever add a confirmation workflow for risky actions, or keep them explain-only for this phase?
- Should host/moderator controls be represented as separate role-gated entrypoints?
- Should exact network diagnostics be treated as low sensitivity or meeting telemetry requiring user consent?
