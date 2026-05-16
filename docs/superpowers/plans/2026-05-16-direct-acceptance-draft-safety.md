# Direct Acceptance Draft Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refuse direct manual acceptance drafts for entrypoints with no executable open steps.

**Architecture:** Keep the guard in `src/ai_presenter/acceptance/manual_record.py`, where acceptance draft target summaries are resolved. CLI already converts `ValueError` into `typer.BadParameter`.

**Tech Stack:** Python dataclasses, Typer CLI tests, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**

- Modify: `tests/unit/test_acceptance_manual_record.py`
- Modify: `tests/unit/test_cli.py`

- [ ] Replace warning-only manual-record expectation for Leave with a refusal expectation.
- [ ] Add CLI refusal test for Recording or Leave.
- [ ] Add output-file refusal test proving no draft file is written.
- [ ] Keep executable entrypoint and flow-only draft tests passing.
- [ ] Run focused tests and confirm red.

### Task 2: Implement Refusal

**Files:**

- Modify: `src/ai_presenter/acceptance/manual_record.py`

- [ ] Add a helper that raises for direct entrypoints with no open steps.
- [ ] Use it from `build_acceptance_target_summary()`.
- [ ] Preserve flow-only draft behavior.

### Task 3: Verify, Review, Commit

**Files:**

- Cycle 042 code, tests, and docs.

- [ ] Run focused pytest, ruff, and mypy.
- [ ] Request review focused on direct refusal, output-file behavior, and flow-only preservation.
- [ ] Run full pytest, ruff, mypy, and `git diff --check`.
- [ ] Commit with `fix: reject no-step acceptance drafts`.

