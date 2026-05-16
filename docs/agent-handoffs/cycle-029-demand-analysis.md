# Cycle 029 Demand Analysis: Stable RingCentral Validation Target IDs

Date: 2026-05-16
Role: demand discovery
Scope: review-only demand analysis. No production code was edited in this pass.

## Context Reviewed

- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `src/ai_presenter/acceptance/validation_targets.py`
- `tests/unit/test_validation_targets.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-021-summary.md`
- `docs/agent-handoffs/cycle-021-technical-scan.md`
- `docs/agent-handoffs/cycle-027-summary.md`
- `docs/agent-handoffs/cycle-028-demand-analysis.md`
- `docs/agent-handoffs/cycle-028-summary.md`

Manual probe:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

The command currently lists label-derived ids such as `p0-add-coworkers-modal`,
`p1-top-bar-coordinate-routes`, and `blocked-recording`.

## Problem

`validation-targets` is already useful as an offline RingCentralVideo planning
tool, but its canonical target ids are generated from mutable checklist labels
and priorities:

```python
id=_target_id(row["priority"], route_or_group)
```

For blocked rows, the id is generated from the route label:

```python
id=f"blocked-{_slug(route_or_group)}"
```

This makes agent handoffs and operator commands brittle. If a checklist title is
clarified or a row moves from `P1` to `P0`, the target id changes even though the
underlying validation task is the same.

## User And Operator Value

- Operators can run stable commands such as
  `ai-presenter validation-targets --package ringcentral-video --target rcv-add-coworkers-modal`
  without depending on the exact checklist label.
- Subagents can pass target ids through handoffs as durable coordination keys.
- Future acceptance docs can reference a validation target before any live
  RingCentralVideo work begins.
- RingCentralVideo safety work becomes easier to audit because blocked,
  explain-only, and executable rows all have explicit identifiers.
- The improvement is offline and privacy-safe: it reads docs and package
  metadata only.

## Recommended Slice

Add an explicit `Target ID` column to the RingCentral validation checklist and
teach `validation-targets` to use that column when present.

Generated ids should remain only as compatibility fallback for checklist tables
that do not have a `Target ID` column. For the current RingCentral checklist,
the explicit column should become the canonical source.

## Naming Style

Use lowercase ASCII kebab-case with a product prefix:

```text
rcv-<route-or-workflow-name>
```

Rules:

- Use `rcv-` for RingCentralVideo validation target ids.
- Do not include priority (`p0`, `p1`) because priority is expected to change.
- Do not include evidence status (`observed`, `repo-tested`, `accepted`) because
  evidence status is expected to change.
- Keep names route- or workflow-oriented rather than UI-copy-oriented.
- Prefer stable nouns from the package route family: `toolbar`, `top-bar`,
  `settings`, `background`, `chat`, `leave-end`.
- Keep ids short enough for CLI use, but specific enough to disambiguate groups.

Recommended initial ids:

| Current Row | Recommended Target ID |
| --- | --- |
| Add coworkers modal | `rcv-add-coworkers-modal` |
| Controller queued Chat question | `rcv-controller-chat-question` |
| App shell launch | `rcv-app-shell-launch` |
| Top-bar coordinate routes | `rcv-top-bar-routes` |
| Common toolbar panels and pickers | `rcv-toolbar-panels` |
| More occurrence routes | `rcv-more-menu-variants` |
| Notes and transcript | `rcv-notes-transcript` |
| Media controls | `rcv-media-controls` |
| Reactions and raise hand | `rcv-reactions-raise-hand` |
| Settings and background | `rcv-settings-background` |
| Overview and explain-only context | `rcv-overview-context` |
| Recording | `rcv-recording` |
| Leave or end meeting | `rcv-leave-end-meeting` |

## Do Not Execute Yet Rows

Yes, this slice should touch the `Do Not Execute Yet` table too.

Reason:

- These rows are frequently referenced in safety reviews and handoffs.
- They are high-risk routes, so stable identifiers reduce ambiguity.
- `--include-blocked` already exposes these rows as validation targets.
- Default output should still exclude them unless `--include-blocked` is passed.

The target ids for blocked rows should be status-neutral (`rcv-recording`,
`rcv-leave-end-meeting`) instead of `blocked-*`. The blocked state belongs in
the row fields (`current`, `validate`, `blocked`, privacy text), not in the
canonical id. If a route later receives an approved confirmation workflow, the
same id can still refer to the same underlying route.

## Acceptance Criteria

- Add `Target ID` to the `Priority Checklist` table.
- Add `Target ID` to the `Do Not Execute Yet` table.
- `validation-targets` uses explicit target ids when the column is present.
- If a table has `Target ID`, blank ids in that table fail with a clear error.
- Duplicate explicit ids fail with a clear error.
- If the `Target ID` column is absent, existing generated-id fallback behavior
  still works for compatibility fixtures.
- `validation-targets --package ringcentral-video --priority P0` lists
  `rcv-add-coworkers-modal` and `rcv-controller-chat-question`.
- `validation-targets --package ringcentral-video --target rcv-add-coworkers-modal`
  renders the Add coworkers detail and the existing draft command.
- `validation-targets --package ringcentral-video --include-blocked` lists
  `rcv-recording` and `rcv-leave-end-meeting`, and still renders them as
  `Do not execute` targets.
- Existing package id validation remains unchanged: backticked entrypoints and
  demo flows in the checklist must still resolve to package metadata.
- The command remains read-only and package-only. It must not open
  RingCentralVideo, write `acceptance-runs.md`, or promote evidence.

## Suggested Test Updates

- Update existing CLI and pure discovery expectations from generated ids to
  explicit `rcv-*` ids.
- Add a pure parser test where a checklist with explicit `Target ID` returns
  that id instead of the generated priority/label slug.
- Add a pure parser test for a blank explicit target id.
- Add a pure parser test for duplicate explicit target ids.
- Keep or add a fixture without `Target ID` to prove generated-id fallback still
  works.
- Add or update the blocked-row test so `include_blocked=True` resolves
  `rcv-recording` and `rcv-leave-end-meeting`.
- Keep focused CLI coverage for `--priority`, `--target`, unknown targets, and
  `--include-blocked`.

## Out Of Scope

- Do not run live RingCentralVideo validation.
- Do not append to or edit `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- Do not promote any route to `Accepted`.
- Do not change package entrypoint ids, demo flow ids, open steps, cleanup
  behavior, or privacy policy.
- Do not change `acceptance-draft` semantics beyond consuming the selected
  target as it already does.
- Do not add JSON output or target aliases in this slice. A temporary alias from
  old generated ids to explicit ids can be considered later if real operator
  docs still depend on the old ids.
- Do not encode localization, voice, or runtime controller changes into this
  slice.

## Recommended Next Step

Proceed with a small technical scan and implementation plan for explicit
RingCentral target ids. The implementation should stay in the existing
`ai_presenter.acceptance.validation_targets` boundary and the RingCentral
knowledge checklist. The next implementation should verify the CLI remains
offline/read-only and that blocked rows stay opt-in through `--include-blocked`.
