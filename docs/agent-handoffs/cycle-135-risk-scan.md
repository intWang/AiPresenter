# Cycle 135 Risk Scan: Spanish Entrypoint Copy And Count Drift

Date: 2026-05-16
Cycle: 135
Scope: risk/content scan only for expanding Spanish localized entrypoint display
copy beyond the current 2/27 pilot, or adding count drift tooling/docs examples.
This handoff is the only intended edit for this task. Do not edit source code,
tests, package YAML, existing durable docs, generated artifacts, staging, or
commits from this scan.

## Current Baseline

Current package/CLI signals from `packages/ringcentral-video.yaml`,
`localization-report --package ringcentral-video --language es --require-complete`,
and `entrypoints --package ringcentral-video --language es`:

- RingCentral Video has 27 operation entrypoints.
- Spanish required package localization remains complete for the current
  required contract: 51/51 demo steps, 12/12 Q&A questions, and 12/12 Q&A
  answers.
- `questionAliases.es` is present on 26/27 entrypoints with 69 aliases.
- Optional Spanish entrypoint display metadata is still partial:
  `localizedTitles.es` on 2/27 entrypoints and `localizedPurposes.es` on 2/27
  entrypoints.
- The two localized entrypoints are `ringcentral.video.overview` and
  `ringcentral.video.top.network-quality`.
- `localizedTitles` and `localizedPurposes` are display/inspection metadata.
  They do not affect matching candidates, alias ordering, Q&A precedence,
  safety gating, controller interrupts, provider routing, voice assets, or live
  RingCentral acceptance.

Durable docs already carry the main boundary: package-local Spanish is not the
same as local SAPI/Piper support or live RingCentral acceptance. Future edits
should keep that separation and avoid turning cycle counts into unsupported
readiness claims.

## Recommended Spanish Copy Candidates

Safest next candidates are explanatory routes that open a menu or settings
surface and have clear cleanup paths, while avoiding private content and
state-changing actions:

- `ringcentral.video.top.views`: good next candidate. It changes layout, not
  meeting membership or media state. Spanish copy can say it opens the Views
  menu to review Gallery view or Full screen. Avoid implying AiPresenter should
  change layout automatically.
- `ringcentral.video.toolbar.more`: good next candidate. It is an expansion
  point for less frequent tools. Spanish copy can describe it as a menu for
  additional meeting controls. Avoid naming risky child actions as if they are
  safe defaults.
- `ringcentral.video.more.settings`: good next candidate. It opens Settings and
  is useful as a general route. Spanish copy should say it opens Settings for
  audio, video, background, translation, join preferences, and general options,
  without claiming any setting is changed.
- `ringcentral.video.toolbar.video-menu`: acceptable low-risk candidate if the
  copy stays device-selection oriented. It may expose camera configuration, so
  say it opens the camera menu for device selection and video settings; do not
  imply toggling video.
- `ringcentral.video.toolbar.audio-menu`: acceptable with care. It opens
  microphone/speaker recovery controls, but also includes leave-computer-audio
  and phone-audio options. Spanish copy should frame it as reviewing or
  recovering devices, not switching audio routes by default.
- `ringcentral.video.more.background`: acceptable if framed as opening Settings
  on Background. Do not imply selecting Blur, uploading assets, or changing the
  user's appearance without explicit request.

Moderate-risk candidates can be added only with privacy clauses and focused
safety tests:

- `ringcentral.video.toolbar.chat`: copy must say the panel can be located or
  opened without reading private messages by default.
- `ringcentral.video.toolbar.participants`: copy must say it can show count and
  people controls without identifying names, roles, or private details by
  default.
- `ringcentral.video.top.meeting-info`: keep answer-only. Copy must emphasize
  private meeting IDs, links, dial-in details, host names, and encryption values.
- `ringcentral.video.more.notes`: keep answer-only. Copy must not imply starting
  notes, transcription, captions, translation, recording, or summary generation.

## No-Go Controls For Copy Expansion

Do not include these in a broad Spanish copy sweep unless a separate cycle owns
the safety design and tests:

- `ringcentral.develop.video.start`: starts an instant meeting.
- `ringcentral.video.toolbar.audio`: toggles live mute/unmute state.
- `ringcentral.video.toolbar.video`: toggles live camera state.
- `ringcentral.video.settings.background.blur`: selects a real background
  effect.
- `ringcentral.video.toolbar.share`: can expose screens/windows and must not
  click final Share during a tour.
- `ringcentral.video.toolbar.invite` and
  `ringcentral.video.main.add-coworkers`: expose invite links, names, emails,
  suggestions, and invite actions.
- `ringcentral.video.toolbar.react`: can send visible meeting signals.
- `ringcentral.video.toolbar.raise-hand`: toggles a visible meeting signal.
- `ringcentral.video.more.recording`: recording is state-changing and
  consent-sensitive.
- `ringcentral.video.toolbar.leave`: leave/end is destructive for the meeting
  session.
- `ringcentral.video.top.report-issue`: opens a blocking modal and should not
  pick issue categories during a feature tour.

For these controls, Spanish display copy is not forbidden forever, but it should
not be treated as low-risk content. The copy must be explanatory, bounded, and
covered by state/safety tests if authored.

## Spanish Copy Style Constraints

- Use neutral, Latin America-friendly Spanish.
- Preserve visible RingCentral UI labels when users must find the exact label:
  `More`, `Settings`, `Views`, `Chat`, `Participants`, `Network quality`,
  `Meeting information`, `Share`, `Invite`, `Notes and Transcript`.
- Prefer "abre", "muestra", "permite revisar", and "ayuda a confirmar" for
  capabilities.
