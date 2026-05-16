# Cycle 038 Demand Analysis: RingCentral Evidence Integrity

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made by the demand agent.

## Recommended Slice

Add an offline RingCentral evidence-index integrity guard.

The guard should prove that `docs/knowledge/ringcentral-video/evidence-index.md` stays aligned with `packages/ringcentral-video.yaml` and with the validation-target catalog before future agents plan live RingCentral work from it.

## User Value

The RingCentral knowledge package is now large enough that stale documentation can create false confidence. Operators need to know every curated package route has a single, explicit evidence level and gap before running or planning validation.

This is valuable without live RingCentral automation because it protects the資料包 itself: the next agent can trust that missing, duplicated, typoed, or invalid evidence rows are caught by tests.

## Success Criteria

- Every RingCentral package entrypoint has exactly one evidence-index row.
- Every evidence-index row references a real package entrypoint.
- Evidence levels are limited to `Accepted`, `Observed`, `Repo-tested`, `Backlog`, or `Blocked`.
- Real validation targets, including blocked rows, have no `unknown` evidence levels.
- Recording and Leave remain blocked and non-executable.
- No live RingCentral clicks, screenshots, or acceptance promotions are made.

## Out Of Scope

- No acceptance-run append.
- No locator, privacy, state, or route confidence promotions.
- No package YAML route changes.
- No semantic search or broad dashboard in this cycle.

