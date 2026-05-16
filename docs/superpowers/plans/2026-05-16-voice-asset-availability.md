# Voice Asset Availability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add side-effect-free local voice asset availability checks for Windows SAPI and Piper routes.

**Architecture:** Keep provider discovery helpers close to the providers, add one runtime voice-asset helper that maps configured voice settings to concrete local requirements, then surface that helper through `doctor` and `voices`. Checks must be read-only and injectable for tests.

**Tech Stack:** Python, Typer, Pydantic-adjacent config models, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/providers/windows_speech.py`
  - Add installed-voice dataclass, SAPI enumeration helper, and substring availability helper.
- Modify `tests/unit/test_windows_speech_provider.py`
  - Add fake SAPI enumeration and matching tests.
- Modify `src/ai_presenter/providers/piper_provider.py`
  - Add Piper asset dataclass, default asset resolver, local file check, and module check.
- Modify `tests/unit/test_piper_provider.py`
  - Add default path and local file availability tests.
- Create `src/ai_presenter/runtime/voice_assets.py`
  - Add `VoiceAssetAvailability` and `check_voice_asset_availability()`.
- Create `tests/unit/test_voice_assets.py`
  - Add route-level tests with injected SAPI listers and Piper resolvers.
- Modify `src/ai_presenter/runtime/diagnostics.py`
  - Add `voice assets` diagnostic after compatible local voice checks.
- Modify `tests/unit/test_diagnostics.py`
  - Add doctor diagnostics for OK/missing SAPI and OK/missing Piper assets.
- Modify `src/ai_presenter/cli.py`
  - Add asset status to `voices --profile` matrix and targeted checks.
- Modify `tests/unit/test_cli.py`
  - Add `voices` matrix and targeted missing-asset behavior.
- Modify `README.md`
  - Explain that `voices` shows local asset status and `doctor --language/--tone` is the strict preflight.
- Modify `docs/runbooks/ringcentral-manual-acceptance.md`
  - Add one local asset preflight checklist item.
- Create `docs/agent-handoffs/cycle-015-implementation.md`
  - Record red/green and verification evidence.

## Tasks

### Task 1: Provider Asset Helpers

**Files:**

- Modify: `src/ai_presenter/providers/windows_speech.py`
- Modify: `tests/unit/test_windows_speech_provider.py`
- Modify: `src/ai_presenter/providers/piper_provider.py`
- Modify: `tests/unit/test_piper_provider.py`

- [ ] **Step 1: Write failing Windows SAPI helper tests**

Add tests that import `InstalledSapiVoice`, `list_installed_sapi_voices`, and
`sapi_voice_available`.

```python
def test_list_installed_sapi_voices_uses_injected_dispatcher() -> None:
    class FakeToken:
        Id = "token-id"

        def GetDescription(self) -> str:
            return "Microsoft Huihui Desktop"

    class FakeVoice:
        def GetVoices(self) -> list[FakeToken]:
            return [FakeToken()]

    def dispatch(name: str) -> FakeVoice:
        assert name == "SAPI.SpVoice"
        return FakeVoice()

    voices = list_installed_sapi_voices(dispatcher=dispatch)

    assert voices == (InstalledSapiVoice(name="Microsoft Huihui Desktop", token_id="token-id"),)


def test_sapi_voice_available_matches_case_insensitive_substrings() -> None:
    voices = (
        InstalledSapiVoice(name="Microsoft Zira Desktop"),
        InstalledSapiVoice(name="Microsoft Huihui Desktop"),
    )

    assert sapi_voice_available("zira", voices) is True
    assert sapi_voice_available("Huihui", voices) is True
    assert sapi_voice_available("Jenny", voices) is False
```

- [ ] **Step 2: Verify Windows helper tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_windows_speech_provider.py::test_list_installed_sapi_voices_uses_injected_dispatcher tests\unit\test_windows_speech_provider.py::test_sapi_voice_available_matches_case_insensitive_substrings
```

Expected: fail because the helper APIs do not exist.

- [ ] **Step 3: Implement Windows helper APIs**

Add:

```python
@dataclass(frozen=True)
class InstalledSapiVoice:
    name: str
    token_id: str | None = None


SapiDispatcher = Callable[[str], Any]


def list_installed_sapi_voices(
    *,
    dispatcher: SapiDispatcher | None = None,
) -> tuple[InstalledSapiVoice, ...]:
    if dispatcher is None:
        win32com_client = importlib.import_module("win32com.client")
        dispatcher = win32com_client.Dispatch
    voice = dispatcher("SAPI.SpVoice")
    installed: list[InstalledSapiVoice] = []
    for token in voice.GetVoices():
        description = token.GetDescription()
        if not isinstance(description, str) or not description.strip():
            continue
        token_id = getattr(token, "Id", None)
        installed.append(
            InstalledSapiVoice(
                name=description.strip(),
                token_id=token_id if isinstance(token_id, str) and token_id.strip() else None,
            )
        )
    return tuple(installed)


def sapi_voice_available(voice_name: str, voices: Iterable[InstalledSapiVoice]) -> bool:
    expected = voice_name.strip().casefold()
    if not expected:
        return False
    return any(expected in voice.name.casefold() for voice in voices)
```

Import `dataclass`, `Iterable`, and keep existing synthesis behavior unchanged.

- [ ] **Step 4: Write failing Piper asset helper tests**

Add tests that import `PiperVoiceAssets`, `default_piper_voice_assets`,
`piper_voice_assets_available`, and `piper_module_available`.

```python
def test_default_piper_voice_assets_use_provider_data_dir(tmp_path: Path) -> None:
    assets = default_piper_voice_assets(data_dir=tmp_path)

    assert assets.voice == "en_US-lessac-medium"
    assert assets.model_path == tmp_path / "en_US-lessac-medium.onnx"
    assert assets.config_path == tmp_path / "en_US-lessac-medium.onnx.json"


def test_piper_voice_assets_available_requires_model_and_config(tmp_path: Path) -> None:
    assets = default_piper_voice_assets(data_dir=tmp_path)
    assert piper_voice_assets_available(assets) is False

    assets.model_path.write_text("model", encoding="utf-8")
    assert piper_voice_assets_available(assets) is False

    assets.config_path.write_text("{}", encoding="utf-8")
    assert piper_voice_assets_available(assets) is True
```

- [ ] **Step 5: Verify Piper helper tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_piper_provider.py::test_default_piper_voice_assets_use_provider_data_dir tests\unit\test_piper_provider.py::test_piper_voice_assets_available_requires_model_and_config
```

Expected: fail because the helper APIs do not exist.

- [ ] **Step 6: Implement Piper helper APIs**

Add:

```python
@dataclass(frozen=True)
class PiperVoiceAssets:
    voice: str
    data_dir: Path
    model_path: Path
    config_path: Path


def default_piper_voice_assets(
    voice: str = "en_US-lessac-medium",
    data_dir: Path | None = None,
) -> PiperVoiceAssets:
    normalized_voice = _require_nonblank(voice, "Piper voice cannot be blank.")
    root = data_dir or _default_data_dir()
    return PiperVoiceAssets(
        voice=normalized_voice,
        data_dir=root,
        model_path=root / f"{normalized_voice}.onnx",
        config_path=root / f"{normalized_voice}.onnx.json",
    )


def piper_voice_assets_available(assets: PiperVoiceAssets) -> bool:
    return assets.model_path.is_file() and assets.config_path.is_file()


def piper_module_available(module_name: str = "piper") -> bool:
    return importlib.util.find_spec(module_name) is not None
```

Import `dataclass` and `importlib.util`. Do not call Piper or download anything.

- [ ] **Step 7: Verify provider helper tests pass**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py
```

Expected: pass.

### Task 2: Runtime Voice Asset Availability

**Files:**

- Create: `src/ai_presenter/runtime/voice_assets.py`
- Create: `tests/unit/test_voice_assets.py`

- [ ] **Step 1: Write failing runtime availability tests**

Create tests with injected dependencies:

```python
from pathlib import Path

from ai_presenter.config.loader import load_profile
from ai_presenter.providers.piper_provider import PiperVoiceAssets
from ai_presenter.providers.windows_speech import InstalledSapiVoice
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice_assets import check_voice_asset_availability


def test_voice_asset_check_finds_chinese_sapi_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    result = check_voice_asset_availability(
        profile,
        PresenterVoiceSettings(language="zh"),
        sapi_voice_lister=lambda: (InstalledSapiVoice("Microsoft Huihui Desktop"),),
    )

    assert result is not None
    assert result.status == "OK"
    assert "windows-sapi-zh" in result.detail


def test_voice_asset_check_reports_missing_chinese_sapi_voice() -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))

    result = check_voice_asset_availability(
        profile,
        PresenterVoiceSettings(language="zh"),
        sapi_voice_lister=lambda: (InstalledSapiVoice("Microsoft Zira Desktop"),),
    )

    assert result is not None
    assert result.status == "FAIL"
    assert "Huihui" in result.detail


def test_voice_asset_check_reports_missing_piper_model(tmp_path: Path) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-piper-speaker.yaml"))
    assets = PiperVoiceAssets(
        voice="en_US-lessac-medium",
        data_dir=tmp_path,
        model_path=tmp_path / "en_US-lessac-medium.onnx",
        config_path=tmp_path / "en_US-lessac-medium.onnx.json",
    )

    result = check_voice_asset_availability(
        profile,
        PresenterVoiceSettings(language="en"),
        piper_asset_resolver=lambda: assets,
        piper_module_checker=lambda: True,
    )

    assert result is not None
    assert result.status == "FAIL"
    assert "en_US-lessac-medium" in result.detail


def test_voice_asset_check_skips_fake_and_openai_routes() -> None:
    profile = load_profile(Path("profiles/ringcentral-video.yaml"))

    assert check_voice_asset_availability(profile, PresenterVoiceSettings()) is None
```

- [ ] **Step 2: Verify runtime availability tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice_assets.py
```

Expected: fail because `runtime.voice_assets` does not exist.

- [ ] **Step 3: Implement runtime availability helper**

Create `src/ai_presenter/runtime/voice_assets.py`:

```python
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from ai_presenter.config.models import AppProfile
from ai_presenter.providers.piper_provider import PiperVoiceAssets
from ai_presenter.providers.piper_provider import default_piper_voice_assets
from ai_presenter.providers.piper_provider import piper_module_available
from ai_presenter.providers.piper_provider import piper_voice_assets_available
from ai_presenter.providers.windows_speech import InstalledSapiVoice
from ai_presenter.providers.windows_speech import list_installed_sapi_voices
from ai_presenter.providers.windows_speech import sapi_voice_available
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import resolve_speech_provider_name

VoiceAssetStatus = Literal["OK", "FAIL"]
SapiVoiceLister = Callable[[], tuple[InstalledSapiVoice, ...]]
PiperAssetResolver = Callable[[], PiperVoiceAssets]
PiperModuleChecker = Callable[[], bool]


@dataclass(frozen=True)
class VoiceAssetAvailability:
    status: VoiceAssetStatus
    route: str
    detail: str


def check_voice_asset_availability(
    profile: AppProfile,
    voice: PresenterVoiceSettings,
    *,
    sapi_voice_lister: SapiVoiceLister = list_installed_sapi_voices,
    piper_asset_resolver: PiperAssetResolver = default_piper_voice_assets,
    piper_module_checker: PiperModuleChecker = piper_module_available,
) -> VoiceAssetAvailability | None:
    route = resolve_speech_provider_name(profile, voice)
    if route == "windows-sapi-en":
        return _check_sapi_voice(route, "Zira", sapi_voice_lister)
    if route == "windows-sapi-zh":
        return _check_sapi_voice(route, "Huihui", sapi_voice_lister)
    if route == "windows-sapi":
        return _check_any_sapi_voice(route, sapi_voice_lister)
    if route == "piper":
        return _check_piper_assets(route, piper_asset_resolver, piper_module_checker)
    return None
```

Implement private helpers so SAPI enumeration exceptions become `FAIL` details and Piper missing
module/model paths name the missing requirement.

- [ ] **Step 4: Verify runtime availability tests pass**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice_assets.py
```

Expected: pass.

### Task 3: Diagnostics And CLI Surfacing

**Files:**

- Modify: `src/ai_presenter/runtime/diagnostics.py`
- Modify: `tests/unit/test_diagnostics.py`
- Modify: `src/ai_presenter/cli.py`
- Modify: `tests/unit/test_cli.py`

- [ ] **Step 1: Write failing diagnostics tests**

Add tests that monkeypatch `diagnostics.check_voice_asset_availability`:

```python
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def test_diagnostics_reports_voice_assets_after_supported_voice(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert any(check.status == "OK" and check.name == "voice assets" for check in report.checks)


def test_diagnostics_fails_for_missing_voice_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = load_profile(Path("profiles/ringcentral-video-bind-speaker.yaml"))
    monkeypatch.setattr(
        diagnostics,
        "check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
        ),
    )

    report = diagnostics.diagnose_configuration(
        profile=profile,
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert report.failed_count == 1
    assert any("Huihui" in check.detail for check in report.checks if check.name == "voice assets")
```

