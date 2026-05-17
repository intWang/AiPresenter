# Cycle 192 Demand Analysis: Running-App Scan Observability

Date: 2026-05-17

## User Need

Operators scanning an arbitrary running desktop app need to know whether the scan was fast and
how much safe structure AiPresenter generated. Recent cycles strengthened RingCentralVideo
manual evidence workflow; the next useful branch is runtime performance observability.

## Chosen Slice

Add privacy-safe timed telemetry for controller running-app scans, plus a small Spanish
language lifecycle count correction.

## Acceptance Criteria

- Successful scans emit `running_app_scanned status=ok duration_ms=...`.
- Failed scans emit `running_app_scanned status=error duration_ms=...` before preserving existing
  error behavior.
- Logged metadata is bounded: process, window class, pid, control count, entrypoint count,
  openable count, explain-only count, package id, and flow id.
- Logs omit window title, control names, user questions, answer text, exception text, meeting
  data, and screenshots.
- Controller scan status shows package id, control count, entrypoint count, and elapsed time.
- Existing scan invalidation behavior remains unchanged.
- Spanish lifecycle docs report `16/16` Q&A questions and answers.

## Non-Goals

- No async/background scan.
- No scan caching or performance optimization yet.
- No package YAML, route, localization content, language/tone behavior, validation target, or
  acceptance-draft changes.
- No live RingCentral run or evidence promotion.