- Avoid "corrige", "garantiza", "diagnostica la causa", "lee", "copia",
  "comparte", "graba", "invita", "silencia", "enciende", "termina", or any
  wording that implies AiPresenter performs a sensitive action by default.
- Keep localized purposes to one concise sentence when possible.
- Include explicit privacy/state boundaries for sensitive surfaces: "sin leer
  contenido privado por defecto", "sin identificar participantes por defecto",
  or "salvo que lo pidas explicitamente" as appropriate.
- Keep English diagnostic terms when they are product labels or observed labels;
  Spanish explanations can surround them. Existing copy uses "packet loss,
  jitter y latency" for `Network quality`.
- Do not use localized title/purpose text as a way to add new aliases, broaden
  fuzzy matching, or create new Spanish action intents.

## Count Drift Tooling And Docs Examples

Low-risk count drift work is read-only or test-only and should report current
package facts without changing package semantics:

- Add a docs example that tells maintainers to refresh counts with
  `localization-report`, `entrypoints --language`, and a package parse/count
  helper before editing durable count claims.
- Add a focused CLI or unit test that asserts optional Spanish display-copy
  counts stay separate from `required_localization_complete`.
- Add a small source-backed count helper only if it reads package models rather
  than grepping YAML text. It should distinguish required localization,
  aliases, optional entrypoint display metadata, and runtime voice support.
- Prefer generated current-count output in handoffs or reviewer commands over
  adding more hardcoded counts to README-style docs.

No-go controls for count drift work:

- Do not make `localizedTitles.es` or `localizedPurposes.es` part of
  `--require-complete` without a separate product decision.
- Do not use raw text grep as the authoritative count for nested YAML metadata
  if package model loading is available.
- Do not update only one count family when adjacent docs also mention entrypoint
  totals, alias totals, Q&A totals, demo step totals, or optional display-copy
  totals.
- Do not add docs examples that imply `entrypoints --language es` validates
  runtime Spanish speech, OpenAI availability, local voices, or live acceptance.
- Do not claim a count was verified unless the command/source and date are
  recorded.

## Must-Have Tests For Future Implementation

For Spanish display-copy expansion:

- Package/model tests load every newly authored `localizedTitles.es` and
  `localizedPurposes.es` value exactly.
- Localization status tests update optional title/purpose counts by exactly the
  number of newly seeded entrypoints while required demo/Q&A completeness stays
  unchanged.
- Answer-rendering tests prove Spanish answers use localized display copy when
  present and fall back to canonical title/purpose when absent.
- Matcher-boundary tests prove localized title/purpose text alone does not
  create a Spanish match or alter alias precedence.
- Q&A precedence tests prove authored Spanish Q&A safety answers still beat
  entrypoint fallback copy.
- Controller/interrupt tests prove answer-only entrypoints and non-operable
  risky prompts do not queue clicks.
- Sensitive-surface tests cover recording, notes/transcript, meeting
  information, invite/link, share, chat privacy, participant identity, reactions,
  raise hand, mic/camera toggles, report issue, and leave/end.
- Provider-boundary tests or existing verification prove Spanish runtime output
  remains OpenAI-backed only; local SAPI/Piper routes still reject Spanish.

For count drift tooling/docs examples:

- Tests build counts from loaded package models, not brittle YAML text.
- Tests keep optional entrypoint display-copy counts separate from required
  localization completeness.
- Tests include a partial-language fixture so a package can pass
  `--require-complete` while optional display-copy counts remain partial.
- CLI/doc examples include the source command and avoid runtime or live
  acceptance claims.

Suggested focused verification for an implementation owner:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe entrypoints --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe doctor --profile profiles/ringcentral-video-openai.example.yaml --package ringcentral-video --flow meeting-control-map-demo --language es --require-localization
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

Expected provider boundary: the OpenAI-backed route can pass Spanish runtime
checks, while local bind-speaker Spanish remains rejected before runtime with a
profile voice compatibility error.

## Claims To Avoid

Avoid these in PR text, durable docs, CLI output, tests, and handoffs:

- "Spanish is fully localized" without limiting the claim to required demo/Q&A
  localization.
- "All Spanish entrypoints are localized" while optional display copy is partial.
- "Spanish local speech works" or "SAPI/Piper supports Spanish."
- "Spanish package localization proves live RingCentral acceptance."
- "Unit tests prove a live RingCentral route."
- "Network quality diagnoses the cause."
- "Chat reads messages" or "Participants identifies who is in the room."
- "Meeting information exposes IDs or links."
- "Notes starts transcription/captions/translation" or "Notes records the
  meeting."
- "Invite sends invitations", "Share starts sharing", "React sends a reaction",
  "Raise hand raises the hand", or "Leave ends the meeting" unless the text is
  explicitly describing a confirmed user-requested action.

Safer wording:

- "Spanish required package localization is complete for demo narration and
  Q&A."
- "Spanish entrypoint display copy is partial and optional."
- "Localized entrypoint display copy is used for answer rendering and package
  inspection only."
- "Safety-sensitive entrypoints remain bounded by question policy, open-step
  eligibility, and Q&A-first safety answers."
- "Live RingCentral acceptance requires dated evidence in acceptance runs."

## Recommendation

Proceed with Spanish display-copy expansion only as a small authored wedge.
Start with `top.views`, `toolbar.more`, `more.settings`, and optionally
`video-menu`, `audio-menu`, or `more.background` if the copy stays
non-operational. Keep privacy and state-changing surfaces out of a broad sweep.

Proceed with count drift tooling/docs examples only if they preserve the
package-local/runtime/live-acceptance boundaries and make counts easier to
refresh from source-backed commands. Do not redefine Spanish completeness or
runtime readiness as part of count hygiene.
