# Cycle 015 Summary: Voice Asset Availability

Date: 2026-05-16

## Completed

Cycle 015 made local speech asset readiness visible before live demos.

- Added Windows SAPI installed-voice discovery and substring availability helpers.
- Added Piper default asset path, local model/config availability, and module availability helpers.
- Added `ai_presenter.runtime.voice_assets` to map selected voice settings to concrete local route
  requirements.
- Added `voice assets` diagnostics after successful configured voice compatibility checks.
- Updated `voices --profile` to show local asset status for supported local routes.
- Updated targeted `voices --profile --language/--tone` to exit nonzero when required local assets
  are missing.
- Updated README and RingCentral manual acceptance runbook with strict local voice preflight notes.

No downloads, audio synthesis, cloud calls, or RingCentral automation are part of this feature.

## Evidence

- TDD red/green evidence is recorded in `docs/agent-handoffs/cycle-015-implementation.md`.
- Independent review is recorded in `docs/agent-handoffs/cycle-015-review.md`.
- Coordinator reran focused verification:
  - `59 passed` for provider, voice asset, diagnostics, and CLI tests.
  - Ruff passed.
  - Mypy passed.
- Coordinator reran full verification:
  - `443 passed, 1 warning in 20.24s`.
  - Warning is the known pywinauto STA COM threading warning.
- Real CLI spot checks covered default catalog, profile matrix, unsupported fake Chinese route, and
  strict `doctor` local SAPI asset preflight.

## Changed Paths

- `src/ai_presenter/providers/windows_speech.py`
- `src/ai_presenter/providers/piper_provider.py`
- `src/ai_presenter/runtime/voice_assets.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_windows_speech_provider.py`
- `tests/unit/test_piper_provider.py`
- `tests/unit/test_voice_assets.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `README.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-16-voice-asset-availability-design.md`
- `docs/superpowers/plans/2026-05-16-voice-asset-availability.md`
- `docs/agent-handoffs/cycle-015-demand-analysis.md`
- `docs/agent-handoffs/cycle-015-technical-scan.md`
- `docs/agent-handoffs/cycle-015-implementation.md`
- `docs/agent-handoffs/cycle-015-review.md`

## Follow-Ups

- Add profile-level configuration for SAPI voice names and Piper voice/model names.
- Add speaker device or virtual microphone availability diagnostics.
- Consider exposing local voice asset status in the controller operator summary.
- Continue RingCentral manual acceptance evidence for the observed Add coworkers UIA route.
