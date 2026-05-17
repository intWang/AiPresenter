# Cycle 205 Demand Analysis: Acceptance-Runs Source Observability

## Value

Cycle 204 wired the Accepted-evidence guard into `validation-targets`, including explicit `--acceptance-runs` handling and sibling-file discovery. The remaining UX gap was observability: rendered output told users which checklist and evidence index were used, but not whether `acceptance-runs.md` was explicitly supplied, auto-discovered, or absent.

This matters because `Accepted` evidence has a stricter trust boundary than `Observed` or `Repo-tested`. Users should be able to audit, from command output alone, whether the Accepted-evidence guard had a manual-run source available.

## Acceptance Criteria

- `validation-targets` output includes an `Acceptance runs:` source line near `Checklist:` and `Evidence:`.
- The line distinguishes all three states:
  - explicit path supplied via `--acceptance-runs`;
  - sibling `acceptance-runs.md` auto-discovered beside the evidence index;
  - no acceptance-runs source available.
- Display shape:
  - `Acceptance runs: <path> (explicit)`
  - `Acceptance runs: <path> (auto-discovered)`
  - `Acceptance runs: none (absent)`
- Path rendering reuses existing relative-path behavior where possible.
- Explicit missing `--acceptance-runs` remains strict and fails before rendering.
- Implicit missing sibling `acceptance-runs.md` remains compatible and renders `none (absent)`.
- The Accepted-evidence guard behavior is unchanged: it runs only when acceptance text is available.

## Non-Goals

- Do not change acceptance evidence eligibility rules.
- Do not promote any evidence level automatically.
- Do not parse or render acceptance-run contents in `validation-targets`.
- Do not make implicit sibling discovery mandatory.
- Do not change `acceptance-draft` behavior.

## Privacy Constraints

- Render only source metadata: path plus source state.
- Never print acceptance-run body text, meeting content, participant names, chat text, invite links, screenshots, or manual evidence details.
- Keep the existing metadata-first RingCentral evidence reminder unchanged.
- Preserve the boundary that rendered validation targets are planning output, not live acceptance evidence.

## Verification

Focused RED/GREEN command:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_validation_targets.py::test_render_validation_target_lines_keeps_normal_draft_command tests\unit\test_validation_targets.py::test_render_validation_target_lines_marks_missing_evidence_source_as_none tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_accepts_backed_accepted_evidence
```

RED result before implementation: four failures because `acceptance_source` and rendered state labels were missing.

GREEN result after implementation: `4 passed in 1.21s`.
