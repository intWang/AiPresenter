# Support Tone Design

Date: 2026-05-16

## Context

AiPresenter currently supports English and Chinese voice families with several tones. The existing tones cover presentation style, but RingCentral operator workflows also need a troubleshooting style for recovery and support moments.

Adding a new language is a larger localization and asset-readiness project. Adding a new tone is a small, provider-agnostic expansion.

## Design

Add a new canonical tone: `support`.

Metadata:

- Label: `Support`
- Aliases: `support`, `supportive`, `helpdesk`, `troubleshooting`, `recovery`, `calm`, `steady`, `reassuring`
- Description: calm, diagnostic, recovery-focused, and reassuring

Behavior:

- `render_voice_instruction()` uses the shared tone description.
- English dynamic presenter text starts with `Let's troubleshoot this.`
- Localized scripted narration remains unchanged unless tone is `concise`.
- Chinese SAPI support tone uses a practical calm rate.

## Non-Goals

- No new presenter language.
- No package localization.
- No provider routing change.
- No new voice assets.
- No live RingCentral acceptance.

