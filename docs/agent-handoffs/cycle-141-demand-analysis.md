# Cycle 141 Demand Analysis: Spanish Display Metadata Routing Guard

Date: 2026-05-17
Cycle: 141
Scope: demand analysis only. This file is the only intended edit for this
cycle. Do not edit source code, tests, package YAML, durable docs, generated
artifacts, staging, commits, or pre-existing `.coverage` changes in this
analysis slice.

Worktree note: Cycle140 already added Spanish `localizedTitles.es` and
`localizedPurposes.es` for:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

Those additions moved optional Spanish display metadata to `8/27` entrypoints.
Cycle141 should harden the boundary around that result, not expand it.

## User Value

- Spanish operators can inspect the three newly localized menu surfaces with
  clearer display text while keeping Spanish question routing predictable.
- Maintainers get regression coverage proving optional display metadata remains
  display/rendering metadata, not a new query-matching signal.
- Future localization wedges can add package-local display copy without
  silently changing which RingCentral control a Spanish question opens or
  describes.
- The project preserves the current safety story: localized copy may make
  inspection clearer, but it must not broaden operation eligibility, add new
  aliases, or alter route selection.

## Current Boundary To Preserve

- `entrypoints --language` resolves the package-local language key, reads
  `OperationEntrypoint.title_for_language()` and
  `OperationEntrypoint.purpose_for_language()`, and labels each field as
  localized or fallback.
- `MaterialPackage.entrypoint_match_candidates` are built from canonical
  entrypoint id, title, area, and purpose fields. They intentionally do not use
  `localizedTitles` or `localizedPurposes`.
- `answer_question()` routes Spanish entrypoint questions by package-owned
  `questionAliases.es`, then by existing canonical match candidates. The
  localized title/purpose may be used after a match is selected to render the
  response, but must not decide the match.
- Existing generic guards cover parts of this boundary. Cycle141 should pin the
  guarantee to the three Cycle140 entrypoints because they are the newest and
  riskiest examples.

## Exact Recommended Scope

Implement a tests-only hardening pass. Recommended edits are limited to focused
unit tests:

- In `tests/unit/test_cli.py`, extend or add `entrypoints --language` assertions
  for the Cycle140 entries:
  - `--area "Meeting toolbar" --language es` shows `audio-menu` and
    `video-menu` with localized title and purpose markers.
  - `--area "More menu" --language es-MX` normalizes to `Language: es` and
    shows `more.background` with localized title and purpose markers.
  - Existing unrelated entries keep their expected localized or fallback
    markers.
- In `tests/unit/test_material_packages.py`, add a RingCentral-specific guard
  that the match candidates for the three Cycle140 entries exclude
  Spanish-only display terms from localized title/purpose copy. Use token-level
  assertions against `entrypoint_match_candidates` so the test verifies the
  construction boundary directly.
- In `tests/unit/test_questions.py`, add Spanish routing assertions that prove
  matching remains alias-driven for these entries:
  - Existing alias queries such as `selector de microfono y altavoz`,
    `selector de camara en video`, and `fondo desde el menu more` still route to
    the same three entrypoint ids.
  - Spanish phrases that appear only in localized purpose copy, such as
    `sin cambiar dispositivos`, `sin cambiar la camara`, and
    `sin seleccionar fondos`, do not route to those entrypoints and return the
    Spanish no-match response.
- Keep the implementation as test coverage only. No product behavior should
  change in this cycle.

Implementation nuance: do not use full localized title strings as the only
negative black-box probes. Current canonical matching can still match shared
English/canonical tokens such as `menu` or `More` without reading
`localizedTitles.es`. The safer proof is a direct match-candidate token guard
plus localized-purpose-only negative question probes.

## Out-of-Scope Boundaries

- Do not edit `packages/ringcentral-video.yaml`.
- Do not add, remove, or change `localizedTitles`, `localizedPurposes`,
  `questionAliases`, Q&A prompts, Q&A answers, demo narration, open steps,
  cleanup modes, route order, question policies, or presenter notes.
- Do not change `src/ai_presenter/cli.py`,
  `src/ai_presenter/packages/models.py`, or
  `src/ai_presenter/runtime/questions.py`.
