# Cycle 021 Technical Scan: RingCentral Validation Target Discovery

Date: 2026-05-16

## Scope

Scan target: minimal implementation path for a RingCentral Video validation target discovery helper and CLI.

Safety boundary for this scan: no production-code edits. Future implementation should remain read-only with respect
to RingCentral, `acceptance-runs.md`, and desktop automation. The helper should only discover and describe validation
targets and, where safe, print an `acceptance-draft` command.

## Current Architecture And Relevant Files

- `packages/ringcentral-video.yaml`
  - Source package for `ringcentral-video`, with profile ids, `operationEntrypoints`, `demoFlows`, explainers, Q&A,
    and manual controls.
  - Entrypoints already contain `id`, `title`, `area`, `purpose`, `openSteps`, `presenterNotes`, and some
    `questionAliases`.
  - Open-step match metadata already exposes useful target-discovery details such as `cleanup`, `occurrence`,
    `controlType`, `alternateTargets`, `x`, `y`, `xFromRight`, and `yFromBottom`.
  - `meeting-control-map-demo` is the main broad acceptance flow. `ringcentral.video.more.recording` and
    `ringcentral.video.toolbar.leave` remain explain-only or blocked.
- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
  - Best source for "what should be validated next".
  - `## Priority Checklist` table has the exact fields needed for discovery: `Priority`, `Route Or Group`,
    `Entrypoints`, `Current State`, `Validate`, `Cleanup`, `Privacy Boundary`, and `Record Result`.
  - `## Do Not Execute Yet` table identifies blocked routes that should be listed only when requested.
- `docs/knowledge/ringcentral-video/evidence-index.md`
  - Best source for evidence context, not proof creation.
  - `## Entry Point Evidence Table` maps package entrypoint ids to `Mode`, `Evidence Level`, and `Main Gap`.
  - `## Validation Priority Queue` is useful for operator context, but the checklist is the cleaner first-slice
    source because it already includes cleanup and privacy boundaries.
- `docs/runbooks/ringcentral-manual-acceptance.md`
  - Already points operators to the checklist before live route validation.
  - Already documents `.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --entrypoint ...`.
  - Future discovery output should feed this existing draft helper rather than replace it.
- `src/ai_presenter/cli.py`
  - `resolve_material_package(package: str) -> Path` already supports package ids and paths.
  - `flows()` and `entrypoints()` are the low-risk list-command patterns to copy.
  - `acceptance_draft()` is the downstream command discovery should suggest.
  - `_write_acceptance_draft_output()` guards draft writes and refuses `acceptance-runs.md`.
- `src/ai_presenter/packages/loader.py`
  - `load_material_package(path: Path) -> MaterialPackage` uses `yaml.safe_load` and Pydantic validation.
- `src/ai_presenter/packages/models.py`
  - `MaterialPackage.entrypoints_by_id` and `demo_flows_by_id` are read-only indexes suited for validating
    checklist references.
  - `MaterialPackage.entrypoint_by_id()` and `demo_flow_by_id()` already provide clear unknown-id errors.
  - No schema change is needed for the first discovery slice.
- `src/ai_presenter/acceptance/manual_record.py`
  - Existing pure acceptance draft module. Discovery should live beside it, not in `runtime` or `desktop`.
  - `AcceptanceDraftRequest`, `build_acceptance_target_summary()`, and `render_manual_acceptance_draft()` establish
    the evidence discipline: drafts are not acceptance evidence.
- `tests/unit/test_cli.py`
  - Uses `CliRunner().invoke(app, [...])`; best place for CLI discovery tests.
- `tests/unit/test_material_packages.py`
  - Already proves package/checklist/evidence coverage and validates package route shape.
- `tests/unit/test_acceptance_manual_record.py`
  - Existing pure acceptance helper tests; keep draft tests here, and put target discovery tests in a new focused file.

## Recommended Minimal Slice

Add a pure read-only module:

- `src/ai_presenter/acceptance/validation_targets.py`

