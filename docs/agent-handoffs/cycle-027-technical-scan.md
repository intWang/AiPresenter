# Cycle 027 Technical Scan: CLI Voice Asset Imports

## Scope

Review only. Inspected:

- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/voice_assets.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_voice_assets.py`

## Import Probe

Probe command, from repo root:

```powershell
$env:PYTHONPATH='src'; @'
import json
import sys
import ai_presenter.cli
prefixes = (
    'ai_presenter.desktop',
    'ai_presenter.runtime.factory',
    'ai_presenter.runtime.controller',
    'ai_presenter.runtime.voice_assets',
    'ai_presenter.providers',
)
loaded = [name for name in sys.modules if name.startswith(prefixes)]
print(json.dumps(loaded, indent=2, sort_keys=True))
'@ | .\.venv\Scripts\python.exe -
```

Observed loaded modules:

```json
[
  "ai_presenter.runtime.controller_view_model",
  "ai_presenter.desktop",
  "ai_presenter.desktop.base",
  "ai_presenter.providers",
  "ai_presenter.providers.base",
  "ai_presenter.providers.piper_provider",
  "ai_presenter.providers.windows_speech",
  "ai_presenter.runtime.voice_assets"
]
```

`runtime.factory`, `runtime.controller`, and `desktop.windows` remain unloaded by the existing lazy wrappers. The provider modules are loaded by the voice asset path.

Important finding: removing only `from ai_presenter.runtime.voice_assets import check_voice_asset_availability` from `cli.py` is not enough, because `cli.py` also imports `diagnose_configuration` and `format_diagnostic_report` from `runtime.diagnostics`, and `runtime.diagnostics` imports `check_voice_asset_availability` at module import time.

## Minimal Code Recommendation

Keep command behavior unchanged, but move the two import paths that lead to `voice_assets` behind CLI-level lazy wrappers.

In `src/ai_presenter/cli.py`:

1. Remove top-level imports:

```python
from ai_presenter.runtime.diagnostics import diagnose_configuration
from ai_presenter.runtime.diagnostics import format_diagnostic_report
from ai_presenter.runtime.voice_assets import check_voice_asset_availability
```

2. Add wrappers near the existing lazy runtime wrappers:

```python
def diagnose_configuration(*args: Any, **kwargs: Any) -> Any:
    from ai_presenter.runtime.diagnostics import diagnose_configuration as _diagnose_configuration

    return _diagnose_configuration(*args, **kwargs)


def format_diagnostic_report(*args: Any, **kwargs: Any) -> Any:
    from ai_presenter.runtime.diagnostics import format_diagnostic_report as _format_diagnostic_report

    return _format_diagnostic_report(*args, **kwargs)


def check_voice_asset_availability(*args: Any, **kwargs: Any) -> Any:
    from ai_presenter.runtime.voice_assets import (
        check_voice_asset_availability as _check_voice_asset_availability,
    )

    return _check_voice_asset_availability(*args, **kwargs)
```

This preserves the existing monkeypatch seam used by CLI voice tests:

```python
monkeypatch.setattr("ai_presenter.cli.check_voice_asset_availability", ...)
```

It also keeps doctor tests compatible when they monkeypatch the diagnostics module directly, because the lazy wrapper imports the same module object at command execution time.

## Test Recommendation

Update `tests/unit/test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules` or rename it to cover provider imports too.

Recommended subprocess assertions:

```python
names = [
    "ai_presenter.desktop.windows",
    "ai_presenter.runtime.factory",
    "ai_presenter.runtime.controller",
    "ai_presenter.runtime.diagnostics",
    "ai_presenter.runtime.voice_assets",
    "ai_presenter.providers.piper_provider",
    "ai_presenter.providers.windows_speech",
]
```

Expected values after `import ai_presenter.cli`: all `False`.

Keep the existing CLI monkeypatch tests for `ai_presenter.cli.check_voice_asset_availability`; they are valuable regression coverage for the wrapper seam:

- `test_voices_profile_reports_local_asset_status`
- `test_voices_targeted_missing_assets_exits_nonzero`

`tests/unit/test_voice_assets.py` should not need behavioral changes. Its dependency injection seams are already on `check_voice_asset_availability(...)` parameters and should remain intact.

## Risks And Notes

- Subprocess import probes need the project environment. A bare `python` failed here until using `.venv\Scripts\python.exe` and `PYTHONPATH=src`.
- Running one pytest node directly produced a coverage-threshold failure even though the selected test passed. Use `--no-cov` for focused probe runs if the project has pytest-cov available, or run the full suite.
- If the CLI import test imports `VoiceAssetAvailability` at module top level, that does not pollute the subprocess probe; keep the actual import assertion in a fresh subprocess.
- Do not replace the CLI monkeypatch seam with a differently named private helper unless tests are updated. The current tests patch `ai_presenter.cli.check_voice_asset_availability`.
- Lazy-importing only the `voices` checker is insufficient while `cli.py` still imports `runtime.diagnostics` at top level.
