# Support Tone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `support` presenter tone for troubleshooting and recovery-oriented operator moments.

**Architecture:** Extend the centralized voice metadata in `src/ai_presenter/runtime/voice.py`; CLI and controller option lists should pick it up from existing constants.

**Tech Stack:** Python Literal metadata, Typer CLI tests, controller label tests, pytest, ruff, mypy.

---

### Task 1: Add Failing Tests

**Files:**

- Modify: `tests/unit/test_voice.py`
- Modify: `tests/unit/test_cli.py`
- Modify: `tests/unit/test_controller.py`

- [ ] Add support tone normalization and alias tests.
- [ ] Add support tone instruction and English dynamic text tests.
- [ ] Add support SAPI rate test.
- [ ] Assert `ai-presenter voices` lists `Support aliases:`.
- [ ] Assert controller voice label renders `English / Support`.
- [ ] Run focused tests and confirm red.

### Task 2: Implement Support Tone

**Files:**

- Modify: `src/ai_presenter/runtime/voice.py`

- [ ] Extend `PresenterTone`.
- [ ] Add tone choice, description, label, and aliases.
- [ ] Add English dynamic text behavior.
- [ ] Add support SAPI rate behavior for Chinese local speech.

### Task 3: Verify, Review, Commit

**Files:**

- Cycle 040 code, tests, and docs.

- [ ] Run focused pytest, ruff, and mypy.
- [ ] Request review focused on tone metadata propagation and no provider-routing changes.
- [ ] Run full pytest, ruff, mypy, and `git diff --check`.
- [ ] Commit with `feat: add support presenter tone`.

