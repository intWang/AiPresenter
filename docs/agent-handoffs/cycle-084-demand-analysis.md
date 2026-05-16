# Cycle 084 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-add-coworkers` only.

This step should explain `Add coworkers` as the empty-room invite/add-people entrypoint. The Japanese narration should help the presenter point out where people can be added or invited, while making clear that the tour does not send invitations, select contacts, perform a name/email search, copy meeting links, or reveal private invite details.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-add-coworkers` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, adaptive routing, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `34/51`.
- `meeting-control-map-demo` Japanese coverage is `5/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-add-coworkers`.
- Existing localization report expectations now point to:
  - `Localization report: 34/51 demo steps`
  - `- meeting-control-map-demo: 5/22 narration localized`
  - `missing: control-map-add-coworkers`
- The existing step uses `entrypointId: ringcentral.video.main.add-coworkers`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`. Those execution semantics should remain unchanged.
- The entrypoint route is a UIA `Add coworkers` button with `cleanup: modal`; this slice should not modify locator or cleanup behavior.
- Existing presenter notes say the dialog includes a name/email field, suggestions, Copy meeting link, Cancel, and Invite; it is functionally similar to toolbar Invite; it appears only in the empty-room "first one here" state; and it should be closed before other controls are touched.
- Adaptive behavior already rewrites this step to toolbar Invite when multiple participants are present. This localization slice should not change that state logic.

## User Need

Japanese users need the control map to explain the people/invite area after top-bar status and support controls. When a presenter is alone in a RingCentral Video room, `Add coworkers` is the visible canvas callout that answers "where do I add or invite someone from here?"

The Japanese text must express these intentions:

- `Add coworkers` is the empty-room entrypoint for the invite/add-people surface.
- It opens the Invite dialog/surface where adding people, finding invite options, or copying meeting information may be available.
- The presenter is explaining location and purpose, not completing an invite workflow.
- Names, email addresses, invite suggestions, search results, meeting links, and copied link values are private by default.
- The presenter should not read or describe invite suggestions, email/name search results, or meeting links unless the user explicitly asks and the visible content is verified.
- The invite dialog blocks the meeting controls, so the tour should close or cancel it before continuing.
- The wording should be concise, natural Japanese product narration for a live meeting tour and may keep product labels such as `Add coworkers` and `Invite` as-is.

## Acceptance Criteria

- `control-map-add-coworkers` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.main.add-coworkers`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 350`
- The existing route remains unchanged:
  - UIA `Add coworkers` button
  - `controlType: button`
  - `cleanup: modal`
- Japanese demo narration coverage advances from `34/51` to `35/51`.
- `meeting-control-map-demo` advances from `5/22` to `6/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-participants`.
- Japanese `--require-complete` still fails because 16 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration identifies `Add coworkers` as an empty-room people/invite entrypoint and explains that the Invite dialog/surface is where people can be added or invited.
- The localized narration includes privacy boundaries for invite suggestions, name/email search results, and meeting links.
- The localized narration must not say or imply:
  - AiPresenter sends an invite;
  - AiPresenter enters, searches, selects, or confirms a contact;
  - AiPresenter copies or reads a meeting link;
  - invite suggestions, contact names, email addresses, participant data, or meeting links are exposed by default;
  - the user is the only participant unless the visible empty-room state has been confirmed;
  - the tour proceeds while leaving the blocking invite dialog open.

## Non-goals

- Do not localize `control-map-participants` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, adaptive meeting-state behavior, or demo sequencing.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, CLI formatting, or source data beyond directly required count expectations and documentation notes.
- Do not broaden this slice into toolbar Invite, Participants, Chat, media controls, sharing, reactions, More, recording, Notes, background, settings, or leave behavior.
- Do not perform live RingCentral invite actions, contact searches, link copying, or participant/contact data inspection as part of this localization demand slice.

## Suggested Next Slice

After `control-map-add-coworkers` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-participants` as the next isolated slice.

That next slice should move from the invite/add-people surface to the participant roster and people controls. It should explain where attendee count, participant search, invite, lock, mute, raise-hand, and more controls live, while keeping participant names and roster details private unless the user explicitly asks and visible content is verified.
