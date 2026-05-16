# Cycle 099 Risk Scan: RingCentral Video Control Map Leave JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-leave` only.

Current Japanese localization baseline is `49/51` demo steps overall, with `meeting-control-map-demo` at `20/22`; the first missing step is `control-map-leave`. This slice is sensitive because Leave is a destructive meeting-lifecycle control. A wording, route, or test-scope mistake could cause AiPresenter to click the Leave control, exit the user from the current meeting, reveal or trigger a host-only End meeting option, end the meeting for other participants, disrupt recording/sharing/notes state, or overclaim that leaving is always safe or reversible.

The safe target is a narrow explain-only localization. The implementation should preserve:

- `action.entrypointId: ringcentral.video.toolbar.leave`
- `action.operation: explain`
- `narration.placement: before`
- the empty `openSteps: []` on `ringcentral.video.toolbar.leave`
- the presenter notes that Leave is destructive and requires explicit confirmation before any leave or end action
- English and Chinese narration text
- the step position after `control-map-settings` and before `control-map-summary`

The core safety rule is: `control-map-leave` may explain what Leave does and why confirmation matters, but it must not click Leave, choose End meeting, confirm any exit dialog, or change meeting state.

## Allowed behavior

- Add exactly one Japanese narration block for `meeting-control-map-demo` -> `control-map-leave`.
- Describe Leave as the exit path from the current meeting.
- Explain that Leave can end the user's presence in the meeting.
- Explain that host or moderator roles may expose stronger end-meeting choices that can affect everyone.
- State that AiPresenter only explains the control during this tour.
- State that AiPresenter does not click Leave, choose End meeting, or confirm an exit unless the user explicitly requests it and confirms the visible option and impact.
- Keep the wording concise enough for a control-map pass, with the detailed confirmation workflow left to a separately approved implementation.

## Forbidden behavior

- Do not click the Leave toolbar button during this localization slice.
- Do not add `openSteps`, route targets, selectors, click instructions, cleanup behavior, offsets, aliases, Q&A, presenter notes, source code, tests, or source-index text unless another explicitly assigned implementation owner owns those files.
- Do not choose or describe choosing `Leave`, `End meeting`, `Leave meeting`, `End for all`, `Cancel`, or any similar dialog button as an action AiPresenter performs in this step.
- Do not promise that leaving is reversible, harmless, private, automatically recoverable, or safe for all meeting roles.
- Do not imply AiPresenter can determine whether the current user is host, moderator, attendee, sole participant, sharing, recording, or taking notes unless a separate live-state workflow verifies that information.
- Do not broaden this slice into `control-map-summary`, aliases, Chinese text, Q&A, live acceptance, confirmation-flow implementation, or route execution.

## Accidental Leave Or End Risk

`ringcentral.video.toolbar.leave` is currently explain-only and has `openSteps: []`. That is the strongest safety boundary in this slice.

Review should fail if:

- any executable open route is added for `ringcentral.video.toolbar.leave`
- `control-map-leave.action.operation` changes from `explain`
- any test expectation starts treating Leave as operable by default
- narration says AiPresenter will click, press, select, confirm, end, or exit during the tour
- the UI is left in a left-meeting, meeting-ended, confirmation-dialog, or lobby/rejoin state as part of validation

Future execution of Leave or End meeting needs a separate confirmation design that accounts for visible dialog text, role, participant impact, meeting state, and recovery.

## Host And Destructive Confirmation

Leave can expose different outcomes depending on role and meeting state. The Japanese narration should acknowledge this without pretending to know the current role.

Safe language:

- "Leave is the exit path from the current meeting."
- "If host-only end options appear, they may affect other participants."
- "AiPresenter explains the control but does not execute it in this tour."
- "A future leave/end action requires an explicit user request plus confirmation of the visible option and likely impact."

Unsafe language:

- "I will leave now."
- "I will end the meeting."
- "Only you will leave."
- "Everyone stays unaffected."
- "This is safe to click."
- "The meeting can be restored."
- "The user is not the host."
- "End meeting will not appear."

Confirmation language should cover both the user's intent and the visible UI choice. A generic "confirmed" is not enough if the dialog shows multiple choices or host-only options.

## Meeting-State Impact

Leaving or ending a meeting can interrupt ongoing work. The risk boundary should treat meeting state as unknown unless separately observed and confirmed.

Potential impacts include:

- the user losing live audio/video presence
- active screen sharing stopping or becoming orphaned
- notes, transcript, or recording workflows changing state
- host/moderator responsibilities being transferred or ended
- other participants being affected by an End meeting action
- the app moving to a left-meeting, ended-meeting, or rejoin surface

The Japanese copy should avoid lifecycle guarantees. It can say Leave ends the user's presence, and that stronger end options may affect everyone, but it should not claim what will happen in the current session beyond the generic product behavior.

## Avoiding Clicks And Routes

This implementation should be text-only. The safest technical state is unchanged:

- `ringcentral.video.toolbar.leave.openSteps` remains empty.
- `control-map-leave` remains an `explain` step.
- No cleanup mode is added; there should be no dialog to clean up because nothing is opened.
- No new route should target a Leave button, end-meeting dialog, confirmation modal, rejoin surface, or meeting-ended state.
- No test should simulate a successful leave/end action as part of this localization slice.

