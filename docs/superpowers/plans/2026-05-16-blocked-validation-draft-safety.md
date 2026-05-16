# Blocked Validation Draft Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent rendered blocked validation targets from displaying executable-looking acceptance draft commands.

**Architecture:** Change only the validation-target renderer. Keep parsing and command-building helpers unchanged.

**Tech Stack:** Python rendering helpers, Typer CLI tests, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**

- Modify: `tests/unit/test_validation_targets.py`
- Modify: `tests/unit/test_cli.py`

- [ ] Add unit render test for blocked `rcv-recording`.
- [ ] Assert blocked render includes `blocked:` and `Do not execute`.
- [ ] Assert blocked render excludes `draft:` and `acceptance-draft`.
- [ ] Assert normal target render still includes draft command.
- [ ] Add CLI test for `--include-blocked --target rcv-recording` excluding draft command.
- [ ] Run focused tests and confirm red.

### Task 2: Implement Renderer Guard

**Files:**

- Modify: `src/ai_presenter/acceptance/validation_targets.py`

- [ ] Update `_render_target_block()` to append draft commands only when `target.blocked_reason is None`.
- [ ] Preserve `blocked:` line and all target metadata.

### Task 3: Verify, Review, Commit

**Files:**

- Cycle 041 code, tests, and docs.

- [ ] Run focused pytest, ruff, and mypy.
- [ ] Request review focused on blocked output safety and normal draft preservation.
- [ ] Run full pytest, ruff, mypy, and `git diff --check`.
- [ ] Commit with `fix: suppress blocked validation drafts`.

