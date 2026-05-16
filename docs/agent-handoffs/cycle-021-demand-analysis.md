# Cycle 021 Demand Analysis: RingCentral Validation Target Discovery

Date: 2026-05-16
Role: demand-analysis worker
Write scope: this file only

## Read Scope

Reviewed local repository context only:

- `docs/agent-handoffs/cycle-017-demand-analysis.md`
- `docs/agent-handoffs/cycle-017-summary.md`
- `docs/agent-handoffs/cycle-018-demand-analysis.md`
- `docs/agent-handoffs/cycle-019-summary.md`
- `docs/agent-handoffs/cycle-020-demand-analysis.md`
- `docs/agent-handoffs/cycle-020-summary.md`
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/packages/loader.py`
- `src/ai_presenter/acceptance/manual_record.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_acceptance_manual_record.py`

Commands run for discovery only:

- `.\.venv\Scripts\ai-presenter flows --package ringcentral-video`
- `.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video`
- `.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers`

No live RingCentral actions were run. No production code, tests, package YAML,
runbook, or knowledge docs were edited.

## Problem Statement

Cycles 017-020 improved the RingCentral validation workflow in pieces:

- `validation-checklist-index.md` gives an operator-ready validation queue.
- `evidence-index.md` maps entrypoints and flows to current evidence gaps.
- `flows` and `entrypoints` list package IDs, titles, areas, and step counts.
- `acceptance-draft` renders a safe offline manual record template for a chosen
  flow, entrypoint, or free-text checklist target.

The remaining friction is target discovery. Before a reviewer can choose the
next validation run, they still have to cross-read package YAML, evidence
tables, the validation checklist, and CLI lists to answer simple questions:

- Which targets are P0/P1 right now?
- Which package entrypoints have `Observed`, `Repo-tested`, `Backlog`, or
  `Blocked` evidence status?
- Which demo flows use an entrypoint, and which flow evidence is weakest?
- Which routes are safe candidates for manual validation versus explain-only?
- What exact command should prepare an acceptance draft for the selected target?

That lookup should be possible from the repo with no RingCentral process, no
profile loading, no desktop scan, and no accidental evidence promotion.

## User Needs

- Operators need a fast offline list of validation targets before entering a
  live meeting or asking another agent to validate a route.
- Reviewers need a reproducible command whose output explains why a target is
  next, not just that an entrypoint exists in the package.
- Future implementation agents need stable IDs for target selection so handoff
  docs can say "run target X" without relying on prose table row names.
- Acceptance workers need direct handoff from discovery to
  `acceptance-draft`, with the draft still clearly separated from proof.
- Maintainers need drift checks that fail when package entrypoints or flows stop
  matching the evidence/checklist docs.
- Privacy reviewers need blocked and high-risk targets to be visible in the
  same list as ordinary validation candidates, so they are not accidentally
  treated as runnable gaps.

## Recommended Scope

Recommended Cycle 021 target: add a small offline validation-target discovery
tool that joins package metadata with RingCentral evidence/checklist status.

In scope:

- Add a pure data model and loader, likely under `src/ai_presenter/acceptance/`,
  for repository validation targets.
- Add a Typer command, recommended name:
  `ai-presenter validation-targets`.
- Load the material package using the existing `resolve_material_package()` and
  `load_material_package()` path.
- Read RingCentral knowledge docs from
  `docs/knowledge/ringcentral-video/` when `--package ringcentral-video` is
  used.
- Produce offline target rows for:
  - package operation entrypoints;
  - package demo flows;
  - validation checklist route groups, if the parser can do this safely.
- Include evidence level/status from `evidence-index.md` for entrypoints and
  flows.
- Include priority, current state, validation action, cleanup, and privacy
  boundary from `validation-checklist-index.md` where a checklist row maps to
  the target.
- Surface blocked/explain-only status for `ringcentral.video.more.recording`
  and `ringcentral.video.toolbar.leave`.
- Include a suggested `acceptance-draft` command for actionable flow or
  entrypoint targets.
- Support a concise human text output by default and a stable machine output
  with `--format json`.
- Add filters that match the real review workflow:
  `--priority P0`, `--evidence-level Observed`, `--kind entrypoint|flow|checklist`,
  `--target <id>`, and possibly `--blocked/--include-blocked`.
- Add focused unit tests around pure parsing/formatting and CLI output.

Recommended small implementation order:

1. Add a pure `ValidationTarget` model and parsing functions.
2. Parse the entrypoint evidence table and flow coverage table from
   `evidence-index.md`.
3. Parse the priority checklist and do-not-execute table from
   `validation-checklist-index.md`.
4. Join parsed doc rows to package entrypoints/flows by stable package IDs.
5. Add `validation-targets` CLI text output and tests.
6. Add JSON output only after text output is stable.

If checklist route-group IDs remain too prose-shaped, add a docs-only `Target ID`
column to the checklist in the implementation cycle before relying on generated
slugs. Stable target IDs are more valuable than clever slugging.

## Out Of Scope

- Live RingCentral interaction, desktop automation, UIA capture, screenshots,
  or controller execution.
- Promoting any route to `Accepted`.
- Writing to `acceptance-runs.md` or appending completed evidence.
- Changing `packages/ringcentral-video.yaml` route behavior or executable
  `openSteps`.
- Adding package-local evidence metadata schema in the first slice. The package
  models currently forbid extra fields, and the existing docs already own the
  evidence semantics.
- Replacing `flows`, `entrypoints`, or `acceptance-draft`.
- Inferring evidence status from automated tests, dry runs, `doctor`, or the
  existence of package routes.
- Reading or storing private meeting content, including chat text, participant
  names, invite links, meeting IDs, shared content, notes, transcripts, device
  lists, account data, or report contents.

## Acceptance Criteria

- `ai-presenter validation-targets --package ringcentral-video` runs without a
  profile, RingCentral process, desktop scan, or live automation.
- Default output includes package id, source docs, and a concise target table.
- The command lists all 27 RingCentral operation entrypoints with title, area,
  evidence level, and whether the target is blocked/explain-only.
- The command lists all 4 demo flows with title, step count, current evidence,
  weakest link, and next validation summary when available.
- P0 output includes:
  - `ringcentral.video.main.add-coworkers` as `Observed` with live click/modal
    cleanup still needed.
  - `meeting-control-map-demo` or the queued Chat checklist target as not
    manually accepted, with `ringcentral.video.toolbar.chat` visible.
- Blocked output clearly marks `ringcentral.video.more.recording` and
  `ringcentral.video.toolbar.leave` as do-not-execute/explain-only.
- Each actionable entrypoint or flow row includes a suggested
  `acceptance-draft` command that does not imply RingCentral has been clicked.
- `--priority P0` and `--kind flow` filters are deterministic and covered by
  tests.
- `--format json` returns stable keys such as `target_id`, `kind`, `priority`,
  `entrypoint_ids`, `flow_ids`, `evidence_level`, `blocked`, `next_step`, and
  `draft_command`.
- Unknown package IDs or missing docs fail with clear errors and do not produce
  partial evidence claims.
- Existing `flows`, `entrypoints`, `acceptance-draft`, `doctor`, `demo`, and
  `controller` command behavior remains unchanged.

## Risks

- Markdown parsing brittleness: the evidence and checklist tables are docs, not
  a formal schema. Keep the parser conservative and fail loudly when required
  columns are missing.
- Stable-ID risk: route-group labels such as "Common toolbar panels and
  pickers" are not stable enough for automation. Prefer package entrypoint/flow
  IDs, or add a `Target ID` checklist column in the same implementation cycle.
- Overclaim risk: an offline target list can look like validation proof. Output
  should say it is repo-derived planning context, not acceptance evidence.
- Drift risk: `evidence-index.md`, `validation-checklist-index.md`, and package
  YAML can disagree. Tests should assert that all package entrypoints and flows
  are represented and that unresolved evidence is displayed as unresolved.
- Privacy risk: output should summarize boundaries, not surface sensitive live
  values or encourage reading them.
- Scope risk: it is tempting to add route metadata to the package schema. Keep
  this cycle to discovery and tests unless stable checklist IDs require a small
  docs-only column.
- Console readability risk: the target list can get wide. Keep text output
  compact and reserve full fields for `--format json` or `--target`.

## Candidate CLI And Output Shape

Recommended command:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video
```

