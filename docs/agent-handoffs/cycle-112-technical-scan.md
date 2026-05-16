# Cycle 112 Technical Scan: RingCentral Video Knowledge Navigation Integrity

Date: 2026-05-16
Scope: technical scan only. This handoff proposes a minimal test/doc slice and does not implement it.

## Goal

Lock down RingCentral Video knowledge-doc navigation so future `docs/knowledge/ringcentral-video/*.md` files cannot become orphaned from the durable indexes.

## Current Test Inventory

Relevant existing coverage:

| File | Current coverage | Gap for this cycle |
| --- | --- | --- |
| `tests/unit/test_material_packages.py` | Validates the RingCentral package shape, localized Q&A and aliases, runtime indexes, explainer coverage, demo-flow references, supported demo actions, and a shallow docs check in `test_ringcentral_validation_checklist_covers_package_routes`. | The shallow docs check confirms package entrypoints are in `validation-checklist-index.md`, demo flows are in `evidence-index.md`, and a few cross-links exist. It does not enumerate knowledge docs and prove every doc is reachable from an index. |
| `tests/unit/test_validation_targets.py` | Parses `validation-checklist-index.md` and `evidence-index.md`; enforces explicit validation target IDs; validates blocked rows; validates the Entry Point Evidence Table covers all 27 package entrypoints exactly once with allowed evidence levels. | Strong evidence-table integrity, but no file-list navigation integrity for the knowledge directory. |
| `tests/unit/test_cli.py` | Covers `validation-targets` and `acceptance-draft` CLI behavior against RingCentral validation docs. | CLI behavior depends on parsed docs, not on all knowledge docs being discoverable from navigation indexes. |
| `tests/unit/test_questions.py` and `tests/unit/test_diagnostics.py` | Cover route safety, aliases, Q&A routing, tone invariants, and doctor/diagnostic signals. | These protect runtime policy, not docs navigation. |

Current RingCentral knowledge docs:

| Doc | Mentioned in `source-index.md` | Mentioned in `evidence-index.md` |
| --- | --- | --- |
| `acceptance-runs.md` | Yes | Yes |
| `evidence-index.md` | Yes | No, expected because it is the evidence index itself. |
| `locator-matrix.md` | No | Yes |
| `observation-log.md` | No | Yes |
| `privacy-matrix.md` | No | Yes |
| `runtime-safety-routing.md` | Yes | Yes |
| `source-index.md` | No | Yes |
| `state-matrix.md` | No | Yes |
| `validation-checklist-index.md` | Yes | Yes |

Scan result: the current docs already satisfy the intended navigation invariant. Cycle 112 can be test-only unless another worker adds an unindexed knowledge doc before implementation.

## Concurrent Worktree Note

During verification, the worktree also showed uncommitted edits outside this handoff. I did not make or modify these changes:

- `tests/unit/test_material_packages.py` adds `test_ringcentral_source_index_registers_knowledge_docs`, requiring every current RingCentral knowledge doc except `source-index.md` to appear as a backticked full path in `source-index.md`.
- `docs/knowledge/ringcentral-video/source-index.md` adds repository-local source rows for `observation-log.md`, `locator-matrix.md`, `state-matrix.md`, and `privacy-matrix.md`.

That in-progress implementation is a stricter source-index-only variant. It may be acceptable if the team wants `source-index.md` to be a complete knowledge-doc registry, but it is broader than the minimal navigation invariant because the existing `evidence-index.md` already links those docs. If keeping that variant, consider adding the dangling full-path reference check below or a second evidence-index assertion so the test also protects broken index links, not only source-index membership.

## Proposed Implementation

Recommended minimal slice: one test-only addition in `tests/unit/test_material_packages.py`, near `test_ringcentral_validation_checklist_covers_package_routes`.

No production code, package YAML, runtime tests, or knowledge docs need to change for the current tree. If the new test fails because a new knowledge doc landed, update the appropriate index instead of weakening the assertion:

- Add ordinary knowledge docs to `docs/knowledge/ringcentral-video/evidence-index.md` primary sources.
- Add durable repo-local source or maintenance-guide docs to `docs/knowledge/ringcentral-video/source-index.md` when they are part of the source taxonomy.
- Keep `evidence-index.md` registered from `source-index.md`; keep `source-index.md` linked from `evidence-index.md`.

