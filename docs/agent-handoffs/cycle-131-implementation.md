# Cycle 131 Implementation: Entrypoint Localized Title/Purpose Rendering

Date: 2026-05-16

## Scope

Implemented optional `OperationEntrypoint` localized display copy for entrypoint answers:

- added `localizedTitles` and `localizedPurposes` package schema fields;
- added helper methods that trim localized values and fall back to canonical English title/purpose;
- updated runtime entrypoint answer rendering to prefer localized title and purpose for the active voice language;
- preserved the Cycle130 Spanish `questionAliases.es` label fallback when localized title is absent;
- added optional localization report counts for entrypoint title/purpose coverage.

## Files Changed

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/packages/localization_status.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-131-implementation.md`

## Behavioral Contract

- `localizedTitles` and `localizedPurposes` are optional maps on operation entrypoints.
- `title_for_language(language)` and `purpose_for_language(language)` return stripped localized copy when present and nonblank, otherwise the canonical `title` or `purpose`.
- Runtime entrypoint answers render localized title and purpose for `voice.language` when present.
- Spanish entrypoint answers still use the first nonblank `questionAliases.es` label when no localized Spanish title exists.
- Localized title/purpose fields are display-only in this cycle. They are not added to fuzzy matching, alias indexes, routing, safety gating, controller interrupt logic, or package YAML.
- Localization reports show optional `localizedTitles.<language>` and `localizedPurposes.<language>` coverage counts. Required localization completeness remains based only on demo narration plus Q&A question/answer coverage.

## Verification

TDD red checks were run before implementation for:

- localized entrypoint schema parsing;
- localized entrypoint runtime rendering;
- optional localization status/CLI counts.

Focused green checks run during implementation:

- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_material_package_parses_localized_entrypoint_title_and_purpose tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_material_packages.py::test_material_package_still_rejects_unknown_entrypoint_keys -q --no-cov`
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_questions.py::test_entrypoint_answer_uses_localized_title_and_purpose tests\unit\test_questions.py::test_entrypoint_answer_uses_localized_title_with_english_purpose_fallback tests\unit\test_questions.py::test_spanish_entrypoint_answer_keeps_alias_label_when_localized_title_missing tests\unit\test_questions.py::test_non_spanish_entrypoint_answer_uses_canonical_title_without_localized_copy tests\unit\test_questions.py::test_localized_entrypoint_title_alone_does_not_create_a_match -q --no-cov`
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py::test_localization_status_renders_partial_coverage_without_failing tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization -q --no-cov`
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_cli.py::test_localization_report_outputs_ringcentral_chinese_coverage tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package -q --no-cov`

Full requested verification should be run before final acceptance:

- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py -q --no-cov`
- `.\.venv\Scripts\ruff check --no-cache src tests`

## Boundaries

- No package YAML content was added or translated.
- No durable product docs or runbooks were updated.
- No live RingCentral, audio, OpenAI, or local Spanish voice acceptance was attempted.
- `.coverage` was already dirty in the worktree and remains out of scope.
