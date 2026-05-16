# Cycle 139 Demand Analysis: Resume Safe Spanish Entrypoint Display Copy

Date: 2026-05-17
Cycle: 139
Scope: demand analysis only. This file is the only intended edit. Do not edit
source, tests, package YAML, README, durable docs, generated artifacts,
staging, commits, or `.coverage` in this analysis slice.

## Recommendation

Best small Cycle139 optimization slice: implement the tiny safe Spanish optional
entrypoint display metadata wedge for:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

This moves Spanish optional `localizedTitles.es` and `localizedPurposes.es`
coverage from `5/27` to `8/27` entrypoints while staying inside package-local
answer rendering and inspection. Cycle138 chose package-local CLI language alias
normalization instead of the display-copy wedge, so the content opportunity is
still open. The new alias normalization makes the wedge more useful because
operators can inspect the same Spanish metadata through `--language es`,
`--language Spanish`, or regional aliases such as `--language es-MX`.

Keep the slice as package content plus focused tests and current-state durable
count updates. Do not combine it with runtime Spanish promotion, local Spanish
speech, broad CLI redesign, live RingCentral acceptance, or performance work.

## Options Evaluated

1. **Spanish optional display metadata wedge from `5/27` to `8/27`**

   Highest value now. The repo already has the model, rendering path,
   `entrypoints --language` inspection, count reporting, and durable-doc count
   guard. The candidate entrypoints are practical operator surfaces: audio
   recovery, camera menu navigation, and Background access from More. They are
   safer than chat, participants, invite, share, recording, notes, leave, or
   direct mic/camera toggles because the copy can explain where controls live
   without changing meeting state.

2. **CLI/docs polish after language alias normalization**

   Useful but lower priority. Cycle138 already normalized known aliases for
   `entrypoints` and `localization-report`, and README already explains that
   Spanish entrypoint inspection is package-local, not runtime validation. A
   later docs polish can add a small sentence saying known aliases such as
   `Spanish` and `es-MX` normalize to package key `es` while unknown keys remain
   raw. That is helpful, but it is less user-facing than adding the next three
   localized display explanations.

3. **Performance/test-speed or package-loading improvement**

   Not the best next slice. Recent focused CLI and package checks run in the
   low-single-second range, and no concrete repeated package-load hotspot or
   failing test-speed problem surfaced. The maintenance playbook says to
   optimize only after preserving behavior with structural tests and clear cache
   invalidation. Defer until a technical scan identifies a specific repeated
   load path or controller refresh bottleneck.

4. **RingCentralVideo acceptance or knowledge docs improvement**

   Valuable but not the best small Cycle139 optimization. The knowledge package
   has current source, evidence, privacy, state, locator, runtime-safety,
   acceptance-runs, and validation-checklist docs. The acceptance backlog still
   needs live manual evidence for More occurrence order, Background cleanup, and
   settings variants, but this cycle can improve the package's Spanish
   explanation for those same surfaces without claiming live acceptance.

5. **Project-local need discovered**

   The main project-local need is to keep content wedges count-guarded and
   boundary-safe. Current durable docs still state Spanish optional display
   metadata at `5/27`, tests assert `5/27`, and `.coverage` is already modified
   in the worktree. No new maintenance doc is needed for Cycle139.

## User Value

- Spanish operators get clearer package-local answers for common audio, camera,
  and background-navigation questions.
- The content complements Cycle138 alias normalization: `Spanish` and `es-MX`
  now resolve to the same visible Spanish metadata as `es`.
- The wedge improves UI guidance without touching live mic/camera state,
  provider routing, controller behavior, package matching, or RingCentral live
  acceptance claims.
- Maintainers get another small, repeatable localization pattern with exact
  count updates and focused tests.

## Proposed Copy Direction

Add Spanish `localizedTitles.es` and `localizedPurposes.es` to exactly the three
recommended entrypoints.

- `ringcentral.video.toolbar.audio-menu`
  - Suggested title: `Menú de micrófono y altavoz`
  - Purpose should explain opening the audio menu to review `Microphone`,
    `Speaker`, `Leave computer audio`, `Use phone audio`, and `More audio
    settings` for recovery/navigation.
  - It must not say the presenter switches devices, leaves computer audio,
    selects phone audio, reads private device names, or changes settings.

