# Cycle 096 Technical Scan: Control Map Notes JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-notes`.

This scan intentionally writes only this handoff file. Do not modify YAML, code, tests, source-index docs, profiles, fixtures, lockfiles, coverage files, or git history during the scan. Other agents may already have local edits; preserve them and do not revert unrelated files.

## Baseline Verified

Command run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current output confirms:

- Overall Japanese demo narration: `46/51`
- `meeting-control-map-demo`: `17/22`
- First missing Japanese step: `control-map-notes`
- Remaining missing control-map steps: `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

Working-tree note: during the scan, `.coverage` was already modified and other agents added concurrent uncommitted work in `tests/unit/test_material_packages.py`, later also `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, plus untracked `docs/agent-handoffs/cycle-096-demand-analysis.md` and `docs/agent-handoffs/cycle-096-risk-scan.md`. Some material-package edits appeared to prepare expected `47/51`, `18/22`, and `control-map-background` assertions. Do not overwrite or revert those edits; reconcile with them if implementing this slice.

## Target Step Shape

`meeting-control-map-demo` -> `control-map-notes` currently has Chinese localized narration but no Japanese localized narration:

```yaml
  - id: control-map-notes
    title: Notes and transcript
    action:
      entrypointId: ringcentral.video.more.notes
      operation: open
    narration:
      text: Notes and Transcript is where meeting notes can be started. It can also record the meeting, so I keep
        the panel visible for explanation and avoid starting anything automatically.
      localizedText:
        zh: Notes and Transcript 是会议笔记和转录面板。这里可以启动笔记，也可能触发录制相关动作，所以我只打开面板说明，不自动点开始。
      placement: during
      actionOffsetMs: 400
```

Add only `localizedText.ja` under this step. Preserve the English text, Chinese text, step order, `entrypointId`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.

The matching operation entrypoint is:

```yaml
- id: ringcentral.video.more.notes
  title: Notes and transcript
  area: Meeting toolbar
  purpose: Open the Notes and Transcript side panel.
  questionAliases:
    zh:
    - 笔记
    - 转录
    - 会议笔记
  openSteps:
  - action: clickWindowControl
    target: More
    match:
      occurrence: '3'
      controlType: button
  - action: clickWindowControl
    target: onconf.controls.NOTES
    match:
      alternateTargets: Notes
      controlType: menuitem
      cleanup: sidePanel
  presenterNotes:
  - In the current observed build, Notes is nested under the More menu.
  - The clickable menu item is exposed to UI Automation as onconf.controls.NOTES, while Notes is visible text.
  - Older layouts may expose Notes directly on the toolbar; prefer the More menu route when a direct Notes button is absent.
  - Observed panel offers Start notes and Also record this meeting.
  - Starting notes or recording changes meeting state, so the default tour only explains the panel.
  - Close the panel before continuing.
```

Important route boundary: this target may open the Notes and Transcript side panel, but must not start notes, start recording, read note or transcript content, or summarize private content unless the user explicitly requests it and the displayed context is confirmed.

## Expected Coverage After Adding Notes

After adding only `localizedText.ja` to `control-map-notes`:

- Overall Japanese demo narration: `46/51` -> `47/51`
- `meeting-control-map-demo`: `17/22` -> `18/22`
- First missing Japanese step: `control-map-notes` -> `control-map-background`
- Remaining missing control-map steps should start with `control-map-background`, followed by `control-map-settings`, `control-map-leave`, and `control-map-summary`
- Japanese Q&A should remain `12/12` questions and `12/12` answers
- `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese should still fail because later `meeting-control-map-demo` steps remain untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage` if not already covered by concurrent edits:
  - `report.demo_localized_steps`: `46` -> `47`
  - `meeting-control-map-demo.localized_steps`: `17` -> `18`
  - first missing step: `control-map-notes` -> `control-map-background`
  - keep total demo steps `51`, control-map total `22`, Q&A counts, alias counts, and `required_localization_complete is False`
- Add `test_meeting_control_map_has_japanese_notes_narration` after `test_meeting_control_map_has_japanese_recording_narration`.
- Update adjacent focused tests that assert the first missing control-map step, especially existing camera-menu/share/reactions/raise-hand/more/recording Japanese tests, so they expect `control-map-background`.
- In the recording focused test, keep `control-map-recording` localized and add an adjacent assertion that `control-map-notes` now has Japanese narration while `control-map-background` remains missing.
- Reuse the existing `meeting-controls-tour` notes test as the closest safety pattern, but target `meeting-control-map-demo` and the `control-map-notes` step.

`tests/unit/test_cli.py`:

- In both Japanese localization-report tests, update:
  - `Localization report: 46/51 demo steps` -> `Localization report: 47/51 demo steps`
  - `- meeting-control-map-demo: 17/22 narration localized` -> `- meeting-control-map-demo: 18/22 narration localized`
  - `missing: control-map-notes` -> `missing: control-map-background`
- Keep `missing: explain-leave` absent.
- Keep localized Q&A counts and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged.
- Keep `test_localization_report_require_complete_fails_for_japanese_demo_gap` exit code `1`.

