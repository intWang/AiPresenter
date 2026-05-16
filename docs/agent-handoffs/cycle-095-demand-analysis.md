# Cycle 095 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-recording` -> `narration.localizedText.ja`.

The user need is a Japanese control-map explanation for the `Start recording` entry that is useful without being operationally risky. Recording is not a passive toolbar discovery item: starting or stopping it changes meeting state, may notify or affect every participant, can create persistent meeting artifacts, and may be controlled by organization policy, host role, meeting permissions, and participant consent expectations.

Current verified localization baseline:

- Overall Japanese demo narration: `45/51`.
- `meeting-control-map-demo`: `16/22`.
- First missing `meeting-control-map-demo` Japanese step: `control-map-recording`.
- Remaining missing control-map steps: `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.

This cycle should let Japanese users understand where recording lives and why AiPresenter treats it carefully. The narration should make clear that `Start recording` is an entry in the More menu, but the control-map tour only explains the entry and does not start, stop, test, or validate recording.

## Presenter behavior

The presenter should treat `control-map-recording` as an explain-only step on `ringcentral.video.more.recording`.

Required behavior in real meeting context:

- Preserve `entrypointId: ringcentral.video.more.recording`.
- Preserve `operation: explain`.
- Preserve `placement: before`.
- Preserve the absence of `actionOffsetMs`.
- Preserve `ringcentral.video.more.recording.openSteps: []`.
- Explain `Start recording` as the recording entry that may be available from `More`.
- State that recording changes meeting state and can affect all participants.
- State that this control-map pass explains the entry only.
- Do not click `Start recording`, open a recording confirmation, start recording, stop recording, pause or resume recording, inspect recording state, or test whether recording is available.
- Do not rely on a prior `More` menu remaining open; `control-map-more` owns menu orientation, while `control-map-recording` owns the recording-specific safety boundary.
- Do not infer host status, organization policy, participant consent, meeting agreement, recording notifications, retention settings, or artifact availability from this narration step.

Good semantics: "Start recording changes the meeting state and may affect everyone in the meeting, so this tour only explains the entry. Starting or stopping recording requires explicit user confirmation, an allowed role or policy context, and clear participant consent or meeting agreement."

## Consent, policy, and host-permission language

The Japanese narration should include the safety boundary without turning into legal advice. It should say that any real start or stop action is conditional on three things:

- The user explicitly confirms the recording action.
- The current role, host permission, or organization policy allows recording.
- Participant consent, meeting agreement, or the visible/user-provided meeting context makes recording appropriate.

Use cautious product language, not legal conclusions. Prefer wording like `現在の役割やポリシーで許可されていること` and `参加者の同意や会議の合意が明確であること` over absolute claims such as "consent is complete" or "recording is allowed." AiPresenter should not promise that it can determine policy, host permission, or legal consent by itself in this localization slice.

Suggested semantic shape, not a required final string:

```text
Start recording は会議状態を変更し、参加者全員に影響する録画の入口です。このツアーでは入口を説明するだけで、録画の開始や停止は自動で行いません。実際に開始または停止する前には、ユーザーへ明確に確認し、現在の役割やポリシーで許可されていること、参加者の同意や会議の合意が明確であることを前提にします。
```

## Tone constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` style: calm, concise, and safety-aware. The line should sound like a meeting coach, not a compliance policy notice.

Recommended tone points:

- Keep the UI label `Start recording` in English when naming the source control.
- Use direct Japanese around it: `録画の入口`, `会議状態を変更`, `参加者全員に影響`, `入口を説明するだけ`.
- Include explicit non-execution wording such as `自動で行いません` or `開始や停止は実行しません`.
- Use `ユーザーへ明確に確認` or `ユーザーが明確に確認した場合` for the confirmation boundary.
- Mention role, permission, or policy as a condition, not as a capability AiPresenter has already verified.
- Mention participant consent or meeting agreement as a condition, not as an assumed fact.
- Stay focused on recording only; do not teach Notes, Background, Settings, Leave, post-meeting recordings, transcripts, summaries, or retention behavior in this step.
- Avoid dramatic or fear-based wording. Recording is sensitive, but the narration should remain practical.

Avoid wording that says or implies:

