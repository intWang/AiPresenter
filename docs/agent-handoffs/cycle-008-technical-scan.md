# Cycle 008 Technical Scan

Date: 2026-05-16

Scope: read-only scan of package/runtime lookup and question paths for the package runtime entrypoint/alias index candidate. Production code was not edited by this sidecar; only this handoff document was created.

Workspace note: the target files were already modified when this scan began, and `src/ai_presenter/packages/models.py` changed again during inspection. Findings below describe the current workspace contents, not a clean baseline.

## Summary

The safest optimization seam is a runtime index around the immutable-by-convention package data: entrypoint lookup by id, package-owned question aliases, demo flow lookup by id, QA candidate normalization, and entrypoint token/risk metadata. Current workspace changes already implement part of this in `MaterialPackage`: a private entrypoint dict and a pre-normalized package alias tuple. That is a reasonable first step, but there are still hot linear scans in question QA matching, entrypoint scoring, and demo flow lookup.

The main compatibility risk is Pydantic copy/mutation behavior. Private attrs avoid YAML/schema churn, but they can become stale if package lists are mutated after validation or if future indexes are copied through `model_copy(update=...)`. This matters because `src/ai_presenter/runtime/controller.py:398` already creates a copied package with an appended question-answer flow.

## Current Code Seams

- `src/ai_presenter/packages/models.py:116` builds validation-time state while checking duplicate entrypoint ids and references. The current candidate now stores `_entrypoints_by_id` and `_entrypoint_question_aliases` at `src/ai_presenter/packages/models.py:166`.
- `src/ai_presenter/packages/models.py:170` exposes `entrypoints_by_id` as a `MappingProxyType`; `src/ai_presenter/packages/models.py:178` uses the private dict in `entrypoint_by_id()`, preserving the unknown-id `KeyError` message.
- `src/ai_presenter/runtime/questions.py:210` still scans `package.qa` twice and rebuilds `_qa_questions()` lists per question. It also re-tokenizes every QA question during fuzzy matching at `src/ai_presenter/runtime/questions.py:224`.
- `src/ai_presenter/runtime/questions.py:253` calls package alias matching first, preserving the current package-over-legacy rule. The package alias scan at `src/ai_presenter/runtime/questions.py:298` now uses `package.entrypoint_question_aliases`, but it is still a linear scan over alias records.
- `src/ai_presenter/runtime/questions.py:262` still scans all `operation_entrypoints`, and `_score_entrypoint_match()` at `src/ai_presenter/runtime/questions.py:313` re-tokenizes id/title/area/purpose every question.
- `src/ai_presenter/runtime/questions.py:353` calls `entrypoint_by_id()` and scans risk words on a concatenated string for every matched entrypoint. This is cheap today, but it is a natural part of an entrypoint search record.
- `src/ai_presenter/runtime/package_demo.py:108` benefits from the new `entrypoint_by_id()` dict when executing actions.
- `src/ai_presenter/runtime/package_demo.py:339` keeps `demo_flow_by_id()` as a linear scan and rebuilds the available-flow string on miss.
- `src/ai_presenter/runtime/package_demo.py:331` scans reversed open steps for cleanup mode. This is per-entrypoint and small; indexing it is lower value unless action execution profiles show it matters.

The current RingCentral package has 27 operation entrypoints, 4 demo flows, 51 demo flow steps, and 3 QA entries. The size is small, so this is mainly about cleaner hot paths and future package scale rather than an urgent bottleneck.

## Safest Index API Shape

Keep YAML-facing Pydantic fields as ordered lists/dicts. Do not replace `operation_entrypoints`, `demo_flows`, `qa`, `questionAliases`, `localizedQuestions`, `localizedAnswers`, or `localizedText` with serialized indexes; tests and CLI output rely on list order.

Recommended public surface:

- Keep `MaterialPackage.entrypoint_by_id(entrypoint_id: str) -> OperationEntrypoint` as the compatibility method.
- Keep `MaterialPackage.entrypoints_by_id -> Mapping[str, OperationEntrypoint]` read-only if diagnostics/tests need direct map access.
- Keep `MaterialPackage.entrypoint_question_aliases -> tuple[EntrypointQuestionAlias, ...]` if the index stays model-local.
- Add a flow lookup seam either as `demo_flow_by_id()` backed by an index wrapper, or `MaterialPackage.flow_by_id()` only if the `model_copy(update=...)` stale-cache risk is handled.
- For the remaining question path, prefer a runtime index record over more Pydantic private attrs:
  - `qa_candidates`: original `QuestionAnswer`, normalized question text, precomputed tokens, source language key.
  - `entrypoint_search_records`: original `OperationEntrypoint`, id/title/area/purpose token sets, and precomputed risk text or `can_operate` value.
  - `package_alias_candidates`: original entrypoint id, language key, original alias, normalized alias, sorted or scanned with longest-alias semantics.

