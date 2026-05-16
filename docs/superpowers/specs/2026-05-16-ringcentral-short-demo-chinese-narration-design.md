# RingCentral Short Demo Chinese Narration Design

Date: 2026-05-16
Cycle: 023

## Goal

Add native Chinese narration text to the two short RingCentralVideo demo flows that still fall back to English: `vbg-blur-demo` and `meeting-basics-demo`.

## User Value

Cycle 022 made RingCentralVideo Chinese Q&A and aliases work. The next visible gap is short guided demos: a user can ask Chinese questions, but the blur and basics flows still speak English. Localizing the seven short-flow steps makes the Chinese presenter feel coherent without taking on the larger `meeting-controls-tour`.

## Scope

In scope:

- Add `narration.localizedText.zh` to every step in `vbg-blur-demo`.
- Add `narration.localizedText.zh` to every step in `meeting-basics-demo`.
- Add tests proving both flows have non-empty Chinese localized text for every step.
- Add a rendering assertion proving a newly localized short-flow step uses Chinese text with `PresenterVoiceSettings(language="zh")`.

Out of scope:

- Runtime, schema, CLI, controller, profile, provider, route, and open-step changes.
- `meeting-control-map-demo`, which is already fully localized.
- `meeting-controls-tour`, which has 22 unlocalized steps and overlaps with the localized map demo.
- Adaptive invite narration stale-localized-text handling. It is a real follow-up risk, but the target flows do not include the invite rewrite path.

## Design

Use the existing `DemoStepNarration.localized_text` model and YAML `localizedText.zh` field. The runtime already calls `render_narration_text()` before synchronized playback, so package content is enough.

The Chinese copy should be authored for spoken guidance, not literal translation. Keep visible RingCentral UI labels such as `Settings`, `Background`, `Blur`, `Participants`, and `Chat` when they help the user match the screen. The Chinese sentence around each label should explain the purpose and privacy/safety implication.

Target steps:

- `vbg-blur-demo`
  - `open-video-settings`
  - `open-background-panel`
  - `select-blur`
  - `verify-meeting-video`
- `meeting-basics-demo`
  - `show-mic`
  - `show-participants`
  - `show-chat`

## Acceptance Criteria

- `packages/ringcentral-video.yaml` contains `localizedText.zh` for all seven target steps.
- Existing English `narration.text` remains ASCII.
- Existing flow ids, step ids, entrypoint ids, operations, placements, offsets, and open steps are unchanged.
- `tests/unit/test_material_packages.py` verifies target-flow Chinese coverage and one Chinese render path.
- Focused pytest and ruff pass for the touched test file.
- Full pytest, mypy, and diff-check pass before Cycle 023 is summarized.

## Risks

- PowerShell can render UTF-8 Chinese as mojibake. Tests should assert semantic properties and file parsing, not copied terminal text.
- `vbg-blur-demo` includes a `select` operation for Blur. Do not change execution safety in this cycle.
- Localized content can become stale if later adaptive logic rewrites English `narration.text` while preserving `localized_text`; track that separately for invite-oriented flows.
