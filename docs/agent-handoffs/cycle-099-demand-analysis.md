# Cycle 099 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-leave` -> `narration.localizedText.ja`.

Japanese users need a clear control-map explanation for `Leave` that treats it as an exit and possible meeting-ending path, not as a routine navigation control. The narration should help a presenter explain where the control is and why it matters while preserving the strongest safety boundary: AiPresenter must not click `Leave`, choose a leave/end option, or confirm any exit action unless the user explicitly requests it and confirms the visible consequence.

Current Japanese localization baseline after cycle 098 and commit `fb8c416`:

- Overall Japanese demo narration: `49/51`.
- `meeting-control-map-demo`: `20/22`.
- Missing `meeting-control-map-demo` Japanese steps: `control-map-leave`, `control-map-summary`.
- First missing `meeting-control-map-demo` Japanese step: `control-map-leave`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.

This cycle should let Japanese users understand that `Leave` ends the current user's presence in the meeting and, depending on host role and visible UI, may expose stronger options such as ending the meeting for everyone. The step should remain a map explanation only. The final `control-map-summary` is intentionally left for a later cycle.

## Presenter behavior

The presenter should treat `control-map-leave` as an explain-only step on the toolbar `Leave` control.

Required behavior in real meeting context:

- Preserve `entrypointId: ringcentral.video.toolbar.leave`.
- Preserve `operation: explain`.
- Preserve `placement: before`.
- Do not add `actionOffsetMs` unless the implementation owner has a separate, explicit reason to change the step shape.
- Explain that `Leave` is the exit path from the current meeting.
- Explain that leaving ends the presenter's current meeting participation or presence.
- Explain that host-context UI may offer an end-meeting option that affects all participants.
- Keep the step at the control-map level: location, role, and safety boundary only.
- Do not click `Leave` during this demo step.
- Do not open the leave confirmation menu or dialog just to show it.
- Do not choose `Leave meeting`, `End meeting for all`, `End meeting`, `Leave`, `OK`, `Confirm`, or any equivalent destructive option.
- Do not close the RingCentral Video window, sign out, disconnect audio, stop recording, stop notes, or otherwise alter meeting state as part of this step.
- If the meeting is already showing a leave/end confirmation because of user or external action, explain the visible choice generically and ask for explicit direction. Do not select any destructive option on the user's behalf.

Good semantics: "`Leave` is the control for exiting the current meeting. It can end your own presence in the meeting, and for a host it may expose an option that ends the meeting for everyone. In this control map, AiPresenter explains the control only. It does not click `Leave` or confirm leaving or ending the meeting unless the user explicitly asks, the visible option and its impact are confirmed, and the user gives a final confirmation."

## Destructive leave and end-meeting boundaries

This slice is safety-sensitive because `Leave` can terminate the user's active meeting state. It may also branch into host-only choices that affect every participant. The Japanese narration should make the destructive boundary explicit without becoming alarmist.

Separate boundaries to preserve:

- Personal exit boundary: leaving the meeting ends the current user's presence in the live meeting. It should not happen during a tour unless the user explicitly requests it.
- All-participant boundary: host flows may include `End meeting for all` or equivalent options. Those affect everyone, so they require an even stronger confirmation than a personal exit.
- Confirmation boundary: an implementation must not treat a generic "show me Leave" request as permission to leave. Real execution requires a current, explicit command to leave or end, visible option identification, consequence restatement, and a final confirmation.
- Role boundary: AiPresenter should not assume the user is host, cohost, attendee, or allowed to end the meeting unless the visible UI or the user states it.
- State boundary: AiPresenter should not infer whether it is safe, polite, policy-compliant, or expected to leave. It should only describe the control and wait for explicit instruction.
- Cleanup boundary: because the step is `operation: explain`, there should be no new dialog cleanup path. If a confirmation surface is already present, prefer pausing for user instruction over auto-selecting a destructive path.

Any real leave or end-meeting action, outside this localization slice, should require all of the following:

- The user explicitly asks to leave the current meeting or end it.
- The visible UI option is identified, such as personal leave versus end for everyone.
- AiPresenter restates the consequence in plain language.
- The user gives a final confirmation after seeing or hearing the consequence.
- No recording, notes, transcript, chat, invite, participant, or meeting identity content is read or summarized unless the user separately requests it.

## Tone constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` voice: calm, concise, practical, and safety-aware. The narration should sound like a meeting coach, not a legal warning.

Recommended tone points:

- Keep the UI label `Leave` in English.
- Use direct Japanese around the label: `退出`, `現在の会議`, `会議から退出`, `参加状態`, `終了`, `全員に影響`, `場所と役割だけ`, `明確に求め`, `表示された選択肢と影響`, `確定しません`.
- Mention host/end-meeting risk as conditional, not guaranteed.
- Say AiPresenter explains the control and does not execute it without confirmation.
- Keep the copy short enough for live narration.
- Avoid panic wording, policy claims, or moralizing about whether the user should leave.

Avoid wording that says or implies:

- AiPresenter clicks `Leave` during the tour.
- AiPresenter opens the leave dialog to demonstrate it.
- The user has already confirmed leaving or ending the meeting.
- The current user is definitely host or definitely allowed to end the meeting.
- Leaving is safe, recommended, expected, reversible, or harmless.
- Ending the meeting for everyone is equivalent to personally leaving.
- The presenter can decide from context that the meeting should end.

