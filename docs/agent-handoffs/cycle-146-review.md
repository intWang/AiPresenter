# Cycle 146 Review: validation-targets Source Traceability Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Findings

- [P2] Path assertions are over-specific to Windows separators.

  `tests/unit/test_cli.py:24`, `tests/unit/test_cli.py:27`,
  `tests/unit/test_validation_targets.py:341`, and
  `tests/unit/test_validation_targets.py:342` assert full header lines with
  backslash-separated paths, for example
  `Checklist: docs\knowledge\ringcentral-video\validation-checklist-index.md`.
  The renderer formats paths with `str(Path(...))` after making them relative to
  `Path.cwd()`, so the same output uses forward slashes on POSIX. These guards
  are valuable, but the exact separator makes the tests brittle outside this
  Windows workspace. Prefer asserting the `Checklist:` / `Evidence:` labels plus
  the expected file names, or deriving the expected display path from `Path(...)`
  in the test.

## Review Notes

- `src/ai_presenter/acceptance/validation_targets.py` has no final diff in the
  reviewed working tree.
- The implementation is test-only for tracked code under review:
  `tests/unit/test_cli.py` and `tests/unit/test_validation_targets.py`.
- The reviewed tests cover all three requested layers:
  listing output, detail output, and renderer output.
- The tests keep the Cycle 145 non-evidence note in listing/detail/renderer
  coverage and do not add a live acceptance claim.
- The traceability assertions are directionally useful because they require both
  checklist and evidence sources to remain visible.

## Verification

Reviewed handoffs:

- `docs/agent-handoffs/cycle-146-demand-analysis.md`
- `docs/agent-handoffs/cycle-146-technical-scan.md`
- `docs/agent-handoffs/cycle-146-risk-scan.md`
- `docs/agent-handoffs/cycle-146-implementation.md`

Diff/status checks:

- `git diff -- src\ai_presenter\acceptance\validation_targets.py tests\unit\test_cli.py tests\unit\test_validation_targets.py docs\agent-handoffs\cycle-146-*.md`
  showed test-only tracked changes; untracked handoff docs are present.
- `git diff -- src\ai_presenter\acceptance\validation_targets.py` produced no
  output.
- `git diff --name-only -- src\ai_presenter\acceptance\validation_targets.py tests\unit\test_cli.py tests\unit\test_validation_targets.py docs\agent-handoffs\cycle-146-*.md`
  listed only:
  - `tests/unit/test_cli.py`
  - `tests/unit/test_validation_targets.py`

Focused tests:

```text
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command
...                                                                      [100%]
3 passed in 1.30s
```

Whitespace check before writing this review:

```text
git diff --check -- tests\unit\test_cli.py tests\unit\test_validation_targets.py
```

Result: no errors; Git emitted LF-to-CRLF working-copy warnings for the two test
files.

## Recommendation

No-go until the separator-specific path assertions are made portable. After
that, the change is narrow and appropriate for Cycle 146.
