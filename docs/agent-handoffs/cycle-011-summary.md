# Cycle 011 Summary: CLI Voice Flags

Date: 2026-05-16

## Completed

Cycle 011 exposed the expanded voice model through user-facing CLI workflows.

- Added `--language` and `--tone` to `ai-presenter demo`.
- Added `--language` and `--tone` to `ai-presenter controller`.
- Reused `PresenterVoiceSettings` normalization for aliases such as `zh-CN`, `English`, `warm`, and `mentor`.
- Added `Loaded voice` output for dry-run and non-dry command startup.
- Passed canonical voice settings into material demo runtime and controller startup.
- Let `PresenterController` receive an initial voice without requiring a setter call.
- Initialized controller session state and Tk language/tone selector labels from the CLI-selected voice.
- Updated README and RingCentral manual acceptance examples.

## Evidence

- TDD red/green evidence is recorded in `docs/agent-handoffs/cycle-011-implementation.md`.
- Independent review is recorded in `docs/agent-handoffs/cycle-011-review.md`.
- Coordinator reran focused verification:
  - `58 passed` for CLI/controller/voice tests.
  - Ruff passed.
  - Mypy passed.
- Coordinator reran full verification:
  - `400 passed, 1 warning in 16.87s`.
  - Warning is the known pywinauto STA COM threading warning.

## Changed Paths

- `src/ai_presenter/cli.py`
- `src/ai_presenter/runtime/controller.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_controller.py`
- `README.md`
- `docs/runbooks/ringcentral-manual-acceptance.md`
- `docs/superpowers/specs/2026-05-16-cli-voice-flags-design.md`
- `docs/superpowers/plans/2026-05-16-cli-voice-flags.md`
- `docs/agent-handoffs/cycle-011-demand-analysis.md`
- `docs/agent-handoffs/cycle-011-technical-scan.md`
- `docs/agent-handoffs/cycle-011-implementation.md`
- `docs/agent-handoffs/cycle-011-review.md`

## Follow-Ups

- Manual acceptance: launch controller with `--language zh-CN --tone friendly` and confirm the Tk selectors and operator summary show Chinese / Friendly.
- Runtime hardening candidate: validate profile/voice compatibility before desktop launch for non-dry `demo`.
- Next optimization candidate: improve package flow lookup/indexing or add a CLI `voices` discovery command that lists supported languages, tones, and aliases.
