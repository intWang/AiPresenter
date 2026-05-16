# Cycle 100 Demand Analysis

## User Need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-summary` -> `narration.localizedText.ja`.

Japanese users need a concise closing summary that helps them understand the whole RingCentral Video control map as a set of areas, not as a list of commands to execute. This is the final wrap-up after the control-map tour has already covered the top bar, people and collaboration controls, media readiness, sharing and interaction, deeper tools, settings, recording, notes, background, and `Leave`.

Current Japanese localization baseline after cycle 099 and commit `f5feaa1`:

- Overall Japanese demo narration: `50/51`.
- `meeting-control-map-demo`: `21/22`.
- Only missing `meeting-control-map-demo` Japanese step: `control-map-summary`.
- Japanese Q&A remains complete at `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.

This slice should complete Japanese demo narration coverage by giving the user a calm final mental model: the top bar is for meeting status and troubleshooting, people controls are for collaboration, media controls are for readiness, sharing and interaction controls are for participation and feedback, and `More` leads to deeper settings or more cautious actions.

## Presenter Behavior

The presenter should treat `control-map-summary` as an explain-only closing step on the overview entrypoint.

Required behavior:

- Preserve `entrypointId: ringcentral.video.overview`.
- Preserve `operation: explain`.
- Preserve `placement: before`.
- Do not add `actionOffsetMs` unless a separate implementation owner explicitly changes the step shape.
- Summarize the whole control map rather than repeating every individual control.
- Mention the top bar for status and troubleshooting.
- Mention people controls for participants and collaboration.
- Mention media controls for readiness before speaking or appearing on camera.
- Mention sharing, interaction, and feedback controls.
- Mention `More` as the place for deeper settings and riskier or more cautious actions.
- Keep it as a closing statement with a clear sense of completion.
- Do not present the summary as proof that the control map fully covers every possible live RingCentral Video UI state.

Good semantic shape, not a required final string:

```text
これが RingCentral Video のコントロールマップです。上部では状態確認とトラブルシューティング、メンバー関連の操作では参加者と共同作業、メディア操作では発話や映像の準備を確認します。共有、リアクション、挙手は会議への参加とフィードバックの入口で、More にはより深い設定や、録画、背景、退出のように慎重に扱う操作がまとまっています。
```

## Safety And Privacy Boundaries

The summary must remain an explanation. It should not start, open, click, toggle, send, share, record, leave, or change any meeting state.

Privacy and safety boundaries to preserve:

- Do not start audio, video, screen sharing, recording, notes, transcript, translation, reactions, raise hand, invite, meeting lock, or any other feature.
- Do not click `Leave`, recording, sharing, settings, `More`, `Background`, `Notes and Transcript`, participants controls, chat controls, or any other risk-bearing control during the summary.
- Do not read or summarize chat messages, participant names, participant roles, captions, transcript, notes, recording content, meeting IDs, invite links, device names, account details, background thumbnails, or private tabs.
- Do not promise that the control map fully covers the user's current live UI, every host or attendee variant, every policy-dependent option, or every RingCentral Video release.
- Do not imply AiPresenter has inspected hidden panels, private content, or unavailable features.
- Do not infer whether recording, notes, transcripts, captions, post-meeting artifacts, participant actions, or host controls are available.
- If the live UI differs from the known map, describe only the visible area generically and avoid claims about missing or hidden controls.

The summary can mention risky areas by category, but it must not normalize executing them. `More` and deeper settings should be framed as places to proceed carefully, especially for recording, background changes, settings changes, notes/transcript, sharing, and leaving.

## Tone Constraints

Use natural Japanese product-demo narration. The copy should sound like a presenter closing a guided tour, not like a compliance warning or marketing flourish.

Recommended tone points:

- Keep it short enough for live narration.
- Prefer clear, practical Japanese: `これが...です`, `上部では`, `メンバー関連`, `メディア操作`, `共有`, `リアクション`, `挙手`, `More`, `より深い設定`, `慎重に扱う操作`.
- Preserve English UI labels where the package already does so, especially `RingCentral Video` and `More`.
- Use a calm closeout rhythm with a strong sense of completion.
- Avoid exaggerated claims such as "everything is covered", "complete control", "perfectly safe", "always", "guaranteed", or "all issues can be solved here".
- Avoid stiff legal phrasing. The step should be safety-aware, not alarmist.

## Acceptance Criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-summary` -> `narration.localizedText.ja`.
- Japanese localization advances from `50/51` to `51/51` overall.
- `meeting-control-map-demo` advances from `21/22` to `22/22`.
- `missing` is empty for Japanese demo narration.
- Japanese `--require-complete` passes.
- Japanese Q&A remains `12/12` questions and `12/12` answers.
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases.
- `control-map-summary.action.entrypointId` remains `ringcentral.video.overview`.
- `control-map-summary.action.operation` remains `explain`.
- `control-map-summary.narration.placement` remains `before`.
- The Japanese text is authored Japanese and contains CJK characters.
- The Japanese text summarizes top bar/status/troubleshooting, people controls/collaboration, media readiness, sharing/interaction/feedback, and `More`/deeper settings/riskier actions.
- The Japanese text does not say AiPresenter starts, clicks, toggles, opens, sends, records, shares, leaves, reads private content, or changes settings.
- The Japanese text does not claim the map is exhaustive for real-time UI variants.

