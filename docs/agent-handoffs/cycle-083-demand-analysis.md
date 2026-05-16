# Cycle 083 Demand Analysis

## Verdict/Recommendation

Proceed with a narrow Japanese localization slice for `meeting-control-map-demo` -> `control-map-report` only.

This step should explain `Report issue` as the top-bar support escalation entrypoint for reporting meeting problems. The Japanese narration may mention audio, video, screen sharing, joining, Notes, transcript, or other meeting issues, but it must keep the action framed as opening a foreground troubleshooting/reporting dialog that the presenter closes before continuing.

The implementation should remain package-content-only for this step. Add `narration.localizedText.ja` to the existing `control-map-report` step, and update only directly related localization coverage expectations and handoff/source-index notes if that is part of the implementation cycle. Do not change runtime behavior, locators, action operation, action timing, cleanup, aliases, Q&A, or flow order.

## Current Gap

- Current Japanese demo narration coverage is `33/51`.
- `meeting-control-map-demo` Japanese coverage is `4/22`.
- The first missing Japanese narration step is `meeting-control-map-demo` -> `control-map-report`.
- Existing localization report tests expect:
  - `Localization report: 33/51 demo steps`
  - `- meeting-control-map-demo: 4/22 narration localized`
  - `missing: control-map-report`
- The existing step uses `entrypointId: ringcentral.video.top.report-issue`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`. Those execution semantics should remain unchanged.
- `ringcentral.video.top.report-issue` is a top-bar coordinate route targeting `Report` at `xFromRight=168,y=21` with `cleanup: modal`; this slice should not modify locator or cleanup behavior.
- The entrypoint purpose is to open the issue reporting dialog for Audio, Video, Screen sharing, Meeting join, Notes and transcript, or Other.
- Existing presenter notes say the dialog blocks other meeting controls, categories should not be chosen during a tour unless the user wants to file a report, and the dialog should be closed with its X because Escape was not reliable in testing.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the control-map overview, meeting-information, network-quality, and view-layout steps, with remaining control-map narration still future work.

## User Need

Japanese users need to know that `Report issue` is not another everyday meeting-control menu like Views or Chat. It is the support escalation path when something is wrong and the user wants to report a meeting problem through RingCentral Video.

The Japanese text must express these intentions:

- `Report issue` is the place to report or escalate meeting problems.
- It can be used for problems such as audio, video, sharing, joining, Notes, transcript, or similar meeting issues.
- Opening it brings up a foreground troubleshooting/reporting dialog.
- The dialog can block other meeting controls, so the demo should close it before moving on.
- The narration should be concise, natural Japanese product guidance for a live meeting tour.
- It may keep product labels such as `Report issue`, `Notes`, or `Transcript` as-is when that reads more naturally and matches the existing package style.

## Acceptance Criteria

- `control-map-report` has `narration.localizedText.ja` attached to the existing step in `packages/ringcentral-video.yaml`.
- The existing action block remains unchanged:
  - `entrypointId: ringcentral.video.top.report-issue`
  - `operation: open`
  - `placement: during`
  - `actionOffsetMs: 400`
- The existing route remains unchanged:
  - top-bar `Report`
  - coordinate route `xFromRight: '168'`, `y: '21'`
  - `cleanup: modal`
- Japanese demo narration coverage advances from `33/51` to `34/51`.
- `meeting-control-map-demo` advances from `4/22` to `5/22`.
- The first remaining missing Japanese step for `meeting-control-map-demo` becomes `control-map-add-coworkers`.
- Japanese `--require-complete` still fails because 17 control-map steps remain untranslated.
- Q&A counts remain unchanged at `12/12` localized questions and `12/12` localized answers.
- `questionAliases.ja` coverage remains unchanged unless a separate task explicitly requests alias work.
- The localized narration includes the key concepts of support escalation/reporting, meeting problem categories, a foreground or blocking dialog, and closing the dialog before continuing.
- The localized narration must not say or imply:
  - AiPresenter automatically submits a report;
  - AiPresenter chooses an issue category for the user;
  - AiPresenter uploads logs, diagnostics, meeting data, transcripts, or recordings;
  - RingCentral support will definitely respond, resolve the issue, or provide a specific outcome;
  - opening the dialog diagnoses the exact cause of audio, video, sharing, joining, Notes, or transcript problems;
  - diagnostic values or private meeting details are read aloud, exposed, or sent;
  - the tour proceeds while leaving the blocking dialog open;
  - the report flow is a normal layout, media, participant, or chat control.
- Focused localization tests and localization report expectations should be adjusted only to reflect the one-step coverage increase.

## Non-goals

- Do not localize `control-map-add-coworkers` or any later `meeting-control-map-demo` step in this slice.
- Do not change `operation: open`, timing, placement, locator references, cleanup behavior, or demo sequencing.
- Do not add logic that selects Audio, Video, Screen sharing, Meeting join, Notes and transcript, Other, or any other issue category.
- Do not submit a report, upload logs, attach diagnostics, copy meeting identifiers, or expose account or meeting details.
- Do not promise support response time, support resolution, root-cause accuracy, or any remediation outcome.
- Do not add or modify Japanese aliases, Q&A, presenter notes, manual controls, profile settings, runtime behavior, diagnostics logic, or CLI formatting beyond directly required count expectations.
- Do not broaden this slice into Network quality, Meeting info, Views, Add coworkers, participant controls, chat, audio/video controls, sharing controls, reactions, recording, Notes, settings, or leaving the meeting.

## Suggested Next Slice

After `control-map-report` is localized and reviewed, continue `meeting-control-map-demo` Japanese coverage with `control-map-add-coworkers` as the next isolated slice.

That next slice should move from support escalation to invitation flow. It should explain that `Add coworkers` opens the invite dialog for adding people or copying meeting information, while avoiding automatic invitations, contact selection, link copying, or sharing private meeting details.
