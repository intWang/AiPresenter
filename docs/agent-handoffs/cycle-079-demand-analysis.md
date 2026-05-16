# Cycle 079 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-overview` only.

This step should introduce the control-map demo as a structured orientation layer for the RingCentral Video meeting surface. The Japanese narration should help users understand that the demo organizes the meeting UI by region and topic: top status and health, the live meeting canvas, collaboration and people entrypoints, media controls, sharing, reactions, More menu, and closeout controls.

The implementation should remain package-content-only. It should add Japanese narration to this one step and update only the directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operations, aliases, Q&A, YAML structure beyond the one localized string, or demo flow order.

## Current Gap

- Current Japanese demo narration coverage is `29/51`.
- `meeting-controls-tour` Japanese coverage is complete at `22/22`.
- `meeting-control-map-demo` remains `0/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-overview`.
- Existing localization report tests expect:
  - `Localization report: 29/51 demo steps`
  - `- meeting-control-map-demo: 0/22 narration localized`
  - `missing: control-map-overview`
- Existing diagnostics tests expect Japanese required localization to fail with `29/51 demo steps`, while Q&A remains complete at `12/12` questions and `12/12` answers.
- `docs/knowledge/ringcentral-video/source-index.md` says Japanese coverage is complete for Q&A, virtual background blur, meeting basics, and all twenty-two `meeting-controls-tour` steps, while control-map narration remains future work.

## User Need

Users who choose Japanese narration need the opening of the control-map demo to establish the mental model before any detailed control explanations begin. This is especially important because `meeting-control-map-demo` is not merely another toolbar tour; it is a "map / structured understanding" demo that explains how the meeting interface is organized.

The Japanese text must express these intentions:

- Treat the meeting window as a control map or structured map, not as a list of buttons to press immediately.
- The top area is for status and meeting health, including identity/status/network-style signals that later steps explain in more detail.
- The center area is the live meeting canvas, where participants and meeting content appear.
- The lower/control area is where users manage collaboration entrypoints, people, microphone/camera media readiness, sharing, reactions, More actions, and leaving or ending paths.
- This overview is an orientation step for what the rest of the demo will explain later.
- The presenter is explaining regions and control categories only at this step.

The tone should be clear, calm, and instructional. It should sound natural in Japanese product narration, but it should preserve the "control map" concept because that is the point of this demo.

## Acceptance Criteria

- `control-map-overview` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- Japanese demo narration coverage advances from `29/51` to `30/51`.
- `meeting-control-map-demo` advances from `0/22` to `1/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-meeting-info`.
- Japanese `--require-complete` still fails because 21 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration communicates UI-region orientation and future demo scope without saying or implying that AiPresenter will click, open, toggle, start, invite, share, record, raise hand, leave, or otherwise change meeting state during the overview.
- The text should not mention reading private meeting values, chat content, participant details, links, dial-in information, transcripts, or other sensitive data. Those boundaries belong to later specific steps.
- The wording should not promise that all controls are always visible, available, or safe for every role; it should describe the meeting surface at the conceptual map level.
- Focused localization tests and the localization report expectations should be adjusted only to reflect the one-step coverage increase.

## Non-goals

- Do not localize `control-map-meeting-info` or any later `meeting-control-map-demo` step in this slice.
- Do not convert this overview into an executable interaction step.
- Do not change `operation: explain` for `control-map-overview`.
- Do not add clicks, opens, toggles, selects, verification logic, cleanup behavior, or locator changes.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, or CLI formatting.
- Do not imply the demo will activate microphone/camera, open sharing, invite participants, send chat, start recording, start notes/transcript, change backgrounds/settings, raise hand, open More, leave the meeting, or end the meeting.
- Do not broaden this into source evidence updates for new RingCentral features.

## Suggested Next Slice

After `control-map-overview` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-meeting-info` as the next isolated slice.

That next slice should handle a more sensitive boundary than this overview because meeting info can expose meeting identity, links, dial-in options, and encryption details. It should explain the location and purpose while preserving privacy by not reading private values aloud unless explicitly requested.