Suggested helper and test shape:

```python
import re

_RINGCENTRAL_KNOWLEDGE_DOC_REF_RE = re.compile(
    r"docs/knowledge/ringcentral-video/([A-Za-z0-9._-]+\.md)"
)


def test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes() -> None:
    knowledge_dir = Path("docs/knowledge/ringcentral-video")
    doc_names = {path.name for path in knowledge_dir.glob("*.md")}
    source_text = (knowledge_dir / "source-index.md").read_text(encoding="utf-8")
    evidence_text = (knowledge_dir / "evidence-index.md").read_text(encoding="utf-8")
    navigation_text = f"{source_text}\n{evidence_text}"

    missing_from_navigation = sorted(
        name for name in doc_names if name not in navigation_text
    )
    missing_from_evidence = sorted(
        name
        for name in doc_names
        if name != "evidence-index.md" and name not in evidence_text
    )
    dangling_knowledge_refs = sorted(
        name
        for name in set(_RINGCENTRAL_KNOWLEDGE_DOC_REF_RE.findall(navigation_text))
        if not (knowledge_dir / name).is_file()
    )

    assert missing_from_navigation == []
    assert missing_from_evidence == []
    assert dangling_knowledge_refs == []
```

## Exact Assertions

The test should assert:

- Every actual `docs/knowledge/ringcentral-video/*.md` basename appears in either `source-index.md` or `evidence-index.md`.
- Every actual knowledge doc except `evidence-index.md` appears in `evidence-index.md`, because that file is the navigation layer for RingCentral evidence and maintenance docs.
- Any full-path `docs/knowledge/ringcentral-video/<file>.md` reference inside the two navigation indexes points to a file that exists.

Expected current green state:

- `missing_from_navigation == []`
- `missing_from_evidence == []`
- `dangling_knowledge_refs == []`

Expected red behavior:

- Adding `docs/knowledge/ringcentral-video/new-topic.md` without an index link fails with `new-topic.md` in `missing_from_navigation` and `missing_from_evidence`.
- Removing `runtime-safety-routing.md` from `evidence-index.md` fails with `runtime-safety-routing.md` in `missing_from_evidence`, even though `source-index.md` still mentions it.
- Removing `evidence-index.md` from `source-index.md` fails with `evidence-index.md` in `missing_from_navigation`.
- Deleting `runtime-safety-routing.md` while leaving a full-path index reference fails with `runtime-safety-routing.md` in `dangling_knowledge_refs`.

## Risks

- A dynamic file-list test will intentionally fail whenever a new knowledge doc is created without navigation links. That is the desired friction, but implementers should update indexes rather than hardcode an allowlist.
- The regex only checks full-path dangling references under `docs/knowledge/ringcentral-video/`. It should not validate unrelated `docs/runbooks/*.md` or `docs/agent-handoffs/*.md` references from `source-index.md`.
- Do not require every knowledge doc to appear in `source-index.md`; `evidence-index.md` is already the broader navigation layer, while `source-index.md` is a taxonomy of official, repo-local, and evidence sources.
- Do not assert exact line text or table order. The invariant is reachability, not prose layout.
- Keep coverage disabled for focused pytest runs to avoid touching the pre-existing dirty `.coverage` file.

## Verification Commands

Focused red/green check after implementing the test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes -q -o addopts=""
```

If adopting the concurrent source-index-only test already present in the worktree, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_ringcentral_source_index_registers_knowledge_docs -q -o addopts=""
```

Related docs/package integrity cluster:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\unit\test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes `
  tests\unit\test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes `
  tests\unit\test_validation_targets.py::test_evidence_index_integrity_covers_every_ringcentral_entrypoint_once `
  tests\unit\test_validation_targets.py::test_discover_validation_targets_has_no_unknown_evidence_for_real_catalog `
  -q -o addopts=""
```

Docs whitespace and scope checks:

```powershell
git diff --check -- tests\unit\test_material_packages.py docs\knowledge\ringcentral-video\source-index.md docs\knowledge\ringcentral-video\evidence-index.md
git status --short
```

Broader optional unit check without coverage side effects:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_validation_targets.py -q -o addopts=""
```

Do not run live RingCentral validation for this slice. This is navigation integrity only, not new acceptance evidence.