- Do not change Spanish runtime voice support, OpenAI/local provider routing,
  profiles, speech assets, controller language choices, `voices`, `doctor`, or
  live RingCentral acceptance claims.
- Do not move optional display metadata beyond `8/27`, and do not make
  `localizedTitles` or `localizedPurposes` part of `--require-complete`.
- Do not attempt to fix broader fuzzy matching behavior in this cycle. If a
  full localized title happens to route because of canonical tokens like
  `menu`, record that as existing matcher behavior, not as a Cycle141 source
  change.
- Do not stage or commit unless a later implementation task explicitly asks for
  it, and do not touch unrelated dirty files such as pre-existing `.coverage`.

## Acceptance Criteria

- The implementation diff is tests-only, aside from the Cycle141 handoff doc if
  carried forward. Package YAML, source runtime/CLI files, durable docs, and
  generated artifacts remain unchanged.
- CLI unit coverage proves the three Cycle140 entries display localized
  title/purpose markers through `entrypoints --language`, including Spanish
  alias normalization from `es-MX` to `es`.
- Material-package unit coverage proves the three Cycle140 entries'
  `entrypoint_match_candidates` do not contain Spanish-only localized display
  terms from `localizedTitles.es` or `localizedPurposes.es`.
- Question-routing unit coverage proves existing Spanish aliases still route to:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- Question-routing unit coverage proves localized-purpose-only Spanish phrases
  do not create matches and return the Spanish no-match response.
- Spanish localization status remains unchanged: required localization complete
  at `51/51` demo steps, `12/12` localized questions, and `12/12` localized
  answers; optional display metadata remains `8/27`; aliases remain `26/27`
  with `69` aliases.
- Focused verification passes:
  - `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
  - `.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -q tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates`
  - The new RingCentral-specific material package and question-routing tests.
  - `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete`
  - `git diff --check`
  - `git status --short`

## Implementation Handoff Prompt

```text
Implement Cycle141's Spanish display metadata routing guard in
C:\Users\rcadmin\Documents\Repos\AiPresenter.

Context:
- Cycle140 added Spanish `localizedTitles.es` and `localizedPurposes.es` for:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- Optional Spanish display metadata is now `8/27`.
- The goal is to harden that localized display metadata affects package-local
  inspection/rendering only and does not become a Spanish query routing or
  matching signal.

Scope:
- Tests only. Do not modify package YAML, source runtime/CLI code, durable docs,
  providers, profiles, routes, aliases, Q&A, narration, cleanup, or acceptance
  records.
- Add or extend `tests/unit/test_cli.py` assertions so
  `entrypoints --package ringcentral-video --area "Meeting toolbar" --language es`
  shows localized title/purpose markers for `audio-menu` and `video-menu`.
- Add or extend `tests/unit/test_cli.py` assertions so
  `entrypoints --package ringcentral-video --area "More menu" --language es-MX`
  normalizes to `Language: es` and shows localized title/purpose markers for
  `more.background`.
- Add a RingCentral-specific `tests/unit/test_material_packages.py` guard that
  the match candidates for `audio-menu`, `video-menu`, and `more.background`
  exclude Spanish-only localized display terms from `localizedTitles.es` and
  `localizedPurposes.es`.
- Add `tests/unit/test_questions.py` cases proving existing Spanish aliases
  still route to the same three ids, while localized-purpose-only Spanish
  phrases such as `sin cambiar dispositivos`, `sin cambiar la camara`, and
  `sin seleccionar fondos` do not create matches.

Boundaries:
- Do not change Spanish matching semantics to make the new display copy match.
- Do not assert that every full localized title is a no-match; current canonical
  matching can match shared tokens such as `menu` or `More` without reading
  localized display metadata.
- Do not expand optional display metadata beyond `8/27`.
- Do not touch unrelated dirty files such as `.coverage`.

Acceptance:
- Focused CLI, material-package, and question-routing pytest checks pass.
- `localization-report --package ringcentral-video --language es --require-complete`
  still exits 0 and reports `51/51`, `12/12`, `12/12`, display metadata `8/27`,
  and aliases `26/27` with `69` aliases.
- `git diff --check` passes.
- `git status --short` shows only intended test/handoff files plus any
  pre-existing unrelated dirty artifacts.
```
