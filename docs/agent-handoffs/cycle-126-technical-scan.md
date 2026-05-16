# Cycle 126 Technical Scan: Accent-Insensitive Spanish Package Aliases

Date: 2026-05-17

Scope: technical scan only for commit `9e2ac26`. This document is the only intended file change. Do not change package alias storage text, do not enable runtime `--language es`, do not broaden Q&A fuzzy matching, and do not submit a commit from this scan.

## Existing Normalization Structure

- Package-owned entrypoint aliases are declared as `operationEntrypoints[*].questionAliases` and are preserved as package text.
- `src/ai_presenter/packages/models.py` flattens aliases into `EntrypointQuestionAlias(entrypoint_id, language, alias, normalized_alias)`.
- Alias normalization is currently only `alias.strip().casefold()`. That means accented Spanish aliases such as `configuracion` vs `configuración`, `reunion` vs `reunión`, `boton` vs `botón`, `camara` vs `cámara`, `microfono` vs `micrófono`, and `transcripcion` vs `transcripción` do not match each other.
- Q&A prompts use `normalize_question_prompt(text)`, also currently `strip().casefold()`. `QuestionAnswerMatchCandidate.normalized_question`, `qa_questions_by_normalized`, Q&A exact matching, Q&A fragment matching, safety heuristics, and diagnostics all depend on that same Q&A normalization.
- Token fallback uses `match_field_tokens()` / `match_meaningful_tokens()` with `[a-z0-9]+` over `casefold()` text. This splits accented words (`reunión` becomes fragments around the accent) and is a fallback path, not the package-owned alias path.
- Runtime question order in `src/ai_presenter/runtime/questions.py` is still the main safety guard:
  1. exact Q&A prompt match;
  2. recording and notes/transcript safety Q&A heuristics;
  3. Q&A fragment/token matching;
  4. package-owned entrypoint alias substring match;
  5. legacy alias table;
  6. entrypoint token scoring.
- `src/ai_presenter/runtime/diagnostics.py` builds alias duplicate, Q&A duplicate, Q&A alias overlap, and Q&A alias substring-risk indexes from the stored normalized strings. Today those diagnostics see accented and unaccented Spanish forms as different strings.
- Spanish remains package-only: diagnostics already report `localization language es is package-only` under runtime language support, while Spanish package localization can be complete.

## Minimal Implementation Plan

Recommended minimal slice: add accent-insensitive matching only for package-owned question aliases, while leaving Q&A normalization and stored alias text unchanged.

1. Add a small helper in `src/ai_presenter/packages/models.py`, for example `normalize_question_alias_match_text(text: str) -> str`.
2. Implement it as `strip().casefold()` plus Unicode decomposition and removal of combining marks, likely with `unicodedata.normalize("NFKD", value)` and `unicodedata.combining(char)`.
3. Use this helper only when building `EntrypointQuestionAlias.normalized_alias`.
4. Keep `alias=alias.strip()` exactly as-is so package storage/display text remains accented and unchanged.
5. In `src/ai_presenter/runtime/questions.py`, normalize the incoming question for package-owned alias checks with the same helper before `_match_package_entrypoint_alias()`.
6. Keep Q&A exact/fragment/fuzzy matching on `normalize_question_prompt()` so this change does not enlarge Q&A fuzzy risk.
7. Do not apply the new helper to `_legacy_entrypoint_alias_matches()` unless a separate explicit decision is made. The target is package-owned aliases only.
8. Keep longest-alias ordering based on the alias match key. Removing accents does not materially change Spanish alias lengths for this candidate, and it preserves the current source-order tie behavior.

Implementation sketch:

```python
import unicodedata

def normalize_question_alias_match_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.strip().casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))
```

Then:

- in `MaterialPackage.validate_entrypoint_references()`: use `normalize_question_alias_match_text(alias)`;
- in runtime alias matching: derive an alias-normalized question once before package alias matching, or inside `_match_package_entrypoint_alias()`;
- keep Q&A matching fed by the existing `normalized = normalize_question_prompt(question)`.

The cleanest runtime shape is to keep `_match_entrypoint(package, normalized_question)` as the public internal flow, but inside `_match_entrypoint_alias()` call package alias matching with the accent-folded question and legacy matching with the original normalized question. That prevents accidental legacy behavior changes.

