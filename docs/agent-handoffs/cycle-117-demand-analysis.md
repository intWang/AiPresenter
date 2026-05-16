# Cycle 117 Demand Analysis: Spanish Report-Only RingCentral Video Q&A

Date: 2026-05-16
Scope: demand analysis only. This file is the only file edited by this handoff.

## Product Demand

Cycle 116 landed the executive-style tone alias slice, not Spanish package coverage. After that work, the Spanish RingCentral Video state is still intentionally partial:

- `localization-report --package ringcentral-video --language es`: `0/51` demo narration steps, `1/12` Q&A questions, `1/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3` aliases.
- `localization-report --package ringcentral-video --language es --require-complete`: exits `1` with `Localization coverage incomplete for es.`
- `voices`: runtime languages remain English, Chinese, and Japanese only. Cycle 116 added `executive`, `briefing`, and `boardroom` as aliases for the existing `formal` tone.
- `demo --language es --dry-run`: still rejects Spanish with `Unsupported presenter language: es`.

The next best Cycle 117 slice is to finish Spanish Q&A coverage for RingCentral Video while keeping Spanish report-only. This converts Spanish from a single background/privacy seed into a useful support and safety answer layer without implying spoken Spanish runtime support or Spanish demo readiness.

## Recommended Scope

Complete Spanish `localizedQuestions.es` and `localizedAnswers.es` for the remaining 11 Q&A items in `packages/ringcentral-video.yaml`. Preserve the existing Spanish background/privacy Q&A and the existing three background aliases.

Keep current RingCentral UI labels in English when they refer to the product surface: `Chat`, `Participants`, `Share`, `Invite`, `Add coworkers`, `Notes`, `Notes and Transcript`, `Settings`, `Background`, `Blur`, `Network quality`, `Report issue`, `Reactions`, and `Raise hand`.

Do not translate the 51 demo narration steps. Do not add Spanish runtime voice support. Do not broaden Spanish entrypoint aliases unless a focused routing test proves a specific high-signal alias is needed.

## Exact Spanish Q&A Set

Add Spanish coverage for these missing items:

| # | English Q&A | Spanish prompt scope | Spanish answer boundary |
| --- | --- | --- | --- |
| 2 | Can the presenter describe shared-screen content? | Ask whether AiPresenter can describe or read shared-screen content. | Only after an approved observation source captures it and the user explicitly allows it; otherwise explain `Share` without inferring or reading private content. |
| 3 | How can I bring people into the meeting? | Ask how to invite people, add coworkers, or copy the meeting invite. | Point to `Invite` and, in empty-room state, `Add coworkers`; do not read private links, emails, names, or suggestions unless explicitly requested and verified. |
| 4 | Can the presenter read meeting messages or participant names? | Ask whether chat content, participant names, roles, or private tabs can be read. | Explain where `Chat` and `Participants` are and summarize verified counts only; do not read private content by default. |
| 5 | Where are host controls for participants? | Ask where host or moderator participant controls live. | Use `Participants` as the discovery panel; do not mute, remove, lock, change security, or read names/roles unless explicitly requested and verified. |
| 6 | Can AiPresenter send a reaction or raise my hand safely? | Ask whether AiPresenter can send a reaction, thumbs up, or raise/lower a hand. | Explain that these are visible meeting signals; do not send or leave a signal active without explicit confirmation, and lower hand after a confirmed demo. |
| 7 | How do I make sure my audio and video are ready? | Ask how to check microphone, speaker, camera, audio, or video readiness. | Check current media state and use audio/video menus for recovery; do not toggle real meeting media unless the user intends the state change. |
| 8 | How do I troubleshoot choppy audio or video? | Ask about unstable audio/video, lag, packet loss, jitter, latency, or connection quality. | Use `Network quality` for diagnostics and `Report issue` only as escalation; do not guess exact causes without observed values. |
| 9 | Where are notes and transcript controls? | Ask where notes, meeting notes, transcript, or transcription controls are. | Point to `Notes`; starting notes can change meeting state, so keep it explain-only unless explicitly requested and allowed. |
| 10 | Where are captions, live transcription, and translation controls? | Ask about captions, live transcription, translated captions, or translation settings. | Use `Notes and Transcript` and `Settings` when available; do not start notes, transcription, captions, translation, read content, or promise summaries by default. |
| 11 | Where can I find post-meeting recordings, transcripts, summaries, or insights? | Ask where post-meeting recordings, transcripts, summaries, or insights are, or whether AiPresenter can read/summarize them. | Explain artifacts may exist only after generation, enablement, and permission; do not claim existence, open/read content, or summarize unless explicitly requested and verified. |
| 12 | How do I handle meeting recording safely? | Ask how to record, where recording is, or whether AiPresenter can start recording. | Recording affects everyone; keep it explain-only until explicit confirmation, allowed role, and participant consent are clear. |

Suggested Spanish phrasing can be concise and support-oriented. For example:

- `Can the presenter describe shared-screen content?`
  - Questions: `¿Puede AiPresenter describir el contenido compartido en pantalla?`; `¿Puedes leer lo que se está compartiendo?`
  - Answer: `Solo si el contenido fue capturado por una fuente de observación aprobada y el usuario lo permite explícitamente. De forma predeterminada, AiPresenter no infiere ni lee contenido privado compartido; puede explicar de forma segura dónde está Share.`
- `How can I bring people into the meeting?`
  - Questions: `¿Cómo invito a otras personas a la reunión?`; `¿Cómo agrego compañeros o copio la invitación?`
  - Answer: `Usa Invite para agregar compañeros o copiar los detalles de la reunión. Si la sala está vacía, Add coworkers puede abrir el mismo flujo de invitación. No leas enlaces privados, correos, nombres ni sugerencias salvo que el usuario lo pida explícitamente y el contenido esté verificado.`
- `Can the presenter read meeting messages or participant names?`
  - Questions: `¿Puede AiPresenter leer mensajes del chat o nombres de participantes?`; `¿Puedes decir quién está en la reunión?`
  - Answer: `AiPresenter puede explicar dónde están Chat y Participants y resumir conteos visibles cuando estén verificados. No debe leer mensajes, nombres, roles ni pestañas privadas salvo que el usuario lo pida explícitamente y el contenido esté verificado.`
- `Where are host controls for participants?`
  - Questions: `¿Dónde están los controles de anfitrión para participantes?`; `¿Cómo administra participantes el anfitrión?`
  - Answer: `Usa el panel Participants para ubicar el conteo de asistentes, búsqueda, invitación y áreas de control para anfitrión o moderador. No silencies a otras personas, no elimines participantes, no bloquees la reunión, no cambies seguridad ni leas nombres o roles salvo que el usuario lo pida explícitamente y el contexto visible esté verificado.`
- `Can AiPresenter send a reaction or raise my hand safely?`
  - Questions: `¿Puede AiPresenter enviar una reacción o levantar la mano por mí?`; `¿Cómo uso Reactions y Raise hand de forma segura?`
  - Answer: `Reactions y Raise hand son señales visibles en la reunión. AiPresenter puede explicar dónde están, pero no debe enviar una reacción, levantar la mano ni dejarla levantada salvo que el usuario lo pida explícitamente. Si solo se está explorando, cierra la tira de reacciones sin enviar nada; después de una demostración confirmada, baja la mano.`
- `How do I make sure my audio and video are ready?`
  - Questions: `¿Cómo verifico que mi audio y video estén listos?`; `¿Cómo reviso el micrófono, altavoz o cámara?`
  - Answer: `Primero revisa el estado del micrófono y la cámara. Luego usa el menú de audio o video para recuperar dispositivos o cambiar la selección. No alternes el audio o video real de la reunión salvo que el usuario quiera cambiar ese estado.`
- `How do I troubleshoot choppy audio or video?`
  - Questions: `¿Cómo soluciono audio o video entrecortado?`; `¿Dónde veo la calidad de red de la reunión?`
  - Answer: `Abre Network quality para revisar pérdida de paquetes, jitter, latencia u otros diagnósticos de la reunión. Usa Report issue solo como ruta de escalamiento y evita adivinar causas exactas sin valores observados.`
- `Where are notes and transcript controls?`
  - Questions: `¿Dónde están las notas y la transcripción?`; `¿Dónde abro Notes and Transcript?`
  - Answer: `Notes abre el panel de notas y transcripción. Iniciar notas puede cambiar el estado de la reunión, así que úsalo solo cuando el usuario lo pida y el contexto de la reunión lo permita.`
- `Where are captions, live transcription, and translation controls?`
  - Questions: `¿Dónde están los subtítulos o la transcripción en vivo?`; `¿Cómo encuentro la traducción de subtítulos?`
  - Answer: `Usa Notes and Transcript como la superficie conocida para controles relacionados con transcripción, y Settings para preferencias de Translation cuando estén disponibles. No inicies notas, transcripción, subtítulos ni traducción; no leas subtítulos o transcripciones ni prometas resúmenes posteriores salvo que el usuario lo pida explícitamente y el contexto visible esté verificado.`
- `Where can I find post-meeting recordings, transcripts, summaries, or insights?`
  - Questions: `¿Dónde encuentro grabaciones, transcripciones, resúmenes o insights después de la reunión?`; `¿Puede AiPresenter resumir la reunión después de que termine?`
  - Answer: `Los artefactos posteriores a la reunión de RingCentral, como grabaciones, transcripciones, resúmenes e insights, pueden estar disponibles solo después de generarse, estar habilitados y ser visibles para un usuario con permiso. AiPresenter puede explicar dónde revisar, pero no debe afirmar que existen, abrirlos, leerlos ni resumirlos salvo que el usuario lo pida explícitamente y el contexto visible esté verificado.`
- `How do I handle meeting recording safely?`
  - Questions: `¿Cómo grabo la reunión de forma segura?`; `¿Puede AiPresenter iniciar la grabación?`
  - Answer: `La grabación cambia el estado de la reunión y puede afectar a todas las personas presentes. Trátala como solo explicación hasta que el usuario confirme explícitamente, el rol actual lo permita y el consentimiento de participantes esté claro.`

