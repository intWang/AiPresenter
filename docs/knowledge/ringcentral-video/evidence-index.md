# RingCentral Video Evidence Index

Date: 2026-05-16

## Purpose

This index connects RingCentral Video package entrypoints to the evidence that supports them. It is a navigation layer, not the source of truth. Update the source documents first, then update this index so future agents can choose the next validation target quickly.

Primary sources:

- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `packages/ringcentral-video.yaml`

## Evidence Levels

| Level | Meaning |
| --- | --- |
| `Accepted` | Automated tests plus dated live/manual acceptance for the current RingCentral build and route. |
| `Observed` | Dated observation exists, but no click/cleanup acceptance exists for the route. |
| `Repo-tested` | Package schema/tests cover the route; no current live acceptance exists. |
| `Backlog` | Product/package knowledge exists, but the route is explain-only or future scope. |
| `Blocked` | Privacy, role, confirmation, missing locator, or unsafe side effect prevents execution. |

## Status Vocabulary Map

Use these terms consistently across this index, the validation checklist, and
acceptance runs:

- `Do Not Execute Yet` is a validation-checklist state, not an evidence level.
- `Backlog` means explain-only or future package scope; it does not permit execution.
- `Blocked` means the route must stay non-executable until privacy, role, confirmation, locator, or side-effect risk is resolved.
- `Observed` requires dated environment context such as build, locale, DPI, window bounds, and scenario.
- `Repo-tested` is local repository evidence only; it must not promote live confidence.
- `Accepted` can only be assigned after `acceptance-runs.md` records a dated live/manual passing acceptance record with cleanup/privacy notes.
- Failed live/manual runs can be recorded in `acceptance-runs.md`, but they must not promote an evidence level to `Accepted`.

Update `acceptance-runs.md` before raising an evidence level.

Current overall state: no executable RingCentral Video route is fully `Accepted` for live operation yet. Cycle 003 produced a read-only empty-room UIA observation for RingCentral Video `26.2.20.355`, `en-US`, 100% DPI, window bounds `(500, 196, 1420, 836)`. Cycle 004 updated `ringcentral.video.main.add-coworkers` to the observed UIA button route but did not perform a live click or modal cleanup acceptance run.

## Accepted Promotion Guard

Every `Accepted` row in the Entry Point Evidence Table must cite `acceptance-runs.md` and a dated manual/live record whose `Outcome` is `pass`.

The same record must identify the entrypoint or route under test and set `Accepted promotion eligible: yes`.

The same record must include promotion rationale, recovery or cleanup notes, and privacy notes.

Do not use failed, blocked, incomplete, skipped, automated-only, dry-run, `doctor`, or read-only observation records as `Accepted` promotion evidence.

## Evidence Records

| Evidence ID | Type | Source | Environment | Scope | Result | Freshness |
| --- | --- | --- | --- | --- | --- | --- |
| `RCV-EVID-001` | Automated baseline | `acceptance-runs.md` Cycle 001 | Local repo test environment | Full unit tests, ruff, mypy, controller dry run | Pass: `362 passed`, ruff pass, mypy pass, controller dry run pass | Repo baseline only; not live RingCentral evidence. |
| `RCV-EVID-002` | Knowledge-doc baseline | `acceptance-runs.md` Cycle 002 | Local repo test environment | Six RingCentral knowledge docs present plus full unit tests | Pass: docs present, `362 passed` | Repo/docs baseline only; no live click acceptance. |
| `RCV-OBS-20260516-01` | Read-only live observation | `observation-log.md` and `acceptance-runs.md` Cycle 003 | RingCentral Video `26.2.20.355`, `en-US`, 100% DPI, bounds `(500, 196, 1420, 836)`, empty-room state | UIA/window metadata labels, state extraction, More order | Pass for read-only observation; no clicks, screenshots, or cleanup validation | Current only for that build/window/DPI/scenario. |
| `RCV-EVID-004` | Package route baseline | `acceptance-runs.md` Cycle 004 | Local repo test environment | `ringcentral.video.main.add-coworkers` route changed to UIA `Add coworkers`; focused/full tests | Pass: focused route test, material package tests, full unit suite | Implemented route only; live modal acceptance missing. |
| `RCV-EVID-010` | Evidence index baseline | This file | Local docs check | Entrypoint coverage, priority queue, source-index registration | Pass when coverage checks report no missing entrypoint or flow IDs | Navigation evidence only; not live RingCentral evidence. |

