# Cycle 141 Technical Scan: Spanish Display Metadata Matcher Boundary

Date: 2026-05-17
Scope: technical scan only. This handoff is the only file owned by this task.

## Worktree Note

- `git status --short` showed pre-existing `.coverage` modification before this
  handoff was written. Leave it alone.
- Do not revert concurrent package, source, test, docs, or coverage edits from
  other workers.
- After this handoff was first written, concurrent edits appeared in
  `tests/unit/test_questions.py` plus untracked
  `docs/agent-handoffs/cycle-141-demand-analysis.md` and
  `docs/agent-handoffs/cycle-141-risk-scan.md`. Treat them as other workers'
  changes.
- This cycle should harden the boundary that `localizedTitles` and
  `localizedPurposes` are display metadata only. They may shape CLI inspection
  and rendered Spanish answer copy after a match, but they must not create a
  Spanish query match.

## Current Matcher Mechanics

- `src/ai_presenter/runtime/questions.py`
  - `answer_question()` logs and delegates to `_answer_question()`.
  - `_answer_question()` normalizes the user prompt, checks `_match_qa()` first,
    then `_match_entrypoint()`, then returns localized no-match text.
  - `_match_qa()` checks exact localized Q&A prompts via
    `package.qa_questions_by_normalized`, special safety Q&A heuristics, Q&A
    fragment containment, package alias presence, and final Q&A token overlap.
  - `_match_entrypoint()` checks `_match_entrypoint_alias()` before token
    scoring. This means package-owned `questionAliases` and the legacy alias
    table intentionally beat canonical title/area/purpose token scoring.
  - `_match_package_entrypoint_alias()` scans
    `package.entrypoint_question_aliases_by_match_order`; this is the intended
    path for Spanish location/control questions.
  - `_score_entrypoint_match()` scores only `EntrypointMatchCandidate` token
    fields.
  - `_render_entrypoint_answer()` and `_entrypoint_answer_label()` are display
    paths. Spanish answer labels should still use `localizedTitles.es` when a
    match was created by Q&A, alias, or canonical package logic.

- `src/ai_presenter/packages/models.py`
  - `OperationEntrypoint.localized_titles` and `.localized_purposes` are parsed
    at lines 53-54 and exposed through `title_for_language()` /
    `purpose_for_language()`.
  - `MaterialPackage.validate_entrypoint_references()` flattens only
    `entrypoint.question_aliases` into `EntrypointQuestionAlias` at lines
    197-209.
  - `_build_qa_question_candidates()` indexes canonical and localized Q&A
    questions only.
  - `_build_entrypoint_match_candidates()` currently builds entrypoint fuzzy
    token candidates only from canonical `id`, `title`, `area`, and `purpose`
    at lines 390-407. Do not add localized title/purpose tokens here.

- `src/ai_presenter/cli.py`
  - `entrypoints()` is a package-local inspection command. With `--language`, it
    prints `title_for_language()` and `purpose_for_language()` plus
    localized/fallback markers. This display behavior is allowed and should not
    be mistaken for runtime matching.
  - `localization_report()` reports counts for `questionAliases.<lang>`,
    `localizedTitles.<lang>`, and `localizedPurposes.<lang>`.
  - `doctor()` can require localization and run alias/Q&A diagnostics, but it
    does not answer questions.

## Implementation Recommendation

This is likely a test-hardening slice first. The current source shape already
keeps localized display metadata out of entrypoint match candidates, and a
no-write probe with a package containing only `localizedTitles.es` /
`localizedPurposes.es` returned no match for `Donde esta el panel de notas y
transcripcion?`.

If the new tests fail, keep the source fix narrow:

- Touch `src/ai_presenter/packages/models.py::_build_entrypoint_match_candidates`
  only if localized title/purpose tokens have been added to
  `EntrypointMatchCandidate`.
- Touch `src/ai_presenter/runtime/questions.py::_match_entrypoint()` or
  `_score_entrypoint_match()` only if a separate runtime path starts reading
  localized title/purpose values for matching.
- Do not change `_render_entrypoint_answer()` or `_entrypoint_answer_label()`
  unless answer rendering breaks after an intended Q&A or alias match.
- Do not change `packages/ringcentral-video.yaml` for this cycle unless a test
  fixture is impossible without a tiny synthetic package.

## Exact Tests To Touch

