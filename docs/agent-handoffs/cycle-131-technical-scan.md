# Cycle 131 Technical Scan: Localized Entrypoint Titles/Purposes

## Scope

Investigated adding localized title/purpose support for `OperationEntrypoint`, plus safer alternatives. This scan is documentation-only; no source, test, package YAML, or durable knowledge docs were modified.

## Current State

`OperationEntrypoint` is strict Pydantic data with English-only `title`, `area`, and `purpose`, plus localized `questionAliases` (`src/ai_presenter/packages/models.py:48`, `src/ai_presenter/packages/models.py:59`). Because `CamelModel` uses `extra="forbid"`, package YAML cannot add new localized title/purpose fields until the model is extended.

Localized package support today exists in three places:

- Demo narration uses `DemoStepNarration.localizedText` (`src/ai_presenter/packages/models.py:78`).
- Q&A uses `localizedQuestions` and `localizedAnswers` (`src/ai_presenter/packages/models.py:106`).
- Entrypoint lookup uses `questionAliases`, precomputed into package alias indexes (`src/ai_presenter/packages/models.py:183`, `src/ai_presenter/packages/models.py:229`).

Title/purpose currently affect behavior in more than display:

- The entrypoint fallback matcher tokenizes English `title`, `area`, and `purpose` (`src/ai_presenter/packages/models.py:376`, `src/ai_presenter/packages/models.py:382`, `src/ai_presenter/packages/models.py:389`).
- Runtime question matching scores title/purpose tokens after Q&A and alias matching (`src/ai_presenter/runtime/questions.py:450`, `src/ai_presenter/runtime/questions.py:482`, `src/ai_presenter/runtime/questions.py:489`).
- Runtime entrypoint answers render `{label}: {entrypoint.purpose}` and currently special-case Spanish labels from aliases only (`src/ai_presenter/runtime/questions.py:527`, `src/ai_presenter/runtime/questions.py:532`).
- Safety operation gating scans English `id`, `title`, and `purpose` for risky action words (`src/ai_presenter/runtime/questions.py:549`).
- CLI `entrypoints` prints English titles (`src/ai_presenter/cli.py:252`, `src/ai_presenter/cli.py:267`).
- Acceptance drafts print English title and purpose (`src/ai_presenter/acceptance/manual_record.py:196`, `src/ai_presenter/acceptance/manual_record.py:201`, `src/ai_presenter/acceptance/manual_record.py:203`).

Localization reports and doctor checks do not currently consider title/purpose coverage. Required localization means demo narration plus Q&A prompts/answers only (`src/ai_presenter/packages/localization_status.py:41`). Entrypoint aliases are reported as informative coverage (`src/ai_presenter/packages/localization_status.py:84`, `src/ai_presenter/packages/localization_status.py:159`) and diagnostics focus on alias/Q&A duplicate and shadowing risks (`src/ai_presenter/runtime/diagnostics.py:289`, `src/ai_presenter/runtime/diagnostics.py:390`, `src/ai_presenter/runtime/diagnostics.py:496`).

The RingCentral package has no `localizedTitle` or `localizedPurpose` fields today. It has 27 operation entrypoints and localized aliases for zh/ja/es subsets (`packages/ringcentral-video.yaml:10`, `packages/ringcentral-video.yaml:15`, `packages/ringcentral-video.yaml:644`). Current report expectations are pinned in tests: zh 15/27 aliases, ja 13/27 aliases, es 26/27 aliases (`tests/unit/test_cli.py:520`, `tests/unit/test_cli.py:542`, `tests/unit/test_cli.py:560`).

## Recommendation

Use a small optional-data addition, not a broad matching change:

1. Add optional fields to `OperationEntrypoint`:
   - `localized_titles: dict[str, str] = Field(default_factory=dict, alias="localizedTitles")`
   - `localized_purposes: dict[str, str] = Field(default_factory=dict, alias="localizedPurposes")`
2. Add two helper methods/properties on `OperationEntrypoint`:
   - `title_for_language(language: str) -> str`
   - `purpose_for_language(language: str) -> str`
   Both should trim localized values and fall back to English when missing or blank.
3. Use those helpers only for rendering localized answers and optional CLI display.
   - In `_render_entrypoint_answer`, render localized label and localized purpose when available.
   - Replace the Spanish alias-label special case with `localizedTitles` first, then keep the alias fallback for Spanish to preserve behavior until package data catches up.
4. Extend localization status with informative counts for localized entrypoint titles and purposes.
   - Do not include these counts in `required_localization_complete` initially. That avoids breaking current `--require-complete` users and mirrors existing optional alias coverage.
5. Keep question matching primarily on `questionAliases`.
   - Do not add localized title/purpose tokens to `_build_entrypoint_match_candidates` in the first pass. Those fields are display/narration labels, while `questionAliases` are already the controlled query surface with duplicate/shadow diagnostics.

This path gives package authors a safer place for localized answer text without weakening the existing alias-first routing model.

## Minimal Implementation Path

1. `src/ai_presenter/packages/models.py`
   - Add `localized_titles` and `localized_purposes` to `OperationEntrypoint`.
   - Add helper methods that return stripped localized values or the English fallback.
   - Keep `EntrypointMatchCandidate` unchanged for the first implementation.

2. `src/ai_presenter/runtime/questions.py`
   - Update `_render_entrypoint_answer` to use `entrypoint.purpose_for_language(voice.language)`.
   - Update `_entrypoint_answer_label` to prefer `entrypoint.title_for_language(voice.language)`.
   - Preserve the current Spanish alias fallback when no localized title exists.

