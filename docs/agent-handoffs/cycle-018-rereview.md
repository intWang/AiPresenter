# Cycle 018 Re-Review

Date: 2026-05-16
Role: re-review worker
Write scope: this file only

## Findings

No blocking findings remain for the Cycle 018 safety issue.

The `acceptance-draft --output` path now delegates to `_write_acceptance_draft_output()` in `src/ai_presenter/cli.py`. That helper refuses output paths whose basename case-folds to `acceptance-runs.md`, refuses any output path that already exists, and only then creates the parent directory and writes the draft.

## Focus Questions

1. Does `acceptance-draft --output` now refuse existing files?
   - Yes. Existing output files raise `typer.BadParameter("Output file already exists: ...")` before writing. The focused unit test preserves sentinel file contents, and an independent temp probe left an existing file unchanged.

2. Does it refuse basename `acceptance-runs.md` even if the file does not exist?
   - Yes. The basename check runs before the existence check and uses `output.name.casefold() == "acceptance-runs.md"`. The focused unit test verifies the file is not created, and the independent temp probe also showed no file was created.

3. Do tests cover both safety cases and preserve normal output-file behavior?
   - Yes. `tests/unit/test_cli.py` covers normal draft file output, refusal of an existing output file, and refusal of a non-existing `acceptance-runs.md` output path.

4. Any remaining evidence-safety or runtime-coupling concern in the fix?
   - No new evidence-safety concern in the fix. The reserved evidence filename and overwrite cases are guarded.
   - No new runtime-coupling concern in the fix itself. The helper only writes a supplied draft string to disk after safety checks. The broader CLI module still has existing runtime imports, but this review found no additional coupling introduced by the overwrite fix.

## Verification Commands/Results

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_acceptance_draft_rejects_existing_output_file tests\unit\test_cli.py::test_acceptance_draft_rejects_acceptance_runs_output_file tests\unit\test_cli.py::test_acceptance_draft_can_write_to_output_file` -> `3 passed in 7.10s`.
- Independent safe temp probe:
  - Existing `draft.md` with sentinel content: command exited `2`; file still contained `sentinel`.
  - Non-existing `acceptance-runs.md`: command exited `2`; file was not created.
  - Non-existing `acceptance-draft.md`: command exited `0`; file was created and contained `Draft only`.

## Result

The original P1 blocker is closed. `acceptance-draft --output` no longer silently overwrites existing files and refuses `acceptance-runs.md` by basename even when that file does not exist.
