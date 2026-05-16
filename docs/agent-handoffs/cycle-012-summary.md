# Cycle 012 Summary: Voice Profile Preflight

Date: 2026-05-16

## Completed

Cycle 012 hardened voice/profile compatibility so unsupported combinations fail before costly or confusing runtime side effects.

- Enriched `validate_profile_voice()` errors with profile id, speech provider, and normalized voice label.
- Added CLI compatibility preflight for `demo` and `controller`.
- Added early runtime validation before material-demo desktop/provider/window setup.
- Added controller validation before initial UI setup and before runner thread creation.
- Updated README and RingCentral manual acceptance runbook with compatibility notes and passing/failing preflight examples.

## Evidence

- TDD red/green evidence is recorded in `docs/agent-handoffs/cycle-012-implementation.md`.
- Independent review is recorded in `docs/agent-handoffs/cycle-012-review.md`.
- Coordinator reran focused verification:
  - `90 passed` for CLI/runtime factory/controller/voice/controller session tests.
  - Ruff passed.
  - Mypy passed.
- Coordinator reran full verification:
  - `407 passed, 1 warning in 21.18s`.
  - Warning is the known pywinauto STA COM threading warning.

## Changed Paths

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/factory.py`
- `src/ai_presenter/runtime/controller.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_runtime_factory.py`
- `tests/unit/test_controller.py`
- `README.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-16-voice-profile-preflight-design.md`
- `docs/superpowers/plans/2026-05-16-voice-profile-preflight.md`
- `docs/agent-handoffs/cycle-012-demand-analysis.md`
- `docs/agent-handoffs/cycle-012-technical-scan.md`
- `docs/agent-handoffs/cycle-012-implementation.md`
- `docs/agent-handoffs/cycle-012-review.md`

## Follow-Ups

- Manual acceptance: run the supported Chinese preflight and failing fake-speech preflight from the runbook.
- Potential UX polish: expose a `voices` or `doctor --language/--tone` report that explains compatibility without requiring a demo/controller command.
- Potential runtime check: detect installed Windows SAPI voices separately from routing compatibility.
