# Cycle 142 Demand Analysis: CLI Spanish Entrypoint Inspection Guard

Date: 2026-05-17
Cycle: 142
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: demand analysis only. This file is the only intended edit for this
analysis slice. Do not edit source code, tests, package YAML, durable docs,
generated artifacts, staging, commits, or pre-existing `.coverage` changes.

Worktree note: while this analysis was being prepared, concurrent
`tests/unit/test_cli.py` edits and
`docs/agent-handoffs/cycle-142-risk-scan.md` /
`docs/agent-handoffs/cycle-142-technical-scan.md` appeared. Treat those as
other workers' Cycle142 context to validate against this demand analysis. Do
not revert, normalize, stage, or claim ownership of them from this doc-only
slice.

## Context

Cycle140 added Spanish optional display metadata for exactly three RingCentral
Video entrypoints:

- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.more.background`

Cycle141 guarded the more important runtime boundary: those
`localizedTitles.es` and `localizedPurposes.es` fields may render after a valid
match, but they must not become query-routing or fuzzy-match inputs.

Cycle142 should stay adjacent and smaller. The remaining user-facing gap is CLI
inspection confidence: maintainers should be able to run `entrypoints` with
`--language es`, `--language Spanish`, or `--language es-MX` and see the same
canonical package-language key plus localized/fallback markers for the three
Cycle140 entries.

## User Value

- Maintainers get a direct regression guard for the manual inspection command
  they use to verify Spanish package display metadata.
- Spanish and regional-language aliases become visibly trustworthy in the CLI:
  `Spanish` and `es-MX` should normalize to the same package-local `es` lookup
  as `es`.
- Future localization slices can rely on `entrypoints --language` as a stable
  audit surface for optional display copy without reopening matcher behavior.
- The guard preserves Cycle141's safety boundary by proving inspection output
  is display-only: it reports localized/fallback source markers, not route
  eligibility.

## Current State

- `src/ai_presenter/cli.py::resolve_package_language_key()` delegates known
  presenter-language aliases through `normalize_presenter_language()` and leaves
  unknown package-only keys raw.
- `src/ai_presenter/cli.py::entrypoints()` prints `Language: <resolved-key>`
  and, when `--language` is present, prints each entrypoint's localized or
  fallback title and purpose source markers.
- `src/ai_presenter/runtime/voice.py` already maps `Spanish`, `es-MX`,
  `es-ES`, `espanol`, and `es` to canonical `es`.
- `tests/unit/test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
  already proves `--language es` shows localized/fallback markers for the
  toolbar and More-menu Cycle140 entries.
- `tests/unit/test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
  already proves `Spanish` and `es-MX` normalize to `Language: es`, but it only
  checks the Meeting toolbar area. It does not yet pin
  `ringcentral.video.more.background` under those alias inputs.

## Exact Recommended Scope

Implement a tests-only CLI inspection guard in `tests/unit/test_cli.py`.

Recommended shape:

- Add or refactor one focused parameterized test, for example
  `test_entrypoints_language_normalizes_spanish_aliases_for_cycle140_display_metadata`.
- Parameterize the language input over `["es", "Spanish", "es-MX"]`.
- For each input, invoke:
  - `entrypoints --package ringcentral-video --area "Meeting toolbar" --language <input>`
  - `entrypoints --package ringcentral-video --area "More menu" --language <input>`
- Assert both invocations exit `0` and print `Language: es`.
- In the Meeting toolbar output, assert:
  - `ringcentral.video.toolbar.audio-menu` appears with `(title: localized)`.
  - Its purpose line ends with `(localized)`.
  - `ringcentral.video.toolbar.video-menu` appears with `(title: localized)`.
  - Its purpose line ends with `(localized)`.
  - A known non-localized toolbar entry, such as
    `ringcentral.video.toolbar.audio`, still appears with `(title: fallback)`.
- In the More menu output, assert:
  - `ringcentral.video.more.background` appears with `(title: localized)`.
  - Its purpose line ends with `(localized)`.
  - A known non-localized More-menu entry, such as
    `ringcentral.video.more.recording`, still appears with `(title: fallback)`.
- Keep the assertions marker-centered where practical. Reuse exact localized
  strings only when the surrounding test style requires it; the Cycle142 value
  is the alias-normalized marker behavior, not another copy snapshot.

This can be done by extending the existing alias-normalization test, by adding
small private assertion helpers inside `tests/unit/test_cli.py`, or by adding a
new adjacent test. The preferred path is the smallest readable diff that proves
all three Cycle140 entrypoints for all three language inputs.

## Approaches Considered

Recommended: parameterize the two area-scoped `entrypoints` calls over the three
language inputs. This keeps output small, covers all Cycle140 entries, and
proves alias normalization for both toolbar and More-menu surfaces.

Acceptable but noisier: run unfiltered `entrypoints --package ringcentral-video
--language <input>` for each language input and assert the three entries in the
full 27-entrypoint output. This is literal to the command wording but makes the
test harder to scan.

Avoid: changing CLI, package, matcher, or runtime source. Current behavior
already supports this guard; Cycle142 should document and pin it, not create a
new behavior path.

## Out-of-Scope Boundaries

- Do not edit `packages/ringcentral-video.yaml`.
- Do not edit `src/ai_presenter/cli.py`,
  `src/ai_presenter/packages/models.py`, `src/ai_presenter/runtime/voice.py`,
  or `src/ai_presenter/runtime/questions.py` unless a later implementation run
  unexpectedly proves the existing alias normalization is broken.
- Do not change Spanish `localizedTitles`, `localizedPurposes`,
  `questionAliases`, Q&A, demo narration, open steps, cleanup modes, route
  order, question policies, providers, profiles, or live RingCentral acceptance
  claims.
- Do not add new matcher tests in this cycle. Cycle141 already owns the runtime
  routing boundary.
- Do not expand optional Spanish display metadata beyond `8/27` entrypoints.
- Do not make optional entrypoint display metadata part of
  `--require-complete`.
- Do not touch unrelated dirty files such as `.coverage`.
- Do not stage or commit unless a later implementation task explicitly asks for
  it.

## Acceptance Criteria

- The implementation diff is tests-only, normally limited to
  `tests/unit/test_cli.py`.
- For each language input `es`, `Spanish`, and `es-MX`, CLI unit coverage proves
  `entrypoints` resolves the package language header to `Language: es`.
- For each of those language inputs, CLI unit coverage proves localized title
  and purpose markers are shown for:
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.more.background`
- For each of those language inputs, CLI unit coverage keeps at least one
  toolbar fallback marker and one More-menu fallback marker visible, so the test
  proves localized and fallback display states together.
