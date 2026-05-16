# Cycle 080 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-meeting-info` only.

This step should explain the meeting-information entrypoint as the place users use to confirm the meeting's identity and related metadata. Because the action opens a panel that may expose meeting details, meeting links, dial-in options, and encryption information, the Japanese narration must preserve the privacy boundary already present in the English and Chinese copy: describe the purpose and location, but do not read, copy, recite, or imply extraction of private values.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-meeting-info` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `30/51`.
- `meeting-control-map-demo` Japanese coverage is `1/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-meeting-info`.
- Existing localization report tests expect:
  - `Localization report: 30/51 demo steps`
  - `- meeting-control-map-demo: 1/22 narration localized`
  - `missing: control-map-meeting-info`
- Existing diagnostics tests expect Japanese required localization to fail with `30/51 demo steps`, while Q&A remains complete at `12/12` questions and `12/12` answers.
- `docs/knowledge/ringcentral-video/source-index.md` says Japanese coverage includes the control-map overview step, while remaining control-map narration is future work.
- The YAML step currently has `entrypointId: ringcentral.video.top.meeting-info`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those execution semantics should remain unchanged.

## User Need

Japanese users need to understand what the top meeting-information control is for before they rely on it during a live meeting. The control answers the "which meeting am I in, and what information identifies it?" question. It is useful for confirming meeting identity, finding where meeting details live, and understanding that related connection or security metadata may be grouped there.

The Japanese text must express these intentions:

- This is a top-area meeting-information entrypoint.
- It helps confirm meeting identity or meeting information, not general meeting controls.
- The panel may contain meeting details, a meeting link, dial-in options, and encryption/security information.
- The presenter is summarizing the kind of information available and why the entrypoint matters.
- Privacy-sensitive values are not read aloud by default.
- If the user explicitly asks for a private value, the presenter should only respond when the value is visibly available and the context has been verified.

The tone should be calm, concise, and safety-aware. It should sound like natural Japanese product narration for a live-meeting assistant, not like a compliance warning pasted into the tour.

## Acceptance Criteria

- `control-map-meeting-info` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.top.meeting-info`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- Japanese demo narration coverage advances from `30/51` to `31/51`.
- `meeting-control-map-demo` advances from `1/22` to `2/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-network`.
- Japanese `--require-complete` still fails because 20 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration includes the key concepts of meeting identity/information and the meeting-information entrypoint.
- The localized narration acknowledges the sensitive categories at a high level: meeting details, link, dial-in options, and encryption/security information.
- The localized narration says private values are summarized or left unread by default; it must not imply reading, copying, announcing, exposing, validating, or storing meeting links, dial-in numbers, meeting IDs, passcodes, encryption details, or other private values.
- Focused localization tests and localization report expectations should be adjusted only to reflect the one-step coverage increase.

## Non-goals

- Do not localize `control-map-network` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, or demo sequencing.
- Do not add logic that reads panel contents, extracts meeting links, copies invite information, copies dial-in numbers, reads meeting IDs or passcodes, or inspects encryption details.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, or CLI formatting beyond directly required count expectations.
- Do not promise that all meeting-information fields are always present or visible; availability may depend on account, role, meeting type, and current RingCentral build.
- Do not broaden this slice into general security, network-quality, invite, phone audio, or encryption-feature coverage.

## Suggested Next Slice

After `control-map-meeting-info` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-network` as the next isolated slice.

That next slice should shift from identity/privacy framing to meeting-health framing: network quality helps users understand audio, video, or sharing issues through packet loss, jitter, latency, or similar diagnostics. It should still avoid overstating what the presenter can diagnose without current visible evidence.