Export the module from:

- `src/ai_presenter/acceptance/__init__.py`

Add one CLI command:

- `ai-presenter validation-targets`

Do not touch:

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/*`
- `src/ai_presenter/desktop/*`
- `docs/knowledge/ringcentral-video/acceptance-runs.md`

The implementation should read the package and docs, validate references, and render operator-friendly target rows.
It should not click, observe, bind, append evidence, or mark anything `Accepted`.

## Proposed Module API

Recommended dataclasses:

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

Recommended functions:

```python
def discover_validation_targets(
    package: MaterialPackage,
    *,
    checklist_text: str,
    checklist_path: Path,
    evidence_text: str | None = None,
    evidence_path: Path | None = None,
    include_blocked: bool = False,
) -> ValidationTargetCatalog:
    ...


def target_by_id(catalog: ValidationTargetCatalog, target_id: str) -> ValidationTarget:
    ...


def render_validation_target_lines(
    catalog: ValidationTargetCatalog,
    *,
    priority: str | None = None,
    target_id: str | None = None,
    include_draft_command: bool = True,
) -> list[str]:
    ...


def acceptance_draft_command(package_id: str, target: ValidationTarget) -> str:
    ...
```

Draft command rule:

- Always include `--checklist-target "P0 Add coworkers modal"` style context.
- Include `--entrypoint` only when the target has exactly one entrypoint.
- Include `--flow` only when the target has exactly one flow.
- For grouped targets with multiple entrypoints, list all entrypoints but do not invent one command that implies a
  single route. The operator can generate per-entrypoint drafts after choosing the exact sub-route.

## Proposed CLI

Command shape:

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target p0-add-coworkers-modal
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

Options:

- `--package`: required, same resolver as `flows`, `entrypoints`, and `acceptance-draft`.
- `--priority`: optional `P0`, `P1`, `P2`, or `P3` filter.
- `--target`: optional discovered target id for detailed output.
- `--checklist`: optional path override, default `docs/knowledge/ringcentral-video/validation-checklist-index.md`.
- `--evidence`: optional path override, default `docs/knowledge/ringcentral-video/evidence-index.md`.
- `--include-blocked`: include `Do Not Execute Yet` rows.

Suggested output for the first P0 route:

```text
Package: ringcentral-video
Checklist: docs/knowledge/ringcentral-video/validation-checklist-index.md

- p0-add-coworkers-modal [P0] Add coworkers modal
  entrypoints: ringcentral.video.main.add-coworkers
  evidence: ringcentral.video.main.add-coworkers=Observed
  current: Observed UIA button, package route repo-tested, no live click acceptance
  validate: In a disposable empty-room meeting, click Add coworkers, confirm Invite/Add coworkers dialog opens, then close it
  cleanup: Modal close by X or Cancel; confirm toolbar is usable again
  privacy: Do not read or store invite links, emails, names, or suggestions
  draft: ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers --checklist-target "P0 Add coworkers modal"
```

## Parsing Strategy

Use the package loader for YAML and a small deterministic Markdown table parser for the two docs.

Checklist parser:

1. Find the `## Priority Checklist` section.
2. Parse the first pipe table in that section by header name, not by fixed column index.
3. Normalize headers with `strip().casefold()`.
4. Extract rows with headers:
   - `priority`
   - `route or group`
   - `entrypoints`
   - `current state`
   - `validate`
   - `cleanup`
   - `privacy boundary`
   - `record result`
5. Extract backticked identifiers only from the `Entrypoints` cell with `` `([^`]+)` ``.
6. Classify each extracted id:
   - if it exists in `package.entrypoints_by_id`, add it to `entrypoint_ids`;
   - if it exists in `package.demo_flows_by_id`, add it to `flow_ids`;
   - otherwise raise `ValueError("Checklist target ... references unknown package id: ...")`.
7. Generate a target id:
   - if a future table has an `ID` or `Target ID` column, use it after validating uniqueness;
   - otherwise derive `"{priority.lower()}-{slug(route_or_group)}"`, such as `p0-add-coworkers-modal`.
8. Validate target id uniqueness and fail loudly on duplicates.

Blocked parser:

- Parse `## Do Not Execute Yet` only when `include_blocked=True`.
- Convert each row into a target with `blocked_reason` set from the `Reason` column.
- Assign ids such as `blocked-recording` and `blocked-leave-or-end-meeting`.
- Validate the backticked entrypoint id against `package.entrypoints_by_id`.

Evidence parser:

1. Find the `## Entry Point Evidence Table` section.
2. Parse columns `Entrypoint`, `Evidence Level`, and `Main Gap`.
3. Build maps by entrypoint id.
4. Treat evidence as context only. Missing evidence rows should not block discovery, but referenced package
   entrypoints missing from evidence should be visible in output as `evidence: unknown`.

Markdown parser constraints:

- A minimal pipe-table splitter is enough for the current docs because table cells do not contain escaped pipes.
- Keep parser failures explicit and actionable.
- Do not parse checklist prose as evidence.
- Keep all file reads UTF-8.

## Exact Tests To Add

Create `tests/unit/test_validation_targets.py`:

- `test_discover_validation_targets_reads_priority_checklist_rows`
  - Load `packages/ringcentral-video.yaml`.
  - Read `validation-checklist-index.md` and `evidence-index.md`.
  - Assert discovered priority targets include `p0-add-coworkers-modal`.
  - Assert that target has priority `P0`, route `Add coworkers modal`, entrypoint ids
    `("ringcentral.video.main.add-coworkers",)`, no flow ids, current state containing `no live click acceptance`,
    cleanup containing `Modal close`, privacy containing `invite links`, and evidence level `Observed`.
- `test_discover_validation_targets_separates_flow_ids_from_entrypoints`
  - Assert `p0-controller-queued-chat-question` has entrypoint id `ringcentral.video.toolbar.chat` and flow id
    `meeting-control-map-demo`.
- `test_discover_validation_targets_filters_by_priority_in_renderer`
  - Render with `priority="P0"`.
  - Assert output includes `p0-add-coworkers-modal` and `p0-controller-queued-chat-question`.
  - Assert output does not include `p1-top-bar-coordinate-routes`.
- `test_target_by_id_reports_available_ids_for_missing_target`
  - Call `target_by_id(catalog, "missing-target")`.
  - Assert the error includes `Unknown validation target: missing-target` and at least one available id.
- `test_discover_validation_targets_rejects_unknown_checklist_entrypoint`
  - Replace `ringcentral.video.toolbar.chat` with `ringcentral.video.toolbar.missing` in checklist text.
  - Assert `ValueError` names the unknown id and the route/group row.
- `test_discover_validation_targets_rejects_duplicate_generated_ids`
  - Append a duplicate `P0 | Add coworkers modal | ...` checklist row.
  - Assert `ValueError` names duplicate target id `p0-add-coworkers-modal`.
- `test_discover_validation_targets_can_include_blocked_rows`
  - Discover with `include_blocked=True`.
  - Assert blocked targets include `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave`.
  - Assert `blocked_reason` contains `consent` for recording and `destructive` for leave.
- `test_acceptance_draft_command_uses_entrypoint_only_for_single_entrypoint_target`
  - For `p0-add-coworkers-modal`, assert command contains `--entrypoint ringcentral.video.main.add-coworkers`
    and `--checklist-target "P0 Add coworkers modal"`.
- `test_acceptance_draft_command_omits_entrypoint_for_group_target`
  - For `p1-top-bar-coordinate-routes`, assert command contains `--checklist-target "P1 Top-bar coordinate routes"`
    and does not contain `--entrypoint`.

Add to `tests/unit/test_cli.py`:

- `test_validation_targets_lists_ringcentral_targets`
  - Invoke `["validation-targets", "--package", "ringcentral-video", "--priority", "P0"]`.
  - Assert exit code `0`, package id, checklist path, `p0-add-coworkers-modal`, `p0-controller-queued-chat-question`,
    and no `Loaded profile`.
- `test_validation_targets_detail_outputs_draft_command`
  - Invoke `["validation-targets", "--package", "ringcentral-video", "--target", "p0-add-coworkers-modal"]`.
  - Assert output includes the single entrypoint, cleanup text, privacy text, and the safe `acceptance-draft` command.
- `test_validation_targets_rejects_unknown_target_with_available_ids`
  - Invoke with `--target missing-target`.
  - Assert nonzero exit and output includes `Unknown validation target: missing-target` plus `p0-add-coworkers-modal`.
- `test_validation_targets_rejects_unknown_checklist_reference`
  - Create a temp checklist file with one row referencing `ringcentral.video.missing`.
  - Invoke `validation-targets` with `--checklist <temp path>`.
  - Assert nonzero exit and output names the unknown id.
- `test_validation_targets_include_blocked_lists_do_not_execute_routes`
  - Invoke with `--include-blocked`.
  - Assert output includes `ringcentral.video.more.recording`, `ringcentral.video.toolbar.leave`, and `Do not execute`.

Do not add live RingCentral tests. Do not write acceptance records during tests.

## Risks And Guardrails

- Evidence inflation: output must not say a target passed or is accepted. It can say evidence level from
  `evidence-index.md`, but must keep that separate from acceptance results.
- Markdown brittleness: parsing docs is acceptable for this helper, but errors should be explicit. If checklist text
  starts changing often, add a stable `Target ID` column in a separate docs/schema cycle.
- Derived ids are only as stable as the route/group labels. For Cycle 021, deterministic slugs are enough; future docs
  can add explicit ids without changing the CLI surface.
- Group target ambiguity: multiple-entrypoint rows should not generate a draft command that pretends one route was
  selected. Use checklist-target-only commands for groups.
- Unknown backticked ids: validate only ids in the `Entrypoints` cell. Backticks elsewhere in docs can be filenames,
  evidence ids, or commands.
- Blocked route safety: recording and leave/end can be displayed for awareness, but keep them out of default output
  unless `--include-blocked` is passed.
- Import boundaries: `validation_targets.py` should import package models only. Do not import `runtime.factory`,
  `controller`, `desktop`, `diagnostics`, or any Windows driver.
- Output encoding: keep structural output ASCII-friendly. Package text may contain existing mojibake; discovery should
  not try to repair or reinterpret it.

## Implementation Order

1. Add `tests/unit/test_validation_targets.py` with the pure discovery tests above.
2. Implement `src/ai_presenter/acceptance/validation_targets.py` using only `MaterialPackage` models and strings.
3. Export the new public objects from `src/ai_presenter/acceptance/__init__.py`.
4. Add CLI tests in `tests/unit/test_cli.py`.
5. Add `validation-targets` in `src/ai_presenter/cli.py`, using `resolve_material_package()` and
   `load_material_package()`.
6. Keep output read-only and command-oriented; do not write target reports to files in the first slice.
7. Run focused tests, then full verification.

## Verification Commands

Focused future implementation checks:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py tests\unit\test_acceptance_manual_record.py tests\unit\test_material_packages.py
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\acceptance src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
git diff --check -- src\ai_presenter\acceptance src\ai_presenter\cli.py tests\unit\test_validation_targets.py tests\unit\test_cli.py
```

Scan-only verification:

```powershell
git diff --check -- docs\agent-handoffs\cycle-021-technical-scan.md
git status --short -- docs\agent-handoffs\cycle-021-technical-scan.md
```

## Key Recommendation

Build target discovery as a pure checklist/evidence reader beside the existing acceptance draft helper. The CLI should
validate package ids, list the next validation targets with cleanup and privacy boundaries, and print draft-safe
commands. It should not change the package schema, touch RingCentral automation, or write acceptance evidence.
