# Cycle 146 Technical Scan: validation-targets Traceability Header Guard

Date: 2026-05-17
Cycle: 146
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Docs-only technical scan. Do not edit source, tests, package YAML, `.coverage`, or generated artifacts in this subtask.

Topic: keep `validation-targets` output traceable to its checklist and evidence source paths, and keep renderer behavior explicit when no evidence path is present.

Boundaries:

- Do not run or record live acceptance.
- Do not stage, delete, overwrite, normalize, or revert `.coverage`.
- Do not revert unrelated work from other agents.

## Current Implementation

`src/ai_presenter/acceptance/validation_targets.py::render_validation_target_lines` already renders a shared header before target blocks:

```text
Package: <package id>
Checklist: <display path>
Evidence: <display path or none>
Note: repo-derived planning list only; not live acceptance evidence.
```

Relevant behavior:

- `Checklist:` always renders `_display_path(catalog.checklist_path)`.
- `Evidence:` renders `_display_path(catalog.evidence_path)` when `catalog.evidence_path` is set.
- `Evidence:` renders `none` when `catalog.evidence_path` is `None`.
- CLI `validation-targets` in `src/ai_presenter/cli.py` reads both default paths and passes them into `discover_validation_targets`, then prints `render_validation_target_lines`.

No source change appears necessary for the requested guard. The behavior exists; the missing piece is durable test coverage for the traceability header.

## Existing Coverage

`tests/unit/test_cli.py::test_validation_targets_lists_ringcentral_targets` already checks:

- command succeeds for `validation-targets --package ringcentral-video --priority P0`;
- `Package: ringcentral-video` is present;
- `validation-checklist-index.md` is present;
- the non-evidence note is present;
- expected P0 target ids are present;
- profile loading noise is absent.

It does not currently assert `evidence-index.md`, so CLI output could lose the evidence path while this test still passes.

`tests/unit/test_validation_targets.py` has renderer coverage for filtering, blocked target draft suppression, normal draft command output, target lookup, catalog integrity, and evidence index parsing. It does not currently have a focused renderer test that pins the header source paths. It also does not have an adjacent renderer test for the `evidence_path=None` fallback that must display `Evidence: none`.

Cycle 145 already added/pinned the non-evidence note in both CLI-adjacent and renderer-adjacent tests. Cycle 146 should stay next to that guard and focus only on checklist/evidence traceability.

## Test Gaps

1. CLI traceability gap:

The primary CLI smoke test checks the checklist file name but not the evidence file name. A future regression could omit or rename the `Evidence:` header, or stop passing the evidence path to the renderer, without failing the existing CLI test.

2. Renderer traceability gap:

Renderer tests do not directly assert the header lines as a contract. Existing tests join output and check target content, notes, and draft commands, but they do not pin both source path lines together.

3. Missing evidence path fallback gap:

`render_validation_target_lines` has explicit logic for `catalog.evidence_path is None`, but there is no small test proving the output says `Evidence: none`. This matters because a catalog can be built without evidence text/path, and the user-facing output should distinguish "no evidence source attached" from an omitted header.

## Recommended Minimal Tests

### CLI Guard

Extend `tests/unit/test_cli.py::test_validation_targets_lists_ringcentral_targets`.

Suggested assertions:

```python
assert "Checklist: " in result.stdout
assert "validation-checklist-index.md" in result.stdout
assert "Evidence: " in result.stdout
assert "evidence-index.md" in result.stdout
```

The test already asserts `validation-checklist-index.md`; the smallest practical change is to add the two `Evidence` assertions. Keeping `Checklist:` as an explicit assertion is useful if maintainers want the header label guarded, not just the file name.

Why here: this is the narrowest CLI-level path for the normal command. It already exercises priority-filtered output, so the guard proves the traceability header survives a common filtered invocation.

### Renderer Header Guard

Add `tests/unit/test_validation_targets.py::test_render_validation_target_lines_includes_source_paths`.

Suggested shape:

```python
def test_render_validation_target_lines_includes_source_paths() -> None:
    catalog = discover_catalog()

    lines = render_validation_target_lines(catalog, priority="P0")
    text = "\n".join(lines)

    assert "Checklist: " in text
    assert "validation-checklist-index.md" in text
    assert "Evidence: " in text
    assert "evidence-index.md" in text
```

