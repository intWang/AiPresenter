# Validation Target Discovery Design

Date: 2026-05-16

## Context

The RingCentralVideo knowledge package now has three useful but separate planning surfaces:

- `packages/ringcentral-video.yaml` defines package entrypoints and demo flows.
- `docs/knowledge/ringcentral-video/evidence-index.md` records evidence level and gaps.
- `docs/knowledge/ringcentral-video/validation-checklist-index.md` lists priority manual validation work, cleanup, and privacy boundaries.

Cycle 018 added `acceptance-draft`, but an operator still has to cross-read docs before choosing a target. Cycle 021 adds an offline discovery view that joins these sources and suggests the next draft command without touching RingCentral or evidence files.

## Chosen Slice

Add a pure `ai_presenter.acceptance.validation_targets` module and a read-only CLI command:

```powershell
ai-presenter validation-targets --package ringcentral-video
```

The command lists validation checklist targets with:

- stable generated target id;
- priority and route/group label;
- referenced package entrypoint and flow ids;
- evidence level/gap context;
- current state, validation action, cleanup, and privacy boundary;
- a draft-safe `acceptance-draft` command.

Default output excludes the `Do Not Execute Yet` table. `--include-blocked` includes blocked/explain-only routes for awareness.

## Data Model

Add frozen dataclasses:

```python
@dataclass(frozen=True)
class ValidationTarget:
    id: str
    priority: str
    route_or_group: str
    entrypoint_ids: tuple[str, ...]
    flow_ids: tuple[str, ...]
    current_state: str
    validate: str
    cleanup: str
    privacy_boundary: str
    record_result: str
    evidence_levels: Mapping[str, str]
    evidence_gaps: Mapping[str, str]
    blocked_reason: str | None = None


@dataclass(frozen=True)
class ValidationTargetCatalog:
    package_id: str
    checklist_path: Path
    evidence_path: Path | None
    targets: tuple[ValidationTarget, ...]
```

The module should depend only on package models and standard library parsing helpers.

## Parsing

Use conservative Markdown pipe-table parsing:

- Find `## Priority Checklist` and parse the first table by header names.
- Required checklist headers: `Priority`, `Route Or Group`, `Entrypoints`, `Current State`, `Validate`, `Cleanup`, `Privacy Boundary`, `Record Result`.
- Extract only backticked ids from the `Entrypoints` cell.
- Classify each id as a package entrypoint id or demo flow id using `MaterialPackage.entrypoints_by_id` and `demo_flows_by_id`.
- Raise `ValueError` when a checklist id is unknown.
- Generate target ids as `{priority.lower()}-{slug(route_or_group)}`, for example `p0-add-coworkers-modal`.
- Fail on duplicate target ids.
- Find `## Entry Point Evidence Table` and parse `Entrypoint`, `Evidence Level`, and `Main Gap`.
- Missing evidence rows should render as `unknown`, not block discovery.
- Parse `## Do Not Execute Yet` only when `include_blocked=True`.

This design accepts docs-derived parsing for the current slice. If target names become unstable, a future cycle should add an explicit `Target ID` column.

## CLI

Add command:

```powershell
ai-presenter validation-targets --package ringcentral-video
```

Options:

- `--package`: required material package id or YAML path.
- `--priority`: optional priority filter such as `P0`.
- `--target`: optional discovered target id for one target.
- `--checklist`: optional checklist path override.
- `--evidence`: optional evidence path override.
- `--include-blocked`: include `Do Not Execute Yet` targets.

Default paths should point at `docs/knowledge/ringcentral-video/validation-checklist-index.md` and `docs/knowledge/ringcentral-video/evidence-index.md`.

The command is read-only. It must not load a profile, run desktop automation, start the controller, run RingCentral, or write `acceptance-runs.md`.

## Output

Default text output begins with:

```text
Package: ringcentral-video
Checklist: docs/knowledge/ringcentral-video/validation-checklist-index.md
Evidence: docs/knowledge/ringcentral-video/evidence-index.md
Note: repo-derived planning list only; not live acceptance evidence.
```

Each target renders as compact text:

```text
- p0-add-coworkers-modal [P0] Add coworkers modal
  entrypoints: ringcentral.video.main.add-coworkers
  evidence: ringcentral.video.main.add-coworkers=Observed
  current: Observed UIA button, package route repo-tested, no live click acceptance
  validate: In a disposable empty-room meeting, click Add coworkers...
  cleanup: Modal close by X or Cancel...
  privacy: Do not read or store invite links...
  draft: ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers --checklist-target "P0 Add coworkers modal"
```

For grouped targets with multiple entrypoints, omit `--entrypoint` from the draft command and include only `--checklist-target`.

## Non-Goals

- No live RingCentralVideo interaction.
- No desktop automation, UIA scanning, screenshots, or controller execution.
- No evidence promotion to `Accepted`.
- No writes to `acceptance-runs.md`.
- No package schema changes.
- No JSON output in this first slice.
- No replacement of existing `flows`, `entrypoints`, or `acceptance-draft`.

## Acceptance Criteria

- `validation-targets --package ringcentral-video --priority P0` lists `p0-add-coworkers-modal` and `p0-controller-queued-chat-question`.
- P0 Add coworkers shows `ringcentral.video.main.add-coworkers`, evidence `Observed`, live click/modal cleanup gap, cleanup text, privacy boundary, and an entrypoint-specific draft command.
- P0 queued Chat shows both `ringcentral.video.toolbar.chat` and `meeting-control-map-demo`.
- `--target p0-add-coworkers-modal` renders only that target.
- Unknown targets fail with the requested id plus available ids.
- Unknown checklist package ids fail with a clear error.
- Duplicate generated ids fail clearly.
- `--include-blocked` lists `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave` with do-not-execute/blocked wording.
- Existing `flows`, `entrypoints`, `acceptance-draft`, `doctor`, `demo`, and `controller` commands remain unchanged.
- Focused unit tests, full pytest, ruff, mypy, and diff check pass.

## Risks

- Markdown parsing can drift. The parser should fail loudly on missing required headers and unknown ids.
- Generated target ids depend on route/group labels. This is acceptable for Cycle 021 but should become explicit docs metadata if agents start relying heavily on them.
- Offline discovery output can be mistaken for proof. Keep the non-evidence note visible in every command output.
- Group draft commands must not imply a single entrypoint was validated.