## Validation Priority Queue

| Priority | Target | Why It Matters | Current Evidence | Next Acceptance Step |
| --- | --- | --- | --- | --- |
| P0 | Controller queued Chat question during `meeting-control-map-demo` | Proves the live interruption UX without high-risk side effects. | Unit tests and runbook checklist; no live manual pass. | Run controller, start the map demo, ask `chat`, confirm queued safe demo and original flow continuity; record in `acceptance-runs.md`. |
| P0 | `ringcentral.video.main.add-coworkers` | Recently changed from coordinate to UIA route; modal cleanup is unvalidated. | Cycle 003 saw `Add coworkers` UIA button; Cycle 004 tests package route. | Click in empty-room meeting, verify Invite/Add coworkers dialog opens, close via modal cleanup, record privacy notes. |
| P1 | Top-bar coordinate routes | Coordinates are the highest layout/DPI risk. | Package routes and locator matrix only. | Validate `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, and `ringcentral.video.top.report-issue` at current bounds/DPI. |
| P1 | Toolbar `More` occurrence order | Many routes depend on occurrence `1`, `2`, or `3`. | Cycle 003 observed empty-room order only. | Recapture in empty-room, one-participant, and two-plus participant states; update locator confidence. |
| P1 | Chat, Participants, Invite, Share cleanup | These are common demo/question targets and privacy-sensitive. | UIA labels observed for toolbar controls; cleanup unaccepted. | Open each panel/modal/picker and verify cleanup without reading private content or clicking final Share. |
| P1 | Notes and transcript route | Known variant uncertainty: direct button vs nested `More` item vs `onconf.controls.NOTES`. | Package route plus locator risk notes. | Record which Notes control exists in the current build and whether side-panel cleanup works. |
| P2 | Background and Settings routes | Settings routes depend on last-opened panel and close behavior. | Package routes and localized Q&A; no live close-path evidence. | Open Background, select Blur only in demo-safe context, verify close/cleanup and restore expectations. |
| P2 | Microphone/camera state labels | State extraction and toggle labels depend on current accessible names. | Cycle 003 saw `Mute` and `Start video`; adapter has related labels. | Capture muted/unmuted and camera on/off variants without exposing room content. |
| P2 | Reactions and Raise hand | Meeting-visible side effects require cleanup confidence. | Package route and privacy policy only. | Open reactions without sending; raise/lower hand in a disposable meeting and record cleanup. |
| P3 | Recording, Leave/end, host/security surfaces | High-impact or role-gated; should remain explain-only. | Official docs and privacy matrix. | Do not execute until confirmation workflow and role-gated policy exist. |

## Entry Point Evidence Table

| Entrypoint | Mode | Evidence Level | Evidence Links | Main Gap |
| --- | --- | --- | --- | --- |
| `ringcentral.develop.video.tab` | Executable profile/app-shell route | `Repo-tested` | Package/profile, manual smoke checklist, locator matrix | Dated UI acceptance for RingCentralDevelop Video tab focus path. |
| `ringcentral.develop.video.start` | Executable profile/app-shell route | `Repo-tested` | Package/profile, manual smoke checklist, locator matrix | Dated UI acceptance for Start button and child meeting launch. |
| `ringcentral.video.overview` | Explain-only | `Backlog` | Package flow/explainer | No locator needed; keep as contextual narration. |
| `ringcentral.video.top.meeting-info` | Executable coordinate route | `Repo-tested` | Locator matrix, privacy matrix | Verify coordinate, panel open, and avoid reading meeting ID/link. |
| `ringcentral.video.top.network-quality` | Executable coordinate route | `Repo-tested` | Locator matrix, privacy matrix | Verify coordinate and decide whether exact diagnostics require consent. |
| `ringcentral.video.top.views` | Executable coordinate route | `Repo-tested` | Locator matrix | Verify coordinate across fullscreen and layout variants. |
| `ringcentral.video.top.report-issue` | Executable coordinate route with modal cleanup | `Repo-tested` | Locator matrix, privacy matrix | Verify dialog close path; do not submit a report. |
| `ringcentral.video.main.add-coworkers` | Executable UIA button route | `Observed` | Observation log, acceptance runs Cycle 003/004, locator matrix, privacy matrix | Live click and modal cleanup acceptance. |
| `ringcentral.video.toolbar.audio` | Executable UIA route | `Observed` | Observation log saw `Mute`; locator matrix; state matrix | Capture muted/unmuted labels and real-meeting confirmation policy. |
| `ringcentral.video.toolbar.audio-menu` | Executable UIA `More` occurrence route | `Observed` | Observation log `More` occurrence 1; locator matrix | Verify current occurrence and audio toast/menu cleanup. |
| `ringcentral.video.toolbar.video` | Executable UIA route | `Observed` | Observation log saw `Start video`; locator matrix; state matrix | Capture camera-on and camera-off labels. |
| `ringcentral.video.toolbar.video-menu` | Executable UIA `More` occurrence route | `Observed` | Observation log `More` occurrence 2; locator matrix | Verify current occurrence and camera menu labels. |
| `ringcentral.video.settings.video` | Executable nested UIA route | `Repo-tested` | Package route, locator matrix | Verify route opens Video settings panel and cleanup closes settings. |
| `ringcentral.video.settings.background` | Executable nested UIA route | `Repo-tested` | Package route, localized Q&A, locator matrix, privacy matrix | Verify route opens Background settings and close path. |
| `ringcentral.video.settings.background.blur` | Executable nested UIA route | `Repo-tested` | Package route, vbg demo, locator matrix, privacy matrix | Verify Blur tile availability and safe selected state. |
| `ringcentral.video.toolbar.share` | Executable UIA route with Escape cleanup | `Observed` | Observation log saw `Share`; locator matrix; privacy matrix | Verify picker opens and cleanup never clicks final Share. |
| `ringcentral.video.toolbar.invite` | Executable UIA route with modal cleanup | `Observed` | Observation log saw `Invite`; locator matrix; privacy matrix | Verify modal close; redact invite links/emails/suggestions. |
| `ringcentral.video.toolbar.participants` | Executable UIA route with toggle cleanup | `Observed` | Observation log saw `Participants`; locator matrix; privacy matrix | Verify panel toggle without reading names or roles. |
| `ringcentral.video.toolbar.chat` | Executable UIA route with toggle cleanup | `Observed` | Observation log saw `Chat`; locator matrix; privacy matrix; controller checklist | Verify panel toggle and queued safe question; do not read messages. |
| `ringcentral.video.toolbar.react` | Executable UIA route with Escape cleanup | `Observed` | Observation log saw `React`; locator matrix; privacy matrix | Verify reaction strip opens without sending a reaction. |
| `ringcentral.video.toolbar.raise-hand` | Executable UIA route with toggle cleanup | `Observed` | Observation log saw `Raise hand`; locator matrix; privacy matrix | Verify raise and lower cleanup in disposable meeting. |
| `ringcentral.video.toolbar.more` | Executable UIA occurrence route | `Observed` | Observation log `More` occurrence 3; locator matrix | Verify overflow More across participant/layout variants. |
| `ringcentral.video.more.recording` | Explain-only | `Blocked` | Official sources, package, privacy matrix | Needs confirmation workflow and host/recording-consent policy before execution. |
| `ringcentral.video.more.notes` | Executable nested UIA route with side-panel cleanup | `Repo-tested` | Package route, locator matrix, state matrix, privacy matrix | Resolve Notes variants and verify cleanup without reading notes/transcript. |
| `ringcentral.video.more.background` | Executable nested UIA route | `Repo-tested` | Package route, locator matrix, privacy matrix | Verify Background route and settings cleanup. |
| `ringcentral.video.more.settings` | Executable nested UIA route | `Repo-tested` | Package route, locator matrix, privacy matrix | Verify last-opened Settings behavior and close path. |
| `ringcentral.video.toolbar.leave` | Explain-only | `Blocked` | Package, privacy matrix, controller checklist | Keep non-executable until explicit confirmation workflow exists. |

## Flow Coverage

| Flow ID | Entrypoints Used | Current Evidence | Weakest Link | Safe To Run Dry | Safe To Run Live | Next Validation |
| --- | --- | --- | --- | --- | --- | --- |
| `vbg-blur-demo` | Background/settings route and `ringcentral.video.settings.background.blur` | Package tests and localized Q&A cover shape; no live settings close-path evidence. | Settings/background cleanup and Blur tile availability. | Yes, dry run and unit tests cover package references. | Not fully accepted; only run in a disposable meeting until settings cleanup is recorded. | Validate Background route, Blur selection, and cleanup with bounds/DPI recorded. |
| `meeting-basics-demo` | Core toolbar controls, audio/video, invite, participants, chat, share/leave explain path | Package and unit tests cover flow references; Cycle 003 observed common toolbar labels. | Cleanup for Invite/Participants/Chat/Share and real-meeting side effects. | Yes. | Not fully accepted; use only with cautious manual supervision. | Validate panel/modal/picker open and cleanup without reading private content. |
| `meeting-controls-tour` | Broad toolbar/top-bar/more/settings tour | Package and unit tests cover flow references; most routes lack live click acceptance. | Top-bar coordinates, More occurrence order, Notes/settings variants. | Yes. | Not accepted for unattended live operation. | Split into smaller live acceptance runs by surface before treating the full tour as accepted. |
| `meeting-control-map-demo` | Overview, top bar, toolbar, More, settings, notes, and explain-only risky endpoints | Controller/runbook uses this as primary acceptance flow; tests cover controller behavior. | Queued Chat question and multiple unaccepted locator/cleanup routes. | Yes. | Not fully accepted; best current live test is supervised controller/queued Chat acceptance. | Run controller, queue `chat` during this flow, then separately validate high-risk route groups. |

## Runbook Mapping

| Runbook Check ID | Runbook Section | Check Summary | Evidence IDs | Last Result | Next Run Notes |
| --- | --- | --- | --- | --- | --- |
| `RUN-SMOKE-001` | Smoke Checklist | Dry-run `run`, `doctor`, `demo`, and `controller`; verify profile/package/flow load. | `RCV-EVID-001`, `RCV-EVID-002` | Automated baselines passed in earlier cycles. | Re-run after packaging or profile changes. |
| `RUN-SMOKE-002` | Smoke Checklist | Open RingCentralDevelop, click Video tab/Start, bind `RingCentralVideoClass`, detect joined state. | `RCV-OBS-20260516-01` partially covers meeting window; app-shell click path not accepted. | Read-only meeting window observation passed; app shell route still needs dated UI acceptance. | Record build, bounds, DPI, and app-shell labels. |
| `RUN-AUDIO-001` | Real Audio And OpenAI Checklist | Verify OpenAI narration and virtual microphone output. | None yet in current knowledge package. | Not run. | Record device names and avoid storing private meeting audio content. |
| `RUN-CTRL-001` | Controller Acceptance Checklist | Target section, operator summary, Start/Pause/Resume/End, disabled controls. | Unit tests and Cycle 005 docs; no manual live record. | Repo-tested only. | Run with current controller UI and append dated result. |
| `RUN-CTRL-002` | Controller Acceptance Checklist | Ask `chat` while `meeting-control-map-demo` is running and verify queued safe demo. | Unit tests, runbook checklist, `RCV-EVID-010` priority queue. | Not live accepted. | Highest-value controller acceptance target. |
| `RUN-CTRL-003` | Controller Acceptance Checklist | Chinese Chat/Leave questions and tone selection. | Cycle 006 and Cycle 009 tests/docs. | Repo-tested only. | Record manual result without reading private chat or clicking Leave. |
| `RUN-APP-001` | Controller Acceptance Checklist | Running desktop app refresh/select/scan and safe/risky generated package questions. | Controller/session tests only. | Repo-tested only. | Keep separate from RingCentral curated package acceptance. |

## Surface Evidence Notes

### Empty-Room Meeting Canvas

- Evidence: Cycle 003 UIA observation saw `You're the first one here` and `Add coworkers`.
- Package entrypoint: `ringcentral.video.main.add-coworkers`.
- Privacy: Invite/Add coworkers may expose names, emails, and meeting links.
- Next evidence: validate live modal open/close without reading invite suggestions or links.