- `ringcentral.video.toolbar.video-menu`
  - Suggested title: `Menú de cámara`
  - Purpose should explain opening the camera menu for camera selection and
    `More video settings`.
  - It must not say the presenter changes cameras, turns video on/off, or
    changes video settings without a user request.

- `ringcentral.video.more.background`
  - Suggested title: `Fondo desde More`
  - Purpose should explain that `More` > `Background` opens Settings on the
    `Background` tab to review `Blur` and virtual background options for
    privacy/appearance setup.
  - It must not say blur is selected, uploaded/custom images are safe to inspect,
    or any background setting is changed by default.

Keep visible RingCentral UI labels literal where users must find them in the
product: `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`,
`More audio settings`, `More video settings`, `More`, `Background`, `Settings`,
and `Blur`.

## Acceptance Criteria

- `packages/ringcentral-video.yaml` adds Spanish `localizedTitles.es` and
  `localizedPurposes.es` for exactly:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- Spanish optional display metadata counts update from `5/27` to `8/27` in
  current-state durable docs and tests that assert live package state.
- Required localization remains complete: `51/51` demo steps, `12/12` localized
  questions, and `12/12` localized answers.
- Spanish aliases remain `questionAliases.es present on 26/27 entrypoints (69
  aliases)`.
- `localization-report --package ringcentral-video --language es
  --require-complete` still exits `0`; optional title/purpose metadata remains
  informational and does not gate required completeness.
- `entrypoints --package ringcentral-video --area "Meeting toolbar" --language
  es` shows localized title/purpose markers for the new audio-menu and
  video-menu entries while unrelated toolbar entries keep their expected
  localized or fallback markers.
- `entrypoints --package ringcentral-video --area "More menu" --language es`
  shows localized title/purpose markers for `more.background` and keeps
  sensitive entries such as recording/notes on their existing fallback or
  answer-only paths.
- Alias-normalized probes keep working:
  - `entrypoints --package ringcentral-video --area "Meeting toolbar" --language
    Spanish`
  - `entrypoints --package ringcentral-video --area "More menu" --language
    es-MX`
  - `localization-report --package ringcentral-video --language Spanish`
- Focused tests update exact Spanish title/purpose strings, exact localized
  entrypoint id set, CLI localized/fallback output, answer rendering, and
  durable-doc count guard.

## Suggested Verification

Run focused checks that match the content blast radius:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy tests\unit\test_questions.py::test_ringcentral_spanish_unseeded_entrypoint_keeps_alias_label_fallback
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es-MX
.\.venv\Scripts\python.exe -m ruff check --no-cache packages tests
git diff --check
git status --short
```

Expected status: intended package, test, durable-doc, and implementation
handoff files only, plus any pre-existing `.coverage` modification left
unstaged and untouched.

## No-Go Areas

- Do not target full Spanish `27/27` entrypoint display localization.
- Do not add display metadata for `meeting-info`, `report-issue`, `chat`,
  `participants`, `invite`, `share`, `recording`, `notes`, `leave`, direct
  mic/camera toggles, `start`, or `select blur` in this slice.
- Do not add or change Spanish aliases, Q&A prompts, Q&A answers, demo
  narration, open steps, cleanup modes, route order, question policies, safety
  routing, matcher behavior, or controller interrupt behavior.
- Do not change Spanish runtime voice support, OpenAI/local provider routing,
  profiles, speech assets, controller language choices, `voices`, `doctor`, or
  live RingCentral acceptance claims.
- Do not make `localizedTitles` or `localizedPurposes` part of
  `--require-complete`.
- Do not edit historical handoffs to reconcile counts.
- Do not stage or commit, and do not touch `.coverage`.

## Suggested Next Slice Summary

Cycle139 should be a compact package-content wedge: add Spanish optional
title/purpose metadata for the audio menu, video menu, and Background-from-More
entrypoints only, then update tests and current-state durable docs from `5/27`
to `8/27`. It is the best next user-visible step after Cycle138 made package
language aliases behave correctly.
