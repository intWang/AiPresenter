# Native Chinese Narration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add native Chinese narration scripts and practical local TTS tone handling for the RingCentral Video control-map demo.

**Architecture:** Extend package narration with optional `localizedText` mappings. Resolve spoken text by language before tone rendering. Keep the RingCentral demo flow order unchanged while adding Chinese-authored scripts for each step.

**Tech Stack:** Python, Pydantic package models, YAML material packages, pytest, Windows SAPI TTS.

---

### Task 1: Localized Narration Model

**Files:**
- Modify: `src/ai_presenter/packages/models.py`
- Modify: `src/ai_presenter/runtime/voice.py`
- Modify: `src/ai_presenter/runtime/factory.py`
- Modify: `tests/unit/test_material_packages.py`
- Modify: `tests/unit/test_voice.py`

- [x] Add failing tests that `DemoStepNarration` accepts `localizedText` and Chinese rendering prefers it.
- [x] Add `localized_text: dict[str, str]` to `DemoStepNarration`.
- [x] Add a `render_narration_text()` helper that chooses localized text by language.
- [x] Update factory narration application to call the new helper.
- [x] Run focused tests until they pass.

### Task 2: Chinese RingCentral Scripts

**Files:**
- Modify: `packages/ringcentral-video.yaml`
- Modify: `tests/unit/test_material_packages.py`

- [x] Add failing coverage that every `meeting-control-map-demo` step has `localizedText.zh`.
- [x] Add native Chinese narration for each control-map step.
- [x] Verify the flow order and safe operation behavior are unchanged.

### Task 3: Local TTS Tone Controls

**Files:**
- Modify: `src/ai_presenter/runtime/voice.py`
- Modify: `src/ai_presenter/runtime/factory.py`
- Modify: `tests/unit/test_runtime_factory.py`
- Modify: `tests/unit/test_windows_speech_provider.py`

- [x] Add failing tests for tone-specific Windows SAPI rate selection.
- [x] Map Chinese professional, conversational, and concise tones to stable SAPI rates.
- [x] Route SAPI provider creation through the selected tone.
- [x] Smoke-test Huihui Chinese synthesis.

### Task 4: Verification And Restart

**Files:**
- Modify: docs only if implementation details differ from this plan.

- [x] Run focused tests.
- [x] Run full `pytest -q`, `ruff`, `mypy`, `doctor`, and `git diff --check`.
- [x] Commit the implementation.
- [x] Restart the controller with `ringcentral-video-piper-speaker`.