If manual validation is performed, it should validate package text and report output only. Do not validate by clicking the live Leave control in a real or disposable meeting as part of this risk-scan scope.

## Localization Overclaiming

The Japanese copy should be calm, operational, and narrower than a workflow promise. It should explain the control and confirmation boundary, not describe a runnable leave/end process.

Safer wording should include:

- `Leave`
- `現在の会議から退出`
- `会議内での参加状態`
- `ホスト`
- `全員に影響`
- `場所と役割だけ`
- `クリックしません`
- `明確な依頼`
- `表示された選択肢`
- `影響`
- `確認`

Unsafe or overclaiming phrases should be rejected when they imply execution, safety guarantees, or role certainty:

- `退出します`
- `終了します`
- `クリックします`
- `選択します`
- `End meeting を選びます`
- `安全です`
- `元に戻せます`
- `他の参加者には影響しません`
- `ホストではありません`
- `自動`
- `すぐに`
- `問題ありません`

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Leave は現在の会議から退出するための入口です。実行すると会議内での参加状態が終わり、ホストの場合は全員に影響する終了系の選択肢が表示されることもあります。このコントロールマップでは場所と役割だけを説明し、ユーザーが明確に依頼し、表示された選択肢と影響を確認できるまで、Leave をクリックしたり End meeting を選んだりしません。
```

This keeps the step focused on exit/end-meeting risk while staying distinct from `control-map-summary`.

## Localization Boundary

Expected coverage movement after implementation:

- Overall Japanese demo narration: `49/51` -> `50/51`
- `meeting-control-map-demo`: `20/22` -> `21/22`
- First missing Japanese step: `control-map-leave` -> `control-map-summary`
- Remaining missing step should be `control-map-summary`

Do not imply full Japanese coverage for `meeting-control-map-demo` until all 22 steps are localized. Japanese `--require-complete` should still fail after this slice because `control-map-summary` remains untranslated.

Japanese Q&A coverage and alias coverage should remain unchanged unless a separate task owns them. This slice should not add Japanese question aliases for Leave; matching and operability boundaries already treat Leave as answer-only/non-operable by default.

## Suggested Test Guardrails

Implementation tests should confirm:

- `control-map-leave` has `localizedText.ja`.
- `control-map-summary` remains without Japanese narration and becomes the first missing step.
- Coverage updates exactly to `50/51` overall and `21/22` for `meeting-control-map-demo`.
- `control-map-leave.action.entrypoint_id == "ringcentral.video.toolbar.leave"`.
- `control-map-leave.action.operation == "explain"`.
- `control-map-leave.narration.placement == "before"`.
- `ringcentral.video.toolbar.leave.open_steps == []`.
- No cleanup mode, action offset, executable selector, or route is added for Leave.
- No Japanese aliases are added for Leave.
- The previous `control-map-settings` step remains localized and keeps its Settings no-change boundary.
- The next `control-map-summary` step remains a separate unlocalized explain step.
- The Japanese copy explains exit risk, possible host/end-meeting impact, no click, no End meeting selection, explicit user request, visible option confirmation, and likely impact confirmation.

Review should update CLI and diagnostics localization-report expectations only if the implementation owner scope includes those test files. This risk-scan handoff itself does not edit tests.

## Commit Hygiene

This risk-scan agent should create only `docs/agent-handoffs/cycle-099-risk-scan.md`.

At scan time, `git status --short` showed `.coverage` modified before this document was created. Treat it as existing or parallel-agent work:

- Do not stage `.coverage`.
- Do not overwrite, revert, normalize, or format files changed by other agents.
- Re-check `git status --short` immediately before staging because other agents may be working in parallel.
- Keep any later implementation commit narrow: one YAML localization block and only directly necessary test/source-index expectation updates if assigned.
- Do not stage unrelated handoff docs, generated artifacts, screenshots, logs, `.coverage`, or other agents' WIP.
- If tests are run, prefer commands that avoid creating or refreshing coverage artifacts, and verify `.coverage` remains unstaged.

No commit should be made by this risk-scan agent.

## Reviewer Checklist

- Confirm this risk-scan subagent changed only `docs/agent-handoffs/cycle-099-risk-scan.md`.
- Confirm no YAML, code, tests, `.coverage`, screenshots, logs, or generated files were changed by this risk-scan subagent.
- Confirm the implementation adds only `meeting-control-map-demo` -> `control-map-leave` -> `narration.localizedText.ja`.
- Confirm Leave remains explain-only and `ringcentral.video.toolbar.leave.openSteps` remains empty.
- Confirm no Leave, End meeting, confirmation-dialog, left-meeting, ended-meeting, or rejoin route is added.
- Confirm the Japanese narration avoids claims that leaving is safe, reversible, host-independent, or harmless to others.
- Confirm the Japanese narration requires explicit user request plus confirmation of the visible choice and likely impact before any future leave/end action.
- Confirm no role, host status, participant impact, recording/share/notes state, or recovery state is inferred beyond generic caution.
- Confirm Japanese coverage advances one step only and the next missing control-map step is `control-map-summary`.
