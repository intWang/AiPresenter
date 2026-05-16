# Cycle 096 Risk Scan: RingCentral Video Control Map Notes JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-notes`.

Current Japanese localization baseline is `46/51` demo steps overall, with `meeting-control-map-demo` at `17/22`; the first missing step is `control-map-notes`. This slice is high-sensitivity because the step opens the `Notes and Transcript` side panel. The observed panel offers `Start notes` and `Also record this meeting`, so a wording or route mistake could start notes, create or expose transcript-adjacent content, or trigger recording-related behavior.

The safe target is a narrow open-and-explain localization. The implementation should preserve:

- `action.entrypointId: ringcentral.video.more.notes`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 400`
- the `ringcentral.video.more.notes` route through `More` occurrence `3`, then `onconf.controls.NOTES`
- `match.alternateTargets: Notes`
- `match.cleanup: sidePanel`
- English and Chinese narration text
- the step position after `control-map-recording` and before `control-map-background`

The core safety rule is: the panel may be opened so the user can see where notes and transcript controls live, but the presenter must not start notes, start transcript-related capture, start recording, read note/transcript content, summarize content, or leave the side panel open after the explanation.

## Allowed behavior

- Add exactly one Japanese narration block for `meeting-control-map-demo` -> `control-map-notes`.
- Describe `Notes and Transcript` as the side panel for meeting notes and transcript-related controls.
- Mention that the panel can expose `Start notes` and `Also record this meeting`.
- Explain that starting notes or recording may affect meeting state, participant expectations, consent, organization policy, and host or meeting permissions.
- Say this control-map step opens the panel for location and role explanation only.
- Say AiPresenter does not press `Start notes`, enable recording, or begin any capture in the tour.
- Say visible note or transcript content is private unless the user explicitly asks and the displayed context is confirmed.
- Close the side panel after the explanation so `control-map-background` starts from a neutral meeting surface.

## Forbidden behavior

- Do not click `Start notes`.
- Do not click, enable, select, or imply selection of `Also record this meeting`.
- Do not start notes, transcription, captions, AI notes, summaries, recording, or any persistent meeting artifact.
- Do not read, quote, summarize, translate, or infer from note content, transcript text, captions, participant speech, meeting summaries, or recording artifacts.
- Do not imply AiPresenter has host permission, participant consent, organization approval, retention-policy compliance, or access to post-meeting artifacts.
- Do not add or change `openSteps`, cleanup behavior, action offsets, aliases, presenter notes, Q&A, source code, tests, source-index text, validation targets, or later demo steps as part of this risk scan.
- Do not broaden this slice into `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`, recording execution, post-meeting artifacts, or alias expansion.

## Panel Open And Cleanup

`ringcentral.video.more.notes` is an executable open route, unlike the explain-only recording entrypoint. That makes cleanup part of the safety boundary:

- The route should still open `More` occurrence `3`, then select the `onconf.controls.NOTES` menu item with alternate target `Notes`.
- The implementation must not change the route into a direct toolbar assumption unless a separate validation task owns that locator update.
- The final menu-item step must keep `cleanup: sidePanel`.
- Review should fail if the Notes side panel remains open before `control-map-background`.
- Review should fail if any note-start, transcript-start, recording prompt, recording indicator, consent dialog, toast, or post-meeting artifact appears as a result of this localization slice.
- If live validation is used, capture only sanitized control labels and cleanup status. Do not capture note text, transcript text, participant names, meeting IDs, recording state details, account details, or spoken content.

## Consent And Policy Wording

The Japanese narration should separate panel explanation from action. It may say that starting notes or recording can involve participant consent, meeting agreement, organization policy, and role or permission checks. It must not claim that consent is already obtained, policy compliance is guaranteed, recording is available, or the current user can start recording.

Safer wording should be conditional: "may require confirmation", "requires an explicit user request", and "only after visible context and permissions are confirmed." Avoid legalistic overreach. The goal is a product-demo safety boundary, not legal advice.

## Suggested Japanese Text

Recommended `localizedText.ja`:

```yaml
        ja: Notes and Transcript は、会議メモと文字起こしを扱うパネルです。ここには Start notes と Also record this meeting があり、メモの開始や録画は会議状態、参加者の同意、組織ポリシーに関わる可能性があります。このコントロールマップではパネルの場所と役割だけを説明し、Start notes や録画は開始しません。表示されたメモや文字起こしの内容は、ユーザーが明確に求め、表示状況が確認できるまで読み上げたり要約したりしません。説明後はパネルを閉じます。