- [ ] **Step 2: Verify diagnostics tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_voice_assets_after_supported_voice tests\unit\test_diagnostics.py::test_diagnostics_fails_for_missing_voice_assets
```

Expected: fail because diagnostics do not call asset checks yet.

- [ ] **Step 3: Implement diagnostics asset checks**

Import `check_voice_asset_availability`. Change `diagnose_configuration()` so when `voice is not None`
it appends the existing `_diagnose_voice()` result, then appends `_diagnose_voice_assets()` only if the
voice compatibility result is OK.

```python
def _diagnose_voice_assets(profile: AppProfile, voice: PresenterVoiceSettings) -> DiagnosticCheck | None:
    result = check_voice_asset_availability(profile, voice)
    if result is None:
        return None
    return DiagnosticCheck(result.status, "voice assets", result.detail)
```

- [ ] **Step 4: Write failing CLI `voices` tests**

Add tests that monkeypatch `ai_presenter.cli.check_voice_asset_availability`:

```python
from ai_presenter.runtime.voice_assets import VoiceAssetAvailability


def test_voices_profile_reports_local_asset_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ai_presenter.cli.check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="OK",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh found installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(app, ["voices", "--profile", "ringcentral-video-bind-speaker"])

    assert result.exit_code == 0
    assert "assets OK" in result.stdout
    assert "Huihui" in result.stdout


def test_voices_targeted_missing_assets_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ai_presenter.cli.check_voice_asset_availability",
        lambda *_args, **_kwargs: VoiceAssetAvailability(
            status="FAIL",
            route="windows-sapi-zh",
            detail="speech=windows-sapi-zh requires installed SAPI voice matching Huihui",
        ),
    )

    result = CliRunner().invoke(
        app,
        ["voices", "--profile", "ringcentral-video-bind-speaker", "--language", "zh-CN"],
    )

    assert result.exit_code == 1
    assert "Selected voice assets unavailable" in result.stdout
    assert "Huihui" in result.stdout
```

- [ ] **Step 5: Verify CLI tests fail**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_profile_reports_local_asset_status tests\unit\test_cli.py::test_voices_targeted_missing_assets_exits_nonzero
```

Expected: fail because CLI does not print asset status yet.

- [ ] **Step 6: Implement CLI surfacing**

Import `check_voice_asset_availability`. In profile matrix mode, append asset status for supported
routes:

```python
asset = check_voice_asset_availability(loaded_profile, voice)
asset_detail = "" if asset is None else f"; assets {asset.status}: {asset.detail}"
typer.echo(f"- {label}: supported via {route}{asset_detail}")
```

In targeted mode, after compatibility passes:

```python
asset = check_voice_asset_availability(loaded_profile, selected_voice)
if asset is not None:
    if asset.status == "FAIL":
        typer.echo(f"Selected voice assets unavailable: {asset.detail}")
        raise typer.Exit(1)
    typer.echo(f"Selected voice assets available: {asset.detail}")
```

- [ ] **Step 7: Verify diagnostics and CLI tests pass**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Expected: pass.

### Task 4: Documentation And Quality Gate

**Files:**

- Modify: `README.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`
- Create: `docs/agent-handoffs/cycle-015-implementation.md`

- [ ] **Step 1: Update docs**

In README voice discovery text, state:

```markdown
`voices --profile ...` also reports local speech asset status for supported local routes.
For a strict pre-demo check, run `doctor --profile ... --language ... --tone ...`; missing SAPI
voices or Piper model files fail before a demo launches.
```

In the RingCentral manual acceptance runbook, add a checklist item that runs:

```powershell
.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly
```

and expects both `[OK] voice:` and `[OK] voice assets:` when the local Huihui SAPI voice is installed.

- [ ] **Step 2: Run focused verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py tests\unit\test_voice_assets.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\providers\windows_speech.py src\ai_presenter\providers\piper_provider.py src\ai_presenter\runtime\voice_assets.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py tests\unit\test_voice_assets.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\providers\windows_speech.py src\ai_presenter\providers\piper_provider.py src\ai_presenter\runtime\voice_assets.py src\ai_presenter\runtime\diagnostics.py src\ai_presenter\cli.py tests\unit\test_windows_speech_provider.py tests\unit\test_piper_provider.py tests\unit\test_voice_assets.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Expected: all focused checks pass.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full suite passes with only the known pywinauto STA warning.

- [ ] **Step 4: Record implementation handoff**

Create `docs/agent-handoffs/cycle-015-implementation.md` with:

- Scope summary.
- Red/green evidence.
- Focused and full verification results.
- Notes about no downloads, no synthesis, and no RingCentral automation.