Expected localization report key lines after implementation:

```text
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 22/22 narration localized
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese `--require-complete` should no longer emit the previous failure line:

```text
Localization coverage incomplete for ja.
```

The command should exit successfully.

## Suggested Test Assertions

Focused implementation tests can update existing Japanese localization expectations and add a summary-specific assertion block.

Useful positive assertions:

```python
assert report.demo_localized_steps == 51
assert report.demo_total_steps == 51
assert report.required_localization_complete is True
assert report.flow_by_id["meeting-control-map-demo"].localized_steps == 22
assert report.flow_by_id["meeting-control-map-demo"].total_steps == 22
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids == ()
assert report.qa_localized_questions == 12
assert report.qa_localized_answers == 12
assert report.entrypoints_with_aliases == 3
assert report.alias_total == 9

assert step.action.entrypoint_id == "ringcentral.video.overview"
assert step.action.operation == "explain"
assert step.narration.placement == "before"
assert "ja" in step.narration.localized_text
assert has_cjk(ja_text)
assert "RingCentral Video" in ja_text
assert "コントロールマップ" in ja_text
assert "上部" in ja_text
assert "状態" in ja_text
assert "トラブルシューティング" in ja_text
assert "メンバー" in ja_text or "参加者" in ja_text
assert "共同作業" in ja_text or "コラボレーション" in ja_text
assert "メディア" in ja_text
assert "準備" in ja_text
assert "共有" in ja_text
assert "リアクション" in ja_text or "フィードバック" in ja_text
assert "More" in ja_text
assert "設定" in ja_text
assert "慎重" in ja_text or "リスク" in ja_text
```

Useful negative assertions:

```python
assert "クリックします" not in ja_text
assert "押します" not in ja_text
assert "開きます" not in ja_text
assert "開始します" not in ja_text
assert "送信します" not in ja_text
assert "共有します" not in ja_text
assert "録画します" not in ja_text
assert "退出します" not in ja_text
assert "変更します" not in ja_text
assert "切り替えます" not in ja_text
assert "読み上げます" not in ja_text
assert "要約します" not in ja_text
assert "すべて" not in ja_text
assert "完全" not in ja_text
assert "必ず" not in ja_text
assert "保証" not in ja_text
assert "安全" not in ja_text
```

CLI and diagnostics expectations should move from incomplete Japanese coverage to complete Japanese coverage:

```python
assert "Localization report: 51/51 demo steps" in result.stdout
assert "- meeting-control-map-demo: 22/22 narration localized" in result.stdout
assert "missing:" not in result.stdout
assert "Localization coverage incomplete for ja." not in result.stdout
```

`test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing` should either be renamed and updated to expect a passing Japanese localization check, or replaced with a new incomplete-package fixture test so diagnostics still retains negative coverage without depending on `ringcentral-video` being incomplete.

## Do Not Do

This demand-analysis handoff must not:

- Edit `packages/ringcentral-video.yaml`.
- Edit tests, runtime code, source-index docs, profiles, fixtures, lockfiles, coverage files, or other handoff files.
- Commit, stage, or revert files.
- Touch unrelated dirty work, including `.coverage` or any parallel-agent edits.

The next implementation slice should not:

- Change any Japanese narration except `control-map-summary`.
- Change English or Chinese narration.
- Change already-localized Japanese steps, including `control-map-leave`.
- Add Japanese Q&A, aliases, presenter notes, routes, locators, cleanup behavior, operation types, manual-control behavior, telemetry, or source-index wording unless a separate implementation assignment explicitly owns those files.
- Start a feature, click a control, open a panel for demonstration, or add a runtime behavior path.
- Add a new host-role detector, recording workflow, sharing workflow, settings workflow, leave workflow, notes/transcript workflow, post-meeting summary, or UI completeness checker.
- Inspect, describe, summarize, screenshot, store, or log chat, participants, captions, notes, transcripts, recordings, meeting identity, device identity, account identity, or other private context.

## Handoff Notes For Implementation

Implementation should be a narrow localization completion update only. Start from the current baseline: Japanese demo coverage `50/51`, `meeting-control-map-demo: 21/22`, and missing only `control-map-summary`.

The closest references are:

- `meeting-control-map-demo` -> `control-map-overview`, which introduces the map structure.
- `meeting-control-map-demo` -> `control-map-more`, which frames deeper and cautious controls.
- `meeting-control-map-demo` -> `control-map-leave`, which established the final destructive-control boundary before the summary.
- The English `control-map-summary` text, which should be localized as a closing map summary, not expanded into a new operational step.

Parallel-agent note: the worktree may contain unrelated or preparatory edits from other agents. Reconcile with current files at implementation time, but do not revert or overwrite unrelated dirty work.

This demand-analysis handoff intentionally creates only `docs/agent-handoffs/cycle-100-demand-analysis.md`. It does not modify package YAML, code, tests, source-index files, other docs, coverage artifacts, or git history.