Suggested semantic shape, not a required final string:

```text
Leave は、現在の会議から退出するための入口です。退出すると自分の会議参加状態が終了し、ホストの場合は End meeting for all のように全員へ影響する終了オプションが表示されることがあります。このコントロールマップでは場所と役割だけを説明し、ユーザーが明確に求め、表示された選択肢と影響を確認できるまで、AiPresenter は Leave をクリックしたり、退出や会議終了を確定したりしません。
```

## Explicit out-of-scope actions

This demand-analysis handoff must not:

- Edit `packages/ringcentral-video.yaml`.
- Edit tests, runtime code, source-index docs, profiles, fixtures, lockfiles, coverage files, or other handoff files.
- Commit, stage, or revert files.
- Touch unrelated dirty work, including `.coverage` or any parallel-agent edits.

The next implementation slice should not:

- Add Japanese narration for `control-map-summary`.
- Change the already-localized `control-map-settings` or earlier control-map narration.
- Change `meeting-controls-tour` narration, including its already-localized `explain-leave` step.
- Change English or Chinese narration.
- Add Japanese aliases, Q&A entries, presenter notes, routes, locators, cleanup behavior, operation types, manual-control behavior, diagnostics behavior, CLI formatting, telemetry, or source-index wording unless explicitly assigned.
- Click or automate `Leave`, `Leave meeting`, `End meeting`, `End meeting for all`, `Confirm`, `OK`, or any equivalent destructive control.
- Add a leave-confirmation workflow, host-role detector, meeting-ending workflow, post-meeting summary, participant notification, recording cleanup, notes cleanup, transcript cleanup, or policy checker.
- Inspect, describe, summarize, screenshot, store, or log meeting IDs, invite links, participant names, chat content, notes, transcripts, recording state, account details, role labels, or other private meeting context unless a separate user request explicitly requires it.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-leave` -> `narration.localizedText.ja`.
- Japanese localization advances from `49/51` to `50/51` overall.
- `meeting-control-map-demo` advances from `20/22` to `21/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-summary`.
- Remaining missing control-map steps contain only `control-map-summary`.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.
- `control-map-leave.action.entrypointId` remains `ringcentral.video.toolbar.leave`.
- `control-map-leave.action.operation` remains `explain`.
- `control-map-leave.narration.placement` remains `before`.
- The Japanese text is authored Japanese and mentions `Leave`.
- The Japanese text explains that `Leave` exits the current meeting or ends the user's current meeting participation.
- The Japanese text mentions that host-context end-meeting options may affect everyone.
- The Japanese text says this control-map step explains the location/role only.
- The Japanese text says AiPresenter does not click `Leave` or confirm leaving/ending without explicit user request and confirmation.
- The Japanese text distinguishes personal leaving from ending the meeting for everyone.
- The Japanese text does not imply host status, permission, safety, reversibility, policy compliance, or user consent.
- Japanese `--require-complete` remains incomplete because `control-map-summary` remains untranslated.

Useful negative assertions for implementation tests:

```python
assert "ja" in leave_step.narration.localized_text
assert "ja" not in summary_step.narration.localized_text
assert leave_step.action.entrypoint_id == "ringcentral.video.toolbar.leave"
assert leave_step.action.operation == "explain"
assert leave_step.narration.placement == "before"
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == [
    "control-map-summary"
]
assert "Leave" in ja_text
assert "退出" in ja_text or "会議から退出" in ja_text
assert "全員" in ja_text
assert "明確" in ja_text
assert "確認" in ja_text
assert "クリック" in ja_text or "実行" in ja_text or "確定" in ja_text
assert "クリックします" not in ja_text
assert "退出します" not in ja_text
assert "終了します" not in ja_text
assert "End meeting for all を選びます" not in ja_text
assert "安全" not in ja_text
assert "ホストです" not in ja_text
```

## Handoff notes for implementation

Implementation should be a narrow localization update only. Start from the current baseline: Japanese demo coverage `49/51`, `meeting-control-map-demo: 20/22`, missing `control-map-leave` and `control-map-summary`.

The closest references are:

- `meeting-controls-tour` -> `explain-leave`, already localized in Japanese. Reuse its calm destructive-control posture, but adapt it to the control-map step and current baseline.
- `meeting-control-map-demo` -> `control-map-leave`, which currently has English and Chinese narration only and already uses an explain-only toolbar entrypoint.
- `meeting-control-map-demo` -> `control-map-settings`, localized in cycle 098, which established the pattern for explaining a risky control without broadening into the next step.

Keep this step separate from the final summary. `control-map-leave` teaches the exit/end-meeting boundary; `control-map-summary` should separately close the map of status, people, media, interaction, advanced tools, and closeout.

Parallel-agent note: the worktree may contain unrelated or preparatory edits from other agents. Reconcile with current files at implementation time, but do not revert or overwrite unrelated dirty work.

After implementation, expected localization report key lines should be:

```text
Localization report: 50/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 21/22 narration localized
  missing: control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

This demand-analysis handoff intentionally creates only `docs/agent-handoffs/cycle-099-demand-analysis.md`. It does not modify package YAML, code, tests, source-index files, other docs, coverage artifacts, or git history.
