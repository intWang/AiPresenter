# Cycle 125 Technical Scan: Spanish Question Alias Coverage

Date: 2026-05-17

Scope: technical scan only. This document is the only intended file change. Do not enable runtime `--language es`, do not edit voice/runtime language choices, and do not submit a commit from this scan.

## Current Alias Structure

- Package-owned aliases live on each `operationEntrypoints[*].questionAliases` map in `packages/ringcentral-video.yaml`.
- `MaterialPackage` flattens them into `entrypoint_question_aliases` as `(entrypoint_id, language, alias, normalized_alias)`.
- Normalization is currently `strip().casefold()` only. It does not remove Spanish accents or punctuation, so aliases should include the natural accented form users are likely to type.
- Runtime matching order in `src/ai_presenter/runtime/questions.py` is:
  1. exact Q&A prompt match from `qa_questions_by_normalized`;
  2. special recording / notes safety Q&A heuristics;
  3. Q&A fragment / token matching;
  4. package-owned entrypoint alias substring match;
  5. legacy alias table;
  6. token match against entrypoint id/title/area/purpose.
- Package-owned aliases are sorted by descending normalized alias length. This helps longer phrases win, but it also means each alias is a substring trigger. Avoid short generic aliases such as `chat`, `notas`, `grabar`, `salir`, `audio`, `video`, `fondo`, `reunión`, or `participantes`.
- Diagnostics in `src/ai_presenter/runtime/diagnostics.py` protect three important surfaces:
  - `question aliases`: cross-entrypoint duplicate normalized aliases.
  - `qa alias overlap`: exact Q&A prompt equals an unrelated alias.
  - `qa alias substring risk`: Q&A prompt contains an unrelated alias in the same language. This is INFO because Q&A-first matching still applies, but new Spanish aliases should not add Spanish substring risks.
- Current Spanish state after commit `346fd0c`: `es` demo steps `51/51`, Q&A localized questions `12/12`, Q&A localized answers `12/12`, but `entrypoints_with_aliases=1/27` and `alias_total=3`. Runtime Spanish remains unsupported by design.

## Recommended Coverage

Original scan recommendation: add Spanish `questionAliases.es` for all 27 entrypoints, with conservative phrase aliases rather than single-word aliases.

Implementation resolution from the main session: the final Cycle 125 slice intentionally stops at `26/27` entrypoints and `69` Spanish aliases. `ringcentral.video.settings.background.blur` is left without a Spanish alias because that entrypoint performs the direct Blur selection action rather than only opening or explaining a location. This raises Spanish alias coverage from `1/27` to `26/27` and Spanish alias total from `3` to `69`, without enabling runtime Spanish.

The reason to cover all entrypoints rather than only Q&A-related controls is that the existing Spanish demo narration now covers the full meeting-control map, and users will naturally ask location/control questions in Spanish across that whole map. Safety-sensitive controls remain non-operable through existing `questionPolicy`, missing executable steps, or `_RISKY_ENTRYPOINT_WORDS`.

Recommended aliases:

| Entrypoint | Suggested `es` aliases |
| --- | --- |
| `ringcentral.develop.video.tab` | `pestaña de video en ringcentral`; `sección de video de ringcentral` |
| `ringcentral.develop.video.start` | `iniciar una reunión nueva`; `empezar reunión instantánea` |
| `ringcentral.video.overview` | `resumen de la ventana de reunión`; `mapa de controles de reunión` |
| `ringcentral.video.top.meeting-info` | `información de la reunión`; `detalles de la reunión`; `id de la reunión`; `enlace de la reunión` |
| `ringcentral.video.top.network-quality` | `calidad de red`; `calidad de conexión`; `diagnóstico de red de la reunión` |
| `ringcentral.video.top.views` | `menú de vista de reunión`; `cambiar diseño de vista`; `vista de galería` |
| `ringcentral.video.top.report-issue` | `reportar problema de la reunión`; `informe de problema técnico` |
| `ringcentral.video.main.add-coworkers` | `agregar compañeros desde la sala vacía`; `invitar compañeros desde el aviso inicial` |
| `ringcentral.video.toolbar.audio` | `control del micrófono`; `botón de micrófono`; `estado del micrófono` |
| `ringcentral.video.toolbar.audio-menu` | `menú de audio de la reunión`; `selección de micrófono y altavoz`; `configuración de micrófono y altavoz` |
| `ringcentral.video.toolbar.video` | `control de cámara`; `botón de cámara`; `estado de la cámara` |
| `ringcentral.video.toolbar.video-menu` | `menú de cámara`; `selección de cámara`; `configuración rápida de video` |
| `ringcentral.video.settings.video` | `configuración avanzada de video`; `ajustes de cámara y calidad` |
| `ringcentral.video.settings.background` | keep existing `configuración de fondo`; `fondo virtual`; `desenfocar fondo`; add `ajustes de fondo` |
| `ringcentral.video.settings.background.blur` | `opción blur de fondo`; `selección de desenfoque de fondo` |
| `ringcentral.video.toolbar.share` | `compartir pantalla`; `botón share de pantalla`; `entrada para compartir contenido` |
| `ringcentral.video.toolbar.invite` | `invitar participantes`; `agregar personas a la reunión`; `copiar invitación de la reunión` |
| `ringcentral.video.toolbar.participants` | `panel de participantes`; `lista de participantes`; `panel de controles de participantes` |
| `ringcentral.video.toolbar.chat` | `panel de chat de la reunión`; `mensajes de chat de la reunión`; `chat dentro de la reunión` |
| `ringcentral.video.toolbar.react` | `panel de reacciones`; `botón de reacciones`; `señales de reacción` |
| `ringcentral.video.toolbar.raise-hand` | `botón de levantar la mano`; `señal de levantar la mano`; `control de mano levantada` |
| `ringcentral.video.toolbar.more` | `menú de más acciones`; `más controles de reunión` |
| `ringcentral.video.more.recording` | `ubicación de start recording`; `controles de grabación de la reunión` |
| `ringcentral.video.more.notes` | `panel de notas y transcripción`; `controles de notas y transcripción`; `notes and transcript en la reunión` |
| `ringcentral.video.more.background` | `background desde más acciones`; `fondo desde el menú more` |
| `ringcentral.video.more.settings` | `configuración de la reunión`; `centro de ajustes de la reunión` |
| `ringcentral.video.toolbar.leave` | `botón para salir de la reunión`; `opciones para abandonar la reunión` |

Avoid these tempting aliases because they are short, broad, or safety-sensitive substring triggers: `chat`, `audio`, `video`, `cámara`, `micrófono`, `notas`, `transcripción`, `subtítulos`, `grabar`, `grabación`, `reacciones`, `levantar la mano`, `salir`, `invitar`, `compartir`, `fondo`, `configuración`, `más`.

Implementation note: the `ringcentral.video.settings.background.blur` row above was deferred in the final patch. It remains useful as a future candidate only if the project adds an explain-only route for Blur; the current entrypoint performs the selection action.

## Q&A Coverage Notes

The existing 12 Spanish localized Q&A prompts should stay. They are the first line of defense for safety and privacy questions. The alias update should be accompanied by tests that prove common Spanish variants still hit Q&A before aliases where needed.

Recommended Q&A-to-entrypoint coverage priorities:

| Q&A | Keep Q&A-first for | Alias support should route location/control variants to |
| --- | --- | --- |
| real background privacy | privacy/background setup | `settings.background`, `settings.background.blur` |
| shared-screen content | reading or describing private shared content | `toolbar.share` |
| bring people into meeting | invite flow and private invite links | `toolbar.invite`; optionally `main.add-coworkers` for empty-room callout wording |
| chat messages / participant names | reading private chat, names, roles, private tabs | `toolbar.chat`, `toolbar.participants` for location-only questions |
| host controls | host/moderator participant controls | `toolbar.participants` |
| reaction / raise hand safety | sending visible signals | `toolbar.react`, `toolbar.raise-hand` for location-only questions |
| audio and video readiness | state changes to real mic/camera | `toolbar.audio`, `toolbar.audio-menu`, `toolbar.video`, `toolbar.video-menu` |
| choppy audio/video | troubleshooting and escalation | `top.network-quality`, `top.report-issue` |
| notes and transcript controls | starting notes changes meeting state | `more.notes` |
| captions/transcription/translation | do not start/read/promise transcript content | `more.notes`, `more.settings` only for location/discovery |
| post-meeting artifacts | do not promise/read recordings/transcripts/summaries | keep Q&A answer-only; do not route to live `more.recording` unless wording is live-meeting control location |
| recording safety | consent/status/action safety | `more.recording` only for location/control questions |

Optional follow-up if Spanish users ask many paraphrases: add extra `localizedQuestions.es` variants for safety Q&As before broadening aliases. Good candidates are:

- `¿Puedes leer el chat o decir quién está en la reunión?`
- `¿Puedes resumir la transcripción de la reunión?`
- `¿Puedes iniciar la grabación?`
- `¿Dónde veo los subtítulos traducidos?`

This is safer than adding bare aliases like `chat`, `transcripción`, or `grabación`.

## Tests To Update Or Add

- Update `tests/unit/test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present` or add a new adjacent test for full Spanish package-owned aliases:
  - assert `build_localization_status(package, language="es").entrypoints_with_aliases == 26`;
  - assert `alias_total == 69`;
  - assert 26 entrypoints have non-empty `question_aliases["es"]`;
  - assert representative alias sets for high-risk controls: share, invite, chat, participants, notes, recording, raise hand, leave.
- Update `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package` expected count from `90 package-owned aliases` to `156 package-owned aliases`.
- Keep `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package` at `84 Q&A question prompts`.
- Keep `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` at `84 Q&A question prompts`.
- Keep `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package` expecting INFO, but the count should remain `11` with the alias set above. If it becomes `12+`, inspect for a new Spanish substring risk before accepting.
- Add a Spanish package-alias routing test in `tests/unit/test_questions.py`, mirroring the Chinese/Japanese package-owned alias tests and monkeypatching `_ENTRYPOINT_ALIASES` to `{}`:
  - `¿Dónde veo la calidad de red?` -> `ringcentral.video.top.network-quality`, `can_operate is True`;
  - `¿Dónde está el panel de chat de la reunión?` -> `ringcentral.video.toolbar.chat`, `can_operate is True`;
  - `¿Dónde está el panel de participantes?` -> Q&A #5 may match first by token route and return answer-only; if the intent is strict alias routing, use `Abrir panel de participantes` or assert the current Q&A-first behavior explicitly;
  - `¿Dónde están los controles de notas y transcripción?` -> Q&A #9 exact first, `ringcentral.video.more.notes`, `can_operate is False`;
  - `¿Dónde está el botón de levantar la mano?` -> `ringcentral.video.toolbar.raise-hand`, `can_operate is False`;
  - `¿Dónde está el botón para salir de la reunión?` -> `ringcentral.video.toolbar.leave`, `can_operate is False`.
- Add Q&A-first safety tests for Spanish paraphrases that contain new alias phrases:
  - `¿Puede leer los mensajes del chat o los nombres de participantes?` remains answer-only Q&A with `entrypoint_id is None`;
  - `¿Cómo reviso audio o video entrecortado?` remains Q&A and routes to `top.network-quality`;
  - `¿Cómo manejo la grabación de la reunión de forma segura?` remains Q&A and routes to `more.recording`, `can_operate is False`;
  - `¿Puede AiPresenter enviar una reacción o levantar la mano de forma segura?` remains answer-only Q&A with `entrypoint_id is None`.
- Do not add tests expecting `PresenterVoiceSettings(language="es")` to work. Continue using `PresenterVoiceSettings(language="en")` for Spanish prompt matching, or use current supported languages only.

## Verification Commands

Use the venv to avoid missing dependency drift from the system Python:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py::test_ringcentral_spanish_seed_qa_and_aliases_are_present
.\.venv\Scripts\python.exe -m pytest tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
.\.venv\Scripts\python.exe -m pytest tests/unit/test_questions.py -k "spanish or package_aliases"
.\.venv\Scripts\python.exe -m pytest tests/unit/test_material_packages.py tests/unit/test_diagnostics.py tests/unit/test_questions.py
.\.venv\Scripts\python.exe -m ai_presenter.cli localization-report --package ringcentral-video --language es
.\.venv\Scripts\python.exe -m ai_presenter.cli doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
```

Expected CLI shape after implementation:

- `localization-report --language es`: still exits `0`, demo `51/51`, Q&A `12/12`, aliases `26/27 entrypoints`, `69` aliases.
- `doctor ... --localization-language es`: still exits `1` because runtime language support remains `[FAIL]`; localization should remain `[OK] required es localization complete`.

## Implementation Notes

- Add aliases only under existing entrypoints in `packages/ringcentral-video.yaml`.
- Preserve existing Spanish background aliases and append `ajustes de fondo`.
- Do not move Q&A items; Q&A ordering is part of first-match behavior.
- If diagnostics report a Spanish `qa alias substring risk`, prefer lengthening or rephrasing the alias instead of accepting a new INFO.
- If a natural Spanish safety question misses Q&A and routes through an alias, add a localized Q&A prompt variant rather than shortening the alias.
