# Cycle 082 Risk Scan: control-map-views JA Narration

Date: 2026-05-16

## Risk Summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-views`.

This handoff is documentation-only. The future implementation should add only the Japanese narration under the existing `control-map-views` step and preserve:

- `entrypointId: ringcentral.video.top.views`
- `operation: open`
- `placement: during`
- `actionOffsetMs: 350`
- the step position after `control-map-network` and before `control-map-report`
- the existing entrypoint cleanup behavior: `cleanup: escape`

`control-map-views` opens the top-bar View layout menu. The entrypoint purpose is layout selection: changing how the current user sees the meeting, including options such as Gallery view, Full screen, and depending on the runtime surface possibly Speaker, Cinematic, or similar layout choices. The English narration is intentionally narrow: it says Views controls how the meeting is arranged on the user's screen and does not change anyone's audio, video, or membership.

The main risk in this localization slice is making a layout menu sound like a meeting-state control. Japanese copy must not imply that AiPresenter switches the user's selected layout during a demo, changes another participant's view, starts or stops media, changes focus/pin/spotlight state, alters screen sharing, or affects membership. It should frame the menu as a place to choose the local visual arrangement only.

Adjacent context matters. `control-map-network` is diagnostic and mentions audio/video/sharing health indicators; `control-map-views` should not inherit diagnostic or remediation language from that step. `control-map-report` is the escalation path and opens a blocking dialog; `control-map-views` should not file reports, pick categories, or treat layout options as troubleshooting outcomes.

## Behavior Boundaries

- Keep this as an open-and-explain step. Do not select Gallery, Speaker, Cinematic, Full screen, or any other layout option during the feature tour unless the user explicitly asks to change the layout.
- Do not imply the narration changes the meeting for everyone. Safe framing: "your screen," "local layout," "how you view the meeting," or "display arrangement."
- Do not describe layout changes as changes to audio, microphone, camera, video transmission, participant membership, host permissions, recording, sharing state, chat, notes, transcript, or network health.
- Do not use verbs that imply media control, such as muting, unmuting, disabling camera, starting video, stopping video, focusing another participant, spotlighting, pinning, promoting, removing, or taking over unless a separate assigned step actually performs that behavior.
- Do not present Speaker/Cinematic/Gallery choices as universal if the runtime may only show a subset. Safe wording can say "such as" or "layout options like" rather than a fixed exhaustive list.
- Do not claim Full screen is the same as sharing the screen or presenting content. It is a local display mode, not a sharing action.
- Do not claim Gallery, Speaker, or Cinematic view changes who is speaking, who is visible to others, or who is prioritized for the whole meeting.
- Preserve cleanup. The Views menu should be closed with Escape before `control-map-report` opens its blocking dialog.
- Do not blur the demo/runtime boundary. In a demo, AiPresenter should point out the menu and explain what it is for; actual layout selection should require explicit user intent.
- Do not alter Q&A, question aliases, presenter notes, openSteps, locator coordinates, network diagnostics, report behavior, or meeting-controls-tour text as part of this localization slice.

## Privacy Notes

- Layout menus are lower privacy risk than meeting info or network diagnostics, but opening them can still reveal participant thumbnails, names, shared content previews, focused speakers, or meeting context behind the menu.
- Japanese narration may name layout categories such as Gallery, Speaker, Cinematic, or Full screen. It should not read participant names, visible chat, shared-screen content, captions, transcript text, or thumbnail details.
- Avoid wording that implies AiPresenter is observing or ranking participants by attention, activity, speaking status, identity, importance, camera state, or screen content.
- If a live validation screenshot is used, ensure it does not capture sensitive participant names, meeting titles, shared documents, chat previews, captions, or thumbnails unless synthetic data is used.
- Cleanup failure is still a privacy issue. Leaving the Views menu open can expose layout choices and visible meeting context during later report or top-bar steps.
- The adjacent Network quality step may expose diagnostics and the adjacent Report issue step may expose support categories. The views narration should not cause either neighboring surface to remain open or be mixed into the screenshot/review evidence.

## Required Test Guards

- Localization coverage should advance only the expected Japanese narration count for `meeting-control-map-demo`: from `3/22` to `4/22`, with first remaining missing step moving from `control-map-views` to `control-map-report`.
- Overall Japanese demo localization totals should advance by exactly one step from the cycle 081 baseline, with `meeting-controls-tour` remaining `22/22`.
- Assert the new Japanese text is attached to `meeting-control-map-demo` -> `control-map-views`, not to `meeting-controls-tour` -> `explain-view-layout`, Q&A, entrypoint presenter notes, aliases, network, report issue, or meeting info.
- Assert `control-map-views.action.entrypointId` remains `ringcentral.video.top.views`.
- Assert `control-map-views.action.operation` remains `open`.
- Assert `control-map-views.narration.placement` remains `during`.
- Assert `control-map-views.narration.actionOffsetMs` remains `350`.
- Assert the entrypoint `ringcentral.video.top.views` still has `cleanup: escape` in its open step.
- Assert the Japanese copy preserves the local-layout boundary: it changes how the user sees the meeting on their own screen.
- Assert the Japanese copy explicitly or clearly preserves that audio, video, and membership are not changed.
- Assert the Japanese copy does not imply the assistant selects or changes the user's layout during the demo.
- Assert the Japanese copy does not mention or imply muting, camera toggling, screen-share start/stop, recording, participant removal, host action, pinning, spotlighting, focus takeover, network diagnosis, report submission, or category selection.
- Assert any listed layout examples are safe and non-exhaustive if runtime options can vary. Gallery, Speaker, Cinematic, and Full screen can be named as examples only if phrased as layout choices, not actions already taken.
- Assert neighboring steps remain unchanged, especially `control-map-network`, `control-map-report`, the `meeting-controls-tour` view layout step, and Q&A answers about sharing, focus, or media controls.
- If live or screenshot-based validation is used, sanitize or avoid artifacts showing participant names, thumbnails, shared content, captions, transcript, meeting title, network values, or report categories. A cleanup failure or visible private meeting context in committed evidence should fail review.
- If implementation updates CLI localization diagnostics, `--require-complete` for Japanese should still fail after this slice because the remaining `meeting-control-map-demo` steps are still untranslated.

## Rollback/Commit Notes

Proceed as a narrow narration-only commit. The safe rollback is to remove only the `localizedText.ja` line/block added under `meeting-control-map-demo` -> `control-map-views`.

Do not rollback or alter other agents' concurrent edits. Before committing, verify the diff contains only the intended Japanese narration and any directly necessary test expectation updates owned by the implementation task. This risk scan itself intentionally changes only `docs/agent-handoffs/cycle-082-risk-scan.md`.

Recommended commit scope for the implementation owner: "Add JA narration for RingCentral control map view layout." Keep actual layout selection, Full screen activation, focus/pin/spotlight behavior, screen-sharing behavior, media state changes, locator changes, cleanup behavior changes, Q&A edits, and broader control-map localization for separate cycles unless explicitly assigned.
