# Cycle 140 Technical Scan: Spanish Entrypoint Display Metadata

Date: 2026-05-17
Scope: read-only scan, except this handoff file.

## Worktree Note

- `.coverage` was already modified before this scan; leave it alone.
- While scanning, another worker added implementation-like edits in
  `packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`,
  `tests/unit/test_material_packages.py`,
  `docs/knowledge/language-lifecycle.md`, and
  `docs/knowledge/ringcentral-video/source-index.md`, plus an untracked
  `docs/agent-handoffs/cycle-140-demand-analysis.md`. Do not revert those.
- Current CLI output already reports the target Spanish display count:
  `localizedTitles.es` and `localizedPurposes.es` on `8/27` entrypoints.
- One stale test remains in the current worktree:
  `tests/unit/test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present`
  still asserts the exact localized-entrypoint id set is the old five-entry set.

## Implementation Map

Primary package data:

- `packages/ringcentral-video.yaml`
  - `ringcentral.video.toolbar.audio-menu`: add `localizedTitles.es` and
    `localizedPurposes.es` directly after the canonical `purpose`.
  - `ringcentral.video.toolbar.video-menu`: same placement.
  - `ringcentral.video.more.background`: same placement.
  - Do not change `questionAliases`, `openSteps`, cleanup modes, `questionPolicy`,
    demo narration, Q&A, or route order.

Existing helpers should not need source changes:

- `src/ai_presenter/packages/models.py`
  - `OperationEntrypoint.localized_titles`
  - `OperationEntrypoint.localized_purposes`
  - `title_for_language()`
  - `purpose_for_language()`
- `src/ai_presenter/packages/localization_status.py`
  - `build_localization_status()`
  - `render_localization_status_lines()`
- `src/ai_presenter/cli.py`
  - `resolve_package_language_key()`
  - `entrypoints()`
  - `localization_report()`
- `src/ai_presenter/runtime/questions.py`
  - `_render_entrypoint_answer()`
  - `_entrypoint_answer_label()`

Tests to touch:

- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_spanish_entrypoint_copy_pilot_is_present()` so
    `expected_spanish_display_copy` contains the prior five plus exactly:
    `ringcentral.video.toolbar.audio-menu`,
    `ringcentral.video.toolbar.video-menu`, and
    `ringcentral.video.more.background`.
  - Keep `test_ringcentral_localization_status_reports_complete_spanish_package()`
    at `8` titles and `8` purposes.
  - Keep or add a focused exact-string guard for the three new entries.
  - Keep `test_ringcentral_spanish_display_metadata_counts_match_durable_docs()`
    deriving counts from `build_localization_status()`.
- `tests/unit/test_cli.py`
  - Keep Spanish report expectations at `8/27`.
  - Add focused `entrypoints --language es` assertions for localized markers on
    `audio-menu`, `video-menu`, and `more.background`.
  - Preserve fallback assertions for unrelated entries such as direct
    audio/video controls and `more.recording`.
- `tests/unit/test_questions.py`
  - Add the three new entries to
    `test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy()`
    so answer rendering proves localized titles/purposes replace English
    purpose text and Spanish alias-label fallback.

Docs to touch:

- `docs/knowledge/language-lifecycle.md`
  - Current Spanish optional display metadata count should be `8/27` for both
    `localizedTitles.es` and `localizedPurposes.es`.
- `docs/knowledge/ringcentral-video/source-index.md`
  - Same `8/27` current-state count.
- Do not edit historical handoffs just to reconcile old `5/27` mentions.

## Count Expectations

After the implementation:

- Entrypoints: `27`
- Demo narration localization for Spanish: `51/51`
- Spanish localized Q&A questions: `12/12`
- Spanish localized Q&A answers: `12/12`
- `questionAliases.es`: `26/27` entrypoints, `69` aliases
- `localizedTitles.es`: `8/27` entrypoints
- `localizedPurposes.es`: `8/27` entrypoints
- `--require-complete` still gates only demo narration and Q&A, not aliases or
  entrypoint display metadata.

## Verification Commands

Focused stale-test check:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_covers_optional_menu_surfaces tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package
```

Focused CLI and package checks:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_spanish_entrypoint_copy_pilot_is_present tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_covers_optional_menu_surfaces tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_normalizes_spanish_language_aliases tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_questions.py::test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy
```

Manual CLI probes:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language Spanish
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es-MX
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language de
```

Final hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache tests\unit\test_cli.py tests\unit\test_material_packages.py tests\unit\test_questions.py
git diff --check
git status --short
```

## Pitfalls

- Language alias normalization is package-local for `entrypoints` and
  `localization-report`: `Spanish` and `es-MX` resolve to `es`, while unknown
  keys such as `de` remain raw lookup keys. Do not route these commands through
  runtime voice validation.
- `entrypoints --language` prints independent `(title: localized|fallback)` and
  `(localized|fallback)` purpose markers. Only the three scoped entries should
  flip from fallback to localized in this wedge.
- `localizedTitles.es` and `localizedPurposes.es` do not create matches.
  Matching still depends on Q&A, `questionAliases`, legacy aliases, and token
  scoring.
- Spanish entrypoint answers use a localized title when present; otherwise
  `_entrypoint_answer_label()` falls back to the first Spanish alias before the
  canonical English title. Adding title metadata changes answer labels for the
  three targets, so question tests should cover that.
- Keep RingCentral UI labels literal where users must find them in-product:
  `Microphone`, `Speaker`, `Leave computer audio`, `Use phone audio`,
  `More audio settings`, `More video settings`, `More`, `Background`,
  `Settings`, and `Blur`.
- Keep copy navigation-focused and privacy-bound. Do not imply switching
  devices, leaving computer audio, selecting phone audio, reading private
  device names, changing camera/video settings, selecting Blur, uploading
  images, inspecting custom assets, or changing the user's background.
- Do not describe Spanish entrypoint display metadata as complete; `8/27` is
  still intentionally partial.
