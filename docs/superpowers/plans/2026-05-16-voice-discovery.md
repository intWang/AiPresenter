# Voice Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe discovery surface for presenter language/tone aliases and profile voice compatibility.

**Architecture:** Expose read-only voice metadata helpers from `runtime.voice`, add a CLI `voices` command for catalog/profile checks, and add opt-in voice diagnostics to `doctor` through `runtime.diagnostics`.

**Tech Stack:** Python, Typer, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/voice.py`
  - Add public helper functions for aliases and tone descriptions.
- Modify `src/ai_presenter/runtime/diagnostics.py`
  - Add optional voice diagnostic support.
- Modify `src/ai_presenter/cli.py`
  - Add `voices` command.
  - Add optional `--language` and `--tone` to `doctor`.
- Modify `tests/unit/test_voice.py`
  - Add metadata helper coverage.
- Modify `tests/unit/test_diagnostics.py`
  - Add voice diagnostic coverage.
- Modify `tests/unit/test_cli.py`
  - Add CLI discovery and doctor voice tests.
- Modify `README.md` and `docs/runbooks/ringcentral-manual-acceptance.md`
  - Add discovery examples.
- Create `docs/agent-handoffs/cycle-013-*.md`.

## Tasks

### Task 1: Public Voice Metadata Helpers

**Files:**

- Modify: `tests/unit/test_voice.py`
- Modify: `src/ai_presenter/runtime/voice.py`

- [ ] **Step 1: Write failing tests**

Add:

```python
def test_presenter_language_aliases_are_public_and_canonical() -> None:
    assert presenter_language_aliases("zh-CN") == (
        "zh",
        "zh-cn",
        "zh-hans",
        "zh-tw",
        "zh-hant",
        "chinese",
        "中文",
    )


def test_presenter_tone_aliases_and_description_are_public() -> None:
    assert presenter_tone_aliases("mentor") == ("coach", "coaching", "mentor")
    assert "step-by-step" in presenter_tone_description("coach")
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py::test_presenter_language_aliases_are_public_and_canonical tests\unit\test_voice.py::test_presenter_tone_aliases_and_description_are_public
```

Expected: fail because helpers do not exist.

- [ ] **Step 3: Implement metadata helpers**

Add helpers that normalize the input and return aliases for the canonical value based on existing alias maps:

```python
def presenter_language_aliases(language: str) -> tuple[str, ...]:
    canonical = normalize_presenter_language(language)
    return tuple(alias for alias, value in _LANGUAGE_ALIASES.items() if value == canonical)


def presenter_tone_aliases(tone: str) -> tuple[str, ...]:
    canonical = normalize_presenter_tone(tone)
    return tuple(alias for alias, value in _TONE_ALIASES.items() if value == canonical)


def presenter_tone_description(tone: str) -> str:
    return _TONE_DESCRIPTIONS[normalize_presenter_tone(tone)]
```

- [ ] **Step 4: Verify green**

Run the same focused tests. Expected: pass.

### Task 2: Diagnostics Voice Check

**Files:**

- Modify: `tests/unit/test_diagnostics.py`
- Modify: `src/ai_presenter/runtime/diagnostics.py`

- [ ] **Step 1: Write failing tests**

Add:

```python
def test_diagnostics_reports_supported_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh-CN", tone="friendly"),
    )

    assert any(
        check.status == "OK"
        and check.name == "voice"
        and "Chinese / Friendly" in check.detail
        and "windows-sapi-zh" in check.detail
        for check in report.checks
    )


def test_diagnostics_reports_unsupported_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh-CN"),
    )

    assert report.failed_count == 1
    assert any(
        check.status == "FAIL"
        and check.name == "voice"
        and "speech provider fake" in check.detail
        for check in report.checks
    )
```

- [ ] **Step 2: Verify red**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_supported_voice tests\unit\test_diagnostics.py::test_diagnostics_reports_unsupported_voice
```

Expected: fail because `diagnose_configuration()` has no `voice` parameter.

- [ ] **Step 3: Implement diagnostic**

Import `PresenterVoiceSettings`, `language_label`, `tone_label`, `resolve_speech_provider_name`, and `validate_profile_voice`.

Extend `diagnose_configuration(..., voice: PresenterVoiceSettings | None = None)`. Append `_diagnose_voice(profile, voice)` only when voice is not `None`.

Implement:

```python
def _diagnose_voice(profile: AppProfile, voice: PresenterVoiceSettings) -> DiagnosticCheck:
    label = f"{language_label(voice.language)} / {tone_label(voice.tone)}"
    try:
        validate_profile_voice(profile, voice)
    except ValueError as exc:
        return DiagnosticCheck("FAIL", "voice", str(exc))
    route = resolve_speech_provider_name(profile, voice)
    return DiagnosticCheck(
        "OK",
        "voice",
        f"{label} supported via speech={route} (configured {profile.providers.speech})",
    )
```

- [ ] **Step 4: Verify green**

Run the same focused diagnostic tests. Expected: pass.

### Task 3: CLI Voices And Doctor Flags

**Files:**

- Modify: `tests/unit/test_cli.py`
- Modify: `src/ai_presenter/cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add:

```python
def test_voices_lists_language_tone_choices() -> None:
    result = CliRunner().invoke(app, ["voices"])

    assert result.exit_code == 0
    assert "Languages:" in result.stdout
    assert "English aliases:" in result.stdout
    assert "Chinese aliases:" in result.stdout
    assert "Tones:" in result.stdout
    assert "Coach aliases:" in result.stdout
```

```python
def test_voices_profile_reports_supported_and_unsupported_languages() -> None:
    result = CliRunner().invoke(app, ["voices", "--profile", "ringcentral-video"])

    assert result.exit_code == 0
    assert "Profile: ringcentral-video" in result.stdout
    assert "Configured speech provider: fake" in result.stdout
    assert "English / Professional: supported via fake" in result.stdout
    assert "Chinese / Professional: unsupported" in result.stdout
```

```python
def test_voices_targeted_incompatible_profile_voice_exits_nonzero() -> None:
    result = CliRunner().invoke(
        app,
        ["voices", "--profile", "ringcentral-video", "--language", "zh-CN", "--tone", "friendly"],
    )

    assert result.exit_code == 1
    assert "Selected voice: Chinese / Friendly" in result.stdout
    assert "speech provider fake" in result.stdout
```

```python
def test_doctor_accepts_language_and_tone_voice_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        [
            "doctor",
            "--profile",
            "ringcentral-video-bind-speaker",
            "--language",
            "zh-CN",
            "--tone",
            "friendly",
        ],
    )

    assert result.exit_code == 0
    assert "[OK] voice: Chinese / Friendly supported via speech=windows-sapi-zh" in result.stdout
```

```python
def test_doctor_rejects_unsupported_profile_voice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostics, "_iter_process_executable_paths", lambda process_name: [])

    result = CliRunner().invoke(
        app,
        ["doctor", "--profile", "ringcentral-video", "--language", "zh-CN"],
    )

    assert result.exit_code == 1
    assert "[FAIL] voice:" in result.stdout
    assert "speech provider fake" in result.stdout
```

- [ ] **Step 2: Verify red**

Run the five new CLI tests. Expected: fail because command/options do not exist.

- [ ] **Step 3: Implement CLI**

Add imports for shared voice choices and metadata helpers.

Add `voices()` command near `flows` and `entrypoints`.

Formatting rules:

- Print catalog sections first.
- If profile is present, print profile/provider and support rows for default tone using validation.
- If language/tone is targeted, print selected voice and exit 1 only if profile validation fails.

Extend `doctor()` with:

```python
language: str | None = typer.Option(None, "--language", help="Optional presenter language voice check.")
tone: str | None = typer.Option(None, "--tone", help="Optional presenter tone voice check.")
```

Resolve voice only when either option is present:

```python
voice = None
if language is not None or tone is not None:
    voice = resolve_voice_settings(language or "en", tone or "professional")
```

Pass `voice=voice` to `diagnose_configuration()`.

- [ ] **Step 4: Verify green**

Run the five CLI tests. Expected: pass.

### Task 4: Docs And Quality Gate

**Files:**

- Modify: `README.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-013-implementation.md`
- Create: `docs/agent-handoffs/cycle-013-review.md`
- Create: `docs/agent-handoffs/cycle-013-summary.md`

- [ ] **Step 1: Update docs**

Add examples:

```powershell
.venv\Scripts\ai-presenter voices
.venv\Scripts\ai-presenter voices --profile ringcentral-video-bind-speaker
.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly
```

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_voice.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\cli.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_voice.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\cli.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\runtime\voice.py tests\unit\test_cli.py tests\unit\test_diagnostics.py tests\unit\test_voice.py
```

Expected: all focused checks pass.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full tests pass with only the known pywinauto STA warning.

- [ ] **Step 4: Review and handoff**

Dispatch a review subagent for CLI output, diagnostic exit behavior, compatibility-rule reuse, and docs clarity. Record implementation evidence, review result, and follow-ups.
