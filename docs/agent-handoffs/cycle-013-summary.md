# Cycle 013 Summary: Voice Discovery

Date: 2026-05-16

## Completed

Cycle 013 made presenter voice support discoverable before running a demo or opening the controller.

- Added public voice metadata helpers for language aliases, tone aliases, and tone descriptions.
- Added optional voice diagnostics to `diagnose_configuration()`.
- Added `ai-presenter voices` for catalog and profile compatibility discovery.
- Added opt-in `doctor --language/--tone` voice compatibility checks.
- Added Windows console safety for non-ASCII alias output.
- Updated README and RingCentral manual acceptance runbook with discovery examples.

## Evidence

- TDD red/green evidence is recorded in `docs/agent-handoffs/cycle-013-implementation.md`.
- Independent review is recorded in `docs/agent-handoffs/cycle-013-review.md`.
- Coordinator reran focused verification:
  - `56 passed` for CLI/diagnostics/voice tests.
  - Ruff passed.
  - Mypy passed.
- Coordinator reran full verification:
  - `417 passed, 1 warning in 21.13s`.
  - Warning is the known pywinauto STA COM threading warning.
- Manual CLI evidence:
  - Supported `voices --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` exited 0.
  - Unsupported `voices --profile ringcentral-video --language zh-CN --tone friendly` exited 1.

## Changed Paths

- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `README.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-16-voice-discovery-design.md`
- `docs/superpowers/plans/2026-05-16-voice-discovery.md`
- `docs/agent-handoffs/cycle-013-demand-analysis.md`
- `docs/agent-handoffs/cycle-013-technical-scan.md`
- `docs/agent-handoffs/cycle-013-implementation.md`
- `docs/agent-handoffs/cycle-013-review.md`

## Follow-Ups

- Consider adding installed Windows SAPI voice detection to `voices`.
- Consider adding Piper voice model availability checks.
- Next code-quality candidate: add a package flow index or helper to improve flow lookup performance and error quality as material packages grow.
