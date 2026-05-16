# Cycle 096 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-notes` -> `narration.localizedText.ja`.

The user need is a Japanese control-map explanation for `Notes and Transcript` that is useful in a live meeting without crossing consent or meeting-state boundaries. This step is more sensitive than a passive toolbar label because the panel can expose meeting content and offers actions such as `Start notes` and `Also record this meeting`. Japanese users should understand where notes and transcript controls live, what the panel is for, and why AiPresenter opens it only to explain the surface instead of starting notes, recording, transcription-adjacent behavior, or reading content.

Current localization baseline after cycle 095:

- Overall Japanese demo narration: `46/51`.
- `meeting-control-map-demo`: `17/22`.
- First missing `meeting-control-map-demo` Japanese step: `control-map-notes`.
- Remaining missing control-map steps: `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.

This cycle should let Japanese users understand that `Notes and Transcript` is the panel for meeting notes and transcript-related controls, while making clear that starting notes, enabling recording, reading transcript content, or summarizing note content requires an explicit user request and verified visible context.

## Presenter behavior

The presenter should treat `control-map-notes` as a panel-opening explanation step on `ringcentral.video.more.notes`.

Required behavior in real meeting context:

- Preserve `entrypointId: ringcentral.video.more.notes`.
- Preserve `operation: open`.
- Preserve `placement: during`.
- Preserve `actionOffsetMs: 400`.
- Preserve the existing `ringcentral.video.more.notes.openSteps` route: open `More`, then select the UI Automation menu item `onconf.controls.NOTES` with `alternateTargets: Notes`.
- Preserve the existing `cleanup: sidePanel` behavior so the panel is closed before continuing.
- Explain that `Notes and Transcript` is the panel for notes and transcript-related controls.
- Explain that the panel may include `Start notes` and `Also record this meeting`.
- Keep the panel visible only long enough to explain the location and role.
- Do not click `Start notes`, `Also record this meeting`, recording controls, transcript controls, caption controls, translation controls, or any generated-content action inside the panel.
- Do not start meeting notes, start or stop recording, enable transcription, read transcript text, read note text, summarize visible content, export content, or claim a post-meeting artifact will exist.
- Do not infer consent, host permission, organization policy, recording status, note availability, transcript availability, or participant agreement from the panel opening successfully.

Good semantics: "Notes and Transcript opens the panel for meeting notes and transcript-related controls. Because `Start notes` and `Also record this meeting` can change meeting state and may involve participant consent, this control-map pass only explains the panel. AiPresenter does not start notes, record, or read note/transcript content unless the user explicitly asks and the visible meeting context is confirmed."

## Notes, transcript, and recording-adjacent consent boundaries

The Japanese narration should describe the panel without turning the control-map step into a consent flow or legal policy explanation. It should communicate three separate boundaries:

- Notes boundary: starting notes can create or alter meeting artifacts, so it stays under explicit user control.
- Transcript boundary: transcript or caption text is meeting content, so AiPresenter should not read, quote, summarize, store, or infer from it unless the user clearly asks and the visible content is verified.
- Recording-adjacent boundary: `Also record this meeting` inherits the recording safety model from cycle 095; AiPresenter must not enable recording or imply that recording is authorized just because the option is visible.

Any real action inside the panel should be conditional on all of the following:

- The user explicitly asks for the action and confirms the intended scope.
- The current visible UI makes the action and its consequences clear.
- Current role, host permission, or organization policy allows the action.
- Participant consent, meeting agreement, or visible/user-provided meeting context makes the action appropriate.

Use cautious product language, not legal conclusions. Prefer phrases equivalent to `ユーザーが明確に求めた場合`, `表示内容を確認できる場合`, `参加者の同意や会議の合意`, and `現在の役割やポリシーで許可される場合`. Avoid claiming that AiPresenter has independently verified consent, policy, permission, transcript availability, recording status, or artifact retention.

Suggested semantic shape, not a required final string:

```text
Notes and Transcript は、会議ノートと文字起こし関連コントロールのパネルです。ここには Start notes や Also record this meeting が表示される場合がありますが、ノートの開始や録画は会議状態と参加者の同意に関わるため、このコントロールマップでは場所と役割だけを説明します。ユーザーが明確に求め、表示内容と会議の合意を確認できるまで、ノート、文字起こし、録画の開始、内容の読み上げや要約は行いません。
```

## Tone constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` voice: calm, concise, safety-aware, and practical. The line should sound like a meeting coach explaining a sensitive panel, not a compliance notice.

Recommended tone points:

- Keep UI labels in English when naming the source controls: `Notes and Transcript`, `Start notes`, and `Also record this meeting`.
- Use direct Japanese around the labels: `会議ノート`, `文字起こし`, `パネル`, `場所と役割`, `ユーザーが明確に求めるまで`.
- Include explicit non-execution wording such as `開始しません`, `録画しません`, `読み上げたり要約したりしません`, or `場所と役割だけを説明します`.
- Mention consent or meeting agreement as a condition, not as an assumed fact.
- Mention visible context or displayed content as a condition before reading or summarizing any notes/transcript material.
- Stay focused on the Notes and Transcript panel. Do not teach Background, Settings, Leave, Summary, post-meeting artifact lookup, or retention behavior in this step.
- Avoid dramatic or fear-based wording. The panel is sensitive, but the narration should remain brief and usable in a demo.

Avoid wording that says or implies:

- AiPresenter starts notes, starts transcription, starts recording, clicks `Start notes`, clicks `Also record this meeting`, or tests whether those actions work.
- Notes, transcript, or recording content is safe to read, private, local-only, already consented to, already authorized, or harmless.
- Every user has permission to start notes or recording.
- Consent, host permission, organization policy, recording notifications, or legal requirements are already satisfied.
- A recording, transcript, notes document, summary, insight, or post-meeting artifact will exist after the meeting.

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not edit tests, runtime code, source-index docs, profiles, fixtures, lockfiles, coverage files, or other handoff files in this demand-analysis handoff.
- Do not commit.
- Do not add Japanese narration for `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change the already-localized `control-map-recording` narration from cycle 095.
- Do not change `meeting-controls-tour` narration, including the already-localized `explain-notes` step.
- Do not change English or Chinese narration.
- Do not add Japanese aliases, Q&A entries, presenter notes, locators, open steps, cleanup behavior, operation types, manual-control behavior, diagnostics behavior, CLI formatting, telemetry, or source-index coverage wording unless the implementation assignment explicitly expands scope.
- Do not add a confirmed notes workflow, transcript reader, recording workflow, permission checker, consent checker, live-state detector, notification detector, artifact lookup, or post-meeting summarizer.
- Do not click `Start notes`, click `Also record this meeting`, start notes, stop notes, start recording, stop recording, enable transcription, enable captions, enable translation, read transcript text, read note text, summarize meeting content, export content, or capture live meeting evidence.
- Do not include screenshots, logs, or validation artifacts containing participant names, meeting IDs, invite links, room imagery, note content, transcript text, recording filenames, or other sensitive meeting context.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-notes` -> `narration.localizedText.ja`.
- Japanese localization advances from `46/51` to `47/51` overall.
- `meeting-control-map-demo` advances from `17/22` to `18/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-background`.
- Remaining missing control-map steps become `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.
- `control-map-notes.action.entrypointId` remains `ringcentral.video.more.notes`.
- `control-map-notes.action.operation` remains `open`.
- `control-map-notes.narration.placement` remains `during`.
- `control-map-notes.narration.actionOffsetMs` remains `400`.
- `ringcentral.video.more.notes.openSteps` still opens `More`, selects `onconf.controls.NOTES` with `alternateTargets: Notes`, and keeps `cleanup: sidePanel`.
- The Japanese text is authored Japanese and mentions `Notes and Transcript` or an unambiguous notes/transcript panel reference.
- The Japanese text mentions notes and transcript-related controls.
- The Japanese text mentions the state-changing or consent-sensitive nature of starting notes and recording-adjacent actions.
- The Japanese text says this control-map pass explains the panel location/role only.
- The Japanese text says AiPresenter does not start notes, start recording, read transcript/note content, or summarize content automatically.
- The Japanese text requires explicit user request or confirmation before any action inside the panel.
- The Japanese text includes participant-consent, meeting-agreement, visible-context, permission, or policy awareness before proceeding.
- The Japanese text stays focused on Notes and Transcript and does not pull in Background, Settings, Leave, Summary, retention, post-meeting artifact lookup, or legal advice.
- The text does not imply AiPresenter clicks, starts, records, transcribes, reads, summarizes, exports, validates, monitors, or demonstrates sensitive panel actions.
- Japanese `--require-complete` remains incomplete because later `meeting-control-map-demo` steps remain untranslated.

Useful negative assertions for implementation tests:

```python
assert "ja" in notes_step.narration.localized_text
assert "ja" not in background_step.narration.localized_text
assert notes_step.action.entrypoint_id == "ringcentral.video.more.notes"
assert notes_step.action.operation == "open"
assert notes_step.narration.placement == "during"
assert notes_step.narration.action_offset_ms == 400
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-background"
)
assert "Notes and Transcript" in ja_text or "文字起こし" in ja_text
assert "ノート" in ja_text or "会議ノート" in ja_text
assert "Start notes" in ja_text or "開始" in ja_text
assert "Also record this meeting" in ja_text or "録画" in ja_text
assert "説明" in ja_text
assert "同意" in ja_text or "合意" in ja_text or "確認" in ja_text
assert "開始します" not in ja_text
assert "録画します" not in ja_text
assert "クリック" not in ja_text
assert "押します" not in ja_text
assert "読み上げます" not in ja_text
assert "要約します" not in ja_text
assert "許可されています" not in ja_text
assert "同意済み" not in ja_text
```

## Handoff notes for implementation

Implementation should be a narrow localization update only. Start from the current baseline after cycle 095: Japanese demo coverage `46/51`, `meeting-control-map-demo: 17/22`, first missing `control-map-notes`.

The closest references are:

- `meeting-controls-tour` -> `explain-notes`, already localized in Japanese with a fuller Notes and Transcript safety boundary.
- `meeting-control-map-demo` -> `control-map-notes`, which currently has English and Chinese only and already opens the panel with `operation: open`.
- `ringcentral.video.more.notes`, whose presenter notes say Notes is nested under `More`, the UI Automation item is `onconf.controls.NOTES`, the panel offers `Start notes` and `Also record this meeting`, starting notes or recording changes meeting state, and the panel should be closed before continuing.
- `meeting-control-map-demo` -> `control-map-recording`, localized in cycle 095, which owns the broader recording entrypoint safety boundary and should remain unchanged.

Keep this step separate from the following control-map slices. `control-map-notes` teaches the Notes and Transcript panel, note/transcript content boundaries, and recording-adjacent caution; `control-map-background` should separately teach appearance and privacy boundaries; `control-map-settings` should separately teach configuration boundaries; `control-map-leave` should separately teach exit confirmation; `control-map-summary` should separately close the tour.

After implementation, expected localization report key lines should be:

```text
Localization report: 47/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 18/22 narration localized
  missing: control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

This demand-analysis handoff intentionally creates only `docs/agent-handoffs/cycle-096-demand-analysis.md`. It does not modify package YAML, code, tests, source-index files, other docs, or git history.
