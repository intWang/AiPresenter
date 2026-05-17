# Cycle 189 Demand Analysis: Manual Evidence Redaction Template

Date: 2026-05-17

## User Need

Operators preparing RingCentralVideo manual acceptance evidence need a repeatable redaction
checklist before they capture or append proof. The goal is to advance live evidence without
leaking chat text, participant names, invite links, meeting IDs, transcripts, device/account
details, shared content, or screenshots with private content.

## Chosen Slice

Add an `Evidence Redaction Checklist` to generated `acceptance-draft` output and mirror the
same checklist in the RingCentral manual acceptance template.

## Acceptance Criteria

- `acceptance-draft` output includes a compact evidence redaction checklist.
- The checklist prefers UIA/window metadata and allowlisted control labels before screenshots.
- Screenshot capture requires a clear verification need and a privacy review path.
- Private meeting content is listed as redact-or-omit material.
- Draft output continues to say it is not acceptance evidence and no live RingCentral action
  has been performed.
- The manual runbook and `acceptance-runs.md` template guide operators to record what was
  redacted or intentionally not captured.

## Non-Goals

- No automated screenshot redaction tool.
- No live RingCentral acceptance run.
- No route, alias, localization, locator, controller UI, or package YAML changes.
- No promotion of any route to `Accepted`, `Observed`, or live-validated status.
