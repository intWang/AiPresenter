# Controller Chat Questions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add chat-style question history and immediate safe answer demonstrations to the AiPresenter controller.

**Architecture:** Extend controller submit results with demonstration status. Reuse the existing package action runner for idle single-step demos and the existing interrupt queue for running demos. Replace the answer label with an append-only Tk `Text` transcript.

**Tech Stack:** Python, Tkinter, pytest, existing `DemoControl`, `PackageActionExecutor`, and material package models.

---

### Task 1: Controller Question Result

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller.py`

- [x] Write failing tests for running, idle, and risky question submit results.
- [x] Add a small `QuestionSubmitResult` dataclass with `answer_text`, `demonstration_status`, and `demonstration_message`.
- [x] Make `PresenterController.submit_question()` return this dataclass.
- [x] Queue safe interrupts while running.
- [x] Start a single-step demo while idle.
- [x] Keep risky answers text-only.

### Task 2: Chat Transcript UI

**Files:**
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller.py`

- [x] Add a pure `format_chat_turns()` helper for testable transcript text.
- [x] Replace the single answer label with a read-only `Text` transcript.
- [x] Append `You`, `AiPresenter`, and demonstration status lines after Submit.
- [x] Clear the input field after Submit.

### Task 3: Verification

**Files:**
- Modify: `README.md` if controller behavior text needs updating.

- [x] Run focused controller tests.
- [x] Run full pytest, ruff, mypy, and doctor.
- [x] Restart the Piper controller for manual review.
