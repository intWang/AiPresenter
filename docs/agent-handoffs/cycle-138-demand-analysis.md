# Cycle 138 Demand Analysis: Resume Safe Spanish Entrypoint Display Copy

Date: 2026-05-16
Cycle: 138
Scope: demand analysis only. This file is the only intended edit. Do not edit
source, tests, package YAML, README, durable docs, generated artifacts,
staging, commits, or `.coverage` in this analysis slice.

## Recommendation

Best small Cycle138 optimization slice: add another tiny Spanish optional
entrypoint display metadata wedge for safe, non-toggling RingCentral Video
entrypoints, moving `localizedTitles.es` / `localizedPurposes.es` from `5/27`
toward `8/27`.

Recommended entrypoints:

- `ringcentral.video.toolbar.audio-menu`: explain the microphone and speaker
  menu as device recovery/navigation. Keep `Microphone`, `Speaker`, `Leave
  computer audio`, `Use phone audio`, and `More audio settings` recognizable.
  The Spanish purpose should say not to switch devices, leave computer audio,
  or read private device names unless the user asks and visible context is
  verified.
- `ringcentral.video.toolbar.video-menu`: explain the camera menu as camera
  selection and the `More video settings` shortcut. The purpose should say not
  to change cameras or video settings unless the user asks.
- `ringcentral.video.more.background`: explain the Background entrypoint from
  the More menu as the path to blur or virtual backgrounds. The purpose should
  frame it as privacy and appearance setup, but avoid claiming blur is selected
  or custom assets are safe to inspect.

This beats another docs-only slice because Cycle137 already added the README
inspection boundary and removed the future-date durable-doc claim. It also
beats a performance slice because the current scan found no concrete failing
package-loading or test-speed pain beyond normal focused-test coverage hygiene.
The project now has the count guard from Cycle135 and the boundary docs from
Cycle137, so a small content wedge is ready again.

## Options Evaluated

1. **Another tiny Spanish display metadata wedge for safe entrypoints**

   Highest value now. The repo already protects the count updates with
   `test_ringcentral_spanish_display_metadata_counts_match_durable_docs`, and
   `entrypoints --language es` has tests that keep inspection package-local.
   Device-recovery menus are useful to Spanish operators and safer than
   privacy-heavy or state-changing controls. Keep the wedge to exactly three
   entrypoints so the author can update package copy, tests, CLI expectations,
   and durable counts together.

2. **CLI/README ergonomics around language, tone, or entrypoint inspection**

   Useful but lower priority for Cycle138. README now includes
   `.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video
   --language es` and states that it inspects package-local display metadata
   only. CLI output already marks `localized` versus `fallback` title and
   purpose fields. A later ergonomics slice could add a compact
   `--localized-only` filter, but that would be a behavior change and should
   not be bundled with package copy.

3. **Performance/test-speed or package-loading improvement**

   Not the best next slice. `load_material_package()` is intentionally simple,
   and package indexes are built by the Pydantic model after load. The
   maintenance playbook already says to prefer structural tests over wall-clock
   thresholds and to cache only with clear invalidation rules. No current test
   failure, slow command, or repeated live package-loading hotspot was found in
   this scan. Defer until a technical scan can identify a specific repeated
   load path, such as multiple CLI subcommands in one process or controller
   refresh loops.

4. **RingCentral Video knowledge package quality or acceptance docs**

   Valuable but not the best small optimization after Cycle137. The knowledge
   package now has source, evidence, privacy, state, locator, runtime-safety,
   acceptance-runs, and validation-checklist docs, plus validation target tests
   that cover evidence-index integrity. A future docs slice could improve
   acceptance-draft examples for sanitized device-menu evidence, but adding
   Spanish display copy first gives those menus clearer package language
   without claiming live acceptance.

5. **Project-local need discovered**

   The repo-local maintenance playbook now captures recurring rules for
   localization wedges, RingCentral evidence, performance hygiene, and staging.
   No immediate new maintenance artifact is needed. The main local need is to
   keep exercising the guardrails with small, reviewable package content
   changes instead of expanding process docs again.

## User Value

- Spanish users get clearer package-local answer/display text for common audio,
  video, and background recovery surfaces.
- Maintainers continue language/tone expansion in a safe, count-guarded way
  after the Cycle137 boundary fix.
- The slice improves practical UI guidance without touching live mic/camera
  state, provider routing, controller behavior, or RingCentral acceptance
  claims.
- Future agents get another concrete pattern for safe Spanish optional display
  metadata on menu-style entrypoints.

## Acceptance Criteria

- Add Spanish `localizedTitles.es` and `localizedPurposes.es` for exactly:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- Optional display metadata counts update from `5/27` to `8/27` everywhere
  current durable docs or tests assert the live state.
- `test_ringcentral_spanish_display_metadata_counts_match_durable_docs`
  derives counts from the package and passes after docs are updated.
- Package tests assert the exact localized title/purpose strings and the exact
  Spanish localized entrypoint id set.
- CLI tests update expected `entrypoints --language es` localized/fallback
  output for the affected areas and `localization-report` counts.
- `localization-report --package ringcentral-video --language es
  --require-complete` still passes required demo/Q&A localization and does not
  treat optional title/purpose metadata as required completeness.
- `entrypoints --package ringcentral-video --language es` shows the new Spanish
  display copy with localized markers and preserves fallback markers elsewhere.
- Focused verification should include:
  - `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy`
  - `.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --language es`
  - `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete`
  - `.\.venv\Scripts\ruff check --no-cache packages tests`
  - `git diff --check`
  - `git status --short`

## No-Go Areas

- Do not target full Spanish `27/27` entrypoint display localization.
- Do not add display metadata for `meeting-info`, `report-issue`, `chat`,
  `participants`, `invite`, `share`, `recording`, `notes`, `leave`, mic/camera
  toggles, `start`, or `select blur` in this slice.
- Do not change Spanish runtime voice support, local SAPI/Piper support,
  profiles, provider routing, speech assets, controller UI, or live
  RingCentral Video acceptance claims.
- Do not change question matching, aliases, Q&A precedence, safety routing,
  `questionPolicy`, operation routes, cleanup modes, or controller interrupt
  behavior.
- Do not make `localizedTitles` or `localizedPurposes` part of
  `--require-complete`.
- Do not edit historical handoffs to reconcile counts.
- Do not stage or commit, and do not touch `.coverage`.

## Suggested Next Slice Summary

Cycle138 should be a compact package-content wedge: add Spanish optional
title/purpose metadata for the audio menu, video menu, and Background entrypoint
only, then update the count-guarded tests and durable docs from `5/27` to
`8/27`. This continues language expansion where it helps real operators while
keeping runtime, safety, and live-acceptance boundaries quiet.
