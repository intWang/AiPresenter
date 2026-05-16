# CLI Voice Flags Design

Date: 2026-05-16

## Context

Cycle 009 expanded `PresenterVoiceSettings` with language aliases and more tones. Operators can already choose those values inside the Tk controller, but scripted CLI runs still start with the default English / Professional voice. That makes Chinese and tone-specific acceptance runs harder to repeat.

## Design

Add voice options to the material-package CLI surfaces:

- `ai-presenter demo` accepts `--language` and `--tone`.
- `ai-presenter controller` accepts the same options and uses them as the initial controller voice.
- Both commands normalize values through `PresenterVoiceSettings`.
- Both commands print the normalized label during load and dry-run output, for example `Loaded voice: Chinese / Friendly`.
- Invalid language or tone values fail as Typer bad parameters before automation or the controller UI starts.

The `run` command is intentionally out of scope because its live presenter loop does not yet thread `PresenterVoiceSettings` through the same material-demo narration path.

## Behavior

- Defaults remain English / Professional.
- Aliases such as `zh-CN`, `English`, `warm`, `mentor`, and `structured` are accepted through the shared voice normalizer.
- `demo` passes the normalized voice into `run_material_demo(..., voice=voice_settings)`.
- `controller` passes the normalized voice into `run_controller(..., voice=voice_settings)`.
- `run_controller()` initializes Tk language and tone menus from the normalized voice label so the first Start click does not silently reset the CLI-selected voice.
- The operator can still change language and tone in the UI after launch.

## Non-Goals

- No new output languages beyond the current English and Chinese families.
- No new TTS providers.
- No `run` command voice flags in this cycle.
- No change to RingCentral package localized copy.

## Acceptance Criteria

- `demo --language zh-CN --tone friendly --dry-run` prints `Loaded voice: Chinese / Friendly`.
- `controller --language English --tone mentor --dry-run` prints `Loaded voice: English / Coach`.
- Non-dry `demo` passes a canonical `PresenterVoiceSettings` object to `run_material_demo`.
- Non-dry `controller` passes a canonical `PresenterVoiceSettings` object to `run_controller`.
- `PresenterController` can be constructed with an initial voice and forwards it to the runner on first start.
- Invalid `--language` and `--tone` values fail before automation starts.
- Focused CLI/controller tests, ruff, mypy, and the full unit suite pass.

## Risks

- Voice labels do not guarantee installed speech support. Provider validation remains in the runtime path.
- Controller initialization can drift if canonical voice values and Tk labels are mapped separately. Use shared `language_label()` and `tone_label()` helpers.
- The CLI options must stay free-form strings so existing aliases continue to work.
