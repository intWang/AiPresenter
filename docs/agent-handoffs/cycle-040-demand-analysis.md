# Cycle 040 Demand Analysis: Support Tone

Date: 2026-05-16
Role: demand discovery
Scope: read-only demand analysis. No implementation changes were made by the demand agent.

## Recommended Slice

Add one new canonical presenter tone: `support`.

Language expansion is larger and riskier because new language families require provider routing, package localization, Q&A localization, and asset readiness. A tone expansion gives operators immediate value while staying centralized in existing voice metadata.

## User Value

`support` is for live troubleshooting and recovery-oriented moments: audio device confusion, camera not starting, network quality, settings recovery, and privacy-safe RingCentral assistance.

It gives operators a more purpose-built voice than generic friendly/formal styles without changing demo flow semantics or requiring new TTS assets.

## Product Contract

- Canonical tone: `support`
- Label: `Support`
- Aliases: `support`, `supportive`, `helpdesk`, `troubleshooting`, `recovery`, `calm`, `steady`, `reassuring`
- Description: calm, diagnostic, recovery-focused, and reassuring
- English dynamic text uses a short troubleshooting prefix.
- Localized scripted narration remains unchanged except existing `concise` truncation.
- Chinese local SAPI rate can stay practical and slightly calmer.

## Acceptance Criteria

- `PresenterVoiceSettings(tone="support").tone == "support"`
- `calm`, `steady`, and `reassuring` normalize to `support`.
- `ai-presenter voices` lists `Support aliases:`.
- Controller voice labels can render `English / Support`.
- `render_voice_instruction()` includes support/recovery language.
- `render_presenter_text()` applies the support prefix.
- Existing language behavior and current tones remain unchanged.

## Out Of Scope

- No new presenter language family.
- No provider, SAPI, Piper, or OpenAI asset changes.
- No package YAML localization changes.
- No live RingCentral automation.

