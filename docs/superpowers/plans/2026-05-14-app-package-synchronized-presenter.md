# App Package Synchronized Presenter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the foundation for app-level material packages, synchronized action/audio timelines, and text-driven live presenter adjustments.

**Architecture:** Keep whole-app knowledge outside runtime code as YAML material packages. A package covers known surfaces, operation entry points, demo flows, concise explainers, and anticipated Q&A; VBG is one RingCentral Video flow inside that package. Convert package demo flows into timeline steps, then execute each step with explicit narration placement (`before`, `during`, `after`) so audio and UI actions can be coordinated. Manual text or future audio input feeds the same directive interface.

**Tech Stack:** Python 3.10, Pydantic, PyYAML, pytest, existing `SpeechProvider` and `MediaOutput` protocols.

---

## File Structure

- `src/ai_presenter/packages/models.py`: Pydantic schema for app material packages, operation entry points, demo flows, and manual controls.
- `src/ai_presenter/packages/loader.py`: YAML loader and validator for material packages.
- `src/ai_presenter/runtime/sync.py`: synchronized timeline runner with before/during/after narration placement.
- `src/ai_presenter/runtime/manual.py`: text directive queue for live presenter adjustments.
- `packages/ringcentral-video.yaml`: first RingCentral Video app material package, including VBG as one demo flow.
- `tests/unit/test_material_packages.py`: package loader and validation tests.
- `tests/unit/test_synchronized_timeline.py`: action/audio ordering and manual override tests.

## Tasks

### Task 1: Material Package Schema

- [ ] Write failing tests for loading the RingCentral Video app package.
- [ ] Add package models and loader.
- [ ] Add validation for duplicate operation IDs and demo flow references to unknown entry points.
- [ ] Add the RingCentral Video app package with pre-familiarized operation entry points across meeting launch, audio/video, background, sharing, invite, participants, chat, reactions, settings, and leave flows.

### Task 2: Synchronized Timeline Runner

- [ ] Write failing tests for `before`, `during`, and `after` narration placement.
- [ ] Implement a timeline runner that synthesizes narration before action execution and plays audio in the requested placement.
- [ ] For `during`, start audio playback in a background thread, execute the action after the configured offset, then surface playback or action failures.

### Task 3: Manual Text Directives

- [ ] Write failing tests for `say: ...` and `skip` text directives.
- [ ] Implement a manual directive queue.
- [ ] Let the timeline runner consume one pending directive per step so humans can override narration or skip the current step.

### Task 4: Verification

- [ ] Run targeted unit tests for packages and synchronized timeline.
- [ ] Run full pytest.
- [ ] Run ruff and mypy.
