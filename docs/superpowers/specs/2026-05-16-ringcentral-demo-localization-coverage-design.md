# RingCentral Demo Localization Coverage Design

Date: 2026-05-16
Cycle: 025

## Goal

Close the last RingCentralVideo Chinese demo narration gap and add a reusable guard so future RingCentral demo flows cannot silently ship without Chinese narration.

## Current State

- `vbg-blur-demo`: 4/4 steps localized.
- `meeting-basics-demo`: 3/3 steps localized.
- `meeting-control-map-demo`: 22/22 steps localized.
- `meeting-controls-tour`: 0/22 steps localized.
- Q&A: 8/8 items localized.
- Package-owned Chinese aliases: 49 records across 15/27 entrypoints.

## Scope

In scope:

- Add `narration.localizedText.zh` to all 22 existing `meeting-controls-tour` steps.
- Add one all-flow Chinese narration coverage guard for RingCentral demo flows.
- Add one render assertion for a newly localized long-tour step.

Out of scope:

- Runtime, schema, CLI, controller, provider, route, and open-step changes.
- New languages beyond current `zh`.
- Renaming, removing, retiring, or aliasing `meeting-controls-tour`.
- Live RingCentralVideo acceptance.

## Design

Use the existing `localizedText.zh` field under each demo step's narration. Keep existing English `narration.text` as ASCII source text, and preserve flow ids, step ids, entrypoint ids, operations, placements, offsets, and open steps.

The Chinese copy should match the current safety posture:

- Invite/Add coworkers: explain invite paths without reading private invite details.
- Meeting info: do not read private IDs or links.
- Chat/participants: explain controls without reading private chat or names.
- Share: explain picker and require confirmation before final sharing.
- Recording and Leave: explain-only.
- Settings and background: configuration guidance only.

Visible UI labels such as `Invite`, `Participants`, `Chat`, `Mute`, `Share`, `React`, `Raise hand`, `More`, `Notes`, `Settings`, and `Leave` may remain in English inside Chinese narration when they match the UI.

## Acceptance Criteria

- Every step in every RingCentral demo flow has nonblank `localizedText.zh`.
- Every `localizedText.zh` contains at least one CJK character.
- Every English `narration.text` remains ASCII.
- One newly localized `meeting-controls-tour` step renders its Chinese text through `render_narration_text(..., PresenterVoiceSettings(language="zh"))`.
- Focused package/voice tests and full verification pass.

## Risks

- The long tour overlaps with `meeting-control-map-demo`; wording can drift over time. The new coverage guard prevents missing localization, not semantic drift.
- PowerShell can render UTF-8 as mojibake. Use tests and file parsing for validation.
- A blanket all-flow guard is a policy choice: future RingCentral demo flows must include Chinese narration from the start. That matches current user goals for language expansion.
