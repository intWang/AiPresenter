# Cycle 132 Risk Scan: Spanish Entrypoint Pilot

Date: 2026-05-16
Cycle: 132
Scope: risk scan only for seeding Spanish `localizedTitles` /
`localizedPurposes` into RingCentral package content, adding safety tests, or
adding CLI localized entrypoint inspection. This file is the only intended edit
for this task. Do not edit source code, tests, package YAML, profiles, generated
artifacts, staging, or commits from this scan.

## Executive Boundary

Cycle132 should stay a tiny content pilot. The goal is not full Spanish product
localization, not live RingCentral acceptance, and not new runtime language
support. A safe pilot can improve Spanish answer copy for a few entrypoints
without changing matching, routing, `questionPolicy`, `openSteps`, or controller
behavior.

The safest implementation shape is:

- add optional Spanish `localizedTitles` / `localizedPurposes` only where the
  model already supports them, or add the model migration first if it does not;
- use those fields for answer/inspection display only;
- keep localized copy out of matcher inputs unless a separate diagnostics cycle
  covers alias overlap, risky words, and Q&A-first safety routing;
- prefer two or three low-risk entrypoints rather than sweeping the RingCentral
  package.

## Current Package Signals

Observed candidate entrypoints in `packages/ringcentral-video.yaml`:

- `ringcentral.video.top.network-quality`: opens a diagnostic popover for
  sharing, video, and audio quality, including packet loss, jitter, and latency.
  It has no `questionPolicy: answerOnly`; presenter notes say to use it for call
  health/troubleshooting and close it with Escape.
- `ringcentral.video.toolbar.chat`: opens the in-meeting chat side panel. Notes
  explicitly say not to read private chat text aloud unless the user asks.
- `ringcentral.video.toolbar.participants`: opens the participant list and
  people controls. Notes explicitly say not to identify participants unless UI
  text is verified and allowed.
- `ringcentral.video.top.meeting-info`: `questionPolicy: answerOnly`; opens a
  popover containing meeting title, host, meeting ID, copy link, dial-in info,
  encryption, and end-to-end encryption option. Notes call out private meeting
  identifiers and copy-link controls.
- `ringcentral.video.more.notes`: `questionPolicy: answerOnly`; opens Notes and
  Transcript through More. Notes call out Start notes and Also record this
  meeting, and say default tours should only explain the panel.

## Pilot Recommendation

Recommended tiny pilot:

- `ringcentral.video.top.network-quality`: safest first entrypoint. Spanish copy
  can explain the diagnostic panel without exposing personal data or changing
  meeting state. Keep copy careful: "permite revisar" rather than "soluciona".
- `ringcentral.video.toolbar.chat`: acceptable only if the Spanish purpose
  includes the privacy boundary. It may open a private-content surface, so pilot
  copy must say the assistant does not read chat content unless explicitly asked.
- `ringcentral.video.toolbar.participants`: acceptable only if the Spanish
  purpose includes the identity boundary. It can mention attendee count and
  participant controls, but must not imply reading names, roles, or identities by
  default.

Keep answer-only or safety-sensitive for this pilot:

- `ringcentral.video.top.meeting-info`: keep `answerOnly` and do not make it a
  pilot opener. Spanish copy can be authored later, but it must emphasize that
  meeting IDs, links, dial-in details, host names, and encryption values are
  private unless explicitly requested.
- `ringcentral.video.more.notes`: keep `answerOnly` and do not use as a tiny
  pilot opener. Notes/transcript touches recording-adjacent and transcript
  surfaces; copy must not imply starting notes, recording, transcription, or
  reading transcript content.
- Any recording, invite/link, leave, mute/unmute, camera toggle, share, report,
  or participant-management entrypoint should stay out of the pilot unless it
  already has focused Spanish safety tests.

If the cycle wants the smallest possible content diff, pilot only
`top.network-quality`. If it needs three examples to prove fallback behavior,
use `top.network-quality`, `toolbar.chat`, and `toolbar.participants`, with
privacy wording required for the latter two.

## Spanish Glossary And Style

Use neutral, Latin America-friendly Spanish with product UI labels preserved
when they are visible RingCentral labels.

- Preserve UI labels: `Network quality`, `Chat`, `Participants`, `Meeting
  information`, `Notes and Transcript`, `More`, `Share`, `Meeting ID`.
- Prefer natural Spanish around labels: "panel de Chat", "lista de
  Participants", "panel Network quality".
- Use "reunión" for meeting, "panel" for panel, "barra superior" for top bar,
  "barra de herramientas" for toolbar, "controles" for controls, "enlace" for
  link, "cifrado" for encryption, "transcripción" for transcript.
- For network metrics, either preserve product/diagnostic labels or pair them
  with Spanish: "packet loss, jitter y latency" is consistent with existing
  narration; "pérdida de paquetes, jitter y latencia" is also acceptable if the
  UI does not display the English labels.
