# Cycle 018 Technical Scan: Manual Acceptance Record Helper

Date: 2026-05-16

## Scope

Scan target: propose an implementation path for a safe RingCentral Video manual acceptance record helper.

Safety boundary: the helper must not automate, click, observe, or bind RingCentral. It should only generate a markdown draft/template that a human can fill after a manual run. The draft must preserve the evidence discipline from `docs/knowledge/ringcentral-video/acceptance-runs.md` and `docs/knowledge/ringcentral-video/validation-checklist-index.md`: checklist procedure is not acceptance evidence until a dated run is recorded.

## Existing CLI Architecture And Relevant Functions

`src/ai_presenter/cli.py` is a single Typer app with top-level commands:

- `run`: loads a profile and can run desktop automation unless `--dry-run` is supplied.
- `demo`: loads profile/package/flow, validates voice/profile compatibility, and can run `run_material_demo`.
- `controller`: loads profile/package/flow and can open the local controller.
- `flows`: lists package demo flows.
- `entrypoints`: lists package operation entrypoints, optionally filtered by `--area`.
- `voices`: lists voice choices and checks profile compatibility.
- `doctor`: validates profile/package/flow/local RingCentral prerequisites.

The safe helper should follow the lightweight CLI patterns used by `flows` and `entrypoints`, not the runtime patterns used by `run`, `demo`, or `controller`.

Relevant existing helpers:

- `resolve_material_package(package: str) -> Path` in `src/ai_presenter/cli.py` resolves either a YAML path or a package id from `packages/`.
- `load_material_package(path: Path) -> MaterialPackage` in `src/ai_presenter/packages/loader.py` reads YAML with `yaml.safe_load` and validates it with Pydantic.
- `MaterialPackage.entrypoint_by_id(entrypoint_id: str)` in `src/ai_presenter/packages/models.py` raises `KeyError("Unknown operation entrypoint: ...")`.
- `MaterialPackage.demo_flow_by_id(flow_id: str)` raises `KeyError("Unknown demo flow: ... Available flows: ...")`.
- `MaterialPackage.entrypoints_by_id` and `demo_flows_by_id` expose read-only indexes already suited for target validation.
- `ai_presenter.runtime.package_demo.demo_flow_by_id` is currently imported by CLI for `demo` and `controller`, but a draft helper can call `MaterialPackage.demo_flow_by_id` directly or reuse the wrapper only for consistent error text.

Test architecture:

- `tests/unit/test_cli.py` uses `CliRunner().invoke(app, [...])` and checks stdout/errors for command behavior.
- `tests/unit/test_material_packages.py` already verifies RingCentral package shape and Cycle 017 checklist coverage.
- Existing tests are unit-friendly and do not require RingCentral for CLI dry-run/listing behavior.

## Acceptance Record Requirements To Preserve

The generated manual draft should include every field from the Manual Acceptance Template in `docs/knowledge/ringcentral-video/acceptance-runs.md`:

- `Tester`
- `RingCentral app/build`
- `App channel`
- `Windows version`
- `Locale`
- `DPI/display scale`
- `Monitor setup`
- `Audio devices`
- `Virtual mic`
- `Profile`
- `Package flow`
- `Meeting role`
- `Meeting scenario`
- `Participant count`
- `Window bounds`
- `Evidence files`
- `Steps executed`
- `Pass/fail`
- `Failures`
- `Recovery`
- `Privacy notes`
- `Locator updates needed`

The draft should also make the Cycle 017 validation discipline visible:

- Include selected package id, app name, and package version.
- Include selected flow id/title/goal when `--flow` is used.
- Include selected entrypoint id/title/area/purpose/open-step summary/presenter notes when `--entrypoint` is used.
- Include selected checklist target text when `--checklist-target` is used.
- Include a short "Do not record as accepted until filled after the manual run" note.
- Include "Post-run documentation order": append to `acceptance-runs.md` first, then update `locator-matrix.md`, `state-matrix.md`, `privacy-matrix.md`, and `evidence-index.md` only if confidence or policy changed.
- Preserve privacy boundaries from the checklist target/package notes where available, especially for invite/chat/participants/share/notes/recording/leave.

## Recommended Module And Function Boundaries

Add a small pure rendering module. Keep it independent from `runtime`, `desktop`, `controller`, `diagnostics`, and all RingCentral window drivers.

Recommended module:

- `src/ai_presenter/acceptance/__init__.py`
- `src/ai_presenter/acceptance/manual_record.py`

Recommended types/functions:

- `AcceptanceDraftRequest`
  - Dataclass carrying optional `profile_id`, `flow_id`, `entrypoint_id`, `checklist_target`, `tester`, `local_timestamp`, and any prefilled environment fields.
- `AcceptanceTargetSummary`
  - Dataclass carrying package/flow/entrypoint/checklist context for rendering.
