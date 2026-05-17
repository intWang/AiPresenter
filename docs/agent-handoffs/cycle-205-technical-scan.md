# Cycle 205 Technical Scan: Render Acceptance Runs Source

## Summary

Render the acceptance-runs source in `validation-targets` output as:

- `Acceptance runs: <path> (explicit)` when a user supplies `--acceptance-runs`;
- `Acceptance runs: <path> (auto-discovered)` when a sibling `acceptance-runs.md` is loaded;
- `Acceptance runs: none (absent)` when no acceptance source is present.

The validation guard itself was already wired through `acceptance_text`; this cycle preserves and displays the source path plus state.

## Implementation Shape

`src/ai_presenter/acceptance/validation_targets.py`:

- Add `acceptance_path: Path | None = None` to `ValidationTargetCatalog`.
- Add `acceptance_source: str = "absent"` to `ValidationTargetCatalog`.
- Add optional `acceptance_path` and `acceptance_source` to `discover_validation_targets(...)`.
- Pass both into `ValidationTargetCatalog(...)`.
- Render `Acceptance runs:` near `Checklist:` and `Evidence:`.

`src/ai_presenter/cli.py`:

- Track the actual acceptance-runs path loaded by `validation-targets`.
- For explicit `--acceptance-runs`, set `acceptance_path = acceptance_runs` and `acceptance_source = "explicit"`.
- For implicit sibling discovery, set `acceptance_path` only when the sibling file exists and is read, with `acceptance_source = "auto-discovered"`.
- Pass both fields into `discover_validation_targets(...)`.

## Tests

- Renderer normal detail output asserts `Acceptance runs: docs/knowledge/ringcentral-video/acceptance-runs.md (auto-discovered)`.
- Renderer no-evidence/direct-discovery output asserts `Acceptance runs: none (absent)`.
- CLI default `validation-targets --package ringcentral-video --priority P0` asserts the auto-discovered source.
- CLI explicit `--acceptance-runs <tmp path>` success path asserts the explicit source.

## Behavior To Preserve

- Direct discovery without `acceptance_text` or `acceptance_path` still works.
- Direct discovery without evidence renders `Evidence: none` and `Acceptance runs: none (absent)`.
- Acceptance-runs is not required for unrelated or synthetic callers.
- Acceptance draft behavior is unchanged and does not imply live/manual evidence.
- No real `acceptance-runs.md` evidence is edited or fabricated.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_marks_missing_evidence_source_as_none tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_accepts_backed_accepted_evidence
```

Result: `4 passed in 1.21s`.
