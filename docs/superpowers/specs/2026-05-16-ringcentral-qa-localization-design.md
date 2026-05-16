# RingCentral Q&A Localization Design

Date: 2026-05-16

## Context

AiPresenter already supports English and Chinese voice settings, expanded tones, package-owned `questionAliases`, and localized Q&A fields. The RingCentralVideo package only uses a small part of that surface today:

- 3 Q&A entries total.
- Only the background privacy Q&A has Chinese localized questions and answer.
- Many Chinese control questions still depend on the legacy Python alias fallback.

Cycle 022 improves live controller usefulness by expanding package-authored Q&A and aliases without changing runtime matching, package schema, route safety, provider behavior, or controller UI.

## Chosen Slice

Make a package-content-only expansion:

- Localize the existing shared-screen and invite Q&A entries.
- Add four new Q&A entries for high-value operator questions:
  - chat/participants privacy;
  - audio/video readiness;
  - network quality troubleshooting;
  - notes/transcript versus recording safety.
- Add package-owned Chinese aliases for selected P0/P1 routes so questions can match without the legacy `_ENTRYPOINT_ALIASES` table.

Do not add localized narration for entire demo flows in this cycle. That is useful but larger, and it belongs in a follow-up content pass.

## Content Rules

- Use existing YAML fields only: `questionAliases`, `localizedQuestions`, `localizedAnswers`, and `relatedEntrypointIds`.
- Keep English answers factual so existing tone wrappers can safely add friendly, coach, formal, conversational, or concise style.
- Chinese localized Q&A answers should sound natural as standalone spoken copy because localized answers currently bypass tone wrappers.
- Do not claim live acceptance. Current RingCentral Video routes remain repo-tested/observed/planned unless acceptance docs say otherwise.
- Keep privacy boundaries explicit for chat, participants, shared screen, notes, recording, invite links, and meeting details.
- Do not make risky routes executable. Invite, Share, Recording, and Leave/End must remain non-operable where they are today.

## Target Q&A

Existing Q&A to localize:

- `Can the presenter describe shared-screen content?`
- `How can I bring people into the meeting?`

New Q&A:

- `Can the presenter read chat or participant names?`
  - Related entrypoints: `ringcentral.video.toolbar.chat`, `ringcentral.video.toolbar.participants`
  - Answer boundary: explain panels/counts; do not read chat text, names, roles, or private tabs unless explicitly requested and verified.
- `How do I make sure my audio and camera are ready?`
  - Related entrypoints: `ringcentral.video.toolbar.audio`, `ringcentral.video.toolbar.audio-menu`, `ringcentral.video.toolbar.video`, `ringcentral.video.toolbar.video-menu`
  - Answer boundary: inspect state first; use menus for device recovery; do not toggle real media without intent.
- `How do I troubleshoot choppy audio or video?`
  - Related entrypoints: `ringcentral.video.top.network-quality`, `ringcentral.video.top.report-issue`
  - Answer boundary: use Network quality for packet loss/jitter/latency context; Report issue is escalation; do not overdiagnose without observed values.
- `Where are notes, transcripts, and recording controls?`
  - Related entrypoints: `ringcentral.video.more.notes`, `ringcentral.video.more.recording`
  - Answer boundary: Notes opens notes/transcript panel; recording changes meeting state and needs confirmation/consent.

## Alias Targets

Add package-owned `questionAliases.zh` where missing for:

- `ringcentral.video.main.add-coworkers`
- `ringcentral.video.toolbar.participants`
- `ringcentral.video.toolbar.audio`
- `ringcentral.video.toolbar.audio-menu`
- `ringcentral.video.toolbar.video`
- `ringcentral.video.toolbar.video-menu`
- `ringcentral.video.top.network-quality`
- `ringcentral.video.top.meeting-info`
- `ringcentral.video.more.notes`
- `ringcentral.video.more.recording`

Keep existing aliases for background, share, invite, chat, and leave.

## Non-Goals

- No runtime matching changes.
- No schema changes for tone-specific localized copy.
- No new languages beyond English and Chinese.
- No controller, CLI, provider, voice readiness, or TTS asset changes.
- No live RingCentral interaction or evidence promotion.
- No demo-flow-wide localized narration in this cycle.
- No removal of the legacy alias table.

## Acceptance Criteria

- `packages/ringcentral-video.yaml` still loads with the current schema.
- Every `qa` item has nonblank `localizedQuestions.zh` and `localizedAnswers.zh`.
- Added Q&A entries have valid `relatedEntrypointIds`.
- Representative Chinese Q&A questions return Chinese answers and expected entrypoint ids.
- Package-owned aliases cover the selected P0/P1 routes and are exposed through `package.entrypoint_question_aliases`.
- With `_ENTRYPOINT_ALIASES` monkeypatched to `{}`, representative Chinese route questions still match package aliases.
- Invite, Share, Recording, and Leave remain non-operable.
- Existing mojibake rejection and package-owned alias precedence tests continue to pass.

## Risks

- Short Chinese aliases can collide. Prefer route-specific multi-character aliases where possible.
- Chinese localized answers bypass tone wrappers. This cycle documents and accepts that behavior instead of changing runtime.
- Content can sound like permission to read private data. Sensitive answers must state consent and verification boundaries.
- Editing YAML with non-ASCII content must preserve UTF-8 and avoid terminal mojibake.
