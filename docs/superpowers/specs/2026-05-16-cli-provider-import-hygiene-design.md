# CLI Provider Import Hygiene Design

Date: 2026-05-16
Cycle: 027

## Problem

`import ai_presenter.cli` currently loads voice asset and speech provider support even for package-only commands. The direct cause is the top-level CLI imports for `runtime.voice_assets` and `runtime.diagnostics`; `runtime.diagnostics` also imports `runtime.voice_assets`, which loads Piper and Windows speech provider modules.

This makes offline package commands such as `localization-report`, `flows`, `entrypoints`, `validation-targets`, and `acceptance-draft` carry a larger dependency surface than their behavior needs.

## Acceptance

- Importing `ai_presenter.cli` leaves these modules unloaded:
  - `ai_presenter.runtime.diagnostics`
  - `ai_presenter.runtime.voice_assets`
  - `ai_presenter.providers.base`
  - `ai_presenter.providers.piper_provider`
  - `ai_presenter.providers.windows_speech`
- The existing desktop/runtime lazy boundary remains intact for:
  - `ai_presenter.desktop.windows`
  - `ai_presenter.runtime.factory`
  - `ai_presenter.runtime.controller`
- Running `localization-report --package ringcentral-video --language zh` does not load diagnostics, voice assets, or provider modules.
- `voices` and `doctor` keep their existing behavior and monkeypatch seams.

## Design

Keep the CLI public call sites stable by replacing the top-level imports with small lazy wrappers in `cli.py`:

- `diagnose_configuration(...)`
- `format_diagnostic_report(...)`
- `check_voice_asset_availability(...)`

Each wrapper imports the real implementation only when the relevant command path runs. This keeps `ai_presenter.cli.check_voice_asset_availability` patchable for the existing voice CLI tests while preventing package-only commands from touching provider support.

## Out Of Scope

- Provider routing and asset detection behavior.
- Diagnostics wording.
- Package schema or localization-report semantics.
- Optional dependency packaging.
