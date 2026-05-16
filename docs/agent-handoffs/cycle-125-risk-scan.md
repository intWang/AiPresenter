# Cycle 125 Risk Scan: Spanish Question Aliases

Date: 2026-05-17

Scope: review the candidate slice of adding Spanish `questionAliases` to
`packages/ringcentral-video.yaml` after commit `346fd0c`. Spanish demo and Q&A
package localization are complete, but presenter runtime Spanish remains
unsupported. The recommended direction is alias expansion only, not `--language
es` runtime promotion.

## 1) Main Risks

1. Runtime support boundary drift

   Spanish is package-local only. Current evidence:

   - `localization-report --package ringcentral-video --language es` reports
     `51/51` demo steps, `12/12` localized Q&A questions, `12/12` localized
     Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3`
     aliases.
   - `demo --language es --dry-run` fails before runtime with `Unsupported
     presenter language: es`.
   - `doctor --require-localization --localization-language es` reports `[OK]
     localization` and `[FAIL] runtime language support`, which is the expected
     package-only boundary.

   Risk: future implementers may see full Spanish package coverage and add `es`
   to `PresenterLanguage`, `_LANGUAGE_ALIASES`, voice labels, controller choices,
   provider routing, or docs without owning the separate runtime promotion and
   acceptance surface.

2. Alias matching is substring-based and language-agnostic at runtime

   Package aliases are normalized with `strip().casefold()`, sorted longest
   first, then matched with `alias.normalized_alias in normalized_question`.
   The matcher does not filter aliases by the selected presenter voice language.
   This is currently useful for package-local alias lookup, but it means Spanish
   aliases can route Spanish-looking questions even while `PresenterVoiceSettings`
   must still be `en`, `zh`, or `ja`.

   Risk: short Spanish nouns such as `chat`, `audio`, `video`, `notas`,
   `fondo`, `reunion`, `grabar`, `compartir`, `salir`, `invitar`, `mas`, or
   `configuracion` can match inside longer prompts and route to an entrypoint
   before the user intended a location/control lookup.

3. Q&A priority can hide unsafe alias additions until prompts drift

   Runtime matching checks Q&A first, then package aliases, then token fallback.
   Exact and fragment Q&A matches protect current Spanish safety prompts, but
   aliases added for Spanish controls can still become dangerous when a user
   asks a phrasing that is not close enough to the authored Q&A. For example,
   `compartir pantalla`, `grabacion`, `notas`, `transcripcion`, `enlace de la
   reunion`, `nombres de participantes`, or `leer chat` should generally remain
   answer-only or safety-Q&A territory, not a generic entrypoint alias.

   Risk: a broad alias may bypass the intended Spanish Q&A answer for a nearby
   but non-identical safety prompt and return an entrypoint answer instead.

4. Cross-entrypoint duplicates and near-duplicates are easy in Spanish

   Existing diagnostics warn on exact normalized aliases that map to different
   entrypoints. Spanish has many tempting duplicate labels:

   - `fondo` could mean `settings.background`, `settings.background.blur`, or
     `more.background`.
   - `configuracion` could mean general settings, video settings, background
     settings, audio device controls, or camera menu.
   - `invitar` could mean `toolbar.invite` or `main.add-coworkers`.
   - `video` could mean camera toggle, camera menu, video settings, or visible
     shared video content.
   - `audio` could mean microphone toggle, microphone/speaker menu, network
     troubleshooting, or "leave computer audio".

   Risk: exact duplicates fail doctor, while semantically duplicate but not exact
   phrases can still create surprising routes.

5. Doctor substring risk will likely increase

   Current doctor baseline is `90 package-owned aliases`, `84 Q&A question
   prompts`, `[OK] qa alias overlap`, and `[INFO] qa alias substring risk` for
   `11` prompts. The substring check is language-scoped, so new Spanish aliases
   will be compared against Spanish localized Q&A prompts. This is expected to
   uncover new INFO entries if aliases appear inside Spanish Q&A text outside
   related entrypoints.

   Risk: implementers may either ignore meaningful new Spanish substring risks
   or "fix" the INFO by weakening diagnostics instead of tightening aliases.

6. Sensitive entrypoints can look harmless as location aliases

   `questionPolicy: answerOnly` protects Meeting information and Notes from
   queued interrupt steps, and empty `openSteps` keeps Recording and Leave
   non-operable from questions. Still, aliasing these surfaces can make the
   assistant identify sensitive controls more often:

   - Meeting information may expose meeting ID, link, dial-in, host, and
     encryption details.
   - Notes/transcript can imply reading, summarizing, recording, or artifact
     availability.
   - Recording changes meeting state and may require consent/policy checks.
   - Leave/end is destructive.
   - Invite/Add coworkers can expose links, suggestions, names, and emails.
   - Share can start screen sharing or imply shared-content inspection.

## 2) Recommended Guardrails

- Keep the implementation YAML-only plus directly necessary tests/docs. Do not
  edit runtime language support.
- Treat Spanish aliases as control-location phrases, not commands. Prefer
  wording like `ubicacion de ...`, `boton de ...`, `panel de ...`, or `menu de
  ...` when the surface is safe to identify.
- Avoid one-word aliases unless the word is uniquely owned by one entrypoint and
  does not appear in Spanish Q&A safety prompts.
- Prefer low-risk first-wave Spanish aliases for orientation and diagnostics:
  meeting overview, network quality, views/layout, participants panel, chat
  panel, microphone/speaker menu, camera menu, reactions location, raise-hand
  location.
- For sensitive controls, either skip aliases or make them explicitly
  location-only and assert `can_operate` remains false where applicable.
- Do not add aliases that are action/content intents, including Spanish forms of
  read, summarize, copy, send, invite someone now, start sharing, start/stop
  recording, transcribe, download, export, leave, end, mute someone, remove
  someone, or change settings.
- Keep aliases unique after `strip().casefold()` across all package-owned
  languages, not only Spanish.
- If doctor substring INFO count changes, review the exact Spanish prompt and
  alias pair. Accept expected INFO only when Q&A-first matching still protects
  the prompt and the alias target is related or clearly location-only.
- Update exact alias-count assertions instead of loosening them.
- Keep `docs/knowledge/language-lifecycle.md` semantics intact: package
  completeness is not runtime support.

## 3) Must-Run Verification

Baseline commands already run during this scan:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es
```