### Meeting Toolbar

- Evidence: Cycle 003 UIA observation saw `Mute`, `Start video`, `Share`, `Invite`, `Participants`, `Chat`, `React`, `Raise hand`, `More`, and `Leave`.
- Package entrypoints: `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.video`, `ringcentral.video.toolbar.share`, `ringcentral.video.toolbar.invite`, `ringcentral.video.toolbar.participants`, `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.react`, `ringcentral.video.toolbar.raise-hand`, `ringcentral.video.toolbar.more`, `ringcentral.video.toolbar.leave`.
- Privacy: chat, participants, invite, share, reactions, raise hand, and leave/end have different side-effect and privacy rules in `privacy-matrix.md`.
- Next evidence: prioritize Chat queued question and panel cleanup, then Participants/Invite/Share cleanup.

### Toolbar More Menus

- Evidence: Cycle 003 observed three visible `More` controls in empty-room state: audio menu, video menu, and overflow More.
- Package entrypoints: `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video-menu`, `ringcentral.video.toolbar.more`, `ringcentral.video.more.notes`, `ringcentral.video.more.background`, `ringcentral.video.more.settings`.
- Main risk: occurrence order may change with participant count, layout, device state, or locale.
- Next evidence: recapture More order in at least empty-room and two-plus participant states.

