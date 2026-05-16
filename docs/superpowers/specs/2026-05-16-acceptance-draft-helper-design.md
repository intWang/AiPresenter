# Acceptance Draft Helper Design

Date: 2026-05-16

## Context

Cycle 017 added `docs/knowledge/ringcentral-video/validation-checklist-index.md`, which makes RingCentral Video manual validation targets easier to choose. The next friction point is evidence recording: `acceptance-runs.md` has a detailed manual template, but operators still have to hand-copy package, flow, entrypoint, cleanup, privacy, and post-run update context.

This design adds an offline helper that prepares a markdown draft. It does not validate RingCentral, click RingCentral, append proof, promote evidence levels, or collect private runtime data.

## Product Shape

Add a CLI command:

```powershell
.\.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers
```

The command renders a markdown draft to stdout. It can optionally write the same draft to a user-specified file with `--output`.

Supported inputs:

- `--package`: required material package id or YAML path.
- `--entrypoint`: optional operation entrypoint id.
- `--flow`: optional demo flow id.
- `--checklist-target`: optional descriptive label copied from the validation checklist.
- `--profile`: optional text prefill only; this command does not load or validate profiles.
- `--tester`: optional text prefill.
- `--local-time`: optional text prefill for deterministic draft headers.
- `--output`: optional file path for the draft.

At least one of `--entrypoint`, `--flow`, or `--checklist-target` is required. If both `--flow` and `--entrypoint` are supplied, the entrypoint must appear in the flow.

## Architecture

Create a pure rendering module:

- `src/ai_presenter/acceptance/__init__.py`
- `src/ai_presenter/acceptance/manual_record.py`

The module will own:

- `AcceptanceDraftRequest`: immutable request dataclass.
- `AcceptanceTargetSummary`: immutable summary dataclass.
- `required_manual_acceptance_fields()`: canonical field labels from `acceptance-runs.md`.
- `build_acceptance_target_summary(package, request)`: validates package target choices.
- `render_manual_acceptance_draft(package, request)`: returns markdown.

The CLI command will:

- Resolve and load the package using existing `resolve_material_package` and `load_material_package`.
- Build the request from CLI options.
- Convert `ValueError` or `KeyError` from target validation into `typer.BadParameter`.
- Echo the draft to stdout unless `--output` is supplied.
- Write only the requested output path when `--output` is supplied.

No runtime/controller/desktop modules should be imported by the new renderer.

## Draft Content

The draft must include:

- A clear draft-only warning.
- Package id, app name, version.
- Optional profile text.
- Optional flow id, title, goal, and referenced entrypoints.
- Optional entrypoint id, title, area, purpose, open steps, and presenter notes.
- Optional checklist target text.
- Every manual template field from `acceptance-runs.md`.
- Blank or placeholder proof fields for pass/fail, failures, recovery, evidence files, privacy notes, and locator updates.
- Post-run documentation order: update `acceptance-runs.md` first, then locator/state/privacy/evidence docs only when the completed run justifies it.

The draft must not:

- Mark anything as passed.
- Use `Accepted` as a default status.
- Claim RingCentral was clicked.
- Insert evidence ids.
- Read or include chat text, participant names, invite links, meeting IDs, shared-screen content, device lists, notes, transcripts, account details, or report contents.

For explain-only or blocked routes such as `ringcentral.video.more.recording` and `ringcentral.video.toolbar.leave`, the draft should preserve package context and warn that the operator should not execute the live action without a separate confirmation workflow.

## Acceptance Criteria

- Pure renderer tests prove every required manual acceptance field appears.
- Entry point draft for `ringcentral.video.main.add-coworkers` includes `clickWindowControl`, `cleanup=modal`, draft-only wording, and Add coworkers context.
- Flow draft for `meeting-control-map-demo` includes flow title/goal and representative referenced entrypoints.
- Unknown entrypoint and unknown flow errors are clear.
- Supplying a flow plus an unrelated entrypoint fails.
- CLI emits stdout draft for entrypoint and flow targets.
- CLI rejects missing target options.
- CLI can write to an output file without appending to `acceptance-runs.md`.
- Existing run/demo/controller/flows/entrypoints/voices/doctor behavior remains unchanged.

## Non-Goals

- No live RingCentral automation or observation.
- No automatic append to `acceptance-runs.md`.
- No checklist markdown parser in this slice.
- No package schema changes.
- No route evidence promotion.
- No profile loading or voice validation in `acceptance-draft`.

## Verification

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\python -m ruff check --no-cache .
.\.venv\Scripts\python -m mypy --no-incremental src tests
```

Expected: all tests pass with the existing pywinauto STA warning only where pytest imports pywinauto.

## Risks

- A draft can look official. The warning must be prominent and repeated near proof fields.
- Markdown output can drift from `acceptance-runs.md`. The required field list should be centralized and optionally tested against the template.
- File writes can be mistaken for evidence. `--output` must write a draft file only and should not special-case `acceptance-runs.md`.
- Checklist parsing is tempting but brittle. This slice accepts checklist target text as context only.