## Acceptance Criteria

A Cycle 117 implementation satisfies this demand when:

- `localization-report --package ringcentral-video --language es` reports `0/51` demo narration steps, `12/12` Q&A questions, `12/12` Q&A answers, and no broad Spanish entrypoint alias expansion beyond any explicitly tested additions.
- `localization-report --package ringcentral-video --language es --require-complete` still fails because Spanish demo narration remains intentionally incomplete.
- `localization-report --package ringcentral-video --language zh --require-complete` and `--language ja --require-complete` still pass.
- `ai-presenter voices` still lists only English, Chinese, and Japanese as runtime languages.
- `demo --language es --dry-run` and direct `PresenterVoiceSettings(language="es")` validation still reject Spanish with `Unsupported presenter language: es`.
- Spanish prompts for shared-screen content, invite links, chat messages, participant names, host controls, reactions, raise hand, audio/video readiness, network quality, notes/transcripts, captions/translation, post-meeting artifacts, and recording route to safe Q&A behavior.
- Sensitive Spanish prompts remain non-operable and do not create a question interrupt step for answer-only Q&A.
- The package keeps UI labels in English where they name RingCentral controls.
- Doctor diagnostics still pass; any changed Q&A prompt or alias count is deliberate, tested, and documented by the implementation handoff.
- No runtime language choices, provider routing, profiles, voice assets, controller options, `questionPolicy`, open steps, locators, production route policy, or live RingCentral acceptance claims change.

## Non-Goals

- Do not add Spanish runtime presenter support.
- Do not add Spanish to `PresenterLanguage`, CLI choices, controller choices, `voices`, provider validation, SAPI/Piper/OpenAI voice routes, or voice asset checks.
- Do not translate demo narration into Spanish in this cycle.
- Do not add Spanish live acceptance claims or require live RingCentral testing.
- Do not add new RingCentral Video entrypoints, locators, flows, state extraction, or official-source docs.
- Do not add broad Spanish `questionAliases.es` coverage across entrypoints unless a specific routing test requires it.
- Do not change canonical tones, tone aliases, tone behavior, route authorization, `can_operate`, Q&A-first matching, or interrupt-step creation.
- Do not edit production code, tests, profiles, packages, `.coverage`, README, Codex home files, or git history as part of this demand-analysis handoff.

## Implementation Guidance

The future implementation should be package-local and test-local only:

- Preferred package edit: `packages/ringcentral-video.yaml`.
- Preferred tests: `tests/unit/test_material_packages.py`, `tests/unit/test_cli.py`, and `tests/unit/test_questions.py`.
- Keep Spanish Q&A phrasing natural for training/support, but semantically aligned with existing English, Chinese, and Japanese safety boundaries.
- Prefer Q&A prompt coverage over entrypoint aliases. Aliases can make Spanish prompts feel operable too early if they include action verbs such as record, read, invite, share, or leave.
- Treat report-only Spanish as a data layer: useful for localization reports and routing tests, not a runtime speech promise.

## Lightweight Validation For This Handoff

Read-only checks run during this demand analysis:

```powershell
git status --short
Test-Path docs\agent-handoffs\cycle-117-demand-analysis.md
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe voices
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
```

Observed results before creating this file:

- `Test-Path docs\agent-handoffs\cycle-117-demand-analysis.md` returned `False`.
- Spanish report output is still `0/51` demo steps, `1/12` Q&A questions, `1/12` Q&A answers, and `questionAliases.es` on `1/27` entrypoints with `3` aliases.
- Spanish `--require-complete` exits `1` with `Localization coverage incomplete for es.`
- `voices` lists English, Chinese, and Japanese only; `formal` aliases include the Cycle 116 additions `executive`, `briefing`, and `boardroom`.
- `demo --language es --dry-run` exits `1` with `Unsupported presenter language: es`.
- `.coverage` is modified and out of scope.

Post-write validation to run:

```powershell
rg -n "[ \t]$" docs\agent-handoffs\cycle-117-demand-analysis.md
rg -n "TB[D]|TO[D]O|fill in detail[s]" docs\agent-handoffs\cycle-117-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-117-demand-analysis.md
git ls-files --others --exclude-standard docs\agent-handoffs\cycle-117-demand-analysis.md
git status --short --untracked-files=all
```

Observed post-write results:

- The trailing-whitespace scan found no matches.
- The placeholder scan found no matches.
- `git diff --check -- docs\agent-handoffs\cycle-117-demand-analysis.md` passed.
- `git ls-files --others --exclude-standard docs\agent-handoffs\cycle-117-demand-analysis.md` listed this handoff as an untracked new file.
- `git status --short --untracked-files=all` showed this handoff plus out-of-scope concurrent changes: `.coverage`, `packages/ringcentral-video.yaml`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, `tests/unit/test_material_packages.py`, `tests/unit/test_questions.py`, and `docs/agent-handoffs/cycle-117-risk-scan.md`. Those files were not edited by this demand-analysis subagent.