- `build_acceptance_target_summary(package: MaterialPackage, request: AcceptanceDraftRequest) -> AcceptanceTargetSummary`
  - Validates selected flow/entrypoint IDs using package indexes.
  - If a flow is selected, include all flow step ids and their referenced entrypoint ids.
  - If an entrypoint is selected, include open steps and notes.
  - If a checklist target is selected, include the raw target label/text; do not treat it as evidence.
- `render_manual_acceptance_draft(package: MaterialPackage, request: AcceptanceDraftRequest) -> str`
  - Pure function returning markdown.
  - No filesystem writes, no desktop calls, deterministic enough for snapshot-style assertions.
- `format_open_steps(entrypoint: OperationEntrypoint) -> list[str]`
  - Converts package `openSteps` into human-readable checklist lines like `clickWindowControl target=Chat cleanup=toggle`.
- `required_manual_acceptance_fields() -> tuple[str, ...]`
  - Centralizes the field list so tests can assert all acceptance template fields are present.

Optional second-slice helper:

- `read_validation_checklist_targets(path: Path) -> list[ValidationChecklistTarget]`
  - Parses the Priority Checklist markdown table only if needed.
  - Treat parser failures as CLI errors for `--list-checklist-targets`, not as blockers for basic package/flow/entrypoint draft rendering.
  - Do not make this parser the source of truth for acceptance evidence.

Recommended CLI command:

- `acceptance-draft`
  - `--package`: required, same resolver as `flows` and `entrypoints`.
  - `--profile`: optional prefill only; do not load or run the profile unless a later cycle explicitly needs profile validation.
  - `--flow`: optional package flow id.
  - `--entrypoint`: optional package entrypoint id.
  - `--checklist-target`: optional free-text checklist target label or route group.
  - `--tester`: optional prefill.
  - `--local-time`: optional prefill for deterministic tests; default can be a placeholder rather than current time.
  - `--output`: optional path to write the draft. If omitted, echo to stdout.

Target selection rule:

- Require at least one of `--flow`, `--entrypoint`, or `--checklist-target`.
- Allow `--flow` plus `--entrypoint` only when the entrypoint appears in that flow; otherwise fail with a clear `BadParameter`.
- Allow checklist target alongside package targets as descriptive context only.

## Exact Files Likely To Change

Production:

- `src/ai_presenter/acceptance/__init__.py`
  - New package marker and optional public exports.
- `src/ai_presenter/acceptance/manual_record.py`
  - New pure request/summary/rendering logic.
- `src/ai_presenter/cli.py`
  - Import the rendering module.
  - Add `@app.command("acceptance-draft")`.
  - Use `resolve_material_package` and `load_material_package`.
  - Convert `KeyError` from flow/entrypoint lookup into `typer.BadParameter`, matching existing `demo`/`controller` behavior.

Tests:

- `tests/unit/test_acceptance_manual_record.py`
  - New focused unit tests for pure rendering and target validation.
- `tests/unit/test_cli.py`
  - Add command integration tests with `CliRunner`.

Docs, optional after the helper exists:

- `docs/runbooks/ringcentral-manual-acceptance.md`
  - Add one line showing the helper command, but keep runbook checkboxes separate from evidence.
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
  - No automatic edit. A generated draft should be copied/appended by a human after the run is actually performed.

Avoid changing:

- `packages/ringcentral-video.yaml` for this first helper. The Cycle 017 summary notes that package-local route metadata should be a separate schema cycle.
- `src/ai_presenter/runtime/*`, `src/ai_presenter/desktop/*`, and controller automation modules.

## TDD-Friendly Tests To Add

Pure renderer tests in `tests/unit/test_acceptance_manual_record.py`:

- `test_manual_acceptance_draft_includes_all_required_template_fields`
  - Load `packages/ringcentral-video.yaml`.
  - Render a draft for `entrypoint_id="ringcentral.video.main.add-coworkers"`.
  - Assert every required field from `acceptance-runs.md` appears exactly as a markdown bullet label.
- `test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance`
  - Assert draft includes `ringcentral.video.main.add-coworkers`, `Add coworkers`, `Meeting canvas`, `clickWindowControl`, `cleanup=modal`, and privacy/notes text.
  - Assert it includes wording like `Draft only` or `Not acceptance evidence until filled after the manual run`.
- `test_manual_acceptance_draft_prefills_flow_steps`
  - Render with `flow_id="meeting-control-map-demo"`.
  - Assert flow title `Meeting Control Map`, goal, and representative referenced entrypoints such as `ringcentral.video.toolbar.chat`.
- `test_acceptance_draft_rejects_unknown_entrypoint`
  - Expect `KeyError` or a module-specific `ValueError` with `Unknown operation entrypoint`.
