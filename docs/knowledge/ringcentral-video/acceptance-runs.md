# RingCentral Video Acceptance Runs

Date: 2026-05-16

## Purpose

Use this file to record dated automated and manual acceptance evidence for RingCentral Video. A checklist in a runbook is not acceptance evidence until a run is recorded here.

## Automated Baseline Template

```markdown
## YYYY-MM-DD - Automated Baseline

- Runner:
- Branch:
- Commit or worktree state:
- Commands:
  - `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
  - `.\.venv\Scripts\python -m ruff check --no-cache .`
  - `.\.venv\Scripts\python -m mypy --no-incremental src tests`
  - `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`
- Results:
- Warnings:
- Follow-up:
```

## Manual Acceptance Template

```markdown
## YYYY-MM-DD HH:mm Local - Manual RingCentral Acceptance

- Tester:
- RingCentral app/build:
- App channel:
- Windows version:
- Locale:
- DPI/display scale:
- Monitor setup:
- Audio devices:
- Virtual mic:
- Profile:
- Package flow:
- Meeting role:
- Meeting scenario:
- Participant count:
- Window bounds:
- Evidence files:
- Steps executed:
- Pass/fail:
- Failures:
- Recovery:
- Privacy notes:
- Locator updates needed:

### Evidence Redaction Checklist

- Prefer UIA/window metadata and allowlisted product-control labels before screenshots.
- Capture screenshots only when there is a clear verification need and a privacy review path.
- Redact or omit chat text, participant names or roles, invite links, meeting IDs, dial-in details, emails, device lists, account/profile content, notes/transcripts, recordings, shared content, and room imagery.
- In Evidence files, name only sanitized artifacts; delete or quarantine raw artifacts.
- In Privacy notes, state what was redacted or intentionally not captured.
```

## Current Automated Evidence From Cycle 001

This is not a fresh Cycle 002 run. It records the verified baseline at the end of Cycle 001 for continuity.

- Runner: main session.
- Worktree: dirty, with Cycle 001 code and docs changes.
- Command: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
- Result: `362 passed, 1 warning`.
- Warning: `pywinauto` STA COM threading warning.
- Command: `.\.venv\Scripts\python -m ruff check --no-cache .`
- Result: `All checks passed!`
- Command: `.\.venv\Scripts\python -m mypy --no-incremental src tests`
- Result: `Success: no issues found in 70 source files`.
- Command: `.\.venv\Scripts\ai-presenter controller --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run`
- Result: profile, package, and flow loaded; controller dry run completed.

## 2026-05-16 - Cycle 002 Automated Baseline

- Runner: main session.
- Worktree: dirty, with Cycle 001 controller changes and Cycle 002 knowledge docs.
- Command: `Get-ChildItem -LiteralPath docs\knowledge\ringcentral-video | Select-Object -ExpandProperty Name`
- Result: six knowledge docs present:
  - `acceptance-runs.md`
  - `locator-matrix.md`
  - `observation-log.md`
  - `privacy-matrix.md`
  - `source-index.md`
  - `state-matrix.md`
- Command: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
- Result: `362 passed, 1 warning in 10.64s`.
- Warning: `pywinauto` STA COM threading warning.
- Skipped: live RingCentral manual acceptance; no live app build, locale, DPI, window bounds, or screenshots were captured in Cycle 002.
- Follow-up: fill the manual acceptance template after the next real RingCentral observation run.

## 2026-05-16 01:15 +08:00 - Cycle 003 Read-Only RingCentral Observation

- Runner: main session.
- Worktree: dirty, with Cycle 001 controller changes, Cycle 002 knowledge docs, and Cycle 003 documentation updates.
- RingCentral app/build: RingCentral Video `26.2.20.355`.
- App channel: RingCentralDevelop embedded RingCentralVideo process.
- Windows version: Microsoft Windows 11 Pro `10.0.26200` build `26200`, 64-bit.
- Locale: `en-US`.
- DPI/display scale: window DPI `96`, scale `100%`.
- Monitor setup: 1920x1080 monitor reported by Windows desktop APIs.
- Profile/package/flow: RingCentral Video knowledge observation, no package flow executed.
- Meeting role: not determined.
- Meeting scenario: empty room / first one here.
- Participant count: not parsed by adapter.
- Window bounds: `(500, 196, 1420, 836)`.
- Evidence:
  - `RingCentralVideo` process title `RingCentral Video`, class `RingCentralVideoClass`.
  - `WindowsDesktopDriver.capture` with `WINDOWS_UI_AUTOMATION` and `WINDOW_METADATA`; no screenshot source requested.
  - Adapter state: `meeting_joined=True`, `camera_off=True`, `confidence=0.85`.
  - Sanitized key labels included `Add coworkers`, `Mute`, `Start video`, `Share`, `Invite`, `Participants`, `Chat`, `React`, `Raise hand`, `More`, `Leave`, and `You're the first one here`.
- Steps executed:
  - Listed RingCentral processes and visible windows.
  - Captured metadata/UIA text from the RingCentralVideo window.
  - Scanned key UIA controls for type and bounds.
- Pass/fail: pass for read-only observation and state extraction evidence.
- Failures:
  - First unsanitized console print hit a Windows codepage encoding error on a private-use UI glyph; rerun with `PYTHONIOENCODING=utf-8` and a key-label allowlist succeeded.
- Privacy notes: no screenshot, no clicks, no chat content, no participant names, no invite links.
- Locator updates needed:
  - Replace or validate `ringcentral.video.main.add-coworkers` coordinate route because a visible UIA `Add coworkers` button was observed.
  - Treat `More` occurrence order as observed only for this empty-room 100% DPI state; verify participant and layout variants.

## 2026-05-16 - Cycle 004 Automated Baseline

- Runner: main session.
- Worktree: dirty, with unrelated pre-existing changes outside the Cycle 004 write ownership.
- Package update: changed `ringcentral.video.main.add-coworkers` from a coordinate route to the Cycle 003 observed UIA `Add coworkers` button route.
- Command: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_add_coworkers_uses_observed_uia_button_route`
- RED result: failed while the route was still `clickWindowRelative`.
- Command: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py`
- GREEN result: `9 passed in 1.15s`.
- Command: `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
- Full verification result: `363 passed, 1 warning in 13.90s`.
- Warning: `pywinauto` STA COM threading warning.
- Manual validation: not performed in Cycle 004; no live click, invite modal open, or modal close validation was attempted.
- Follow-up: manually validate the live RingCentral `Add coworkers` click route and modal cleanup before treating it as accepted.

## Manual Acceptance Backlog

- Run `doctor` against an open RingCentral build and record `config.ini` status.
- Execute queued Chat question during `meeting-control-map-demo`.
- Ask Chinese Chat and Leave questions.
- Verify top-bar coordinate routes at current DPI/window size.
- Verify Invite, Participants, Chat, Share, Reactions, Notes, Background, Settings cleanup.
- Record Notes layout variant.
- Record More button occurrence order.
- Record side-panel close coordinates and fallbacks.