If the index remains embedded in `MaterialPackage`, add explicit tests for stale-index behavior before adding flow or QA/token indexes. `model_copy(update=...)` does not re-run full validation in the obvious way callers expect, so a private `_flows_by_id` copied from the old package can miss the `question-answer-demo` flow appended in `src/ai_presenter/runtime/controller.py:398`.

## Pydantic And Type Risks

- `CamelModel` uses `ConfigDict(populate_by_name=True, extra="forbid")`, so package YAML aliases are schema: `operationEntrypoints`, `openSteps`, `questionAliases`, `localizedQuestions`, `localizedAnswers`, `localizedText`, and `demoFlows` must keep working.
- `PrivateAttr` is a good fit for non-serialized runtime indexes, but it is not deep immutability. `entrypoints_by_id` is read-only, while the underlying `OperationEntrypoint` models and the package lists remain mutable.
- Direct mutation after validation can stale the current private indexes. Existing code appears to treat loaded packages as immutable, but temporary package generation and controller question-flow creation build new package objects rather than mutating entrypoints.
- `MaterialPackage.model_construct()` would bypass validators and leave private indexes empty. I did not find a current call site, but it is worth avoiding in tests/factories.
- The current alias dataclass stores `language`, but matching intentionally ignores `voice.language`. Existing behavior scans every localized alias regardless of presenter language.
- Do not make blank aliases match anything. Current candidate strips and skips blank aliases at `src/ai_presenter/packages/models.py:128`.

## Alias And Localization Compatibility

- Package-owned aliases must take precedence over the legacy static alias table. Locked by `tests/unit/test_questions.py:151`.
- Longest package-owned alias must win when multiple aliases match the same question. Locked by `tests/unit/test_questions.py:201`.
- Legacy aliases remain a fallback and should still tolerate packages that do not include every old alias. See `src/ai_presenter/runtime/questions.py:282`.
- Mojibake Chinese input must not be treated as a supported alias. Locked by `tests/unit/test_questions.py:100`.
- Chinese matching relies on substring aliases and localized QA text because `_TOKEN_PATTERN` at `src/ai_presenter/runtime/questions.py:54` only tokenizes ASCII `[a-z0-9]+`. Do not switch to Unicode token scoring as part of this index cleanup unless behavior is deliberately re-specified.
- Localized QA matching scans `QuestionAnswer.localized_questions` across all languages at `src/ai_presenter/runtime/questions.py:239`; localized answer selection uses only `voice.language` at `src/ai_presenter/runtime/questions.py:246`.
- `packages/ringcentral-video.yaml:202`, `:244`, `:265`, `:302`, and `:437` contain package-owned `questionAliases`. `packages/ringcentral-video.yaml:1176` and `:1182` contain localized QA question/answer data.
- Demo narration localization is separate: `DemoStepNarration.localized_text` is consumed by `src/ai_presenter/runtime/voice.py:55`, not by question matching.

## Test Locations

- `tests/unit/test_material_packages.py:78` covers the read-only entrypoint index; `:90` covers unknown-id `KeyError`; `:97` covers normalized package alias records.
- `tests/unit/test_questions.py:39` through `:263` covers Chinese aliases, package-owned aliases, precedence, longest alias, mojibake rejection, and localized QA answers.
- `tests/unit/test_questions.py:266` through `:429` keeps existing operability and fuzzy entrypoint behavior from regressing.
- `tests/unit/test_package_demo.py:199` through `:479` covers action execution, cleanup modes, alternate targets, and action logging; these should remain green when `entrypoint_by_id()` changes internals.
- `tests/unit/test_material_packages.py:126` and `:156` cover flow/entrypoint reference behavior and localized demo narration expectations.
- `tests/unit/test_temporary_package.py:16` through `:90` is important for generated package compatibility because it constructs `MaterialPackage` in memory rather than loading YAML.
- Add new tests before adding a demo flow index:
  - `demo_flow_by_id()` uses an indexed path and preserves the miss message with available flow ids.
  - `_target_with_question_flow()` can find the appended `question-answer-demo` after `model_copy(update={"demo_flows": ...})`.
  - `model_copy(update={"operation_entrypoints": [...]})` either rebuilds indexes or is documented/guarded as unsupported.

## Recommended Next Step

