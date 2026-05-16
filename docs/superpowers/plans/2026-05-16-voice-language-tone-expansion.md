# Voice Language And Tone Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand presenter language aliases and tone modes while keeping runtime voice routing canonical and provider-safe.

**Architecture:** Normalize `PresenterVoiceSettings` construction in `runtime.voice`, expose shared language/tone choice metadata, and update controller labeling/options to consume that metadata. Keep TTS provider routing based on canonical `en`/`zh` values.

**Tech Stack:** Python dataclasses, Tkinter controller, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/voice.py`
  - Add canonical language/tone literals and option metadata.
  - Replace generated dataclass init with a normalizing init.
  - Add tone descriptions and render behavior for friendly/coach/formal.
- Modify `src/ai_presenter/runtime/controller_view_model.py`
  - Use shared label helpers from `runtime.voice`.
- Modify `src/ai_presenter/runtime/controller.py`
  - Build OptionMenus from shared voice choices.
- Modify `tests/unit/test_voice.py`
  - Add normalization, rejection, rendering, provider routing, and SAPI rate tests.
- Modify `tests/unit/test_controller.py` and `tests/unit/test_controller_view_model.py`
  - Add label coverage for expanded tones.

## Tasks

### Task 1: Voice Settings Normalization

**Files:**

- Modify: `tests/unit/test_voice.py`
- Modify: `src/ai_presenter/runtime/voice.py`

- [ ] **Step 1: Write failing tests**

Add tests:

```python
def test_voice_settings_normalize_language_aliases() -> None:
    assert PresenterVoiceSettings(language="zh-CN").language == "zh"
    assert PresenterVoiceSettings(language="zh-Hans").language == "zh"
    assert PresenterVoiceSettings(language="English").language == "en"
    assert PresenterVoiceSettings(language="en-US").language == "en"


def test_voice_settings_normalize_expanded_tones() -> None:
    assert PresenterVoiceSettings(tone="friendly").tone == "friendly"
    assert PresenterVoiceSettings(tone="warm").tone == "friendly"
    assert PresenterVoiceSettings(tone="mentor").tone == "coach"
    assert PresenterVoiceSettings(tone="structured").tone == "formal"


def test_voice_settings_reject_unknown_language_and_tone() -> None:
    with pytest.raises(ValueError, match="Unsupported presenter language"):
        PresenterVoiceSettings(language="es")
    with pytest.raises(ValueError, match="Unsupported presenter tone"):
        PresenterVoiceSettings(tone="shouty")
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_voice_settings_reject_unknown_language_and_tone
```

Expected: tests fail because aliases/new tones are unsupported.

- [ ] **Step 3: Implement normalizing init**

Use `@dataclass(frozen=True, init=False)` for `PresenterVoiceSettings`, set canonical `language` and `tone` in `__init__`, and add helper functions `normalize_presenter_language()` and `normalize_presenter_tone()`.

- [ ] **Step 4: Verify green**

Run the same focused pytest command. Expected: all three tests pass.

### Task 2: Tone Rendering And Provider Routing

**Files:**

- Modify: `tests/unit/test_voice.py`
- Modify: `src/ai_presenter/runtime/voice.py`

- [ ] **Step 1: Write failing rendering/routing tests**

Add tests for new tones:

```python
def test_voice_instruction_describes_expanded_tones() -> None:
    assert "warm" in render_voice_instruction(PresenterVoiceSettings(tone="friendly"))
    assert "step-by-step" in render_voice_instruction(PresenterVoiceSettings(tone="coach"))
    assert "formal" in render_voice_instruction(PresenterVoiceSettings(tone="formal"))


def test_render_presenter_text_applies_expanded_english_tones() -> None:
    assert render_presenter_text("Open Chat.", PresenterVoiceSettings(tone="friendly")).startswith(
        "Happy to help."
    )
    assert render_presenter_text("Open Chat.", PresenterVoiceSettings(tone="coach")).startswith(
        "Let's walk through it."
    )
    assert render_presenter_text("Open Chat.", PresenterVoiceSettings(tone="formal")).startswith(
        "Certainly."
    )


def test_language_aliases_use_existing_provider_routing() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    assert resolve_speech_provider_name(profile, PresenterVoiceSettings(language="zh-CN")) == (
        "windows-sapi-zh"
    )
```

- [ ] **Step 2: Verify red**

Run the three new tests. Expected: they fail until render/provider code supports expanded values.

- [ ] **Step 3: Implement render and rate behavior**

Extend `_TONE_DESCRIPTIONS`, `render_presenter_text()`, `_render_chinese()`, and `sapi_rate_for_voice()` for new tones. Keep localized narration behavior unchanged except concise.

- [ ] **Step 4: Verify green**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py
```

Expected: all voice tests pass.

### Task 3: Controller Voice Choices

**Files:**

- Modify: `src/ai_presenter/runtime/voice.py`
- Modify: `src/ai_presenter/runtime/controller_view_model.py`
- Modify: `src/ai_presenter/runtime/controller.py`
- Modify: `tests/unit/test_controller.py`
- Modify: `tests/unit/test_controller_view_model.py`

- [ ] **Step 1: Write failing controller label tests**

Add tests:

```python
def test_render_voice_label_supports_expanded_tone() -> None:
    assert render_voice_label(PresenterVoiceSettings(language="zh-CN", tone="friendly")) == (
        "Chinese / Friendly"
    )
```

Also add a view-model assertion for `PresenterVoiceSettings(tone="coach")` rendering `English / Coach`.

- [ ] **Step 2: Verify red**

Run the new controller label tests. Expected: fail because label maps do not include expanded tones and `zh-CN` is not accepted.

- [ ] **Step 3: Centralize labels**

Expose `language_label()`, `tone_label()`, `PRESENTER_LANGUAGE_CHOICES`, and `PRESENTER_TONE_CHOICES` from `runtime.voice`. Update `controller_view_model.render_voice_label()` and controller `OptionMenu` setup/current voice construction to use these shared choices.

- [ ] **Step 4: Verify green**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_view_model.py
```

Expected: controller tests pass.

### Task 4: Quality Gate

**Files:**

- Create: `docs/agent-handoffs/cycle-009-implementation.md`
- Create: `docs/agent-handoffs/cycle-009-review.md`
- Create: `docs/agent-handoffs/cycle-009-summary.md`

- [ ] **Step 1: Run verification**

Run:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\voice.py src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\controller_view_model.py tests\unit\test_voice.py tests\unit\test_controller.py tests\unit\test_controller_view_model.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: all checks pass with only known environmental warnings.

- [ ] **Step 2: Request review**

Dispatch a review subagent for behavior drift, provider compatibility, UI choice consistency, and type safety.

- [ ] **Step 3: Write handoff docs**

Record red/green evidence, verification output, review result, and remaining follow-ups.