- No package YAML, source runtime/CLI behavior, aliases, Q&A, durable docs, or
  localization counts change.
- Spanish localization status remains unchanged: required localization complete
  at `51/51` demo steps, `12/12` localized questions, and `12/12` localized
  answers; optional `localizedTitles.es` and `localizedPurposes.es` remain
  `8/27`; `questionAliases.es` remains `26/27` with `69` aliases.
- Focused verification passes without updating coverage artifacts:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata
```

If the implementation adds a newly named test, include that test in the focused
pytest command instead of, or in addition to, the existing alias-normalization
test.

Recommended final hygiene:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
git diff --check
git status --short
```

Expected status should show only intended test/handoff changes plus any
pre-existing unrelated dirty artifacts.

## Implementation Handoff Prompt

```text
Implement Cycle142's CLI Spanish entrypoint inspection guard in
C:\Users\rcadmin\Documents\Repos\AiPresenter.

Context:
- Cycle140 added Spanish optional display metadata for:
  - ringcentral.video.toolbar.audio-menu
  - ringcentral.video.toolbar.video-menu
  - ringcentral.video.more.background
- Cycle141 guarded that localizedTitles.es and localizedPurposes.es do not alter
  question routing or entrypoint match candidates.
- Cycle142 should guard CLI inspection only: entrypoints --language es,
  --language Spanish, and --language es-MX should all resolve to Language: es
  and show localized/fallback markers for the three Cycle140 entries.

Scope:
- Tests only. Prefer limiting the implementation diff to tests/unit/test_cli.py.
- Add or extend a focused parameterized CLI test over language inputs:
  es, Spanish, es-MX.
- For each input, invoke:
  entrypoints --package ringcentral-video --area "Meeting toolbar" --language <input>
  entrypoints --package ringcentral-video --area "More menu" --language <input>
- Assert each result exits 0 and prints Language: es.
- Assert the Meeting toolbar output shows localized title and purpose markers
  for ringcentral.video.toolbar.audio-menu and
  ringcentral.video.toolbar.video-menu.
- Assert the More menu output shows localized title and purpose markers for
  ringcentral.video.more.background.
- Assert one toolbar fallback marker and one More-menu fallback marker remain
  present, such as ringcentral.video.toolbar.audio and
  ringcentral.video.more.recording.

Boundaries:
- Do not modify package YAML, source code, runtime voice support, matcher logic,
  aliases, Q&A, demo narration, providers, profiles, durable docs, acceptance
  files, or localization counts.
- Do not add new matcher tests; Cycle141 already owns that guard.
- Do not expand optional Spanish display metadata beyond 8/27.
- Do not touch unrelated dirty files such as .coverage.

Verification:
- Run focused no-coverage pytest for the entrypoints language tests:
  $env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata
- If you add a new test name, include it in that command.
- Run:
  $env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py
  .\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py
  .\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
  git diff --check
  git status --short

Acceptance:
- es, Spanish, and es-MX all print Language: es for entrypoints inspection.
- The three Cycle140 entries show localized title and purpose markers under all
  three language inputs.
- At least one toolbar and one More-menu fallback marker remain asserted.
- No source, package YAML, routing, alias, localization-count, durable-doc, or
  unrelated dirty-file changes are introduced.
```