```

Useful positive assertions can include:

- `Notes and Transcript`
- `Start notes`
- `Also record this meeting`
- `会議メモ`
- `文字起こし`
- `録画`
- `会議状態`
- `参加者の同意`
- `組織ポリシー`
- `場所と役割`
- `開始しません`
- `読み上げたり要約したりしません`
- `パネルを閉じます`

Unsafe or overclaiming phrases should be rejected when they imply execution or content access:

- `Start notes を押します`
- `Start notes をクリック`
- `Also record this meeting を選択します`
- `メモを開始します`
- `文字起こしを開始します`
- `録画します`
- `録画を開始します`
- `内容を読み上げます`
- `内容を要約します`
- `自動`
- `すぐに`
- `同意済み`
- `許可されています`
- `安全なので`

## Localization Boundary

Expected coverage movement after implementation:

- Overall Japanese demo narration: `46/51` -> `47/51`
- `meeting-control-map-demo`: `17/22` -> `18/22`
- First missing Japanese step: `control-map-notes` -> `control-map-background`
- Remaining missing steps should start with `control-map-background`, then `control-map-settings`, `control-map-leave`, and `control-map-summary`

Do not imply full Japanese coverage for `meeting-control-map-demo` until all 22 steps are localized. Japanese `--require-complete` should still fail after this slice because later control-map steps remain untranslated.

## Suggested Test Guardrails

Implementation tests should confirm:

- `control-map-notes` has `localizedText.ja`.
- `control-map-background` remains without Japanese narration and becomes the first missing step.
- Coverage updates exactly to `47/51` overall and `18/22` for `meeting-control-map-demo`.
- `control-map-notes.action.entrypoint_id == "ringcentral.video.more.notes"`.
- `control-map-notes.action.operation == "open"`.
- `control-map-notes.narration.placement == "during"`.
- `control-map-notes.narration.action_offset_ms == 400`.
- `ringcentral.video.more.notes` keeps open-step targets `More` and `onconf.controls.NOTES`.
- The first Notes open step keeps `occurrence == "3"` and `controlType == "button"`.
- The second Notes open step keeps `alternateTargets == "Notes"`, `controlType == "menuitem"`, and `cleanup == "sidePanel"`.
- `questionAliases.ja` remains unchanged for Notes; global Japanese alias coverage remains `3/27` entrypoints and `9` aliases.
- The previous `control-map-recording` step remains localized and explain-only.
- The next `control-map-background` step remains a separate unlocalized open step.
- The Japanese copy explains the panel, start controls, consent or policy sensitivity, no automatic start, no reading/summarizing content, and panel cleanup.

Review should also update CLI and diagnostics localization-report expectations only if the implementation owner scope includes those test files. This risk-scan handoff itself does not edit tests.

## Commit Hygiene

This risk-scan agent should create only `docs/agent-handoffs/cycle-096-risk-scan.md`.

At scan time, `git status --short` showed `.coverage` modified, and a concurrent `tests/unit/test_material_packages.py` diff appeared while this scan was running. Treat those as existing or parallel-agent work:

- Do not stage `.coverage`.
- Do not overwrite, revert, or normalize `tests/unit/test_material_packages.py` unless the implementation owner deliberately takes over that file.
- Re-check `git status --short` immediately before staging because other agents may be working in parallel.
- Keep the implementation commit narrow: one YAML localization block and only directly necessary test/source-index expectation updates if assigned.
- Do not stage unrelated handoff docs, generated artifacts, screenshots, logs, or other agents' WIP.
- If tests are run, prefer commands that avoid creating or refreshing coverage artifacts, and verify `.coverage` remains unstaged.

## Reviewer Checklist

- Confirm this risk-scan subagent changed only `docs/agent-handoffs/cycle-096-risk-scan.md`.
- Confirm no YAML, code, tests, `.coverage`, screenshots, logs, or generated files were changed by this risk-scan subagent.
- Confirm the implementation adds only `meeting-control-map-demo` -> `control-map-notes` -> `narration.localizedText.ja`.
- Confirm the Notes route remains an open-and-explain side-panel route with `cleanup: sidePanel`.
- Confirm `Start notes` and `Also record this meeting` are described but not clicked, selected, or implied as started.
- Confirm no note, transcript, caption, summary, recording, or post-meeting artifact content is read, summarized, stored, or captured.
- Confirm the Japanese narration mentions consent or policy sensitivity conditionally without overclaiming permission or compliance.
- Confirm Japanese coverage advances one step only and the next missing control-map step is `control-map-background`.
