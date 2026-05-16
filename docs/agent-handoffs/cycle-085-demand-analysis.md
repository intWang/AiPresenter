# Cycle 085 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-participants` only.

This step should explain `Participants` as the meeting roster and people-controls surface. The Japanese narration should help the presenter point out where the roster, attendee count, participant search, invite controls, host controls, and more options live, while making clear that the tour does not read names, identify roles, search participants, invite people, lock the meeting, mute others, raise/lower hands, or change attendee state.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-participants` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, adaptive routing, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `35/51`.
- `meeting-control-map-demo` Japanese coverage is `6/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-participants`.
- Existing localization report expectations now point to:
  - `Localization report: 35/51 demo steps`
  - `- meeting-control-map-demo: 6/22 narration localized`
  - `missing: control-map-participants`
- The existing step uses `entrypointId: ringcentral.video.toolbar.participants`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those execution semantics should remain unchanged.
- The entrypoint route clicks the toolbar `Participants` button with `controlType: button` and `cleanup: toggle`; this slice should not modify locator or cleanup behavior.
- Existing presenter notes say this surface is for attendee count and meeting control, but participant names should not be identified unless UI text is verified and allowed.
- The observed panel includes Participant and Chat tabs, search, invite, lock, mute, raise-hand, and more controls. This slice should explain those as available surfaces, not operate them.

## User Need

Japanese users need the control map to explain where the roster and people controls live after the empty-room invite entry point. In a live RingCentral Video meeting, `Participants` answers "where do I see the people panel and related controls?" without requiring the presenter to expose personal meeting details.

The Japanese text must express these intentions:

- `Participants` opens the participant roster/people panel.
- The panel is where attendee count, names/roles, participant search, invite controls, host controls such as lock/mute, raise-hand state, and more options may appear.
- The presenter is explaining location and purpose, not managing attendees.
- Names, roles, attendee count, participant search results, invite details, host-control availability, and more-menu contents are private or context-sensitive by default.
- The presenter should not read names or roles, search participants, invite someone, lock the meeting, mute others, change hand state, open more options, or alter attendee state unless the user explicitly asks and visible content is verified.
- The panel should be toggled or closed before continuing to Chat so the next control is not obscured.
- The wording should be concise, natural Japanese product narration for a live meeting tour and may keep product labels such as `Participants`, `Invite`, and `Chat` as-is.

## Acceptance Criteria

- `control-map-participants` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.toolbar.participants`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- The existing route remains unchanged:
  - toolbar `Participants` button
  - `controlType: button`
  - `cleanup: toggle`
- Japanese demo narration coverage advances from `35/51` to `36/51`.
- `meeting-control-map-demo` advances from `6/22` to `7/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-chat`.
- Japanese `--require-complete` still fails because 15 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration identifies `Participants` as the meeting roster/people-controls panel and explains that attendee count, search, invite, lock, mute, raise-hand, and more controls may live there.
- The localized narration includes privacy boundaries for names, roles, attendee count, participant search, invite controls, host controls, and more options.
- The localized narration must not say or imply:
  - AiPresenter reads participant names or roles by default;
  - AiPresenter searches the participant list;
  - AiPresenter invites people;
  - AiPresenter locks the meeting;
  - AiPresenter mutes or manages other attendees;
  - AiPresenter changes hand state or attendee state;
  - attendee count, roles, host status, search results, or more-menu contents are exposed by default;
  - the user has host permission unless visible UI verifies it;
  - the tour proceeds while leaving the participant panel obstructing the next Chat step.

## Non-goals

- Do not localize `control-map-chat` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, adaptive meeting-state behavior, or demo sequencing.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, CLI formatting, or source data beyond directly required count expectations and documentation notes.
- Do not broaden this slice into toolbar Invite, Chat, media controls, sharing, reactions, More, recording, Notes, background, settings, security, host-control workflows, or leave behavior.
- Do not perform live participant search, invite actions, meeting lock/unlock, mute actions, attendee management, role inspection, or participant data reading as part of this localization demand slice.

## Suggested Next Slice

After `control-map-participants` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-chat` as the next isolated slice.

That next slice should move from people controls to the written side channel. It should explain where Chat lives and what it is for, while keeping public/private message contents private unless the user explicitly asks and visible content is verified.
