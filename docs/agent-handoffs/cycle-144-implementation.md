# Cycle 144 Implementation: RingCentral Source-Index Test Reference Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Implemented a narrow docs-plus-test guard for the RingCentral Video knowledge
package. This slice only touched:

- `tests/unit/test_material_packages.py`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/agent-handoffs/cycle-144-implementation.md`

No source code, package YAML, profiles, CLI behavior, or generated artifacts
were changed. The pre-existing dirty `.coverage` file was not touched.

## Changes

- Added `test_ringcentral_source_index_test_references_exist` to require every
  backticked `tests/unit/*.py` or `tests/integration/*.py` reference in
  `source-index.md` to point at a real repository file.
- Updated the Profile/runtime behavior row in `source-index.md` from the stale
  `tests/unit/test_ringcentral_profile.py` reference to existing, matching
  tests:
  - `tests/unit/test_runtime_factory.py`
  - `tests/unit/test_profile_runner.py`
  - `tests/integration/test_ringcentral_profile.py`
- Added `test_ringcentral_knowledge_docs_preserve_evidence_boundaries` to keep
  the RingCentral evidence vocabulary separated:
  - `Accepted`, `Observed`, and `Repo-tested`
  - checklist procedure versus proof
  - `acceptance-runs.md` as the dated evidence record
  - `runtime-safety-routing.md` as maintenance guidance, not acceptance proof
- Tightened `source-index.md` source discipline so executable live confidence
  requires privacy, side-effect, cleanup, and dated acceptance evidence.

## Red/Green Verification

Red run before the source-index fix:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_source_index_test_references_exist
```

Result: failed as expected because `tests/unit/test_ringcentral_profile.py`
was referenced in `source-index.md` but does not exist.

Green run after the source-index fix and evidence-boundary guard:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_source_index_test_references_exist tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries
```

Result: `2 passed`.

## Boundaries

- No live RingCentral acceptance was run or claimed.
- `Repo-tested`, `Observed`, checklist procedure, runtime readiness, and dated
  live/manual acceptance remain separate evidence states.
- Runtime/provider tests are cited as repo-local evidence only; they do not
  promote RingCentral routes to live acceptance.
- Checklist and runbook content remain procedure until a dated run is recorded
  in `acceptance-runs.md`.

## Follow-Up

- If future source-index rows cite test files, keep them backticked so the guard
  can catch stale paths.
- If evidence wording changes, update the guard intentionally with the new
  durable boundary sentence rather than deleting the semantic assertion.
