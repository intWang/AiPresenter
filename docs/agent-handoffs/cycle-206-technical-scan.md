# Cycle 206 Technical Scan: Discoverability for `--acceptance-runs`

## Summary

Improve discoverability for `validation-targets --acceptance-runs` in two places:

- CLI help explains that `--acceptance-runs` is an Accepted-evidence guard source, not live evidence.
- The RingCentral manual acceptance runbook shows when to use `--acceptance-runs <path>` and explains the `Acceptance runs:` output states without implying live validation.

Preserve the no-live-evidence boundary: this option only selects or reports the guard source used to validate evidence rows against `acceptance-runs.md`; it does not create, promote, or prove live acceptance evidence.

## Exact Changes

`src/ai_presenter/cli.py`:

- Update the `validation-targets` option help for `--acceptance-runs` to say it is an Accepted evidence guard source and is not live evidence.

`tests/unit/test_cli.py`:

- Add a focused CLI help test requiring `--acceptance-runs`, `Accepted evidence guard source`, and `not live evidence`.

`docs/runbooks/ringcentral-manual-acceptance.md`:

- Extend the validation-targets runbook bullet to mention `--acceptance-runs <path>` only for non-default guard sources.
- Add a neighboring bullet explaining `Acceptance runs:` source states.

`tests/unit/test_material_packages.py`:

- Extend the RingCentral evidence-boundary test with assertions for:
  - `--acceptance-runs <path>`;
  - the guard-source-only boundary;
  - explicit / auto-discovered / absent state wording;
  - `acceptance-runs.md` and `source-index.md` guard-input boundaries.

## Boundary To Preserve

Do not edit or fabricate live acceptance runs. Do not claim live RingCentral validation, live acceptance, or route promotion. The new wording is discoverability only: path/source visibility plus guard semantics.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_cli.py::test_validation_targets_help_explains_acceptance_runs_guard_source tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
```

Result reported by subagent after implementation: `2 passed in 0.63s`.
