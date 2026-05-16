# Stable Validation Target IDs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make RingCentral validation target IDs stable by reading explicit `Target ID` values from the knowledge checklist while keeping generated-ID fallback for older checklists.

**Architecture:** Keep the behavior inside the existing `acceptance.validation_targets` parser. The markdown checklist becomes the canonical source for RingCentral IDs; parser fallback preserves custom checklist compatibility.

**Tech Stack:** Python dataclasses, markdown table parsing helpers, Typer CLI tests, pytest.

---

### Task 1: Parser Behavior Tests

**Files:**
- Modify: `tests/unit/test_validation_targets.py`

- [ ] **Step 1: Add failing tests**

Add tests for explicit IDs, duplicate explicit IDs, blank explicit IDs, and fallback generated IDs when the column is absent.

- [ ] **Step 2: Verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py::test_discover_validation_targets_uses_explicit_target_ids tests\unit\test_validation_targets.py::test_discover_validation_targets_rejects_duplicate_validation_target_ids tests\unit\test_validation_targets.py::test_discover_validation_targets_rejects_blank_explicit_target_id tests\unit\test_validation_targets.py::test_discover_validation_targets_falls_back_to_generated_ids_without_target_id_header --no-cov
```

Expected: explicit/duplicate/blank tests fail before implementation.

### Task 2: Parser Implementation

**Files:**
- Modify: `src/ai_presenter/acceptance/validation_targets.py`

- [ ] **Step 1: Add optional header parsing**

Extend `_parse_first_table` with `optional_headers`.

- [ ] **Step 2: Add explicit-or-generated helper**

Add a helper that returns the explicit target ID when present and nonblank, otherwise returns the fallback generated ID only if the column is absent.

- [ ] **Step 3: Use helper in priority and blocked parsers**

Priority and blocked tables both request optional `Target ID`.

- [ ] **Step 4: Verify GREEN**

Run the focused parser tests again.

### Task 3: RingCentral Checklist And CLI Expectations

**Files:**
- Modify: `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- Modify: `tests/unit/test_validation_targets.py`
- Modify: `tests/unit/test_cli.py`

- [ ] **Step 1: Add `Target ID` column to checklist tables**

Use `rcv-*` IDs without priority or blocked status.

- [ ] **Step 2: Update real checklist and CLI tests**

Expect `rcv-add-coworkers-modal`, `rcv-controller-chat-question`, `rcv-recording`, and `rcv-leave-end-meeting`.

- [ ] **Step 3: Run affected tests**

```powershell
.\.venv\Scripts\python -m pytest tests\unit\test_validation_targets.py tests\unit\test_cli.py::test_validation_targets_lists_ringcentral_targets tests\unit\test_cli.py::test_validation_targets_detail_outputs_draft_command tests\unit\test_cli.py::test_validation_targets_rejects_unknown_target_with_available_ids tests\unit\test_cli.py::test_validation_targets_include_blocked_lists_do_not_execute_routes --no-cov
```

### Task 4: Verification And Review

**Files:**
- Create: `docs/agent-handoffs/cycle-029-review.md`
- Create: `docs/agent-handoffs/cycle-029-summary.md`

- [ ] **Step 1: Run manual CLI smoke**

```powershell
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --priority P0
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --target rcv-add-coworkers-modal
.\.venv\Scripts\ai-presenter validation-targets --package ringcentral-video --include-blocked
```

- [ ] **Step 2: Run full verification**

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m mypy src tests
.\.venv\Scripts\python -m ruff check src tests
```

- [ ] **Step 3: Request review subagent**

Ask for review of fallback compatibility, blank/duplicate ID errors, docs table shape, and CLI output.
