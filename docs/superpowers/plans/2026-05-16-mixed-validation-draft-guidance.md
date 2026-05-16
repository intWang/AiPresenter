# Mixed Validation Draft Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate more specific acceptance draft guidance for validation targets that combine one flow with one entrypoint.

**Architecture:** Reuse the existing `ValidationTarget` ID classification and `AcceptanceDraftRequest` validation. Only command rendering and intended-steps wording change.

**Tech Stack:** Python helpers, Typer CLI tests, pytest.

---

### Task 1: Failing Tests

**Files:**
- Modify: `tests/unit/test_validation_targets.py`
- Modify: `tests/unit/test_acceptance_manual_record.py`
- Modify: `tests/unit/test_cli.py`

- [ ] Add a validation-target test for `rcv-controller-chat-question` asserting the draft command contains `--flow meeting-control-map-demo`, `--entrypoint ringcentral.video.toolbar.chat`, and the existing checklist target.
- [ ] Add an acceptance-draft test asserting mixed `Steps executed` mentions both flow and entrypoint.
- [ ] Add a CLI test for `validation-targets --target rcv-controller-chat-question`.
- [ ] Run focused tests and verify RED.

### Task 2: Minimal Implementation

**Files:**
- Modify: `src/ai_presenter/acceptance/validation_targets.py`
- Modify: `src/ai_presenter/acceptance/manual_record.py`

- [ ] Add the single-flow-plus-single-entrypoint branch to `acceptance_draft_command()`.
- [ ] Add mixed wording to `_intended_steps()`.
- [ ] Run focused tests and verify GREEN.

### Task 3: Verification And Review

**Files:**
- Create: `docs/agent-handoffs/cycle-030-review.md`
- Create: `docs/agent-handoffs/cycle-030-summary.md`

- [ ] Run affected tests and manual CLI smoke.
- [ ] Run full pytest, mypy, and ruff.
- [ ] Request review focused on command specificity, group fallback, and draft wording.