Useful filters:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --kind flow
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target ringcentral.video.main.add-coworkers
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --evidence-level Observed --format json
```

Default text output shape:

```text
Package: ringcentral-video
Sources: packages/ringcentral-video.yaml; docs/knowledge/ringcentral-video/evidence-index.md; docs/knowledge/ringcentral-video/validation-checklist-index.md
Note: repo-derived target list only; not live acceptance evidence.

Priority Kind       Target                                      Evidence     Status
P0       entrypoint ringcentral.video.main.add-coworkers        Observed     needs live click + modal cleanup
         title: Add coworkers [Meeting canvas]
         flows: meeting-control-map-demo
         next: Click Add coworkers in a disposable empty-room meeting; verify modal close.
         draft: ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers --checklist-target "Add coworkers modal"

P0       flow       meeting-control-map-demo                    Repo-tested  queued Chat not manually accepted
         title: Meeting Control Map (22 steps)
         entrypoints: ringcentral.video.toolbar.chat, ringcentral.video.main.add-coworkers, ...
         next: Start the map demo, ask chat, confirm queued safe demo and original flow continuity.
         draft: ai-presenter acceptance-draft --package ringcentral-video --flow meeting-control-map-demo --checklist-target "Controller queued Chat question"

P3       entrypoint ringcentral.video.more.recording            Blocked      do not execute
         title: Start recording [More menu]
         next: design confirmation and role policy before any live action.
```

Candidate JSON row shape:

```json
{
  "target_id": "entrypoint:ringcentral.video.main.add-coworkers",
  "kind": "entrypoint",
  "priority": "P0",
  "package_id": "ringcentral-video",
  "title": "Add coworkers",
  "area": "Meeting canvas",
  "entrypoint_ids": ["ringcentral.video.main.add-coworkers"],
  "flow_ids": ["meeting-control-map-demo"],
  "evidence_level": "Observed",
  "current_state": "Observed UIA button, package route repo-tested, no live click acceptance",
  "blocked": false,
  "validate": "In a disposable empty-room meeting, click Add coworkers, confirm Invite/Add coworkers dialog opens, then close it",
  "cleanup": "Modal close by X or Cancel; confirm toolbar is usable again",
  "privacy_boundary": "Do not read or store invite links, emails, names, or suggestions",
  "draft_command": "ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers --checklist-target \"Add coworkers modal\""
}
```

## Key Recommendation

Build `validation-targets` as an offline discovery command that joins the
existing package, evidence index, and validation checklist into one reviewer
view. Keep it evidence-aware but non-executing: it should help an operator pick
the next target and prepare an acceptance draft, not validate RingCentral or
change evidence state.
