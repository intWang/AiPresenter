# Cycle 011 Technical Scan: CLI Voice Flags

Date: 2026-05-16

## Existing Seams

- `src/ai_presenter/cli.py` is Typer-based.
- `run_material_demo()` already accepts `voice: PresenterVoiceSettings | None`.
- `PresenterController` keeps a `_voice` and forwards it into the runner, but its constructor currently defaults to English / Professional.
- `run_controller()` builds Tk `StringVar`s from the first shared choices, so an initial voice must also initialize menu labels.
- `runtime.voice` already provides normalization and label helpers.

## Files To Modify

- `src/ai_presenter/cli.py`
  - Add voice options to `demo()` and `controller()`.
  - Add a helper that converts `ValueError` from `PresenterVoiceSettings` into `typer.BadParameter`.
  - Echo `Loaded voice: <label>`.
  - Pass voice into runtime entry points.
- `src/ai_presenter/runtime/controller.py`
  - Add optional initial voice to `PresenterController.__init__`.
  - Add optional keyword-only voice to `run_controller()`.
  - Initialize session, controller, and Tk menu labels from the initial voice.
- `tests/unit/test_cli.py`
  - Add dry-run, invalid input, and monkeypatched runtime-call assertions.
- `tests/unit/test_controller.py`
  - Add initial voice forwarding coverage.

## Risks

- Invalid profile/language combinations still validate in the runtime path; this cycle only validates syntactic voice values before automation.
- Keep CLI options as strings, not enums, so aliases continue to work.
- The worktree contains changes from prior cycles; edits must be narrow and must not revert unrelated files.
