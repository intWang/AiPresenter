# Cycle 027 Demand Analysis: CLI Import Hygiene

Date: 2026-05-16
Role: demand analysis
Scope: review-only; no implementation changes recommended here.

## Recommendation

Do a small Cycle 027 slice to make `ai_presenter.cli` stop importing voice asset/provider support at module import time. This is worth doing because the CLI now has several package-only and offline helper commands that should stay cheap, predictable, and independent from local desktop/audio/provider readiness.

This is a hygiene improvement, not an urgent user-facing feature. The value is strongest as a guardrail for future package tooling: `localization-report`, `flows`, `entrypoints`, `validation-targets`, and `acceptance-draft` should remain package/document readers, not accidental speech-provider initializers.

## Current Evidence

- `src/ai_presenter/cli.py` already lazy-loads the heavy runtime factory/controller paths for `run`, `demo`, and `controller`.
- `tests/unit/test_cli.py::test_cli_import_does_not_load_desktop_runtime_modules` protects that current boundary for:
  - `ai_presenter.desktop.windows`
  - `ai_presenter.runtime.factory`
  - `ai_presenter.runtime.controller`
- Importing `ai_presenter.cli` still loads provider-adjacent modules through voice asset checks:
  - `ai_presenter.runtime.voice_assets`
  - `ai_presenter.providers.base`
  - `ai_presenter.providers.piper_provider`
  - `ai_presenter.providers.windows_speech`
- There are two paths to fix, not one:
  - direct top-level `from ai_presenter.runtime.voice_assets import check_voice_asset_availability` in `cli.py`
  - indirect top-level `from ai_presenter.runtime.diagnostics import diagnose_configuration` in `cli.py`, because `runtime.diagnostics` imports `runtime.voice_assets`

Manual import probe run during analysis:

```powershell
@'
import json, sys
import ai_presenter.cli
names = [
    'ai_presenter.desktop.windows',
    'ai_presenter.runtime.factory',
    'ai_presenter.runtime.controller',
    'ai_presenter.runtime.voice_assets',
    'ai_presenter.providers.base',
    'ai_presenter.providers.piper_provider',
    'ai_presenter.providers.windows_speech',
]
print(json.dumps({name: name in sys.modules for name in names}, indent=2, sort_keys=True))
'@ | .\.venv\Scripts\python -
```

Observed result:

```json
{
  "ai_presenter.desktop.windows": false,
  "ai_presenter.providers.base": true,
  "ai_presenter.providers.piper_provider": true,
  "ai_presenter.providers.windows_speech": true,
  "ai_presenter.runtime.controller": false,
  "ai_presenter.runtime.factory": false,
  "ai_presenter.runtime.voice_assets": true
}
```

## User And Operator Value

Package-only commands are increasingly part of the operator workflow:

- `flows` confirms the exact demo flow id before launch.
- `entrypoints` inspects package controls and areas without opening RingCentral.
- `localization-report` reports localization coverage without loading a profile or running automation.
- `validation-targets` and `acceptance-draft` help plan manual evidence work without executing routes.

Those commands should work in the lightest possible environment: a package installed with Typer, Pydantic, and PyYAML should not need to touch Piper, Windows SAPI helpers, or speech-provider support just to inspect YAML and markdown. Keeping the import boundary clean reduces surprise on machines without audio/provider setup, makes subprocess CLI tests more deterministic, and preserves the mental model that package tooling is offline and read-only.

This matters especially after Cycle 026 because `localization-report` is intentionally positioned as a low-friction package audit command. If importing the CLI still loads provider support, the command remains behaviorally correct today, but its dependency surface tells future contributors the wrong story.

## Small Acceptance Slice

Recommended acceptance criteria:

- Importing `ai_presenter.cli` does not load:
  - `ai_presenter.runtime.voice_assets`
  - `ai_presenter.providers.base`
  - `ai_presenter.providers.piper_provider`
  - `ai_presenter.providers.windows_speech`
  - the already-protected desktop/factory/controller modules
- Package-only commands keep their current output and still do not load profiles:
  - `flows --package ringcentral-video`
  - `entrypoints --package ringcentral-video`
  - `localization-report --package ringcentral-video --language zh`
  - `validation-targets --package ringcentral-video`
  - `acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.toolbar.chat`
- Voice asset checks still run where they are actually needed:
  - `voices --profile ...`
  - `voices --profile ... --language ...`
  - `doctor --profile ... --language ...`
- Existing voice/profile validation behavior remains unchanged for `demo`, `controller`, `voices`, and `doctor`.

Likely implementation shape:

- Move `check_voice_asset_availability` import behind a small helper or inside the `voices` branch that checks profile assets.
- Stop importing `runtime.diagnostics` at `cli.py` module load. Import `diagnose_configuration` and `format_diagnostic_report` inside the `doctor` command, or make `runtime.diagnostics` lazy-load `voice_assets` only inside `_diagnose_voice_assets`.
- Strengthen the existing import hygiene test so it asserts provider modules and `runtime.voice_assets` remain absent after `import ai_presenter.cli`.
- Add one package-only command subprocess probe if needed to ensure `localization-report` does not load provider modules while executing.

## Out Of Scope

- Do not change provider behavior, voice routing, SAPI/Piper detection, or asset availability wording.
- Do not remove `doctor` voice asset checks; keep strict pre-demo voice checks intact when `--language` or `--tone` is supplied.
- Do not restructure the provider package or split `providers.base` unless the small lazy-import slice cannot pass without it.
- Do not change localization-report semantics, package schema, or package validation rules.
- Do not introduce optional dependency groups in this cycle; that is a separate packaging decision.

## Priority

P2. This is a small, valuable maintenance slice that protects the increasingly important offline/package CLI surface. It should follow any user-visible demo correctness work, but it is a good next step before adding more package audit commands.