For this cycle, either stop at the current entrypoint/alias private indexes, or add only a small runtime wrapper that is rebuilt where packages enter a runtime operation. I would not add more Pydantic private indexes until the team decides how to handle `model_copy(update=...)` and post-validation mutation.

The highest-value remaining work is:

1. Precompute entrypoint token sets for `_score_entrypoint_match()` without changing scoring.
2. Precompute QA candidates from default and localized questions without changing language-independent matching.
3. Add flow lookup indexing only with an explicit copy/rebuild story.

## Commands Used

```powershell
Get-Content -LiteralPath 'C:\Users\rcadmin\.codex\superpowers\skills\using-superpowers\SKILL.md'
git status --short
rg --files
Test-Path -LiteralPath 'C:\Users\rcadmin\Documents\Repos\AiPresenter\docs\agent-handoffs\cycle-008-technical-scan.md'
(Get-Content -LiteralPath 'src\ai_presenter\packages\models.py').Count
(Get-Content -LiteralPath 'src\ai_presenter\runtime\questions.py').Count
(Get-Content -LiteralPath 'src\ai_presenter\runtime\package_demo.py').Count
rg -n "entry|alias|localized|answer|question|demo|package|material|Knowledge|BaseModel|Field|model_" src tests packages profiles docs\agent-handoffs
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\packages\models.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\questions.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\package_demo.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'tests\unit\test_questions.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'tests\unit\test_package_demo.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'tests\unit\test_material_packages.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'tests\unit\test_material_runtime.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'tests\unit\test_controller.py' | Select-Object -Skip 140 -First 210 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 140), $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'tests\unit\test_temporary_package.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\packages\loader.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
rg -n "entrypoint_by_id|demo_flow_by_id|operation_entrypoints|demo_flows|question_aliases|localized_questions|localized_answers|localized_text" src tests
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\session.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\controller.py' | Select-Object -Skip 360 -First 70 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 360), $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\temporary_package.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\voice.py' | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'packages\ringcentral-video.yaml' | Select-Object -Skip 190 -First 125 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 190), $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'packages\ringcentral-video.yaml' | Select-Object -Skip 748 -First 255 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 748), $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'packages\ringcentral-video.yaml' | Select-Object -Skip 1168 -First 36 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 1168), $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-007-review.md' | Select-Object -First 120 | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\agent-handoffs\cycle-000-tech-scan.md' | Select-Object -First 180 | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
rg -n "entrypoint_by_id\(|demo_flow_by_id\(|questionAliases|localizedQuestions|localizedAnswers|localizedText|model_copy\(" src tests packages
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\factory.py' | Select-Object -Skip 270 -First 55 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 270), $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'src\ai_presenter\runtime\diagnostics.py' | Select-Object -Skip 160 -First 75 | ForEach-Object { '{0,4}: {1}' -f ($i++ + 160), $_ }
git diff -- src\ai_presenter\packages\models.py
git diff -- src\ai_presenter\runtime\questions.py
git diff -- src\ai_presenter\runtime\package_demo.py
git diff -- tests\unit\test_material_packages.py
git diff -- tests\unit\test_questions.py
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\superpowers\specs\2026-05-16-package-runtime-index-design.md' | Select-Object -First 200 | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$i=1; Get-Content -Encoding UTF8 -LiteralPath 'docs\superpowers\plans\2026-05-16-package-runtime-index.md' | Select-Object -First 240 | ForEach-Object { '{0,4}: {1}' -f $i++, $_ }
$raw = Get-Content -Encoding UTF8 -LiteralPath 'packages\ringcentral-video.yaml'; $sections = @{}; for ($i=0; $i -lt $raw.Count; $i++) { if ($raw[$i] -match '^operationEntrypoints:') { $sections.operation = $i }; if ($raw[$i] -match '^demoFlows:') { $sections.flows = $i }; if ($raw[$i] -match '^explainers:') { $sections.explainers = $i }; if ($raw[$i] -match '^qa:') { $sections.qa = $i }; if ($raw[$i] -match '^manualControls:') { $sections.manual = $i } }; $entrypoints = ($raw[$sections.operation..($sections.flows-1)] | Select-String -Pattern '^- id:' | Measure-Object).Count; $flows = ($raw[$sections.flows..($sections.explainers-1)] | Select-String -Pattern '^- id:' | Measure-Object).Count; $flowSteps = ($raw[$sections.flows..($sections.explainers-1)] | Select-String -Pattern '^\s\s- id:' | Measure-Object).Count; $qa = ($raw[$sections.qa..($sections.manual-1)] | Select-String -Pattern '^- question:' | Measure-Object).Count; "entrypoints=$entrypoints flows=$flows flow_steps=$flowSteps qa=$qa"
```

