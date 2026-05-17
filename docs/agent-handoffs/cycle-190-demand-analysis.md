# Cycle 190 Demand Analysis: Validation Target Evidence Reminder

Date: 2026-05-17

## User Need

Operators use `validation-targets` to choose the next RingCentralVideo manual route before
generating an acceptance draft. They need the metadata-first redaction guidance at this
target-selection step, not only inside the later draft template.

## Chosen Slice

Add a single header-level evidence reminder to `validation-targets` output when the selected
RingCentralVideo targets include unblocked P0 or P1 manual validation work.

## Acceptance Criteria

- `validation-targets --package ringcentral-video --priority P0` shows the reminder once.
- `validation-targets --package ringcentral-video --priority P1` shows the reminder once.
- A specific P0 target shows the reminder before any `draft:` command.
- P2-only output, blocked-only output, and non-RingCentral catalogs do not show the reminder.
- Existing non-evidence wording, draft command generation, parsing, evidence levels, and route
  states remain unchanged.

## Non-Goals

- No live RingCentral acceptance run.
- No evidence-level promotion.
- No screenshot redaction tooling.
- No package YAML, route, alias, localization, controller UI, or acceptance-draft behavior change.
