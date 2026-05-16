# Cycle 140 Demand Analysis: Spanish Entrypoint Display Metadata Wedge

Date: 2026-05-17
Cycle: 140
Scope: demand analysis only. This file is the only intended edit for this
cycle. Do not edit source code, tests, package YAML, durable docs, generated
artifacts, staging, commits, or `.coverage` in this analysis slice.

Worktree note: if package, test, or durable-doc edits for this wedge are already
present when this handoff is read, treat them as implementation work to validate
against the criteria below, not as part of this analysis edit.

## User Value

- Spanish operators get clearer package-local display text for three high-use,
  menu-style RingCentral Video surfaces: audio recovery, camera menu access,
  and Background access from More.
- The wedge turns the existing Spanish entrypoint inspection work into more
  practical output: `entrypoints --language es`, `--language Spanish`, and
  regional aliases such as `--language es-MX` can show localized title/purpose
  metadata for these common controls.
- The change improves explanation quality without changing live meeting state.
  The three target entrypoints open menus or settings panels; the copy can
  describe navigation while preserving safety boundaries around device
  switching, background changes, private device names, and meeting controls.
- Maintainers get a small, count-guarded localization pattern that continues
  the Spanish optional display metadata path from the prior `5/27` baseline to
  the target `8/27` state without implying full Spanish entrypoint display
  localization.

## Exact Scope Recommendation

Implement the safe Spanish optional display metadata wedge by adding
`localizedTitles.es` and `localizedPurposes.es` for exactly these package
entrypoints:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

Recommended copy direction:

| Entrypoint | Suggested `localizedTitles.es` | Purpose constraints |
| --- | --- | --- |
| `ringcentral.video.toolbar.audio-menu` | `Menú de micrófono y altavoz` | Explain opening the audio menu to review `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio settings` for navigation or recovery. Do not imply switching devices, leaving computer audio, selecting phone audio, reading private device names, or changing settings. |
| `ringcentral.video.toolbar.video-menu` | `Menú de cámara` | Explain opening the camera menu to review camera selection and `More video settings`. Do not imply changing cameras, turning video on or off, or changing video settings. |
| `ringcentral.video.more.background` | `Fondo desde More` | Explain `More` > `Background` as opening `Settings` on the `Background` tab for privacy/appearance setup. Do not imply selecting Blur, uploading images, inspecting custom assets, or changing the user's background. |

Expected implementation shape:

- Edit only `packages/ringcentral-video.yaml`, the focused tests that assert
  Spanish display metadata and CLI output, and current-state durable docs that
  intentionally track the live `localizedTitles.es` / `localizedPurposes.es`
  counts.
- Move optional Spanish display metadata counts from the prior `5/27` baseline
  to the target `8/27` state.
- Preserve required localization completeness: `51/51` demo narration steps,
  `12/12` localized questions, and `12/12` localized answers.
- Preserve Spanish question alias coverage and matching semantics; this wedge is
  display metadata only.

## Out-of-Scope Boundaries

- Do not target full Spanish `27/27` entrypoint display localization.
- Do not add display metadata for `meeting-info`, `report-issue`, `chat`,
  `participants`, `invite`, `share`, `recording`, `notes`, `leave`, direct
  mic/camera toggles, `start`, `settings.video`, `settings.background`, or
  `settings.background.blur`.
- Do not add or change Spanish aliases, Q&A prompts, Q&A answers, demo
  narration, open steps, cleanup modes, route order, question policies, safety
  routing, matcher behavior, or controller interrupt behavior.
- Do not make `localizedTitles` or `localizedPurposes` part of
  `--require-complete`; they remain optional display/inspection metadata.
- Do not change Spanish runtime voice support, OpenAI/local provider routing,
  profiles, speech assets, controller language choices, `voices`, `doctor`, or
  live RingCentral acceptance claims.
