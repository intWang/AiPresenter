# Cycle 112 Implementation: RingCentral Video Knowledge Navigation Guard

Date: 2026-05-16

## Scope

Cycle 112 adds a focused navigation-integrity guard for the RingCentral Video knowledge package. It does not change production code, package YAML, profiles, runtime routing, localization data, live evidence levels, locators, or acceptance records.

## Demand Addressed

Future RingCentral Video knowledge pages should not become hidden from the two durable entry points maintainers use:

- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`

The guard keeps canonical knowledge docs discoverable while allowing intentionally temporary files to stay out of the package navigation if they use a `draft-` or `scratch-` prefix, or include `<!-- nav: ignore -->`.

## Implementation

Updated `docs/knowledge/ringcentral-video/source-index.md` so the repository-local sources table explicitly lists these existing knowledge docs:

- `docs/knowledge/ringcentral-video/observation-log.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`

Added `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes`.

The test checks:

- every canonical `docs/knowledge/ringcentral-video/*.md` file except `source-index.md` is referenced from `source-index.md`;
- every canonical knowledge doc except `evidence-index.md` is referenced from `evidence-index.md`;
- every canonical doc appears in at least one of the two navigation indexes;
- every full-path RingCentral knowledge-doc reference in the two indexes points to an existing file.

## TDD Notes

Red check:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k source_index_registers_knowledge_docs
```

Expected failure:

- `locator-matrix.md`
- `observation-log.md`
- `privacy-matrix.md`
- `state-matrix.md`

Green checks:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k knowledge_docs_are_registered_in_navigation_indexes
```

Result: `1 passed, 84 deselected`.

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes tests\unit\test_validation_targets.py
```

Result: `26 passed`.

## Review Focus

- Confirm this is navigation integrity only, not live RingCentral acceptance evidence.
- Confirm the guard does not fetch external URLs or parse full markdown prose.
- Confirm `.coverage` remains unstaged.
- Confirm no production code, package YAML, runtime behavior, or localization counts changed.

## Post-Review Adjustment

The review found one minor non-blocking gap: dangling RingCentral knowledge references were initially detected only when written as backticked repo-relative paths. The regex now detects any full-path `docs/knowledge/ringcentral-video/*.md` reference in the two navigation indexes, including plain text or Markdown link targets.
