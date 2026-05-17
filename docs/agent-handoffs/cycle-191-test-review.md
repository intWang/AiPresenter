# Cycle 191 Test Review

Date: 2026-05-17

## RED Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_render_validation_target_lines_adds_detail_entrypoint_draft_examples_for_groups tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_priority_lists_without_entrypoint_draft_examples tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_single_entrypoint_detail_without_examples tests\unit\test_cli.py::test_validation_targets_detail_outputs_entrypoint_draft_examples_for_group
```

Result before implementation: two tests failed because grouped `--target` output lacked
`entrypoint draft examples:`. The priority-list and single-entrypoint guards passed.

## Focused Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py tests\unit\test_cli.py -k validation_targets tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
```

Result: `40 passed, 76 deselected`.

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --target rcv-top-bar-routes
```

Result: output kept the group `draft:` and added four entrypoint draft examples.

```powershell
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --priority P1
.\.venv\Scripts\ai-presenter.exe validation-targets --package ringcentral-video --include-blocked --target rcv-recording
```

Result: P1 priority output did not include `entrypoint draft examples:`. Blocked output still
omitted `draft:` and `acceptance-draft`.

## Independent Review

An independent review found no regressions against the requested acceptance-target constraints.

- Detail examples are scoped to selected grouped targets.
- Priority-list, single-entrypoint, mixed flow-plus-entrypoint, and blocked outputs remain
  conservative.
- `.coverage` was still unstaged during review.

Reviewer targeted verification result: `8 passed`.

## Required Before Commit

Run full repository verification and cached-diff checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src tests
git diff --cached --check
git diff --cached -- .coverage
git diff --cached --stat
git diff --cached --name-only
```
