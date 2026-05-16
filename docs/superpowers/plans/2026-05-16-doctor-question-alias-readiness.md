# Doctor Question Alias Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `doctor` diagnostic that surfaces package-owned question alias conflicts before runtime.

**Architecture:** Reuse `MaterialPackage.entrypoint_question_aliases` in `src/ai_presenter/runtime/diagnostics.py`. Do not change matching or package validation.

**Tech Stack:** Python dataclasses, Typer CLI tests, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**

- Modify: `tests/unit/test_diagnostics.py`
- Modify: `tests/unit/test_cli.py`

- [ ] Add diagnostics OK test for the real RingCentral package.
- [ ] Add diagnostics WARN test for duplicate normalized alias across entrypoints.
- [ ] Add diagnostics OK test for duplicate normalized alias repeated on the same entrypoint.
- [ ] Add CLI WARN test using a temporary package path and a known-good RingCentral config path.
- [ ] Run the new focused tests and confirm red.

### Task 2: Implement Diagnostic

**Files:**

- Modify: `src/ai_presenter/runtime/diagnostics.py`

- [ ] Add `_diagnose_question_aliases(material_package)`.
- [ ] Group aliases by normalized alias.
- [ ] Detect cross-entrypoint conflicts.
- [ ] Append the diagnostic from `_diagnose_material_package()`.
- [ ] Keep runtime question matching unchanged.

### Task 3: Verify, Review, Commit

**Files:**

- Cycle 039 code, tests, and docs.

- [ ] Run focused pytest, ruff, and mypy.
- [ ] Request review subagent focused on output compatibility, duplicate grouping, and non-fatal behavior.
- [ ] Apply any review fixes.
- [ ] Run full pytest, ruff, mypy, and `git diff --check`.
- [ ] Commit with `feat: report duplicate package question aliases`.

