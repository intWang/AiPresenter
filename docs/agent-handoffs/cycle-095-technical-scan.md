# Cycle 095 Technical Scan: Control Map Recording JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-recording`.

This scan intentionally creates only this handoff file. Do not modify YAML, code, tests, source index, profiles, or other docs in this scan. Other agents may already have local edits; preserve them and do not revert unrelated files.

## Baseline Verified

Command run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current output confirms:

- Overall Japanese demo narration: `45/51`
- `meeting-control-map-demo`: `16/22`
- First missing Japanese step: `control-map-recording`
- Remaining missing steps: `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

Working-tree note: at scan time, `.coverage` was already modified and `tests/unit/test_material_packages.py` had concurrent uncommitted edits that appear to prepare recording expectations. Do not overwrite or revert those files unless the implementation owner deliberately takes over that work.

## Target Step Shape

`meeting-control-map-demo` -> `control-map-recording` currently has Chinese localized narration but no Japanese localized narration:

```yaml
  - id: control-map-recording
    title: Recording
    action:
      entrypointId: ringcentral.video.more.recording
      operation: explain
    narration:
      text: Recording changes the meeting state and may affect consent, so it is explain-only in this tour. I would
        ask before starting or stopping it.
      localizedText:
        zh: 录制会改变会议状态，也可能涉及参会人的同意。所以这里我只解释入口，不会自动开始或停止录制。
      placement: before
```

Add only `localizedText.ja` under this step. Preserve the English text, Chinese text, step order, action route, `operation: explain`, and `placement: before`. Do not add `actionOffsetMs`.

The matching operation entrypoint is:

```yaml
- id: ringcentral.video.more.recording
  title: Start recording
  area: More menu
  purpose: Start recording the meeting.
  questionAliases:
    zh:
    - 录制
    - 录像
    - 记录会议
  openSteps: []
  presenterNotes:
  - Observed under More as Start recording.
  - Treat this as a state-changing action during a tour.
  - AiPresenter should explain this entry without clicking it unless the user explicitly asks to start recording.
```

Important route boundary: this target is intentionally explain-only. `ringcentral.video.more.recording` has no executable `openSteps`, so the implementation must not add a route that clicks `Start recording`.

## Expected Coverage After Adding Recording

After adding only `localizedText.ja` to `control-map-recording`:

- Overall Japanese demo narration: `45/51` -> `46/51`
- `meeting-control-map-demo`: `16/22` -> `17/22`
- First missing Japanese step: `control-map-recording` -> `control-map-notes`
- Remaining missing steps should start with `control-map-notes`, followed by `control-map-background`, `control-map-settings`, `control-map-leave`, and `control-map-summary`
- Japanese Q&A should remain `12/12` questions and `12/12` answers
- `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese should still fail because later `meeting-control-map-demo` steps remain untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`:

- Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.demo_localized_steps`: `45` -> `46`
  - `meeting-control-map-demo.localized_steps`: `16` -> `17`
  - first missing step: `control-map-recording` -> `control-map-notes`
  - keep total demo steps `51`, control-map total `22`, Q&A counts, alias counts, and `required_localization_complete is False`
- Add `test_meeting_control_map_has_japanese_recording_narration` after `test_meeting_control_map_has_japanese_more_narration`.
- Update adjacent focused tests that assert the current first missing control-map step, especially the existing control-map camera-menu/share/reactions/raise-hand/more Japanese tests, from `control-map-recording` to `control-map-notes`.
- In the More focused test, change the adjacent recording assertion from `"ja" not in recording_step.narration.localized_text` to `"ja" in recording_step.narration.localized_text`.

`tests/unit/test_cli.py`:

- In both Japanese localization-report tests, update:
  - `Localization report: 45/51 demo steps` -> `Localization report: 46/51 demo steps`
  - `- meeting-control-map-demo: 16/22 narration localized` -> `- meeting-control-map-demo: 17/22 narration localized`
  - `missing: control-map-recording` -> `missing: control-map-notes`
- Keep `missing: explain-leave` absent.
- Keep localized Q&A counts and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged.
- Keep `test_localization_report_require_complete_fails_for_japanese_demo_gap` exit code `1`.

