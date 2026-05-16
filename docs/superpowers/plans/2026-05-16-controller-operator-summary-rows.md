# Controller Operator Summary Rows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the controller operator state easier to scan by rendering the existing view model as compact rows.

**Architecture:** Keep `ControllerOperatorViewModel` as the source of truth. Add a pure row renderer, preserve the compatibility one-line renderer, and update Tk wiring to display newline-joined rows.

**Tech Stack:** Python dataclasses, Tkinter StringVar/Label, pytest.

---

### Task 1: Failing Row Renderer Tests

**Files:**
- Modify: `tests/unit/test_controller_view_model.py`

- [ ] Add a test for ready material package rows.
- [ ] Add a test proving the Actions row appears only when Start or Submit has disabled reasons.
- [ ] Run the tests and verify RED.

### Task 2: Row Renderer Implementation

**Files:**
- Modify: `src/ai_presenter/runtime/controller_view_model.py`

- [ ] Add `ControllerOperatorSummaryRow`.
- [ ] Add `controller_operator_summary_rows()`.
- [ ] Add `render_controller_operator_summary_rows()`.
- [ ] Preserve `render_controller_operator_summary()` by joining the row strings.
- [ ] Run the focused row tests and verify GREEN.

### Task 3: Tk Wiring

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller.py`

- [ ] Add a tiny `render_operator_summary_text()` helper that newline-joins row strings.
- [ ] Use that helper in `refresh_operator_view()`.
- [ ] Set the operator summary label `justify="left"`.
- [ ] Add a focused helper test proving the controller-facing text is multiline.

### Task 4: Verification And Review

**Files:**
- Create: `docs/agent-handoffs/cycle-031-review.md`
- Create: `docs/agent-handoffs/cycle-031-summary.md`

- [ ] Run focused controller tests.
- [ ] Run full pytest, mypy, and ruff.
- [ ] Request review focused on UI scanability, row stability, and behavior preservation.
