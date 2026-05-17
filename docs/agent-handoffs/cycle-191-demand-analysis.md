# Cycle 191 Demand Analysis: Per-Entrypoint Draft Examples

Date: 2026-05-17

## User Need

Operators selecting broad RingCentralVideo P1 validation targets need a quick way to generate
focused acceptance drafts for individual entrypoints. A group-only draft command preserves the
checklist target, but it lacks `Entrypoint Context`, open steps, and target-specific presenter
notes.

## Chosen Slice

When `validation-targets` is run for one selected multi-entrypoint target, keep the existing
group `draft:` command and add compact `entrypoint draft examples:` underneath it.

## Acceptance Criteria

- `--target rcv-top-bar-routes` shows examples for meeting info, network quality, views, and
  report issue.
- `--target rcv-toolbar-panels` shows examples for invite and share, proving the helper applies
  to another grouped target.
- `--priority P1` remains scan-friendly and does not render per-entrypoint examples.
- Single-entrypoint targets remain unchanged.
- Mixed flow-plus-entrypoint targets remain unchanged.
- Blocked targets still show no draft commands.
- Existing metadata-first evidence reminder behavior stays unchanged.

## Non-Goals

- No live RingCentral validation.
- No evidence-level promotion.
- No package YAML, route, localization, or acceptance-draft template changes.
- No new validation target schema.
