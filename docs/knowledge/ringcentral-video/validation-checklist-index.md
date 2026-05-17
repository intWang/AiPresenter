# RingCentral Video Validation Checklist Index

Date: 2026-05-16

## Purpose

This checklist turns known RingCentral Video evidence gaps into safe manual validation work. It is procedure, not proof. Dated proof belongs in `acceptance-runs.md`; runbook checkboxes are not acceptance evidence.

## Update Rule

1. Append a dated run to `acceptance-runs.md`.
2. Record build, locale, DPI, window bounds, role, scenario, participant count, action, cleanup, pass/fail, failures, recovery, privacy notes, and locator updates.
3. Update `locator-matrix.md`, `state-matrix.md`, `privacy-matrix.md`, and `evidence-index.md` only after the run is recorded.
4. Do not promote a route to `Accepted` from automated tests, dry runs, `doctor`, or read-only UIA observation alone.
5. Treat private-surface prompt examples as policy guidance only; they do not prove route acceptance or permit private-content capture during validation.

## Priority Checklist

| Priority | Target ID | Route Or Group | Entrypoints | Current State | Validate | Cleanup | Privacy Boundary | Record Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | rcv-add-coworkers-modal | Add coworkers modal | `ringcentral.video.main.add-coworkers` | Observed UIA button, package route repo-tested, no live click acceptance | In a disposable empty-room meeting, click Add coworkers, confirm Invite/Add coworkers dialog opens, then close it | Modal close by X or Cancel; confirm toolbar is usable again | Do not read or store invite links, emails, names, or suggestions | `acceptance-runs.md`, then `evidence-index.md` and `locator-matrix.md` |
| P0 | rcv-controller-chat-question | Controller queued Chat question | `ringcentral.video.toolbar.chat`, `meeting-control-map-demo` | Unit-tested, not manually accepted | Start the map demo, ask `chat`, confirm queued safe demo and original flow continuity | Toggle or close Chat panel | Do not read chat message text | `acceptance-runs.md`, then controller/runbook notes |
| P1 | rcv-app-shell-launch | App shell launch | `ringcentral.develop.video.tab`, `ringcentral.develop.video.start` | Repo-tested only | Focus RingCentralDevelop, open Video tab, click Start, bind RingCentralVideo window | Leave meeting only if the disposable session requires it | Do not expose account or meeting identifiers | `acceptance-runs.md` |
| P1 | rcv-top-bar-routes | Top-bar coordinate routes | `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, `ringcentral.video.top.report-issue` | Repo-tested, coordinate drift risk | Open each route at recorded bounds/DPI and confirm expected panel/dialog/menu | Escape for popovers/menus; modal X for Report issue | Do not read meeting IDs, links, dial-in details, account data, or report contents | `acceptance-runs.md`, then `locator-matrix.md` |
| P1 | rcv-toolbar-panels | Common toolbar panels and pickers | `ringcentral.video.toolbar.invite`, `ringcentral.video.toolbar.participants`, `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.share` | Observed labels, cleanup unaccepted | Open each surface and verify it can close without state changes | Modal, toggle, or Escape according to route | Do not read names, roles, chat text, invite links, suggestions, or shared content | `acceptance-runs.md`, then `privacy-matrix.md` if policy changes |
| P1 | rcv-more-menu-variants | More occurrence routes | `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video-menu`, `ringcentral.video.toolbar.more` | Observed only in empty-room en-US 100% DPI state | Recapture More order in empty-room, one-participant, two-plus participant, narrow, and fullscreen variants | Escape after each menu | Do not infer hidden recording/settings state | `observation-log.md`, `acceptance-runs.md`, then `locator-matrix.md` |
| P1 | rcv-notes-transcript | Notes and transcript | `ringcentral.video.more.notes` | Repo-tested, route variant unresolved | Open Notes from the current build route and identify direct vs nested label | Side-panel close or toggle; do not start notes | Do not read notes, transcript, or recording prompts beyond sanitized labels | `acceptance-runs.md`, then `state-matrix.md` |
| P2 | rcv-media-controls | Media controls | `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.video` | Observed labels, variant states missing | Capture Mute/Unmute and Start video/Stop video variants in a disposable meeting | Restore original mic/camera state | Avoid exposing room video or private audio device details | `acceptance-runs.md`, then `state-matrix.md` |
| P2 | rcv-reactions-raise-hand | Reactions and raise hand | `ringcentral.video.toolbar.react`, `ringcentral.video.toolbar.raise-hand` | Observed labels, side effects unaccepted | Open reactions without sending; raise and lower hand in disposable meeting | Escape reactions; lower hand after toggle | Reactions and hand state are visible meeting signals | `acceptance-runs.md` |
| P2 | rcv-settings-background | Settings and background | `ringcentral.video.settings.video`, `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.background`, `ringcentral.video.more.settings` | Repo-tested, close behavior unaccepted | Open each settings route, confirm panel, optionally select Blur only in demo-safe context | Settings close by X; verify return to meeting | Do not expose device names, room imagery, custom assets, or account preferences | `acceptance-runs.md`, then `locator-matrix.md` |
| P3 | rcv-overview-context | Overview and explain-only context | `ringcentral.video.overview` | Backlog/explain-only | Confirm narration context still matches current meeting canvas | No UI cleanup | Do not infer participant identities or private state | `acceptance-runs.md` if manually reviewed |

## Do Not Execute Yet

| Route | Target ID | Entrypoint | Reason |
| --- | --- | --- | --- |
| Recording | rcv-recording | `ringcentral.video.more.recording` | Recording changes meeting state and may require participant consent. Keep explain-only until confirmation and role policy exist. |
| Leave or end meeting | rcv-leave-end-meeting | `ringcentral.video.toolbar.leave` | Leaving or ending a meeting is destructive. Keep explain-only until a tested confirmation workflow exists. |

## Evidence Upgrade Rules

- `Accepted` requires a dated passing manual/live record in `acceptance-runs.md`, with cleanup/privacy notes complete.
- `Observed` can come from sanitized UIA/window metadata, but does not prove click or cleanup.
- `Repo-tested` means package shape or runtime code was tested locally, not that RingCentral accepted the route live.
- `Blocked` means privacy, role, confirmation, locator, or side-effect risk prevents execution.

## Post-Run Documentation Checklist

- Update `acceptance-runs.md` first.
- Update `locator-matrix.md` when locator confidence or cleanup changes.
- Update `state-matrix.md` when UI labels or state extraction changes.
- Update `privacy-matrix.md` before expanding any sensitive route.
- Update `evidence-index.md` last so it reflects recorded evidence instead of intention.