Observed current baseline:

- Spanish localization: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A
  answers, `1/27` alias entrypoints, `3` aliases.
- Doctor: `90 package-owned aliases`, `84 Q&A question prompts`, duplicate alias
  check OK, Q&A alias overlap OK, substring risk remains INFO at `11` prompts,
  `0 warnings`, `0 failed`.
- Runtime Spanish: `demo --language es` fails with `Unsupported presenter
  language: es`.
- Package-only Spanish doctor check: localization OK, runtime language support
  FAIL.

After adding Spanish aliases, run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py::test_localization_report_outputs_spanish_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --require-localization --localization-language es
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language es --dry-run
.\.venv\Scripts\ruff check --no-cache packages tests docs
git diff --check
```

Focused tests to add or update:

- A Spanish alias ownership/count test in `tests/unit/test_material_packages.py`
  that asserts the exact `questionAliases.es` entrypoint count and alias total.
- A Spanish package-owned routing test in `tests/unit/test_questions.py` with
  `_ENTRYPOINT_ALIASES` monkeypatched to `{}` so the YAML aliases, not the legacy
  table, are being tested.
- Spanish safety examples that remain Q&A-first or answer-only:
  notes/transcript action/content prompts, recording safety prompts, shared
  screen content prompts, participant/chat privacy prompts, and meeting-info
  value-reading prompts.
- A runtime boundary regression proving `--language es` is still rejected.
- Doctor expectation updates for exact package-owned alias count and any reviewed
  substring-risk count/details.

## 4) Reviewer Checklist

- Confirm the diff does not touch `src/ai_presenter/runtime/voice.py`,
  controller language choices, provider routing, voice assets, or runtime Spanish
  docs.
- Confirm `questionAliases.es` is the only package behavior being expanded unless
  a directly related test/doc assertion must change.
- Confirm each Spanish alias is a location/control synonym, not an execution,
  content-reading, copying, exporting, summarizing, or state-changing command.
- Confirm no exact normalized alias maps to more than one entrypoint.
- Confirm broad aliases such as `configuracion`, `menu`, `mas`, `audio`,
  `video`, `fondo`, `notas`, `transcripcion`, `grabacion`, `compartir`,
  `invitar`, `salir`, or `reunion` are either absent or justified by tests.
- Confirm Q&A-first behavior still wins for current Spanish localized Q&A prompts.
- Confirm any sensitive Spanish alias maps to an entrypoint whose `can_operate`
  and interrupt-step behavior are explicitly tested.
- Confirm doctor still has no warnings or failures in the ordinary profile/package
  run.
- Confirm the package-only doctor command still reports Spanish localization OK
  and runtime language support FAIL.
- Confirm `demo --language es --dry-run` remains unsupported.
- Confirm docs and test names do not describe Spanish as live-demo ready,
  runnable, voice-ready, or accepted.
- Confirm generated `.coverage` or other local artifacts are not included.

## 5) Out Of Scope / Do Not Touch

- Do not enable runtime `es` support.
- Do not add `es`, `es-es`, `es-mx`, `spanish`, or `espanol` to presenter
  language normalization.
- Do not add Spanish voice labels, voice provider routing, speech assets,
  controller/demo language options, or acceptance evidence.
- Do not alter Q&A precedence, alias substring matching semantics, legacy alias
  fallback behavior, or diagnostics severity to make aliases pass.
- Do not add or change open steps, selectors, cleanup behavior, operation types,
  route execution, manual controls, or `questionPolicy`.
- Do not expand Spanish Q&A content unless the cycle explicitly owns Q&A.
- Do not add aliases for Leave/End, Recording, Notes/Transcript action/content,
  Share execution/content inspection, Invite sending/copy-link behavior, or
  broad Settings as part of a low-risk alias batch.
- Do not weaken existing Chinese or Japanese alias assertions while updating
  Spanish counts.
- Do not commit from this risk-scan task.
