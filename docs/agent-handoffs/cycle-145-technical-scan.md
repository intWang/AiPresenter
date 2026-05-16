# Cycle 145 Technical Scan: validation-targets Evidence Boundary Note

Date: 2026-05-17
Cycle: 145
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

This scan is docs-only. It does not change source, tests, packages, or coverage artifacts.

Topic: keep `validation-targets` CLI output explicit that the list is repo-derived planning material only, not live acceptance evidence.

## Existing Output Note

Current implementation already has the required note:

- `src/ai_presenter/acceptance/validation_targets.py:28` defines `_NON_EVIDENCE_NOTE = "repo-derived planning list only; not live acceptance evidence."`
- `src/ai_presenter/acceptance/validation_targets.py:159` renders it as `Note: repo-derived planning list only; not live acceptance evidence.`
- `src/ai_presenter/cli.py:329` to `src/ai_presenter/cli.py:364` routes `validation-targets` through `render_validation_target_lines`, so normal list, priority-filtered, detail, and blocked output share the same header note.

The implementation does not currently appear to lack the note, so this scan does not recommend a source edit.

## Existing Test Gap

`tests/unit/test_cli.py` has good behavioral coverage for the command:

- `test_validation_targets_lists_ringcentral_targets` checks package, checklist path, target ids, and that profile loading noise is absent.
- `test_validation_targets_detail_outputs_draft_command` checks a normal detail target and draft command.
- `test_validation_targets_mixed_target_outputs_flow_and_entrypoint_draft_command` checks mixed flow and entrypoint draft output.
- `test_validation_targets_rejects_unknown_target_with_available_ids` checks missing target diagnostics.
- `test_validation_targets_rejects_unknown_checklist_reference` checks checklist integrity failure.
- `test_validation_targets_include_blocked_lists_do_not_execute_routes` checks blocked rows are listable.
- `test_validation_targets_blocked_target_omits_draft_command` checks blocked routes do not offer draft commands.

None of those tests currently asserts the evidence-boundary note.

`tests/unit/test_validation_targets.py` covers parser integrity, target ids, evidence index integrity, renderer filtering, blocked rendering, and draft command generation. It currently checks draft command presence or absence, but it does not directly pin the renderer-level note.

`test_acceptance_draft_*` tests are adjacent but not the best guard for this issue. They verify draft templates and refusal behavior; `acceptance-draft` is a separate command and should keep its own `Draft only` boundary. The `validation-targets` note should be guarded on the `validation-targets` renderer/CLI path instead.

## Recommended Minimal Guards

1. Extend `tests/unit/test_cli.py::test_validation_targets_lists_ringcentral_targets`.

Expected assertion:

```python
note = "Note: repo-derived planning list only; not live acceptance evidence."
assert note in result.stdout
assert result.stdout.count(note) == 1
```

Why here: this is the narrowest CLI-level smoke test for the standard `validation-targets` path. It already invokes the command with `--priority P0`, proving the note survives filtered output.

2. Add `tests/unit/test_validation_targets.py::test_render_validation_target_lines_marks_output_as_planning_only`.

Expected assertion:

```python
catalog = discover_catalog()
lines = render_validation_target_lines(catalog, target_id="rcv-add-coworkers-modal")

assert "Note: repo-derived planning list only; not live acceptance evidence." in lines
assert lines.count("Note: repo-derived planning list only; not live acceptance evidence.") == 1
```

Why here: this pins the shared renderer contract without going through Typer. If a future CLI or caller reuses `render_validation_target_lines`, the boundary remains protected.

Optional alternative: if maintainers prefer no new test, extend `test_discover_validation_targets_filters_by_priority_in_renderer` with the same exact-note assertion after it joins the rendered lines. A separate test gives a clearer failure name.

## Focused Verification Commands

After adding the guard assertions, run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_validation_targets.py::test_render_validation_target_lines_marks_output_as_planning_only
```

If choosing to extend the existing renderer test instead of adding a new one, use:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_validation_targets.py::test_discover_validation_targets_filters_by_priority_in_renderer
```

For a wider but still focused acceptance sweep of this feature area:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes tests\unit\test_cli.py::test_validation_targets_blocked_target_omits_draft_command tests\unit\test_validation_targets.py
```

## Risk Boundary

- Do not promote checklist rows, CLI inspection, dry runs, `doctor`, or repo-local tests into live RingCentral acceptance evidence.
- Do not edit package YAML, profile/provider config, controller behavior, locator routes, acceptance run records, or generated coverage as part of this guard.
- Do not stage or revert `.coverage`; current status shows it as an unrelated dirty artifact.
- Keep the assertion exact enough to catch semantic drift from `not live acceptance evidence`.
- Avoid asserting every output mode unless a future refactor introduces separate render paths. Today the CLI shares the renderer, so one CLI smoke assertion plus one renderer contract assertion is enough.
- If future implementation removes the note, document the missing note first; source changes should be handled by a separate implementation task.

## Current Scan Result

The smallest practical guard is a pair of wording assertions:

- CLI guard: extend `test_validation_targets_lists_ringcentral_targets`.
- Renderer guard: add `test_render_validation_target_lines_marks_output_as_planning_only`.

This preserves the existing behavior while making the evidence boundary durable.
