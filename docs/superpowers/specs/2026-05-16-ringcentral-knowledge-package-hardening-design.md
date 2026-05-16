# RingCentral Knowledge Package Hardening Design

Date: 2026-05-16

## Context

Cycle 000 found that `packages/ringcentral-video.yaml` is already a useful in-meeting control map, but it does not yet have enough evidence structure to grow safely. The package contains executable routes, coordinate fallbacks, privacy notes, bilingual narration for one flow, and explain-only controls. Those facts currently live inside YAML notes, runbooks, tests, specs, and chat handoffs.

Cycle 001 improved how the controller consumes existing package knowledge. Cycle 002 should harden the RingCentralVideo knowledge base itself before adding more broad feature coverage.

## Goals

- Create a companion knowledge package under `docs/knowledge/ringcentral-video/`.
- Preserve the existing YAML schema; do not add package fields in this cycle.
- Index official RingCentral sources and repository-local evidence.
- Split current knowledge into source, observation, locator, state, privacy, and acceptance matrices.
- Make brittle areas visible: coordinate locators, `More` occurrence matching, Notes variants, Settings last-opened panel, modal/side-panel cleanup, and English-only UI labels.
- Give future subagents a precise place to record manual observations, version/build, locale, DPI, window bounds, meeting role, participant count, locator confidence, cleanup behavior, and privacy constraints.

## Non-Goals

- No changes to `packages/ringcentral-video.yaml`.
- No new Pydantic schema fields.
- No new desktop automation or product behavior.
- No claim that unverified RingCentral surfaces are executable.
- No manual acceptance run against the live RingCentral app in this cycle.

## Source Strategy

Use two source classes:

- Official RingCentral documentation for product-scope discovery and feature taxonomy.
- Local repository artifacts for executable claims, adapter behavior, tests, and accepted routes.

Official sources should be treated as product knowledge, not automation proof. A support page can justify adding a source reference or future coverage candidate, but only local observation and tests should justify executable locator confidence.

## Document Structure

Create:

- `docs/knowledge/ringcentral-video/source-index.md`
  - Official sources, local sources, what each source supports, and where it should feed the package.
- `docs/knowledge/ringcentral-video/observation-log.md`
  - Append-only template and current known observations from repo-local evidence.
- `docs/knowledge/ringcentral-video/locator-matrix.md`
  - Current entrypoints, locator type, cleanup, confidence, and verification need.
- `docs/knowledge/ringcentral-video/state-matrix.md`
  - Meeting states represented by adapter/package/runbook, plus missing states.
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
  - Sensitive surfaces, allowed summaries, disallowed readings, and confirmation rules.
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
  - Manual and automated acceptance record template plus current command baseline.

## Acceptance Criteria

- The new docs explain what is known, what is only source-backed, and what still requires live observation.
- Every currently brittle locator category has an explicit verification note.
- Every privacy-sensitive RingCentral surface has a default policy.
- Future agents can add observations without editing YAML.
- Verification includes at least a docs file listing check and a full no-coverage test run or a clearly scoped explanation if tests are skipped.

## Self-Review

- The design is documentation-only and avoids schema churn.
- It directly follows Cycle 000 and Cycle 001 handoff recommendations.
- It does not overclaim official documentation as live automation evidence.
