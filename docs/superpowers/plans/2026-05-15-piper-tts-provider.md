# Piper TTS Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a free Piper TTS speech provider and a RingCentral profile that can use it for more natural local English narration.

**Architecture:** Introduce a focused `PiperSpeechProvider` that shells out to `python -m piper`, reads the generated WAV into `SpeechAudio`, and plugs into the existing provider registry. Keep profile and media output behavior unchanged so existing demos continue to run.

**Tech Stack:** Python, pytest, pydantic profiles, Piper TTS CLI, existing `SpeechProvider` and `MediaOutput` interfaces.

---

## File Structure

- `src/ai_presenter/providers/piper_provider.py`: new provider, subprocess runner, WAV validation.
- `src/ai_presenter/runtime/factory.py`: register `piper` when selected by profile.
- `profiles/ringcentral-video-piper-speaker.yaml`: test profile using Piper and speaker output.
- `tests/unit/test_piper_provider.py`: unit tests for synth success, blank text, subprocess errors.
- `tests/unit/test_runtime_factory.py`: provider registry test for `piper`.
- `README.md`: short note for installing and smoke testing Piper.

---

### Task 1: Piper Provider Unit Tests

**Files:**
- Create: `tests/unit/test_piper_provider.py`

- [ ] **Step 1: Write the failing success and error tests**

Create `tests/unit/test_piper_provider.py`:

```python
import subprocess
import wave
from pathlib import Path

import pytest

from ai_presenter.providers.piper_provider import PiperSpeechProvider


def write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16_000)
        wav.writeframes(b"\x00\x00" * 1600)


def test_piper_provider_returns_wav_audio(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        output_path = Path(command[command.index("-f") + 1])
        write_wav(output_path)
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    provider = PiperSpeechProvider(
        voice="en_US-lessac-medium",
        runner=runner,
        temp_dir=tmp_path,
    )

    audio = provider.synthesize("Hello from Piper.")

    assert audio.mime_type == "audio/wav"
    assert len(audio.data) > 46
    assert calls[0][0:3] == ["python", "-m", "piper"]
    assert "en_US-lessac-medium" in calls[0]
    assert calls[0][-1] == "Hello from Piper."


def test_piper_provider_rejects_blank_text(tmp_path: Path) -> None:
    provider = PiperSpeechProvider(temp_dir=tmp_path)

    with pytest.raises(ValueError, match="Speech text cannot be blank"):
        provider.synthesize("   ")


def test_piper_provider_reports_failed_command(tmp_path: Path) -> None:
    def runner(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="missing model")

    provider = PiperSpeechProvider(runner=runner, temp_dir=tmp_path)

    with pytest.raises(RuntimeError, match="missing model"):
        provider.synthesize("Hello.")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_piper_provider.py -q --no-cov`

Expected: FAIL with `ModuleNotFoundError: No module named 'ai_presenter.providers.piper_provider'`.

- [ ] **Step 3: Commit nothing**

Do not commit yet; Task 2 supplies the implementation.

---

### Task 2: Piper Provider Implementation

**Files:**
- Create: `src/ai_presenter/providers/piper_provider.py`
- Test: `tests/unit/test_piper_provider.py`

- [ ] **Step 1: Implement provider**

Create `src/ai_presenter/providers/piper_provider.py`:

```python
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from ai_presenter.providers.base import SpeechAudio

PiperRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]


class PiperSpeechProvider:
    def __init__(
        self,
        *,
        voice: str = "en_US-lessac-medium",
        data_dir: Path | None = None,
        download_dir: Path | None = None,
        timeout_seconds: float = 30,
        runner: PiperRunner | None = None,
        temp_dir: Path | None = None,
    ) -> None:
        self._voice = _require_nonblank(voice, "Piper voice cannot be blank.")
        self._data_dir = data_dir
        self._download_dir = download_dir
        self._timeout_seconds = timeout_seconds
        self._runner = runner or _run_piper
        self._temp_dir = temp_dir

    def synthesize(self, text: str) -> SpeechAudio:
        speech_text = text.strip()
        if not speech_text:
            raise ValueError("Speech text cannot be blank.")

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
            dir=self._temp_dir,
        ) as output_file:
            output_path = Path(output_file.name)

        try:
            command = self._command(output_path, speech_text)
            result = self._runner(command, self._timeout_seconds)
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
                raise RuntimeError(f"Piper TTS failed: {detail}")
            data = output_path.read_bytes()
            if len(data) <= 46:
                raise RuntimeError("Piper TTS returned empty audio.")
            return SpeechAudio(
                data=data,
                mime_type="audio/wav",
                sample_rate=0,
                channels=1,
            )
        finally:
            output_path.unlink(missing_ok=True)

    def _command(self, output_path: Path, text: str) -> list[str]:
        command = ["python", "-m", "piper", "-m", self._voice, "-f", str(output_path)]
        if self._data_dir is not None:
            command.extend(["--data-dir", str(self._data_dir)])
        if self._download_dir is not None:
            command.extend(["--download-dir", str(self._download_dir)])
        command.extend(["--", text])
        return command


def _run_piper(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Python executable was not found while running Piper TTS.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Piper TTS timed out.") from exc


def _require_nonblank(value: str, message: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(message)
    return normalized
```