- Do not edit historical handoffs to reconcile counts.
- Do not stage or commit unless the implementation task explicitly asks for it,
  and do not touch pre-existing `.coverage` changes.

## Acceptance Criteria

- `packages/ringcentral-video.yaml` adds Spanish `localizedTitles.es` and
  `localizedPurposes.es` for exactly:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- The exact Spanish localized entrypoint id set expands from the prior five
  baseline entries to exactly eight entries, with no unrelated additions.
- `localization-report --package ringcentral-video --language es` reports
  `localizedTitles.es present on 8/27 entrypoints` and
  `localizedPurposes.es present on 8/27 entrypoints`.
- `localization-report --package ringcentral-video --language es
  --require-complete` still exits `0`, proving optional title/purpose metadata
  does not gate required completeness.
- Required Spanish package localization remains complete: `51/51` demo steps,
  `12/12` localized questions, and `12/12` localized answers.
- Spanish aliases remain stable, including `questionAliases.es present on 26/27
  entrypoints (69 aliases)`.
- `entrypoints --package ringcentral-video --area "Meeting toolbar" --language
  es` shows localized title/purpose markers for `audio-menu` and `video-menu`
  while unrelated toolbar entries keep their expected localized or fallback
  markers.
- `entrypoints --package ringcentral-video --area "More menu" --language es`
  shows localized title/purpose markers for `more.background` while sensitive
  or broader entries keep their expected localized, fallback, or answer-only
  behavior.
- Alias-normalized probes keep the same canonical Spanish behavior for
  `--language Spanish` and `--language es-MX`.
- Focused tests assert the chosen exact Spanish title/purpose strings, the exact
  localized entrypoint id set, CLI localized/fallback output, answer rendering,
  and durable-doc count guard.
- Verification includes focused pytest checks, `localization-report`,
  `entrypoints` probes for `es`, `Spanish`, and `es-MX`, `ruff check --no-cache
  packages tests`, `git diff --check`, and `git status --short`.

## Handoff Prompt For Implementation

```text
Implement Cycle140's safe Spanish entrypoint display metadata wedge in
C:\Users\rcadmin\Documents\Repos\AiPresenter.

Scope:
- Add Spanish `localizedTitles.es` and `localizedPurposes.es` for exactly:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- Move optional Spanish display metadata counts from `5/27` to `8/27`.
- Update only package YAML, focused tests, and current-state durable docs that
  intentionally assert those live counts.

Copy boundaries:
- Audio menu copy may explain reviewing `Microphone`, `Speaker`, `Leave computer
  audio`, `Use phone audio`, and `More audio settings`; it must not imply
  switching devices, leaving computer audio, selecting phone audio, reading
  private device names, or changing settings.
- Camera menu copy may explain camera selection and `More video settings`; it
  must not imply changing cameras, toggling video, or changing video settings.
- Background copy may explain `More` > `Background` opening `Settings` on the
  `Background` tab for privacy/appearance setup; it must not imply selecting
  Blur, uploading images, inspecting custom assets, or changing the background.

Out of scope:
- No aliases, Q&A, demo narration, routes, cleanup, matcher, safety, controller,
  provider, voice, profile, live RingCentral acceptance, or `--require-complete`
  behavior changes.
- Do not expand beyond the three listed entrypoints.
- Do not touch unrelated dirty files such as pre-existing `.coverage`.

Acceptance:
- `localizedTitles.es` and `localizedPurposes.es` report `8/27`.
- Required Spanish localization remains complete at `51/51`, `12/12`, and
  `12/12`.
- Spanish aliases remain `26/27` and `69 aliases`.
- CLI `entrypoints` output marks the three new entries localized and preserves
  expected fallback/localized markers elsewhere.
- Alias-normalized Spanish probes for `es`, `Spanish`, and `es-MX` still work.
- Focused pytest, CLI probes, `ruff check --no-cache packages tests`,
  `git diff --check`, and `git status --short` pass with only intended files
  changed.
```
