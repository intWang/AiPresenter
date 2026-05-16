# RingCentral Video State Matrix

Date: 2026-05-16

## Purpose

This matrix shows which RingCentral Video states are represented in AiPresenter and which states still need observation or tests. It keeps state recognition separate from feature knowledge and locator confidence.

## State Coverage

| State | Current Source | Current Handling | Confidence | Gap |
| --- | --- | --- | --- | --- |
| RingCentralDevelop Video tab | package/profile | Focus desktop app and click Video tab before Start. | Medium repo confidence | Needs dated UI acceptance for app shell. |
| Meeting process launched | profile/runbook | Start creates/binds `RingCentralVideo` with class `RingCentralVideoClass`. | Medium repo confidence | Needs build/version record. |
| In-meeting joined | adapter | Joined only when RingCentral process/class plus in-meeting evidence or first-one-here signal. Cycle 003 empty-room UIA snapshot extracted `meeting_joined=True` with confidence `0.85`. | Medium repo confidence | Needs snapshots for one-person/two-plus variants. |
| Empty room / first one here | adapter/package | `You're the first one here` can support joined state; Add coworkers may be present. Cycle 003 observed both labels in RingCentral Video `26.2.20.355`. | Medium repo confidence | Need participant-count variants and route update for Add coworkers. |
| Two-plus participants | adapter/adaptive demo | Participant count can skip Add coworkers and prefer Invite. | Medium repo confidence | Need participant tiles/badge variants. |
| Mic muted/unmuted | adapter/package | `Unmute microphone` means muted; `Mute microphone` means unmuted. | Medium repo confidence | Need current UIA labels and localized labels. |
| Camera off/on | adapter/package | `Start video` means off; `Stop video` means on. Cycle 003 empty-room UIA snapshot extracted `camera_off=True`. | Medium repo confidence | Need camera-on and localized labels. |
| Permission dialog | adapter | Recognizes permission required labels. | Low repo confidence | Needs prompt types and safe recovery. |
| Waiting room / waiting for host | adapter | Recognizes waiting room/host labels. | Low repo confidence | Needs prejoin snapshots and UX policy. |
| Connection warning | adapter | Recognizes reconnecting/unstable labels. | Low repo confidence | Needs network quality and CPU usage surface mapping. |
| Invite modal | package/runbook | Opens Invite; private links should not be read. | Medium repo confidence | Needs close-path evidence. |
| Participants side panel | package/runbook | Toggle Participants; avoid naming people unless asked and verified. | Medium repo confidence | Needs host vs attendee controls. |
| Chat side panel | package/runbook | Toggle Chat; do not read private chat by default. | Medium repo confidence | Needs public/private tab observation. |
| Share picker | package/runbook | Open Share only; do not click final Share. | Medium repo confidence | Needs picker labels, active sharing state, stop sharing. |
| Reactions strip | package | Open reactions; no reaction should be sent by default. | Medium repo confidence | Needs close path and reaction labels. |
| Raised hand | package | Toggle and lower after demonstration. | Medium repo confidence | Needs host/attendee variants. |
| Notes and transcript panel | package/handoff | Route via More; variant uncertainty noted. | Low repo confidence | Resolve direct toolbar vs nested More variants. |
| Background/settings dialog | package | Opens settings panels and Blur. | Low repo confidence | Need last-opened Settings panel behavior. |
| Recording available | official/package | Explain-only in package. | Explain only | Need confirmation workflow and host-role observation before action. |
| Leave meeting | package | Explain-only in package. | Explain only | Keep non-executable. |

## Missing Or Weak States

- Audio join prompt.
- Camera preview before meeting.
- Host not started.
- Meeting ended.
- Left meeting.
- Recording consent prompt.
- Recording active.
- Sharing active.
- Stop sharing.
- Whiteboard active.
- Captions enabled.
- Live transcription active.
- Breakout room active.
- Waiting room management.
- Security settings panel.
- Moderator assignment.
- Device warning toast.
- CPU usage detail.
- Post-meeting recordings, summaries, transcripts, or insights.

## State Policy

- State extraction should stay conservative. Unknown states should reduce confidence rather than inventing meeting context.
- Prejoin and permission states should block normal in-meeting narration until resolved or explicitly explained.
- Privacy-sensitive active states such as chat, sharing, recording, transcription, and participant panels must not cause content reading by default.
- State fixtures should be sanitized before committing.
