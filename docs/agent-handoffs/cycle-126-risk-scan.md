# Cycle 126 Risk Scan: Accent-Insensitive Spanish Alias Matching

Date: 2026-05-17

Scope: review the candidate direction after commit `9e2ac26`: make
package-owned aliases match unaccented Spanish user input and surface matching
diagnostics. The current implementation normalizes questions and aliases with
`strip().casefold()`, sorts package-owned aliases longest-first, then performs
substring matching across all package languages. Diagnostics use the package
model's normalized aliases/questions for duplicate, Q&A overlap, and Q&A
substring-risk checks.

This scan is risk guidance only. It does not implement accent folding.

## 1) Main Risks

1. Runtime and diagnostics normalization drift

   Accent-insensitive matching cannot be runtime-only. If runtime folds
   `reunión` to `reunion`, `botón` to `boton`, `micrófono` to `microfono`, or
   `más` to `mas`, then diagnostics must check duplicate aliases, Q&A exact
   overlap, and Q&A substring risk using the same canonical form. Otherwise the
   app can route an unaccented prompt to one entrypoint while doctor still
   reports no duplicate or overlap.

   Highest-risk examples:

   - `reunión` / `reunion` may appear in many Spanish aliases and Q&A prompts.
   - `más` / `mas` can broaden `More` routing.
   - `botón` / `boton`, `menú` / `menu`, `cámara` / `camara`, and `micrófono` /
     `microfono` are common location words, not entrypoint-specific words.
   - `grabación` / `grabacion`, `transcripción` / `transcripcion`, and
     `invitación` / `invitacion` sit near safety-sensitive controls.

2. Cross-language duplicate risk may become invisible or too noisy

   Current duplicate diagnostics are cross-entrypoint and cross-language because
   `aliases_by_normalized` groups every package-owned alias by normalized text.
   Accent folding will mostly affect Latin-script languages, but there are two
   failure modes:

   - If canonical forms are checked globally, harmless language-local
     collisions could be reported as cross-language conflicts if future
     packages add French, Portuguese, or mixed English/Spanish aliases.
   - If canonical forms are checked only inside Spanish, aliases still match
     language-agnostically at runtime, so a folded Spanish alias could collide
     with an English alias and route unexpectedly.

   Because runtime alias matching is not scoped by presenter voice language,
   diagnostics should continue to flag cross-entrypoint duplicates globally.
   The report should include languages so reviewers can tell Spanish fold
   collisions from same-language duplicates.

3. Chinese and Japanese matching may be accidentally changed

   Do not run broad transliteration, romanization, width folding, or punctuation
   stripping over all languages. Existing Chinese and Japanese aliases depend on
   direct substring matching and carefully curated CJK phrases. Accent folding
   should be a diacritic-removal pass for Latin combining marks only, after
   Unicode decomposition, and should leave Han, Kana, and existing Japanese
   mojibake-negative behavior alone.

   Specific risks:

   - CJK question fragments could become blank or malformed if a regex keeps
     only ASCII after folding.
   - Japanese voiced sound marks, half-width/full-width forms, or Kana should
     not be treated as "accents" in this cycle.
   - Existing Chinese/Japanese Q&A-first safety tests must remain behaviorally
     identical.

4. Q&A-first safety can be bypassed for unaccented safety prompts

   The question path checks Q&A before aliases, but Q&A exact/fragment matching
   currently uses the same simple normalized string. If alias matching becomes
   accent-insensitive and Q&A matching does not, a user asking unaccented
   Spanish safety questions could miss the authored Q&A prompt and fall through
   to a broad alias.

   Examples to protect:

   - `Como manejo la grabacion de la reunion de forma segura?`
   - `Puede leer los mensajes del chat o los nombres de participantes?`
   - `Puede describir el contenido compartido en pantalla?`
   - `Donde estan notas y transcripcion?`
   - `Puede enviar una reaccion o levantar la mano de forma segura?`

   Q&A canonical matching must be at least as permissive as alias canonical
   matching, and Q&A-first tests need unaccented variants.

5. Diagnostics duplicate, overlap, and substring checks must share one
   canonicalizer

   There should be a single package-level canonical matching helper used for:

   - Stored `EntrypointQuestionAlias.normalized_alias`.
   - `QuestionAnswerMatchCandidate.normalized_question`.
   - Runtime `answer_question()` query normalization.
   - Diagnostics duplicate alias grouping.
   - Diagnostics Q&A duplicate grouping.
   - Diagnostics Q&A alias exact overlap.
   - Diagnostics Q&A alias substring risk.

   A split between `normalize_question_prompt()` and an alias-only
   `normalize_alias_for_match()` is risky unless both functions explicitly share
   the same canonical form for matching diagnostics.

6. Short broad aliases become more dangerous after folding

   Accent folding expands the number of strings that match each alias. This is
   useful for Spanish typing, but broad aliases such as `mas`, `menu`, `boton`,
   `audio`, `video`, `fondo`, `notas`, `chat`, `reunion`, `configuracion`,
   `grabacion`, `transcripcion`, `invitar`, `compartir`, and `salir` become more
   likely to match unrelated prompts.

   The current longest-first ordering helps when two aliases overlap, but it
   does not make a short alias safe. A short alias can still win when the longer
   intended phrase is absent, misspelled, or unaccented differently.

## 2) Recommended Guardrails

- Add one clearly named canonical matching helper in `src/ai_presenter/packages/models.py`,
  then route runtime and diagnostics through it. Keep display text unchanged.
- Keep `casefold()` and whitespace trim semantics. Add Latin diacritic removal
  only for matching, not for stored `alias` display values.