`tests/unit/test_diagnostics.py`:

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update `45/51 demo steps` -> `46/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A detail assertions unchanged.

## Route And Action Assertions For Recording

The new focused recording test should lock the explain-only boundary:

```python
assert step.action.entrypoint_id == "ringcentral.video.more.recording"
assert step.action.operation == "explain"
assert step.narration.placement == "before"
assert step.narration.action_offset_ms is None
assert "ja" in step.narration.localized_text
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-notes"
)
```

Also assert:

- `recording_entrypoint.open_steps == []`
- `recording_entrypoint.question_aliases` does not gain `ja`
- global Japanese alias coverage remains `3` entrypoints and `9` aliases
- presenter notes still include `Observed under More as Start recording.`
- presenter notes still include `Treat this as a state-changing action during a tour.`
- presenter notes still say AiPresenter should explain without clicking unless explicitly asked to start recording
- previous step `control-map-more` remains localized and remains an `open` operation on `ringcentral.video.toolbar.more`
- next step `control-map-notes` remains without Japanese narration and becomes the first missing step

## Safe Japanese Text Constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-controls-tour` recording narration, but keep this control-map step concise.

Required semantic content:

- Mention `Start recording`.
- Explain that recording changes the meeting state.
- Mention participant consent or agreement.
- Mention policy or permission constraints, including host permission where appropriate.
- Make clear this is only an entrypoint explanation.
- State that AiPresenter does not start or stop recording in this tour.
- State that actual start/stop requires a clear user request and confirmation.
- Avoid implying recording can be started casually or silently.

Suggested Japanese text:

```yaml
        ja: Start recording は会議の状態を変え、参加者の同意、組織ポリシー、ホスト権限に関わる録画の入口です。このコントロールマップでは入口だけを説明し、録画の開始や停止は行いません。実際に扱う場合は、ユーザーが明確に求め、通知や参加者の合意が確認できてから進めます。
```

Positive text assertions can include:

- `Start recording`
- `会議の状態`
- `参加者`
- `同意`
- `ポリシー`
- `ホスト権限`
- `入口`
- `録画の開始や停止は行いません`
- `明確に求め`
- `通知`

Negative assertions should reject execution or unsafe promise language:

- `録画します`
- `録画を始めます`
- `録画を開始します`
- `録画を停止します`
- `Start recording をクリック`
- `クリックします`
- `自動`
- `すぐに`
- `安全なので`
- `許可されています`

Do not add Japanese `questionAliases` for recording in this slice. Plain Japanese recording questions should remain future alias work unless explicitly assigned.

## Source Index Update If Needed

Current `docs/knowledge/ringcentral-video/source-index.md` says Japanese coverage includes the overview through `more` steps of `meeting-control-map-demo`.

If the implementation assignment includes source-index maintenance, update only the localization coverage sentence so it advances from coverage through `more` to coverage through `recording`, while keeping remaining control-map narration and other entrypoint aliases marked as future work.

Expected wording concept:

- Before: `.../share/reactions/raise-hand/more steps of meeting-control-map-demo`
- After: `.../share/reactions/raise-hand/more/recording steps of meeting-control-map-demo`

Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused red/green pytest command for the implementation round:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_more_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_recording_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected localization report after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
Localization report: 46/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 17/22 narration localized
  missing: control-map-notes, control-map-background, control-map-settings, control-map-leave, control-map-summary
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

Implementation diff should be limited to one `localizedText.ja` block for `control-map-recording`, directly necessary test expectation updates, and the source-index coverage sentence if included by the implementation assignment.

## Safe Implementation Constraints

- Do not localize `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change English or Chinese narration.
- Do not change `operationEntrypoints`, `openSteps`, presenter notes, action placement, offsets, cleanup, aliases, Q&A, profiles, source code, or tests beyond the directly assigned implementation files.
- Do not start, stop, pause, resume, or promise recording.
- Do not click `Start recording` during tests or manual validation for this slice.
- Do not add screenshots, logs, fixtures, or review artifacts that capture participant names, meeting identifiers, recording state, transcript content, or account details.