- `tests/unit/test_questions.py`
  - Concurrent work already added
    `test_ringcentral_spanish_alias_routes_render_optional_display_metadata`
    and
    `test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches`.
    Keep them if they remain in the worktree; they are aligned with this scan.
  - Add a synthetic-package regression adjacent to
    `test_localized_entrypoint_title_alone_does_not_create_a_match()`.
  - Recommended test name:
    `test_localized_entrypoint_title_and_purpose_do_not_create_spanish_match`.
  - Fixture shape:
    - one entrypoint with canonical English `title="Internal Control"`,
      `purpose="Open internal controls."`, and no `questionAliases`;
    - `localizedTitles.es = "Panel de notas y transcripcion"`;
    - `localizedPurposes.es = "Abre el panel de notas y transcripcion."`;
    - no Q&A.
  - Assert `answer_question(..., question="Donde esta el panel de notas y transcripcion?", voice=PresenterVoiceSettings(language="es"))`
    returns `entrypoint_id is None` and `can_operate is False`.
  - Add a companion positive control in the same test or an adjacent test:
    when the same package adds `questionAliases.es = ["panel de notas y transcripcion"]`,
    the same question should match that entrypoint. This proves the blocker is
    display metadata, not Spanish text in general.
  - If the concurrent RingCentral tests are retained and the owner wants to
    avoid another synthetic fixture, ensure they cover both sides explicitly:
    Spanish alias prompts match and render localized copy, while Spanish
    fragments sourced only from display metadata return no match.
  - Keep existing positive rendering tests:
    `test_entrypoint_answer_uses_localized_title_and_purpose`,
    `test_ringcentral_spanish_entrypoint_answer_uses_localized_pilot_copy`,
    and `test_spanish_entrypoint_answer_uses_package_alias_label`.

- `tests/unit/test_material_packages.py`
  - Keep `test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates`.
  - Strengthen it if needed by also asserting the candidate token sets do not
    contain Spanish tokens from `localizedTitles.es` and `localizedPurposes.es`
    together, not only a few sample words.
  - Keep `test_material_package_exposes_normalized_question_alias_index`; it is
    the package-owned alias index contract.
  - Do not change Spanish coverage count tests unless another cycle changes
    package data. Current expected Spanish state is `questionAliases.es` on
    `26/27` entrypoints with `69` aliases and `localizedTitles.es` /
    `localizedPurposes.es` on `8/27` entrypoints.

- `tests/unit/test_cli.py`
  - No matcher behavior should be asserted through CLI entrypoint display.
  - Keep `test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy`
    and `test_entrypoints_language_normalizes_spanish_alias_for_display_metadata`
    as display-only guards.
  - If adding a CLI guard, assert only that `entrypoints --language es` prints
    localized/fallback markers. Do not claim that printed Spanish metadata is
    query-matchable.

- `tests/unit/test_diagnostics.py`
  - Usually no change. Existing alias diagnostics operate on
    `entrypoint_question_aliases`, not localized display metadata.
  - Add diagnostics coverage only if an implementation changes package indexes
    so localized title/purpose can accidentally appear in alias diagnostics.

## Focused Verification Commands

Run no-coverage focused tests so `.coverage` remains untouched:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match tests\unit\test_questions.py::test_localized_entrypoint_title_and_purpose_do_not_create_spanish_match
```

Run the positive Spanish alias/Q&A controls:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_location_questions_match_curated_aliases tests\unit\test_questions.py::test_ringcentral_spanish_safety_questions_stay_qa_first_with_aliases tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_safety_questions_stay_qa_first
```

Run display-only CLI/package guards:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy tests\unit\test_cli.py::test_entrypoints_language_normalizes_spanish_alias_for_display_metadata tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_material_packages.py::test_ringcentral_spanish_display_metadata_counts_match_durable_docs
```

Manual probes after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar" --language es
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --area "More menu" --language es-MX
```

Final hygiene:

```powershell
.\.venv\Scripts\ruff.exe check --no-cache src\ai_presenter\runtime\questions.py src\ai_presenter\packages\models.py tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_cli.py
git diff --check
git status --short
```

## Scan Verification Already Run

Existing guards passed:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match tests\unit\test_questions.py::test_ringcentral_spanish_location_questions_match_package_aliases_without_legacy_table tests\unit\test_cli.py::test_entrypoints_language_inspects_ringcentral_localized_and_fallback_copy
```

Result: `4 passed in 1.58s`.

No-write synthetic probe result:

```text
None False No encontre un control que coincida en el contexto activo de la app.
```

## Pitfalls

- Do not treat `entrypoints --language es` output as a matcher input contract.
  That command intentionally displays localized metadata for humans.
- Do not add localized title/purpose tokens to
  `EntrypointMatchCandidate`. That would make optional Spanish display copy
  route live questions.
- Do not broaden `_match_package_entrypoint_alias()` to inspect
  `localized_titles` or `localized_purposes`; it must stay tied to
  `questionAliases`.
- Do not weaken Q&A-first behavior to make alias tests easier. Spanish safety
  questions should continue to hit Q&A before aliases where authored.
- Do not change `questionPolicy`, `openSteps`, or `_can_operate()` in this
  slice. Matching intent and operation permission are separate.
- Do not change package language alias normalization in `cli.py`; `Spanish` and
  `es-MX` should still resolve to `es` for package inspection, and unknown keys
  should remain raw package-local lookups.
- Beware accent folding: `normalize_question_prompt()` strips Latin diacritics,
  so tests should cover either accented and unaccented Spanish variants or use
  unaccented prompts as the lower-friction regression.
- Keep Spanish display metadata partial. Current `8/27` title/purpose coverage
  is intentional and does not imply all RingCentral entrypoints have Spanish
  display copy.
