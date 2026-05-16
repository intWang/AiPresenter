# Cycle 127 Technical Scan: RingCentralVideo Knowledge Counts And Language Boundary

Date: 2026-05-17

Scope: docs/package/runtime scan only. This handoff is the only intended file change. Do not edit source code, package YAML, existing docs, stage files, or commit from this scan.

## Executive Finding

The current runtime/package behavior is internally consistent after Cycle 126:

- `packages/ringcentral-video.yaml` has 27 operation entrypoints, 4 demo flows, 51 demo steps, 21 explainers, 12 Q&A items, and 3 manual controls.
- Package-owned `questionAliases` total is 156 aliases: `es=69`, `zh=49`, `ja=34`, `en=4`.
- Entrypoints with aliases by language: `es=26/27`, `zh=15/27`, `ja=13/27`, `en=1/27`.
- Q&A prompt candidates total is 84. This is not 12; it is the flattened matching set built from each canonical Q&A question plus localized question variants.
- Spanish, Chinese, and Japanese package localization are complete for required package content: `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers.
- Spanish remains package-only. `PresenterLanguage` is still `en | zh | ja`, and `demo --language es` still rejects with `Unsupported presenter language: es`.
- Latin-diacritic normalization now lives in `normalize_question_prompt()` and is shared by package aliases, Q&A candidates, token fallback, diagnostics, and legacy alias precomputation. It uses `NFD`, removes combining marks only after Latin base characters, then recomposes with `NFC`.

The durable docs still have a few stale counts and descriptions. The highest-value cleanup is docs-only: update `runtime-safety-routing.md`, `observation-log.md`, and a small source-index wording refresh. Historical handoffs should generally be left as history, but a future docs cleanup may add explicit correction notes to the stale Cycle 125/126 handoffs if those files are still used as working references.

## Evidence Checked

Commands run from `C:\Users\rcadmin\Documents\Repos\AiPresenter`:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
```

Observed outputs:

- Spanish localization report: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers, `questionAliases.es` on `26/27` entrypoints with `69` aliases.
- Chinese localization report: `51/51`, `12/12`, `12/12`, `questionAliases.zh` on `15/27` entrypoints with `49` aliases.
- Japanese localization report: `51/51`, `12/12`, `12/12`, `questionAliases.ja` on `13/27` entrypoints with `34` aliases.
- Doctor with package/flow: `156 package-owned aliases`, `84 Q&A question prompts`, `11` Q&A alias substring-risk prompts as INFO, `27/27` explainer coverage, `0 warnings`, `0 failed`.
- Doctor with `--localization-language es`: localization OK, runtime language support FAIL because `es` is package-only.
- Demo dry run with `--language es`: exit 1 with `Unsupported presenter language: es`.

Direct package count probe:

- Flow steps: `vbg-blur-demo=4`, `meeting-basics-demo=3`, `meeting-controls-tour=22`, `meeting-control-map-demo=22`.
- `build_localization_status(..., language="es").required_localization_complete` is `True`.
- First Spanish alias normalization sample: `pestana de video en ringcentral` is the match key for authored package text `pestaña de video en ringcentral`; the package display text keeps the accent.

## Current Runtime Facts

### Package-Owned Question Aliases

`src/ai_presenter/packages/models.py` flattens `operationEntrypoints[*].questionAliases` into `EntrypointQuestionAlias(entrypoint_id, language, alias, normalized_alias)`.

Current facts:

- Stored `alias` text remains package-authored display text.
- `normalized_alias` is built by `normalize_question_prompt(alias)`.
- Alias match order is longest normalized alias first, preserving source-order ties.
- Runtime package alias matching still happens after Q&A exact/safety/fragment checks.
- Diagnostics use the same normalized alias strings for duplicate/overlap/substring checks.

Do not describe current alias normalization as `strip().casefold()` only. That was superseded by Cycle 126.

### Q&A Prompt Counts

The package has 12 Q&A items, but doctor reports 84 Q&A question prompts. Both numbers are correct:

- 12 is the authored `qa` item count.
- 84 is the flattened matching candidate count from canonical questions plus localized question variants.

Docs should avoid saying "12 Q&A prompts" unless they mean "12 Q&A items." For diagnostics and routing, use "84 Q&A question prompts."

### Language Lifecycle

`docs/knowledge/language-lifecycle.md` is already aligned with current behavior:

- Spanish is package-local complete and query-ready.
- Spanish is not a runtime presenter language.
- `doctor --require-localization --localization-language es` can report package localization OK and runtime language support FAIL at the same time.
- `demo --language es` and `controller --language es` must remain unsupported until a runtime-promotion cycle owns voice/provider/UI/acceptance.

Runtime source confirms this boundary:

- `src/ai_presenter/runtime/voice.py` defines `PresenterLanguage = Literal["en", "zh", "ja"]`.
- `_LANGUAGE_ALIASES` has no `es`/Spanish alias.
- `normalize_presenter_language("es")` raises `Unsupported presenter language: es`.
- `src/ai_presenter/runtime/diagnostics.py` has a separate runtime language support check for package-only localization languages.

### Spanish Package-Only Localization

Spanish package content is complete for required package localization, and Spanish package aliases are broad enough for location/control queries across most entrypoints:

- Required package localization: `51/51`, `12/12`, `12/12`.
- Alias coverage: `26/27`, `69`.
- The only entrypoint without `questionAliases.es` is `ringcentral.video.settings.background.blur`, intentionally left without Spanish aliases because it performs direct Blur selection rather than only opening or explaining a location.

Do not call this "runtime Spanish support," "Spanish voice support," or "Spanish live-demo readiness."

### Latin-Diacritic Normalization

Current code in `src/ai_presenter/packages/models.py`:

- `normalize_question_prompt(text)` calls `_strip_latin_diacritics(text.strip().casefold())`.
- `_strip_latin_diacritics()` decomposes with `unicodedata.normalize("NFD", text)`.
- Combining marks are removed only when the previous base character is Latin.
- The result is recomposed with `unicodedata.normalize("NFC", ...)`.

This means `camara` and `cámara` normalize to the same match key, while the change is not Japanese width folding, transliteration, stemming, semantic matching, or fuzzy edit distance.

## Exact Recommended Edits

### 1. `docs/knowledge/ringcentral-video/runtime-safety-routing.md`

Replace the `## Localization And Counts` bullet block that currently says verified on `2026-05-16`, `87` aliases, and `71` Q&A prompts.

Recommended replacement:

```markdown
Current expected package signals, verified on 2026-05-17 with `localization-report` and `doctor`:

- Operation entrypoints: 27.
- Demo flows: 4, with 51 total demo steps.
- Explainers: 21, covering 27/27 entrypoints.
- Q&A items: 12.
- Q&A question prompts: 84.
- Package-owned aliases: 156.
- Spanish aliases: 26/27 entrypoints, 69 aliases.
- Chinese aliases: 15/27 entrypoints, 49 aliases.
- Japanese aliases: 13/27 entrypoints, 34 aliases.
- Spanish, Chinese, and Japanese required package localization coverage: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers.
- Spanish remains package-only: `doctor --require-localization --localization-language es` should report localization OK and runtime language support FAIL, and `demo --language es` should still fail with `Unsupported presenter language: es`.
- `doctor` may report one INFO-level Q&A alias substring risk summary covering 11 prompts; this is expected until the package design changes.
```

Also add a short normalization sentence under `Current Runtime Anchors` or `Localization And Counts`:

```markdown
Question normalization now uses a shared Latin-diacritic-insensitive match key in `src/ai_presenter/packages/models.py`; it uses canonical decomposition (`NFD`) and removes combining marks only after Latin base characters.
```

### 2. `docs/knowledge/ringcentral-video/observation-log.md`

The seed observation says the package has `3 QA items`. Replace that one sentence with:

```markdown
- Known shape: 27 operation entrypoints, 4 demo flows, 51 demo steps, 21 explainers, 12 Q&A items, 156 package-owned question aliases, and manual controls for `say`, `skip`, and `focus`.
```

Keep the evidence qualifier directly above it: this is repository package evidence, not live app observation.

### 3. `docs/knowledge/ringcentral-video/source-index.md`

The repository signal row for `packages/ringcentral-video.yaml` is mostly correct but underspecifies Spanish and alias diagnostics. Recommended replacement for that row's signal cell:

```markdown
27 entrypoints, 4 flows, 51 demo steps, 21 explainers, 12 Q&A items, 156 package-owned aliases, complete Spanish/Chinese/Japanese required package localization, manual controls, safety notes.
```

Recommended replacement for the `src/ai_presenter/runtime/questions.py` row's signal cell:

```markdown
Q&A-first matching, then package-owned localized `questionAliases`, legacy aliases, and token scoring; shared Latin-diacritic-insensitive normalization supports Spanish unaccented prompts while Spanish remains package-only.
```

### 4. `docs/agent-handoffs/cycle-125-technical-scan.md`

This is a historical handoff, so prefer adding a correction note near the top instead of rewriting the whole file.

Recommended note:

```markdown
Correction note from Cycle 127: Cycle 126 superseded the normalization facts in this scan. Matching normalization is no longer `strip().casefold()` only; `normalize_question_prompt()` now performs Latin-diacritic folding with `NFD` and is shared by package aliases, Q&A candidates, diagnostics, token fallback, and legacy alias precomputation. The implemented Spanish alias count remains `26/27` entrypoints and `69` aliases, with `156` package-owned aliases and `84` Q&A question prompts overall.
```

### 5. `docs/agent-handoffs/cycle-126-technical-scan.md`

This handoff is now stale in its proposed implementation details. If future agents still use it, add a supersession note near the top.

Recommended note:

```markdown
Superseded by Cycle 126 implementation and Cycle 127 scan: the final implementation did not keep diacritic folding package-alias-only. `normalize_question_prompt()` is the shared match normalizer for package aliases, Q&A candidates, diagnostics, token fallback, and legacy alias precomputation. It uses `NFD`, not `NFKD`, and removes combining marks only after Latin base characters. Spanish remains package-only and package counts did not change: `51/51`, `12/12`, `12/12`, `26/27` Spanish alias entrypoints, `69` Spanish aliases, `156` package-owned aliases, and `84` Q&A question prompts.
```

### 6. `docs/agent-handoffs/cycle-126-test-review.md`

The residual-risk section still says tests do not cover the compatibility-normalization boundary introduced by `NFKD`, even though the same file records the main-session resolution to `NFD`. If cleanup edits historical handoffs, replace that residual bullet with:

```markdown
- Compatibility-normalization risk was addressed in the main-session resolution by switching from `NFKD` to `NFD` and adding a halfwidth Japanese regression. Remaining normalization risk is limited to future changes that might reintroduce compatibility folding, transliteration, stemming, semantic matching, or broader fuzzy behavior.
```

## Do Not Change

- Do not edit `packages/ringcentral-video.yaml` for this cleanup; counts are already coherent.
- Do not enable `PresenterVoiceSettings(language="es")`.
- Do not add Spanish to `PresenterLanguage`, `_LANGUAGE_ALIASES`, controller language choices, provider routes, or `voices` catalog.
- Do not add unaccented duplicate Spanish aliases to YAML; normalization is already the match mechanism.
- Do not weaken Q&A-first matching, `questionPolicy: answerOnly`, `_can_operate()`, or Notes/Transcript and recording safety heuristics.
- Do not stage `.coverage`.

## Verification For Follow-Up Docs Cleanup

After updating durable docs, run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

Expected: localization reports match the counts above; doctor package/flow has `0 warnings` and `0 failed`; package-only Spanish doctor exits nonzero only because runtime language support fails; demo Spanish dry run exits nonzero with `Unsupported presenter language: es`; only intended docs files are changed.