- Make the helper Unicode-aware and conservative: decompose with NFKD/NFD,
  remove combining marks only when the base character is Latin, then recompose
  or compare the resulting canonical string. Do not ASCII-encode, transliterate,
  romanize, or strip CJK.
- Preserve language-agnostic runtime behavior unless the cycle explicitly owns a
  larger routing design. If runtime remains language-agnostic, diagnostics must
  keep global cross-entrypoint duplicate checks.
- Treat the folded canonical form as the diagnostic key. If `reunión` and
  `reunion` map to different entrypoints, doctor should warn.
- Q&A exact/fragment matching must use the same folded canonical question as
  aliases so unaccented Spanish safety questions stay Q&A-first.
- Keep Q&A substring risk language-scoped, but compare folded canonical alias
  strings against folded canonical localized Q&A prompts.
- Do not silence new substring INFO results by changing severity or skipping
  Spanish. Review the specific alias/Q&A pairs and tighten aliases if needed.
- Avoid adding or blessing short broad aliases as part of this normalization
  work. Normalization should support existing curated aliases; it should not
  expand the alias vocabulary.
- Preserve `questionPolicy: answerOnly` behavior and `_can_operate()` gating.
  Accent folding must not make sensitive aliases operable.
- Keep Spanish runtime support unsupported. This feature is input matching for
  package-owned aliases, not `--language es` presenter support.

## 3) Must Verify

Focused behavior tests:

- Accented and unaccented Spanish location prompts route identically for a
  representative safe set:
  `reunión`/`reunion`, `botón`/`boton`, `menú`/`menu`, `cámara`/`camara`,
  `micrófono`/`microfono`, `más`/`mas`, `información`/`informacion`.
- Unaccented Spanish Q&A safety prompts remain Q&A-first before alias fallback:
  recording safety, chat/participant privacy, shared-screen content, notes and
  transcript, reactions/raise-hand.
- Sensitive entrypoints reached through unaccented Spanish aliases still have
  the expected `can_operate is False` and do not create question interrupt
  steps where policy requires answer-only.
- Chinese and Japanese package-owned alias route tests still pass with the
  legacy alias table disabled.
- Existing mojibake-negative tests still prove corrupted Chinese/Japanese input
  is not accepted as a supported alias.
- Short Spanish broad terms without a curated full phrase either do not match or
  match only where an existing test explicitly accepts the behavior.

Focused diagnostics tests:

- Duplicate alias diagnostics warn when two entrypoints differ only by accents,
  for example `reunión` vs `reunion` or `menú de cámara` vs `menu de camara`.
- Q&A duplicate diagnostics use folded canonical prompts.
- Q&A alias overlap diagnostics warn when a folded Q&A prompt exactly equals a
  folded package-owned alias for an unrelated entrypoint.
- Q&A alias substring diagnostics use folded canonical matching and keep the
  language-scoped alias index.
- RingCentral baseline doctor still reports no warnings or failures after
  expected count/detail updates, and any changed substring INFO count is reviewed
  rather than blindly accepted.

Suggested commands after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_material_packages.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run
.\.venv\Scripts\ruff check --no-cache src tests docs
git diff --check
```

Expected boundary checks:

- `demo --language es --dry-run` still fails with unsupported presenter
  language.
- Spanish localization and alias coverage counts remain package-local evidence,
  not runtime language support evidence.
- Doctor duplicate/overlap checks may become stricter because folded canonical
  forms expose new collisions. Treat that as a useful signal.

## 4) Review Checklist

- Confirm there is exactly one canonical matching path for runtime matching and
  diagnostics matching.
- Confirm the canonicalizer removes Latin diacritics without changing Chinese or
  Japanese strings.
- Confirm all package model cached indexes are rebuilt from the canonical form:
  aliases, Q&A prompts, Q&A exact map, match order, diagnostics indexes.
- Confirm no runtime language support, voice labels, provider routing,
  controller language menus, or Spanish voice docs are added.
- Confirm Q&A-first matching still runs before package-owned aliases for exact,
  safety, fragment, and meaningful-token paths.
- Confirm `_match_package_entrypoint_alias()` is not made more permissive than
  Q&A matching.
- Confirm diagnostics exact duplicate, Q&A duplicate, Q&A alias overlap, and Q&A
  alias substring risk use folded canonical strings.
- Confirm diagnostic messages still show original languages and enough original
  alias/prompt context for review, even if the key is folded.
- Confirm short broad Spanish aliases are not introduced or newly legitimized by
  tests.
- Confirm sensitive aliases for Meeting information, Notes/Transcript,
  Recording, Share, Invite/Add coworkers, Reactions/Raise hand, Audio/Video
  toggles, and Leave remain non-operable where current policy says they should.
- Confirm Chinese and Japanese alias counts and route tests are unchanged unless
  the diff explicitly owns that change.
- Confirm no generated `.coverage` or local artifacts are included.

## 5) Non-Goals

- Do not enable runtime Spanish presenter language support.
- Do not add Spanish voice assets, voice provider routing, controller options,
  acceptance evidence, or app UI language choices.
- Do not add new Spanish aliases merely because folding makes them easier to
  type.
- Do not broaden alias matching with fuzzy edit distance, stemming, semantic
  matching, token bag matching, or LLM-based intent routing.
- Do not romanize, transliterate, or otherwise normalize Chinese/Japanese in
  this cycle.
- Do not change Q&A content, open steps, cleanup behavior, operation types,
  selectors, or `questionPolicy`.
- Do not downgrade diagnostics to keep the doctor report green.
- Do not commit from this risk-scan task.
