# Cycle 082 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-views` only.

This step should explain `Views` as the top-bar entrypoint for changing the user's local meeting layout. The Japanese narration may mention examples such as gallery-style viewing, speaker-focused viewing, cinematic viewing, or full-screen presentation if the implementation team chooses wording that matches the visible product surface. It must keep the behavior framed as a view/layout choice, not a media, sharing, focus, participant, or meeting-state change.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-views` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `32/51`.
- `meeting-control-map-demo` Japanese coverage is `3/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-views`.
- Existing localization report tests expect:
  - `Localization report: 32/51 demo steps`
  - `- meeting-control-map-demo: 3/22 narration localized`
  - `missing: control-map-views`
- The existing step uses `entrypointId: ringcentral.video.top.views`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those execution semantics should remain unchanged.
- `ringcentral.video.top.views` is a top-bar coordinate route targeting `Views` at `xFromRight=237,y=21` with `cleanup: escape`; this slice should not modify locator or cleanup behavior.
- The entrypoint purpose is layout selection: `Switch the meeting layout, including Gallery view and Full screen.`
- Existing presenter notes say observed options include Gallery and Full screen, and that the menu changes presentation layout, not meeting membership or media state.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the control-map overview, meeting-information, and network-quality steps, with remaining control-map narration still future work.

## User Need

Japanese users need to understand where the meeting view/layout control lives after learning the top-bar meeting information and network health controls. In the control-map sequence, `Views` should tell users how to adjust the way the meeting canvas is presented on their own screen, especially when they want to see more participants, focus on a speaker, use a more cinematic layout, or enter a full-screen-style presentation.

The Japanese text must express these intentions:

- `Views` is the layout/view entrypoint in the top bar.
- It changes how the meeting appears to the user on their own screen.
- Gallery-style, speaker-focused, cinematic, or full-screen-style viewing are acceptable examples if phrased as layout/view examples rather than guaranteed option names beyond the observed UI.
- The control is about visual arrangement and viewing mode, not audio, camera, membership, sharing, focus ownership, or meeting permissions.
- The narration should be concise, natural Japanese product guidance for a live meeting tour.
- It may keep the product label `Views` as-is, matching the existing package style.

## Acceptance Criteria

- `control-map-views` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.top.views`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- The existing route remains unchanged:
  - top-bar `Views`
  - coordinate route `xFromRight: '237'`, `y: '21'`
  - `cleanup: escape`
- Japanese demo narration coverage advances from `32/51` to `33/51`.
- `meeting-control-map-demo` advances from `3/22` to `4/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-report`.
- Japanese `--require-complete` still fails because 18 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration includes the key concepts of `Views`, local meeting layout/view arrangement, and examples such as gallery or full-screen-style viewing.
- The localized narration must not say or imply:
  - AiPresenter selects or switches a layout for the user;
  - opening the menu changes microphone, camera, screen sharing, recording, participant membership, permissions, or meeting state;
  - the view change affects other participants' media state or meeting membership;
  - the view change controls presenter focus, spotlight, pinning, active speaker ownership, or shared-content state;
  - layout changes are guaranteed not to affect sharing or focus in every product state;
  - full-screen, cinematic, speaker, or gallery options are always present for every account, role, window size, platform, or RingCentral build.
- Focused localization tests and localization report expectations should be adjusted only to reflect the one-step coverage increase.

## Non-goals

- Do not localize `control-map-report` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, or demo sequencing.
- Do not add logic that actually chooses Gallery, Speaker, Cinematic, Full screen, or any other layout option.
- Do not promise that layout changes preserve sharing, focus, spotlight, pinning, active speaker state, recording, captions, or media state across all contexts.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, or CLI formatting beyond directly required count expectations.
- Do not broaden this slice into `Report issue`, network diagnostics, meeting information, participant controls, chat, audio/video controls, sharing controls, reactions, recording, whiteboard, apps, captions, summaries, or leaving the meeting.

## Suggested Next Slice

After `control-map-views` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-report` as the next isolated slice.

That next slice should move from local view layout to support escalation. It should explain that `Report issue` opens a foreground troubleshooting/reporting dialog for meeting problems, while keeping it separate from normal tour navigation, automatic diagnostics, or sending a report without user intent.
