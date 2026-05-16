# Cycle 078 Demand Analysis: JA Leave Narration

Date: 2026-05-16

## Verdict/Recommendation

Proceed with a narrow Japanese narration slice for `meeting-controls-tour` -> `explain-leave`.

This should be a package-content localization pass only. `Leave` is the final Japanese gap in `meeting-controls-tour`, but it is also a destructive meeting-exit control. The Japanese narration must explain what the control does while making it unmistakable that AiPresenter will not click it, leave the meeting, or end the meeting unless the user explicitly confirms that action.

## Current Gap

- Current Japanese demo narration coverage should remain `28/51` before this slice.
- Current `meeting-controls-tour` Japanese narration coverage should remain `21/22` before this slice.
- The only remaining missing controls-tour step is `explain-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- Japanese aliases remain unchanged at `3/27` entrypoints and `9` aliases.
- `docs/knowledge/ringcentral-video/source-index.md` currently says Japanese coverage includes the first twenty-one controls-tour steps through `settings`.
- `tests/unit/test_cli.py` currently expects `Localization report: 28/51 demo steps`, `- meeting-controls-tour: 21/22 narration localized`, and `missing: explain-leave` for Japanese.
- `tests/unit/test_material_packages.py` currently expects Japanese report totals of `28/51` and controls-tour `21/22`.
- The source step has English and Chinese narration but no Japanese narration:
  - Step: `meeting-controls-tour` -> `explain-leave`.
  - Entrypoint: `ringcentral.video.toolbar.leave`.
  - Operation: `explain`.
  - Placement: `before`.
  - English intent: `Leave exits the meeting. It is a destructive control, so the presenter explains it but does not click it without explicit confirmation.`
- The related entrypoint `ringcentral.video.toolbar.leave` has `openSteps: []`.
- Entrypoint notes say to treat this as destructive during a tour; clicking Leave can immediately show the left-meeting state in the test build; AiPresenter should explain without clicking unless the user explicitly asks to end the meeting; and a verbal confirmation is required before any leave or end action.
- Existing safety policy under `safety.leaveMeeting` says to ask for explicit confirmation before clicking Leave and to distinguish leaving the meeting from ending a meeting for everyone when the UI exposes that choice.

## User Need

Japanese users need the controls tour to identify the meeting exit path without accidentally disconnecting them or ending a live meeting. A user may ask where the Leave button is because they want to understand the toolbar, not because they intend to leave immediately. Hosts and moderators have additional risk because the UI may expose an option that ends the meeting for everyone rather than only removing the local user.

The Japanese narration must express these intentions:

- `Leave` is the meeting exit path.
- Clicking or confirming Leave can remove the current user from the meeting.
- Because it is destructive, the tour explains the control only.
- AiPresenter does not click Leave during the tour.
- AiPresenter does not leave the meeting, end the meeting, or choose any leave/end option without explicit user confirmation.
- If the user has host-like privileges and the UI exposes an end-meeting choice, ending the meeting for everyone is different from ordinary local exit and must be treated as higher-risk.
- The narration should avoid implying that the demo will proceed by opening a confirmation dialog, testing the button, or performing a safe trial click.

## Acceptance Criteria

- Add `localizedText.ja` only under `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-leave` -> `narration`.
- Preserve `entrypointId: ringcentral.video.toolbar.leave`.
- Preserve `operation: explain`; do not convert it to `open`, `click`, `select`, or any executable action.
- Preserve `placement: before`.
- Preserve `ringcentral.video.toolbar.leave` with `openSteps: []`.
- Japanese demo narration should advance from `28/51` to `29/51`.
- `meeting-controls-tour` Japanese narration should advance from `21/22` to `22/22`.
- `meeting-controls-tour` should no longer report missing Japanese narration steps.
- Japanese Q&A and alias counts should remain unchanged.
- Japanese `--require-complete` should still fail because `meeting-control-map-demo` remains uncovered for Japanese.
- Japanese text should be authored Japanese text, not copied English or Chinese.
- Japanese text should include the UI label `Leave`.
- Japanese text should clearly say this is a meeting exit or leaving control.
- Japanese text should include destructive/safety wording equivalent to: explain only, do not click, explicit confirmation required.
- Japanese text should distinguish ordinary leaving from ending the meeting for everyone when the user is host or when the UI exposes that choice.
- Focused tests may assert the unchanged entrypoint/action/placement, `openSteps: []`, Japanese CJK presence, required safety terms, and forbidden phrases that imply clicking, opening a leave dialog, exiting, ending, or automatically selecting an option.
- `source-index.md` may be updated in the implementation cycle to say Japanese coverage is complete for all twenty-two `meeting-controls-tour` steps.

## Non-goals

- Do not localize any `meeting-control-map-demo` step in this slice.
- Do not change the already localized `explain-settings`, `explain-background-settings`, `explain-notes`, `explain-recording`, or any earlier controls-tour Japanese narration.
- Do not modify English or Chinese narration unless a separate review scopes it.
- Do not alter operation entrypoints, open-step routes, cleanup behavior, locators, runtime behavior, diagnostics behavior, CLI behavior, or telemetry.
- Do not add Japanese aliases or new Q&A.
- Do not click `Leave`.
- Do not open a Leave confirmation dialog as part of the tour.
- Do not leave the meeting.
- Do not end the meeting for everyone.
- Do not claim that clicking Leave is reversible or safe to demonstrate.
- Do not collapse ordinary local exit and host end-meeting behavior into the same risk level.
- Do not infer the user's intent to leave from a location or explanation question; require explicit confirmation before any leave or end action.

## Suggested Next Slice

After this step is localized and reviewed, move to Japanese narration for `meeting-control-map-demo`, starting with the first missing control-map step as a separate slice. Keep that follow-up distinct because this cycle should finish only the long controls tour and should not broaden into the second 22-step demo flow.