- [ ] **Step 2: Run provider tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_piper_provider.py -q --no-cov`

Expected: PASS.

- [ ] **Step 3: Commit**

```powershell
git add src\ai_presenter\providers\piper_provider.py tests\unit\test_piper_provider.py
git commit -m "feat: add piper speech provider"
```

---

### Task 3: Provider Registry And Profile

**Files:**
- Modify: `src/ai_presenter/runtime/factory.py`
- Create: `profiles/ringcentral-video-piper-speaker.yaml`
- Modify: `tests/unit/test_runtime_factory.py`

- [ ] **Step 1: Write failing registry test**

Add to `tests/unit/test_runtime_factory.py`:

```python
def test_provider_registry_supports_piper_profile() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))

    registry = create_provider_registry(profile)

    assert profile.providers.speech == "piper"
    assert registry.speech(profile.providers.speech).__class__.__name__ == "PiperSpeechProvider"
```

- [ ] **Step 2: Create profile**

Copy `profiles/ringcentral-video-bind-speaker.yaml` to `profiles/ringcentral-video-piper-speaker.yaml`, then change:

```yaml
id: ringcentral-video-piper-speaker
providers:
  vision: fake
  narration: fake
  speech: piper
```

- [ ] **Step 3: Verify test fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_runtime_factory.py::test_provider_registry_supports_piper_profile -q --no-cov`

Expected: FAIL because `piper` is not registered.

- [ ] **Step 4: Register provider**

In `src/ai_presenter/runtime/factory.py`, import:

```python
from ai_presenter.providers.piper_provider import PiperSpeechProvider
```

Add inside `create_provider_registry()`:

```python
    if profile.providers.speech == "piper":
        registry.register_speech("piper", PiperSpeechProvider())
```

- [ ] **Step 5: Run registry test**

Run: `.\.venv\Scripts\python.exe -m pytest tests\unit\test_runtime_factory.py::test_provider_registry_supports_piper_profile -q --no-cov`

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add src\ai_presenter\runtime\factory.py profiles\ringcentral-video-piper-speaker.yaml tests\unit\test_runtime_factory.py
git commit -m "feat: add piper RingCentral profile"
```

---

### Task 4: Documentation And Smoke Test

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add README instructions**

Add a short section:

```markdown
## Piper TTS

For a free local neural TTS test:

```powershell
.venv\Scripts\python -m pip install piper-tts
.venv\Scripts\python -m piper.download_voices en_US-lessac-medium
.venv\Scripts\ai-presenter controller --profile ringcentral-video-piper-speaker --package ringcentral-video --flow meeting-control-map-demo
```

The first Piper voice download can take a little while. The profile outputs to the configured speaker device.
```

- [ ] **Step 2: Run automated verification**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_piper_provider.py tests\unit\test_runtime_factory.py -q --no-cov
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src tests
```

Expected: all pass.

- [ ] **Step 3: Install Piper for local smoke**

Run:

```powershell
.\.venv\Scripts\python.exe -m pip install piper-tts
.\.venv\Scripts\python.exe -m piper.download_voices en_US-lessac-medium
```

Expected: install succeeds and the voice downloads.

- [ ] **Step 4: Smoke synthesize one line**

Run:

```powershell
@'
from pathlib import Path
from ai_presenter.config.loader import load_profile
from ai_presenter.runtime.factory import create_provider_registry, create_media_output
profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
registry = create_provider_registry(profile)
audio = registry.speech(profile.providers.speech).synthesize("This is AiPresenter using Piper.")
print(len(audio.data))
create_media_output(profile).play(audio)
'@ | .\.venv\Scripts\python.exe -
```

Expected: prints a byte count above 46 and plays audible speech on the configured speaker device.

- [ ] **Step 5: Commit docs**

```powershell
git add README.md
git commit -m "docs: add piper tts smoke test"
```

---

## Self-Review

Spec coverage:

- Free TTS provider: Tasks 1 and 2.
- Existing providers unchanged: Task 3 only registers `piper`.
- RingCentral test profile: Task 3.
- Smoke path: Task 4.
- Error handling and tests: Tasks 1 and 2.

Placeholder scan:

- No `TBD`, `TODO`, or unspecified test steps.

Type consistency:

- `PiperSpeechProvider.synthesize()` returns `SpeechAudio`, matching existing speech providers.
- Registry key is consistently `piper`.
