# Cycle 136 Demand Analysis: Resume Small Spanish Display Copy

Date: 2026-05-16
Cycle: 136
Scope: demand analysis only. This file is the only intended edit. Do not edit
source, tests, package YAML, durable docs, README, generated artifacts,
staging, commits, or `.coverage` in this analysis slice.

## Recommendation

Best small Cycle136 optimization slice: add a tiny Spanish optional display-copy
wedge for low-risk RingCentral Video entrypoints, moving
`localizedTitles.es` / `localizedPurposes.es` from `2/27` toward `5/27`, with
matching tests and durable-doc count updates.

Cycle135 added the missing count-drift guard, so the repo is now safer for the
content step Cycle135 deferred. Keep the wedge small and authorial: three
entrypoints is enough to prove the workflow without turning this into a broad
localization push.

Recommended entrypoints:

- `ringcentral.video.top.views`: layout-only, local visual effect. Spanish copy
  should keep `Views`, `Gallery view`, and `Full screen` recognizable and say it
  does not alter audio, video, or participants.
- `ringcentral.video.toolbar.more`: opens an expansion menu for additional
  controls. Copy should frame it as navigation, not permission to trigger child
  actions such as recording, share, invite, or leave.
- `ringcentral.video.more.settings`: opens the Settings dialog. Copy can name
  Audio, Video, Background, Translation, Join preferences, and General while
  avoiding claims that any setting is changed.

Defer `meeting-info` for this wedge even though it is documented as feasible:
it is answer-only and privacy-sensitive, so it deserves a separate focused
privacy wording/test pass.

## Options Evaluated

1. **Spanish display-copy wedge**: highest value now. It improves localized
   answer rendering and `entrypoints --language es` inspection for common,
   low-risk RingCentral Video routes. Cycle135's guard should catch stale
   `2/27` durable-doc claims when the package moves to the new count.
2. **CLI/report UX around optional metadata counts**: useful, but lower
   urgency. `localization-report` already prints title/purpose counts clearly,
   and `entrypoints --language es` already marks localized versus fallback
   fields. A README inspection example is a good later polish slice, not the
   best Cycle136 main task.
3. **Tone/language documentation or tests**: mostly covered for this boundary.
   `docs/knowledge/language-lifecycle.md` already separates package-local
   display text, runtime voice support, OpenAI-backed Spanish, local SAPI/Piper
   rejection, and live acceptance. Add docs only if the content wedge exposes a
   new ambiguity.
4. **Higher-impact local improvement discovered**: the durable-doc count guard
   now exists in `tests/unit/test_material_packages.py`, and current commands
   still show Spanish display metadata at `2/27`. The best use of that new
   guard is to exercise it with a small count-changing content slice.

## User Value

- Spanish users get more natural answer/display text for common RingCentral
  Video navigation surfaces.
- Maintainers prove the new count guard works during a real content update.
- The project advances language coverage without changing runtime voice
  support, matching behavior, safety gating, or live automation risk.
- Future agents get a concrete pattern for adding optional display metadata:
  package copy, exact tests, CLI expectations, and durable-doc counts together.

## Acceptance Criteria

- Add Spanish `localizedTitles.es` and `localizedPurposes.es` for exactly the
  selected low-risk entrypoints, preferably `top.views`, `toolbar.more`, and
  `more.settings`.
- Optional display metadata counts update from `2/27` to `5/27` everywhere
  current durable docs or tests assert the live state.
- `test_ringcentral_spanish_display_metadata_counts_match_durable_docs`
  continues to derive counts from the real package and passes after docs are
  updated.
- Package tests assert the exact localized title/purpose strings and the exact
  localized entrypoint id set.
- CLI tests update expected `localization-report` counts and any
  `entrypoints --language es` fallback/localized markers affected by the chosen
  entries.
- `localization-report --package ringcentral-video --language es
  --require-complete` still passes required demo/Q&A localization and does not
  treat optional display metadata as required completeness.
- `entrypoints --package ringcentral-video --language es` shows the new Spanish
  display copy with localized markers and preserves fallback markers elsewhere.
- Verification includes the focused package/CLI tests, `ruff` for touched Python
  files, `git diff --check`, and `git status --short`.

## What Not To Do This Cycle

- Do not target full Spanish `27/27` entrypoint display localization.
- Do not change Spanish runtime voice support, provider routing, profiles,
  controller UI, speech assets, or live RingCentral acceptance claims.
- Do not broaden Spanish aliases, fuzzy matching, Q&A precedence, or safety
  routing through localized title/purpose text.
- Do not add high-risk controls such as start meeting, mic/camera toggles,
  share, invite, recording, leave/end, report issue, chat, participants, notes,
  or meeting information in this tiny wedge.
- Do not make `localizedTitles` or `localizedPurposes` part of
  `--require-complete`.
- Do not rewrite historical handoffs just because counts change.
- Do not stage or commit, and do not touch `.coverage`.