## Tests To Add Or Update

Add focused tests rather than broad fixture churn.

- `tests/unit/test_material_packages.py`
  - Add a unit package with Spanish aliases containing accents, then assert `alias.alias` preserves the accented text while `alias.normalized_alias` is accent-folded.
  - Cover at least `configuración`, `reunión`, `botón`, `cámara`, `micrófono`, `transcripción`.
  - Update any assertion that currently expects `normalized_alias == expected_alias.casefold()` only if it uses a Spanish accented fixture. Existing Chinese/Japanese tests can remain unchanged.

- `tests/unit/test_questions.py`
  - Add a package-owned alias runtime test with `_ENTRYPOINT_ALIASES` monkeypatched to `{}`.
  - Assert unaccented Spanish input matches accented package aliases:
    - `configuracion de fondo` -> `ringcentral.video.settings.background`;
    - `boton start en ringcentral video` -> `ringcentral.develop.video.start`;
    - `control de camara en la barra` -> `ringcentral.video.toolbar.video`;
    - `estado del microfono en reunion` -> `ringcentral.video.toolbar.audio`;
    - `panel de notas y transcripcion` -> `ringcentral.video.more.notes`.
  - Keep voice as `PresenterVoiceSettings(language="en")`; do not add `language="es"`.
  - Add a Q&A-first regression where an unaccented Spanish safety prompt still returns the Q&A route, for example recording or chat/participants safety, proving alias accent folding does not jump ahead of Q&A.

- `tests/unit/test_diagnostics.py`
  - Add/adjust duplicate alias diagnostics so `configuracion` and `configuración` on different entrypoints are a duplicate normalized package-owned alias.
  - Add/adjust same-entrypoint duplicate coverage so accented and unaccented variants on the same entrypoint remain OK.
  - Add a Q&A alias overlap or substring-risk diagnostic using an unaccented Q&A prompt and an accented Spanish alias only if the implementation intentionally uses the alias-folded key in diagnostics. Recommendation: diagnostics should use the same package alias match key so doctor catches runtime-equivalent collisions.

Do not update Spanish localization counts unless the implementation changes package data, which this candidate should not do.

## Risk Points

- Q&A fuzzy expansion is the main risk. Avoid applying accent folding to `normalize_question_prompt()`, `QuestionAnswerMatchCandidate`, `qa_questions_by_normalized`, or `match_meaningful_tokens()` in this slice.
- Diagnostics must stay aligned with runtime package-alias behavior. If runtime treats `camara` and `cámara` as equivalent but doctor does not, duplicate/overlap checks will miss real alias conflicts.
- Alias substring matching is still broad. Accent folding makes more Spanish user text eligible to hit package aliases, so keep the change package-alias-only and rely on the existing Q&A-first ordering.
- Legacy alias table behavior should not change. Folding legacy aliases could unexpectedly widen Chinese/Japanese/English routes and is outside the target.
- Unicode decomposition can affect non-Spanish scripts if applied globally. For CJK/Japanese aliases it should usually be a no-op, but tests should confirm existing Chinese/Japanese package alias routing still passes.
- The `normalized_alias` field name currently means simple casefolded text. After this change it becomes the alias match key. This is acceptable if documented in tests/diagnostics, but avoid changing public stored `alias`.

## Validation Commands

Use the project venv and keep the scope tight first:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py -k "alias or spanish"
.\.venv\Scripts\python.exe -m pytest tests/unit/test_questions.py -k "spanish or package_owned_alias or qa_first"
.\.venv\Scripts\python.exe -m pytest tests/unit/test_diagnostics.py -k "alias"
```

Then run the full affected files:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py tests/unit/test_questions.py tests/unit/test_diagnostics.py
.\.venv\Scripts\python.exe -m ai_presenter.cli doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
```

Expected doctor shape remains: Spanish localization OK, runtime language support FAIL because `es` is still package-only.

## Core Recommendation

Add an accent-folded match key for package-owned aliases and apply the same key to package-alias diagnostics. Leave package alias display/storage text accented, leave Q&A normalization alone, keep `PresenterVoiceSettings(language="es")` unsupported, and verify with unaccented Spanish alias inputs plus Q&A-first safety regressions.