Optional tighter variant:

```python
assert any(
    line.startswith("Checklist: ") and "validation-checklist-index.md" in line
    for line in lines
)
assert any(
    line.startswith("Evidence: ") and "evidence-index.md" in line
    for line in lines
)
```

Why here: this pins the shared renderer contract without Typer. If future callers use the renderer outside the CLI, the source header remains protected.

### Renderer Missing Evidence Guard

Add `tests/unit/test_validation_targets.py::test_render_validation_target_lines_marks_missing_evidence_path_as_none`.

Suggested shape:

```python
def test_render_validation_target_lines_marks_missing_evidence_path_as_none() -> None:
    catalog = discover_validation_targets(
        load_ringcentral_package(),
        checklist_text=load_checklist_text(),
        checklist_path=Path("docs/knowledge/ringcentral-video/validation-checklist-index.md"),
        evidence_text=None,
        evidence_path=None,
    )

    text = "\n".join(
        render_validation_target_lines(catalog, target_id="rcv-add-coworkers-modal")
    )

    assert "Checklist: " in text
    assert "validation-checklist-index.md" in text
    assert "Evidence: none" in text
    assert "ringcentral.video.main.add-coworkers=unknown" in text
```

The final `unknown` assertion is optional but useful adjacent coverage: without evidence text, the target's per-entrypoint evidence level should remain explicit rather than pretending an evidence source exists.

Why here: this directly covers the renderer branch that formats missing evidence as `none`. The CLI always reads an evidence path today, so the CLI is not the best place to force this fallback.

## Need To Edit Source?

No source edit is recommended by this scan.

The implementation already emits both path labels and the `none` fallback:

- `Checklist: {_display_path(catalog.checklist_path)}`
- `Evidence: {_display_path(catalog.evidence_path) if catalog.evidence_path else 'none'}`

If the proposed tests fail in a fresh implementation branch, inspect for concurrent edits before changing source. This repo has active parallel work, and `.coverage` is already dirty.

## TDD Red-Light Method

Because this task guards existing behavior, adding the tests may be immediately green. To prove the tests are meaningful without committing source changes:

1. Add the test assertions first.
2. Run the focused tests and confirm the current behavior.
3. Temporarily break only a local working copy of the renderer header, for example by changing `Evidence:` to another label or removing the `else 'none'` branch.
4. Run the same focused tests and confirm the intended test fails.
5. Restore the temporary renderer change before the final diff.
6. Confirm `git diff -- src/ai_presenter/acceptance/validation_targets.py` is empty.

For this docs-only subtask, do not perform the temporary source edit. The above is the recommended red-light method for the later implementation task.

## Focused Verification Commands

After implementing the tests in a separate implementation task, run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_validation_targets.py::test_render_validation_target_lines_includes_source_paths tests\unit\test_validation_targets.py::test_render_validation_target_lines_marks_missing_evidence_path_as_none
```

If the renderer header guard is folded into an existing renderer test instead of a new test, replace the new test id with the edited existing test id.

For this handoff document only, run:

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-146-technical-scan.md
git diff --check -- docs\agent-handoffs\cycle-146-technical-scan.md
```

## Risk Notes

- Keep assertions focused on output traceability, not live acceptance claims.
- Do not broaden this into package, route, provider, or controller behavior.
- Do not require CLI to support missing evidence files as `none`; today a missing CLI evidence file is an input error. The `none` fallback belongs to renderer/catalog coverage.
- Avoid brittle absolute path assertions. File-name or header-prefix assertions are enough because `_display_path` intentionally depends on the current working directory.
- Preserve the Cycle 145 non-evidence note assertions while adding this traceability guard.

## Current Scan Result

Smallest recommended implementation:

- Extend `test_validation_targets_lists_ringcentral_targets` with `Evidence:` and `evidence-index.md` assertions.
- Add one renderer test for both source paths.
- Add one renderer test for `Evidence: none` with `evidence_text=None` and `evidence_path=None`.

Expected source impact: none.