3. `src/ai_presenter/packages/localization_status.py`
   - Add report fields for `entrypoints_with_localized_titles` and `entrypoints_with_localized_purposes`.
   - Render a new optional section or two lines under `Entrypoint aliases`, e.g. `localizedTitles.ja present on 0/27 entrypoints`.
   - Keep `required_localization_complete` unchanged.

4. `src/ai_presenter/cli.py`
   - Optional but useful: add `--language` to `entrypoints` so package owners can inspect localized labels without changing the default English output.
   - Default output should remain unchanged to avoid snapshot churn.

5. `packages/ringcentral-video.yaml`
   - Add a tiny seed first, preferably one non-destructive route such as `ringcentral.video.toolbar.chat` or `ringcentral.video.more.notes`.
   - Do not attempt full package localization in the model-change PR.

## Tests to Add or Update

Add focused tests before implementation:

- `tests/unit/test_material_packages.py`
  - Load a minimal inline `MaterialPackage` with `localizedTitles` and `localizedPurposes`.
  - Assert model fields parse, blank localized values fall back, and `with_demo_flow()` preserves/rebuilds the data.
  - Assert current `entrypoint_match_candidates` still use English tokens only unless a deliberate second-phase matching change is made.

- `tests/unit/test_questions.py`
  - A package-owned localized title/purpose answer test: with `PresenterVoiceSettings(language="ja")`, entrypoint answer should use localized title and purpose.
  - A fallback test: localized title without localized purpose uses localized title plus English purpose, and missing localized title preserves the current behavior.
  - A Spanish regression test: if no `localizedTitles.es` exists, the existing alias label behavior remains.

- `tests/unit/test_material_packages.py` or a new localization-status test
  - Assert localized title/purpose counts are reported separately from required coverage.
  - Assert `required_localization_complete` remains true when narration and Q&A are complete but localized title/purpose coverage is partial or zero.

- `tests/unit/test_cli.py`
  - If adding `entrypoints --language`, assert default output remains English and localized output uses localized title when present.
  - Update localization-report expectations to include the new optional lines.

- `tests/unit/test_diagnostics.py`
  - No required change for the first pass if localized titles/purposes are not used for matching.
  - If a later pass uses localized title/purpose for matching, add duplicate/shadow diagnostics before enabling that behavior.

## Safer Alternative

If the immediate need is only localized question routing, do not add localized title/purpose yet. Continue expanding `questionAliases.<language>` because aliases already have:

- deterministic source-order and length-based matching (`src/ai_presenter/packages/models.py:328`);
- duplicate alias diagnostics (`src/ai_presenter/runtime/diagnostics.py:390`);
- Q&A alias overlap and substring-risk diagnostics (`src/ai_presenter/runtime/diagnostics.py:496`);
- localization report visibility (`src/ai_presenter/packages/localization_status.py:159`).

This is the lowest-risk path for "where is X" questions. It does not solve localized answer labels/purposes, though, which is the main reason to add explicit localized title/purpose fields.

## Verification Performed

Using the repo virtualenv:

- `.\\.venv\\Scripts\\ai-presenter.exe localization-report --package ringcentral-video --language ja`
  - Passed. Output shows 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers, and `questionAliases.ja` on 13/27 entrypoints.
- `.\\.venv\\Scripts\\ai-presenter.exe entrypoints --package ringcentral-video --area "Meeting toolbar"`
  - Passed. Output shows English titles only, e.g. `ringcentral.video.toolbar.audio: Microphone control [Meeting toolbar]`.
- `.\\.venv\\Scripts\\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language ja`
  - Passed. Doctor reports required ja localization complete and no failures.
- `.\\.venv\\Scripts\\python.exe -m pytest tests/unit/test_material_packages.py::test_material_package_exposes_precomputed_entrypoint_match_candidates tests/unit/test_questions.py::test_package_owned_alias_matches_without_legacy_alias_table tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage -q --no-cov`
  - Passed: 3 tests.

Also tried the same targeted pytest command without `--no-cov`; the three tests passed, but the run failed the global `--cov-fail-under=80` gate because only a small subset was executed. For implementation verification, run either focused tests with `--no-cov` during iteration or a broader test selection that satisfies coverage.

## Recommended Verification Commands

After implementation:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/unit/test_material_packages.py tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py -q
.\\.venv\\Scripts\\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\\.venv\\Scripts\\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\\.venv\\Scripts\\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language ja
```

During narrow TDD iteration:

```powershell
.\\.venv\\Scripts\\python.exe -m pytest tests/unit/test_material_packages.py::test_material_package_parses_localized_entrypoint_title_and_purpose tests/unit/test_questions.py::test_entrypoint_answer_uses_localized_title_and_purpose -q --no-cov
```

## Risk Notes

- Adding localized title/purpose to fuzzy matching immediately would broaden the match surface without alias diagnostics. That can accidentally route safety-sensitive controls, especially because Q&A-first matching and alias substring warnings are carefully tuned.
- Required localization should not include title/purpose in the first pass. Current complete zh/ja/es package checks would otherwise fail until all 27 entrypoints have new fields.
- Safety gating should continue to inspect English `id/title/purpose`. Localized purpose text should not be the only source for detecting risky operations.
- Default CLI and acceptance draft output should remain English unless a language option is explicitly requested, to avoid breaking existing operational workflows and tests.