- Use "permite revisar", "ayuda a confirmar", and "muestra" for capabilities.
  Avoid stronger claims like "corrige", "garantiza", or "detecta la causa".
- Use explicit privacy clauses where needed: "sin leer contenido privado por
  defecto", "salvo que lo pidas explícitamente", and "sin identificar
  participantes por defecto".
- Keep copy concise. Localized purposes should be one sentence where possible,
  and should not become mini runbooks.

Suggested pilot copy style:

- Network quality title: "Calidad de red"
- Network quality purpose: "Abre Network quality para revisar packet loss,
  jitter y latency de Share, video y audio cuando la reunión se siente
  inestable."
- Chat title: "Panel de Chat"
- Chat purpose: "Abre Chat como canal escrito de la reunión, manteniendo el
  contenido privado salvo que pidas leerlo explícitamente."
- Participants title: "Panel de Participants"
- Participants purpose: "Abre la lista de participantes y controles de personas
  sin identificar nombres ni detalles privados por defecto."

## No-Go Conditions

Do not accept Cycle132 work if any of these are true:

- Package YAML uses `localizedTitles` or `localizedPurposes` before strict model
  support exists for those exact keys.
- The implementation weakens strict package validation to permit unknown keys.
- Localized titles or purposes participate in matching, routing, alias
  expansion, route ordering, or risky-entrypoint detection without a dedicated
  matcher diagnostics update.
- `questionPolicy: answerOnly` changes for Meeting information, Notes and
  Transcript, recording, invite/link, leave, or any other safety-sensitive
  entrypoint.
- Any `openSteps`, cleanup behavior, target coordinates, menu routes, or side
  panel behavior changes as part of this content pilot.
- Chat copy implies AiPresenter may read messages by default.
- Participants copy implies AiPresenter may identify attendees by default.
- Meeting information copy reads or promises access to Meeting ID, links,
  dial-in details, host names, or encryption values by default.
- Notes copy implies starting notes, recording, transcription, summarization, or
  reading transcript content.
- Spanish copy is used to claim full Spanish localization, local Spanish speech
  support, production readiness, or live RingCentral acceptance.
- Tests require real OpenAI credentials, network access, audio devices, or a
  live RingCentral window.
- Unrelated worktree changes, including `.coverage`, are staged or committed.

## Must-Have Tests

Require focused tests before accepting a code/content implementation:

- Model/schema load: the RingCentral package loads with optional Spanish
  `localizedTitles` and `localizedPurposes`; packages without those fields still
  load.
- Strict validation: unknown neighboring keys still fail so the schema migration
  does not become permissive.
- Spanish answer rendering: Spanish fallback answers use localized title and
  purpose when present, preserving expected UI labels.
- Partial fallback: missing Spanish title or purpose has an intentional fallback
  that is tested and does not claim complete localization.
- Q&A precedence: authored `localizedAnswers.es` still wins over entrypoint
  fallback copy.
- Safety preservation: answer-only entrypoints remain `can_operate=False` and do
  not create controller interrupt steps.
- Privacy wording: Spanish answers for Chat and Participants include the
  "explicit request / no private reading by default" boundary if those
  entrypoints are in the pilot.
- Matcher boundary: adding localized display copy does not change alias
  precedence, route ordering, accent folding, or Q&A-first routing.
- CLI inspection: if a localized entrypoint inspection command is added, it must
  show the selected language, fallback source, entrypoint id, `questionPolicy`,
  and whether `openSteps` exist, without implying the entrypoint is safe to
  operate.
- Localization reports: existing Spanish package localization counts should not
  be silently redefined. If entrypoint title/purpose coverage becomes required,
  report it as a separate count with explicit expectations.
- Provider boundary: Spanish remains OpenAI-backed only unless a separate cycle
  changes speech provider support.

Suggested verification shape:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
git diff --check
git status --short
```

Expected results should mention no live acceptance and should not require a live
RingCentral session.

## Claims To Avoid

Avoid these claims in PR text, docs, CLI output, tests, and handoffs:

- "Spanish is fully localized."
- "RingCentral Spanish support is production ready."
- "Spanish works locally."
- "SAPI/Piper supports Spanish."
- "Network quality diagnoses the cause."
- "Chat can read messages."
- "Participants identifies who is in the room."
- "Meeting information exposes the meeting ID/link."
- "Notes starts transcription" or "Notes records the meeting."
- "Unit tests prove live RingCentral acceptance."

Safer wording:

- "Spanish entrypoint answer copy is available for a small pilot set."
- "Localized display copy is used for answer rendering/inspection only."
- "Safety-sensitive entrypoints remain answer-only."
- "Live RingCentral acceptance remains unproven by this change."

## Recommendation

Proceed only with a tiny display-copy pilot. Use `top.network-quality` first,
then optionally `toolbar.chat` and `toolbar.participants` if their privacy
boundaries are included in the Spanish purpose text and covered by tests. Keep
`top.meeting-info` and `more.notes` answer-only/safety-sensitive, and do not let
localized display fields affect matching or operation routing in this cycle.
