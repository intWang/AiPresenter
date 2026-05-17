# Cycle 206 Demand Analysis: `--acceptance-runs` Discoverability

## Value

Cycle 205 made `validation-targets` report the acceptance-runs source state (`auto-discovered`, `explicit`, or `absent`). Cycle 206 makes that behavior discoverable before operators run evidence workflows.

Users need to understand that `--acceptance-runs` supplies the source document used by the Accepted-evidence guard. It validates whether `Accepted` evidence rows are backed by dated passing manual/live records, but it does not create, collect, or promote live evidence by itself.

## Acceptance Criteria

- CLI help for `validation-targets --help` describes `--acceptance-runs` as the Accepted-evidence guard source.
- CLI help explicitly says `--acceptance-runs` is not live evidence.
- The manual acceptance runbook includes a short operator-facing note near the `validation-targets` command explaining:
  - the default `acceptance-runs.md` is auto-discovered beside the evidence index;
  - `--acceptance-runs <path>` overrides that guard source;
  - the option only supplies guard input for validating `Accepted` rows;
  - completed manual/live results must still be recorded in `acceptance-runs.md`.
- Knowledge docs cross-reference the same boundary consistently:
  - `evidence-index.md`
  - `acceptance-runs.md`
  - `source-index.md`
- Unit coverage protects the CLI help wording and runbook/source wording.

## Non-Goals

- Do not change acceptance evidence parsing semantics.
- Do not change `validation-targets` target discovery or filtering.
- Do not create live RingCentral evidence.
- Do not promote any route to `Accepted`.
- Do not broaden screenshot or private-content collection policy.

## Privacy Constraints

- Keep the metadata-first evidence policy intact.
- Do not imply that CLI validation can replace a dated manual/live acceptance record.
- Do not instruct operators to capture chat text, participant names, invite links, meeting IDs, dial-in details, emails, account/profile content, notes/transcripts, recordings, shared content, or room imagery.
- Failed, blocked, incomplete, skipped, automated-only, dry-run, `doctor`, and read-only observation records must not be described as `Accepted` promotion evidence.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_help_explains_acceptance_runs_guard_source tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
```

Focused result after implementation: `2 passed in 0.44s`.
