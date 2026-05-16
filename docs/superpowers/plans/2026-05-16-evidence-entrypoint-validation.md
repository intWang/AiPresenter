# Evidence Entrypoint Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an offline integrity guard for the RingCentral evidence-index entrypoint table.

**Architecture:** Keep the guard in `src/ai_presenter/acceptance/validation_targets.py`, next to the existing markdown table parser. Reuse it from `discover_validation_targets()` when evidence text is supplied.

**Tech Stack:** Python dataclasses, markdown table parsing already in the module, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**

- Modify: `tests/unit/test_validation_targets.py`

- [ ] Add a real-doc test proving the evidence index covers 27 RingCentral package entrypoints exactly once.
- [ ] Add a real-catalog test proving no validation target has `unknown` evidence when blocked rows are included.
- [ ] Add synthetic missing-entrypoint, unknown-entrypoint, duplicate-entrypoint, and invalid-level tests.
- [ ] Run the new focused tests and confirm they fail before implementation.

### Task 2: Implement Evidence Integrity Guard

**Files:**

- Modify: `src/ai_presenter/acceptance/validation_targets.py`

- [ ] Add an evidence integrity report dataclass.
- [ ] Add allowed evidence levels.
- [ ] Detect duplicate evidence entrypoint rows while parsing.
- [ ] Validate unknown and missing entrypoint IDs against `MaterialPackage.entrypoints_by_id`.
- [ ] Validate evidence levels.
- [ ] Route `discover_validation_targets()` through the helper when evidence text is supplied.

### Task 3: Verify, Review, Commit

**Files:**

- Cycle 038 code, tests, and docs.

- [ ] Run focused pytest, ruff, and mypy.
- [ ] Request a review subagent focused on validation strictness, CLI compatibility, and evidence-level policy.
- [ ] Apply any necessary follow-up.
- [ ] Run full pytest, ruff, mypy, and `git diff --check`.
- [ ] Stage only Cycle 038 files and commit with `fix: validate evidence entrypoint ids`.

