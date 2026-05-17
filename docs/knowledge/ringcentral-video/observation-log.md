# RingCentral Video Observation Log

Date: 2026-05-16

## Purpose

This is the append-only place to record what AiPresenter has actually observed about RingCentral Video. Do not treat official documentation as locator evidence. A live observation should include enough environment detail for another agent to reproduce or challenge it.

## Observation Template

```markdown
## YYYY-MM-DD HH:mm Local - Short Title

- Observer:
- RingCentral app/build:
- Channel:
- OS/version:
- Locale:
- DPI/display scale:
- Monitor setup:
- Window title/class/process:
- Window bounds:
- Meeting scenario:
- Role:
- Participant count:
- Surface:
- Evidence:
- Controls or labels observed:
- Locator confidence:
- Cleanup path:
- Privacy/safety notes:
- Follow-up:
```

## Seed Observations From Repository Evidence

### 2026-05-17 - Current Package Shape

- Source: `packages/ringcentral-video.yaml`
- Evidence type: repository package, not live app observation.
- Known shape: 27 operation entrypoints, 4 demo flows, 51 demo steps, 21 explainers, 16 Q&A items, 222 Q&A question prompts, 171 package-owned question aliases, and manual controls for `say`, `skip`, and `focus`.
- Alias shape: English aliases cover 4/27 entrypoints with 17 aliases, Chinese aliases cover 15/27 entrypoints with 49 aliases, Japanese aliases cover 13/27 entrypoints with 34 aliases, Spanish aliases cover 26/27 entrypoints with 69 aliases, and French aliases cover 1/27 entrypoints with 2 aliases.
- French seed note: French package-local coverage is 3/51 demo steps and 1/16 Q&A questions/answers; it is not runtime `--language fr` support or live acceptance.
- Change note: English Chat panel aliases now include `open chat`, `show chat`, `where is chat`, and `chat button` so Presenter-meta-prefixed Chat location requests remain explicit RingCentralVideo intents.
- Limit: this does not prove the local RingCentral build still exposes the same UIA labels, menu order, or coordinates.

### 2026-05-16 - Current Package Shape

- Source: `packages/ringcentral-video.yaml`
- Evidence type: repository package, not live app observation.
- Known shape: 27 operation entrypoints, 4 demo flows, 51 demo steps, 21 explainers, 12 Q&A items, 156 package-owned question aliases, and manual controls for `say`, `skip`, and `focus`.
- Strong surfaces: meeting top bar, meeting toolbar, audio/video readiness, invite, participants, chat, reactions, notes, background, settings, recording explain-only, leave explain-only.
- Limit: this does not prove the local RingCentral build still exposes the same UIA labels, menu order, or coordinates.

### 2026-05-16 - Adapter State Extraction

- Source: `src/ai_presenter/adapters/ringcentral.py`
- Evidence type: repository code and tests, not live app observation.
- Recognized window: process `RingCentralVideo`, class `RingCentralVideoClass`.
- Recognized mic labels: `Unmute microphone`, `Mute microphone`.
- Recognized camera labels: `Start video`, `Stop video`.
- Recognized participant labels: `Participants N`, `Participants (N)`, `Participants: N`.
- Recognized dialogs: `permission required`, `permissions required`, `waiting room`, `waiting for host`.
- Recognized connection warning: `reconnecting`, `your connection is unstable`.
- Limit: English UI labels only; locale variants are not represented.

### 2026-05-16 - Manual Acceptance Requirements

- Source: `docs/runbooks/ringcentral-manual-acceptance.md`
- Evidence type: checklist.
- Important prerequisite: `DisableAffinityMask=true` in the RingCentralVideo executable directory `config.ini`.
- Smoke path: run, doctor, demo, controller dry-run; open RingCentralDevelop; bind meeting window; verify joined state and event narration.
- Controller path: target selection, questions, language/tone, running-app scan, queued safe question, Chinese question input.
- Limit: a checklist is not a dated live pass record until filled into `acceptance-runs.md`.

## Live Observations

## 2026-05-16 01:15 +08:00 - Empty-Room UIA Snapshot

- Observer: main session.
- RingCentral app/build: RingCentral Video `26.2.20.355`.
- Channel: RingCentralDevelop embedded RingCentralVideo process.
- OS/version: Microsoft Windows 11 Pro `10.0.26200` build `26200`, 64-bit.
- Locale: `en-US`.
- DPI/display scale: window DPI `96`, scale `100%`.
- Monitor setup: 1920x1080 monitor reported by Windows desktop APIs.
- Window title/class/process: `RingCentral Video` / `RingCentralVideoClass` / `RingCentralVideo` pid `21160`.
- Window bounds: `(500, 196, 1420, 836)`.
- Meeting scenario: empty meeting room with `You're the first one here` callout.
- Role: not determined from UIA labels.
- Participant count: not parsed by adapter in this snapshot.
- Surface: Windows UI Automation and window metadata only; no screenshot.
- Evidence: `WindowsDesktopDriver.capture(..., WINDOWS_UI_AUTOMATION, WINDOW_METADATA)` plus sanitized key-control scan.
- Adapter state: `meeting_joined=True`, `mic_muted=None`, `camera_off=True`, `participant_count=None`, `active_dialog=None`, `connection_warning=None`, `confidence=0.85`.
- Controls or labels observed:
  - `You're the first one here` text at `(984, 448, 1374, 488)`.
  - `Add coworkers` button at `(1029, 493, 1329, 541)`.
  - Toolbar buttons: `Mute`, `Start video`, `Share`, `Invite`, `Participants`, `Chat`, `React`, `Raise hand`, `More`, `Leave`.
  - `More` button order by visible button bounds: audio menu `(633, 766, 652, 785)`, video menu `(708, 766, 727, 785)`, overflow More `(1181, 762, 1256, 834)`.
- Locator confidence: live evidence confirms the empty-room UIA labels and `More` order for this build/window/DPI only. It also suggests `ringcentral.video.main.add-coworkers` should prefer a UIA `Add coworkers` button route over its current coordinate route.
- Cleanup path: none; read-only observation.
- Privacy/safety notes: no screenshot, no clicks, no chat/participant content read. Labels were filtered to product controls and generic state text.
- Follow-up: replace or test the `Add coworkers` coordinate route; recapture with two-plus participants, localized UI, and a non-empty chat/participants panel without reading private content.

## Needed Live Observations

- Top-bar coordinate routes at common window sizes and DPI scales.
- Toolbar `More` occurrence order with one participant and two-plus participant states.
- Notes location variants: direct toolbar button vs nested More item vs `onconf.controls.NOTES`.
- Settings behavior when last selected panel differs.
- Side-panel and modal close behavior for Chat, Participants, Notes, Invite, Report issue, Background, Settings.
- Prejoin and transient states: audio join prompt, camera preview, host not started, left meeting, meeting ended, recording consent, sharing active, device warning toast.
- Host/moderator-only surfaces: security, waiting room, participant management, recording controls.