- `test_acceptance_draft_rejects_entrypoint_not_in_selected_flow`
  - Use a real flow and an entrypoint not referenced by that flow if available; otherwise construct a minimal package in-memory or tmp YAML.
- `test_required_manual_acceptance_fields_matches_acceptance_runs_template`
  - Optional guard that reads `docs/knowledge/ringcentral-video/acceptance-runs.md` and compares field labels inside the Manual Acceptance Template to `required_manual_acceptance_fields()`.

CLI tests in `tests/unit/test_cli.py`:

- `test_acceptance_draft_outputs_entrypoint_template`
  - `CliRunner().invoke(app, ["acceptance-draft", "--package", "ringcentral-video", "--entrypoint", "ringcentral.video.toolbar.chat"])`
  - Assert exit code 0, package id, entrypoint id, `Privacy notes:`, `Locator updates needed:`, and no runtime automation text like `Loaded profile`.
- `test_acceptance_draft_outputs_flow_template`
  - Use `--flow meeting-control-map-demo`.
  - Assert flow context and referenced entrypoints are present.
- `test_acceptance_draft_requires_target`
  - Invoke with only `--package`.
  - Assert nonzero and a clear message naming `--flow`, `--entrypoint`, or `--checklist-target`.
- `test_acceptance_draft_rejects_missing_flow_with_available_flows`
  - Assert output includes `Unknown demo flow: missing-flow` and `Available flows:`.
- `test_acceptance_draft_can_write_to_output_file`
  - Use `tmp_path / "acceptance-draft.md"` and assert file content equals or contains rendered stdout-free draft.

Suggested verification commands:

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py`
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests`
- `.\.venv\Scripts\python -m ruff check --no-cache .`
- `.\.venv\Scripts\python -m mypy --no-incremental src tests`

No test should launch or click RingCentral.

## Edge Cases And Risks

- Evidence inflation: the helper must not use `Accepted`, `pass`, or evidence ids as defaults. Use blank `Pass/fail:` and explicit draft language.
- Timestamp ambiguity: defaulting to current time can make tests flaky. Prefer a placeholder in pure rendering and let CLI optionally fill current local time only if requested, or expose `--local-time` for deterministic tests.
- Flow versus entrypoint mismatch: if both are supplied, validate that the entrypoint appears in the selected flow so the draft does not imply the wrong run scope.
- Checklist parsing brittleness: markdown tables are documentation, not stable APIs. First slice can accept `--checklist-target` as text; parse/list checklist rows only in a later slice if needed.
- Privacy-sensitive notes: package presenter notes include useful policy text, but the helper should not infer private data. It should remind the tester what not to read/capture.
- Destructive or blocked routes: `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave` have no executable `openSteps` and are listed as Do Not Execute Yet. Drafts for these should say explain-only/blocked and leave steps blank rather than inventing actions.
- File writes: `--output` should create only the requested draft path. It should not append to `acceptance-runs.md` automatically, because only a filled post-run record is evidence.
- Encoding: several package localized strings are mojibake/non-ASCII in existing fixtures. Keep generated structural labels ASCII-safe where possible; include package text only as loaded.
- Typer option names: use a single command name and explicit options so it fits current `CliRunner` tests and Windows shell examples.
- Import risk: do not import `runtime.factory`, `controller`, `desktop`, or `diagnostics`; those modules can touch automation concerns or environment checks irrelevant to a draft.

## Safe Implementation Path

1. Write failing pure renderer tests for required template fields and entrypoint context.
2. Create `src/ai_presenter/acceptance/manual_record.py` with dataclasses, the required field tuple, and markdown rendering.
3. Make the pure tests pass using only `MaterialPackage`, `DemoFlow`, and `OperationEntrypoint` data.
4. Add flow rendering tests and the flow/entrypoint mismatch test.
5. Add `acceptance-draft` CLI tests in `tests/unit/test_cli.py`.
6. Add the Typer command in `src/ai_presenter/cli.py`, using existing `resolve_material_package` and `load_material_package`.
7. Add `--output` only after stdout rendering is covered; keep file writing in the CLI command, not in the pure renderer.
8. Run focused tests, then full unit suite, ruff, and mypy.
9. Optionally update `docs/runbooks/ringcentral-manual-acceptance.md` with a single helper example after implementation passes.

Recommended first command shape:

```powershell
.\.venv\Scripts\ai-presenter acceptance-draft `
  --package ringcentral-video `
  --entrypoint ringcentral.video.main.add-coworkers `
  --checklist-target "P0 Add coworkers modal" `
  --output docs\knowledge\ringcentral-video\drafts\add-coworkers-acceptance-draft.md
```

The output path above is only an example for a future implementation. The helper should not write to `acceptance-runs.md` unless a human explicitly chooses to append a completed, truthful post-run record.