`tests/unit/test_diagnostics.py`:

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `46/51 demo steps` -> `47/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A detail assertions unchanged.

## Route And Action Assertions For Notes

The new focused notes test should lock the panel-open route and no-start boundary:

```python
assert step.action.entrypoint_id == "ringcentral.video.more.notes"
assert step.action.operation == "open"
assert step.narration.placement == "during"
assert step.narration.action_offset_ms == 400
assert "ja" in step.narration.localized_text
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-background"
)
```

Also assert:

- `notes_entrypoint.question_aliases` does not gain `ja`
- global Japanese alias coverage remains `3` entrypoints and `9` aliases
- `[open_step.target for open_step in notes_entrypoint.open_steps] == ["More", "onconf.controls.NOTES"]`
- first open step remains `action == "clickWindowControl"`, `target == "More"`, `match["occurrence"] == "3"`, and `match["controlType"] == "button"`
- second open step remains `action == "clickWindowControl"`, `target == "onconf.controls.NOTES"`, `match["alternateTargets"] == "Notes"`, `match["controlType"] == "menuitem"`, and `match["cleanup"] == "sidePanel"`
- presenter notes still mention `Start notes`, `Also record this meeting`, state-changing notes or recording behavior, and closing the panel before continuing
- previous step `control-map-recording` remains localized, `operation: explain`, and has no `openSteps`
- next step `control-map-background` remains without Japanese narration and becomes the first missing step

## Safe Japanese Text Constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-controls-tour` notes narration, but keep this control-map step concise.

Required semantic content:

- Mention `Notes` and `Notes and Transcript`.
- Mention `Start notes` and `Also record this meeting`.
- Explain that notes/transcript is a side panel or panel location for meeting notes and transcript work.
- State that starting notes or recording remains under user control.
- State that the tour opens or shows the panel for explanation only.
- State that AiPresenter does not start notes, start recording, read note/transcript content, summarize content, or promise post-meeting artifacts unless the user explicitly asks and visible context is confirmed.
- Mention closing the panel after explanation or before continuing.

Suggested Japanese text:

```yaml
        ja: Notes は Notes and Transcript パネルを開き、会議メモや文字起こしに関する入口を確認できる場所です。ここには Start notes と Also record this meeting があるため、ツアーではパネルを説明するだけにし、ユーザーが明確に求めるまでメモ開始や録画は行いません。メモや文字起こしの内容も、明確な依頼と確認済みの表示状況なしには読み上げたり要約したりしません。説明後はパネルを閉じます。
```

Positive text assertions can include:

- `Notes`
- `Notes and Transcript`
- `Start notes`
- `Also record this meeting`
- `パネル`
- `会議メモ`
- `文字起こし`
- `説明するだけ`
- `ユーザー`
- `明確に求める`
- `録画`
- `読み上げたり要約したりしません`
- `閉じます`

Negative assertions should reject execution or unsafe promise language:

- `Start notes を押します`
- `Also record this meeting を選択します`
- `メモを開始します`
- `録画を開始します`
- `録画します`
- `文字起こしします`
- `内容を読み上げます`
- `要約します`
- `会議後に共有します`
- `自動`
- `すぐに`
- `許可されています`

Do not add Japanese `questionAliases` for notes in this slice. Plain Japanese notes/transcript questions should remain future alias work unless explicitly assigned.

## Source Index Update If Needed

Current `docs/knowledge/ringcentral-video/source-index.md` says Japanese coverage includes the overview through `more/recording` steps of `meeting-control-map-demo`.

If the implementation assignment includes source-index maintenance, update only the localization coverage sentence so it advances from coverage through `more/recording` to coverage through `more/recording/notes`, while keeping remaining control-map narration and other entrypoint aliases marked as future work.

Expected wording concept:

- Before: `.../share/reactions/raise-hand/more/recording steps of meeting-control-map-demo`
- After: `.../share/reactions/raise-hand/more/recording/notes steps of meeting-control-map-demo`

Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused red/green pytest command for the implementation round:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_more_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_recording_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_notes_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected localization report after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
Localization report: 47/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 18/22 narration localized
  missing: control-map-background, control-map-settings, control-map-leave, control-map-summary
questionAliases.ja present on 3/27 entrypoints (9 aliases)
```

Japanese required-complete should still fail:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: exit code `1`, with `Localization coverage incomplete for ja.`

Diff checks for the implementation round:

```powershell
git diff -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
git diff --check -- packages/ringcentral-video.yaml tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py docs/knowledge/ringcentral-video/source-index.md
```

Implementation diff should be limited to one `localizedText.ja` block for `control-map-notes`, directly necessary test expectation updates, and the source-index coverage sentence if included by the implementation assignment.

## Safe Implementation Constraints

- Do not localize `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change English or Chinese narration.
- Do not change `operationEntrypoints`, `openSteps`, presenter notes, action placement, offsets, cleanup, aliases, Q&A, profiles, source code, or tests beyond the directly assigned implementation files.
- Do not start notes, start recording, toggle captions, enable transcript, send messages, change settings, or leave the meeting.
- Do not read, quote, summarize, export, or promise access to notes, transcripts, captions, summaries, insights, recordings, participant names, meeting IDs, meeting links, account data, or private messages unless a later task explicitly adds verified behavior and tests for it.
- Do not add screenshots, logs, fixtures, or review artifacts that capture participant names, meeting identifiers, recording state, transcript content, note content, or account details.