- AiPresenter starts, stops, clicks, toggles, tests, validates, or demonstrates recording.
- Recording is safe, private, local-only, invisible, reversible, or harmless.
- Every user has permission to record.
- Consent, host permission, organization policy, retention, or legal requirements are already satisfied.
- A recording, transcript, summary, insight, or post-meeting artifact will exist after the meeting.

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not edit tests, runtime code, source-index docs, profiles, fixtures, lockfiles, coverage files, or other handoff files in this demand-analysis handoff.
- Do not commit.
- Do not add Japanese narration for `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change the already-localized `control-map-more` narration from cycle 094.
- Do not change `meeting-controls-tour` narration, including the already-localized `explain-recording` step.
- Do not change English or Chinese narration.
- Do not add Japanese aliases, Q&A entries, presenter notes, locators, open steps, cleanup behavior, operation types, manual-control behavior, diagnostics behavior, CLI formatting, or telemetry.
- Do not add a confirmed recording workflow, permission checker, consent checker, live-state detector, notification detector, or artifact lookup.
- Do not click `Start recording`, open recording confirmation UI, start recording, stop recording, pause recording, resume recording, inspect recording state, read recording-related content, or capture live meeting evidence.
- Do not include screenshots, logs, or validation artifacts containing participant names, meeting IDs, invite links, room imagery, transcript text, note content, recording filenames, or other sensitive meeting context.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-recording` -> `narration.localizedText.ja`.
- Japanese localization advances from `45/51` to `46/51` overall.
- `meeting-control-map-demo` advances from `16/22` to `17/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-notes`.
- Remaining missing control-map steps become `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.
- `control-map-recording.action.entrypointId` remains `ringcentral.video.more.recording`.
- `control-map-recording.action.operation` remains `explain`.
- `control-map-recording.narration.placement` remains `before`.
- `control-map-recording` does not gain `actionOffsetMs`.
- `ringcentral.video.more.recording.openSteps` remains empty.
- The Japanese text is authored Japanese and includes `Start recording` or an unambiguous recording-entry reference.
- The Japanese text says recording changes meeting state and can affect participants.
- The Japanese text says the tour explains only the entry and does not automatically start or stop recording.
- The Japanese text requires explicit user confirmation before starting or stopping recording.
- The Japanese text includes role, host-permission, or policy awareness before recording can proceed.
- The Japanese text includes participant-consent or meeting-agreement awareness before recording can proceed.
- The Japanese text stays focused on recording and does not pull in Notes, Background, Settings, Leave, post-meeting artifacts, retention, transcripts, summaries, or legal advice.
- The text does not imply AiPresenter clicks, starts, stops, toggles, validates, monitors, or demonstrates recording.
- Japanese `--require-complete` remains incomplete because later `meeting-control-map-demo` steps remain untranslated.

Useful negative assertions for implementation tests:

```python
assert "ja" in recording_step.narration.localized_text
assert "ja" not in notes_step.narration.localized_text
assert recording_step.action.entrypoint_id == "ringcentral.video.more.recording"
assert recording_step.action.operation == "explain"
assert recording_step.narration.placement == "before"
assert recording_step.narration.action_offset_ms == 0
assert recording_entrypoint.open_steps == []
assert "Start recording" in ja_text or "録画" in ja_text
assert "会議状態" in ja_text
assert "参加者" in ja_text
assert "説明するだけ" in ja_text or "入口を説明" in ja_text
assert "確認" in ja_text
assert "権限" in ja_text or "役割" in ja_text or "ポリシー" in ja_text
assert "同意" in ja_text or "合意" in ja_text
assert "録画を開始します" not in ja_text
assert "録画を停止します" not in ja_text
assert "クリック" not in ja_text
assert "押します" not in ja_text
assert "選択します" not in ja_text
assert "許可されています" not in ja_text
assert "同意済み" not in ja_text
assert "録画中" not in ja_text
```

## Handoff notes for implementation

Implementation should be a narrow localization update only. Start from the current baseline after cycle 094: Japanese demo coverage `45/51`, `meeting-control-map-demo: 16/22`, first missing `control-map-recording`.

The closest references are:

- `meeting-controls-tour` -> `explain-recording`, already localized in Japanese with stronger recording safety language.
- `meeting-control-map-demo` -> `control-map-recording`, which currently has English and Chinese only and is already `operation: explain`.
- `ringcentral.video.more.recording`, whose presenter notes say `Start recording` is observed under `More`, is state-changing during a tour, and should be explained without clicking unless the user explicitly asks to start recording.

Keep this step separate from the following detailed safety slices. `control-map-recording` teaches recording consent, policy, permission, and no-start boundaries; `control-map-notes` should separately teach notes/transcript panel boundaries; `control-map-background` should separately teach appearance and privacy boundaries; `control-map-settings` should separately teach configuration boundaries; `control-map-leave` should separately teach exit confirmation.

After implementation, expected localization report key lines should be:

```text
Localization report: 46/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 17/22 narration localized
  missing: control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

This demand-analysis handoff intentionally creates only `docs/agent-handoffs/cycle-095-demand-analysis.md`. It does not modify package YAML, code, tests, source-index files, other docs, or git history.
