# Cycle 126 Implementation: Accent-Insensitive Match Normalization

Date: 2026-05-17

## Goal

Make Spanish package-owned aliases and authored Q&A prompts robust to unaccented
Latin input while keeping Spanish runtime support disabled.

## Implemented Changes

- Added Latin-diacritic folding to `normalize_question_prompt()` in
  `src/ai_presenter/packages/models.py`.
- Kept stored package text unchanged. `EntrypointQuestionAlias.alias` still
  preserves the authored accented string; `normalized_alias` is now the match
  key.
- Updated package alias construction, Q&A candidate construction, Q&A exact
  indexes, diagnostics indexes, tokenization, and legacy alias precomputation to
  share the same normalization path.
- Removed combining marks only when they follow Latin base characters. This is
  intended to preserve Chinese/Japanese matching behavior and avoid
  romanization/transliteration.
- Added focused tests for:
  - accented stored text with unaccented match keys;
  - unaccented Spanish location prompts routing to curated aliases;
  - unaccented Spanish safety prompts staying Q&A-first and non-operable;
  - halfwidth Japanese input not being folded into fullwidth Japanese aliases;
  - diagnostics catching accent-folded alias duplicates and Q&A/alias overlap.
- Review follow-up narrowed decomposition from `NFKD` to `NFD` so compatibility
  forms such as halfwidth Japanese are not normalized into package aliases.

## Non-Goals Preserved

- No package YAML alias additions.
- No Spanish runtime support.
- No voice/provider/controller/profile changes.
- No `questionPolicy`, open step, cleanup, demo flow, or locator changes.
- No fuzzy edit-distance, semantic, stemming, or LLM-based intent matching.

## Verification So Far

Red phase:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_normalizes_latin_diacritics_for_matching tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_location_questions_match_curated_aliases tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_safety_questions_stay_qa_first tests\unit\test_diagnostics.py::test_diagnostics_warns_for_accent_folded_question_alias_duplicates tests\unit\test_diagnostics.py::test_diagnostics_allows_accent_folded_same_entrypoint_alias_duplicates tests\unit\test_diagnostics.py::test_diagnostics_warns_when_accent_folded_qa_shadows_entrypoint_alias
```

Result before implementation: `4 failed, 4 passed`. Failures showed accented
aliases still normalized with plain `casefold()`, `menu de camara` routed to the
audio menu, and diagnostics did not catch folded duplicate/overlap cases.

Green phase:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_normalizes_latin_diacritics_for_matching tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_location_questions_match_curated_aliases tests\unit\test_questions.py::test_ringcentral_spanish_unaccented_safety_questions_stay_qa_first tests\unit\test_diagnostics.py::test_diagnostics_warns_for_accent_folded_question_alias_duplicates tests\unit\test_diagnostics.py::test_diagnostics_allows_accent_folded_same_entrypoint_alias_duplicates tests\unit\test_diagnostics.py::test_diagnostics_warns_when_accent_folded_qa_shadows_entrypoint_alias
```

Result: `8 passed`.

Affected file tests after review follow-up:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
```

Result: `308 passed`.

Static checks:

```powershell
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
.\.venv\Scripts\mypy --no-incremental src tests
```

Results: ruff passed; mypy reported no issues in `81` source files.

CLI smoke:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
```

Result: `4 passed`.

Review follow-up:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_halfwidth_japanese_input_is_not_folded_into_package_alias
```

Result before the review fix: `1 failed`. The halfwidth Japanese prompt
matched a fullwidth Japanese package alias under `NFKD`; changing to `NFD`
keeps the prompt unmatched while Spanish Latin diacritic folding still works.

Final verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
```

Results: `808 passed, 1 warning`; ruff passed; mypy reported no issues in `81`
source files.

Manual CLI checks:

- `ai-presenter doctor --profile ringcentral-video-bind-speaker --package
  ringcentral-video --flow meeting-control-map-demo` reports `0 warnings, 0
  failed`.
- `ai-presenter localization-report --package ringcentral-video --language es`
  still reports `51/51`, `12/12`, `12/12`, and `26/27 (69 aliases)`.
- `ai-presenter doctor --profile ringcentral-video-bind-speaker --package
  ringcentral-video --flow meeting-control-map-demo --require-localization
  --localization-language es` reports package localization OK and the expected
  runtime language support failure for `es`.
- `ai-presenter demo --profile ringcentral-video-bind-speaker --package
  ringcentral-video --flow meeting-control-map-demo --language es --dry-run`
  still rejects `es` as an unsupported presenter runtime language.

## Review Notes

Reviewer should focus on:

- Whether folding only Latin diacritics is implemented conservatively enough for
  Japanese voiced marks and CJK text.
- Whether changing `normalize_question_prompt()` is acceptable for Q&A exact and
  duplicate behavior.
- Whether diagnostics and runtime now share the same match key.
- Whether `demo --language es` remains unsupported in final verification.