### Top Bar

- Evidence: repo package and locator matrix only.
- Package entrypoints: `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, `ringcentral.video.top.report-issue`.
- Main risk: coordinate routes depend on window bounds and DPI.
- Privacy: meeting info can expose IDs/links; report issue can expose account/environment data.
- Next evidence: validate coordinates with bounds/DPI recorded in the acceptance run.

### Settings And Background

- Evidence: repo package, localized Q&A, and demo flow tests.
- Package entrypoints: `ringcentral.video.settings.video`, `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.background`, `ringcentral.video.more.settings`.
- Main risk: last-opened settings panel and close behavior can differ by route.
- Privacy: background can reveal room/custom images; settings can reveal devices and account preferences.
- Next evidence: validate Background route, Blur tile availability, and cleanup path in a disposable meeting.

### Notes, Transcript, Recording, Leave

- Evidence: package and policy docs only for execution-sensitive paths.
- Package entrypoints: `ringcentral.video.more.notes`, `ringcentral.video.more.recording`, `ringcentral.video.toolbar.leave`.
- Main risk: notes/transcripts/recording/leave have high privacy or meeting-impact side effects.
- Docs-only private-surface examples do not upgrade `Repo-tested`, `Observed`, `Blocked`, or `Accepted` evidence states.
- Next evidence: keep recording and leave explain-only; validate Notes panel shape without starting notes/transcription or reading content.

## Risk Queue

| Risk ID | Affected IDs | Evidence Gap | Privacy Constraint | Priority | Suggested Validation |
| --- | --- | --- | --- | --- | --- |
| `RISK-RCV-001` | `ringcentral.video.main.add-coworkers` | UIA route observed and implemented, but no live click/modal cleanup evidence. | Invite links, emails, and suggestions must not be read or captured. | P0 | Disposable empty-room click/cleanup run; record modal open and close only. |
| `RISK-RCV-002` | `ringcentral.video.top.meeting-info`, `ringcentral.video.top.network-quality`, `ringcentral.video.top.views`, `ringcentral.video.top.report-issue` | Coordinate routes have no current bounds/DPI acceptance. | Meeting info/report issue can reveal meeting or account data. | P1 | Validate with window bounds/DPI recorded and avoid reading exact sensitive values. |
| `RISK-RCV-003` | `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video-menu`, `ringcentral.video.toolbar.more`, `ringcentral.video.more.notes`, `ringcentral.video.more.background`, `ringcentral.video.more.settings` | `More` occurrence order observed only in one empty-room state. | More menu can expose recording/settings/notes surfaces. | P1 | Recapture UIA order in empty-room, one-participant, two-plus participant, and narrow/fullscreen states. |
| `RISK-RCV-004` | `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.participants`, `ringcentral.video.toolbar.invite`, `ringcentral.video.toolbar.share` | Common panel/modal/picker cleanup is not accepted. | Do not read chat, names, invite links, or shared content. | P1 | Open and close each surface with sanitized evidence only. |
| `RISK-RCV-005` | `ringcentral.video.more.notes` | Notes control variant and cleanup are unresolved. | Do not start notes/transcription or read content. | P1 | Record direct-vs-nested Notes labels and side-panel close path. |
| `RISK-RCV-006` | `ringcentral.video.settings.background`, `ringcentral.video.settings.background.blur`, `ringcentral.video.more.background`, `ringcentral.video.more.settings` | Settings close behavior and last-opened panel are not accepted. | Settings/background can expose devices, room privacy, custom images, account preferences. | P2 | Validate routes in a disposable meeting and record cleanup/restoration behavior. |
| `RISK-RCV-007` | `ringcentral.video.more.recording`, `ringcentral.video.toolbar.leave` | High-impact controls are explain-only and blocked. | Recording and leave/end always require confirmation and role/safety policy. | P3 | Do not execute; design confirmation workflow before any route change. |

## Acceptance Run Requirements For New Evidence

Every new live/manual acceptance record should include:

- RingCentral app/build, channel, locale, DPI/display scale, monitor setup, and window bounds.
- Meeting role, scenario, participant count, and whether it is a disposable meeting.
- The package entrypoint IDs tested.
- Whether the route was read-only, clicked, toggled, or explain-only.
- Cleanup path and whether cleanup restored the original state.
- Privacy notes describing what was intentionally not read or captured.
- Locator updates needed, especially for coordinate routes and `More` occurrence routes.

Use `acceptance-runs.md` for the dated record. Then update `locator-matrix.md`, `state-matrix.md`, and this index if confidence changes.

## Maintenance Checklist

- [ ] When adding a package entrypoint, add a row to the entry point evidence table.
- [ ] When planning a manual route run, start from `validation-checklist-index.md` and record the dated result in `acceptance-runs.md` before changing evidence levels.
- [ ] When a live observation changes locator confidence, update both `locator-matrix.md` and this index.
- [ ] When a manual acceptance run passes or fails, add the dated run to `acceptance-runs.md` and update the validation priority queue.
- [ ] When a privacy policy changes, update `privacy-matrix.md` before changing any executable route.
- [ ] Keep checklist items separate from dated acceptance evidence.
