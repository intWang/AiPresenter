# Cycle 097 Technical Scan: Control Map Background JA

Scope for the next implementation slice: add Japanese narration only to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-background`.

This scan intentionally writes only this handoff file. Do not modify YAML, code, tests, source-index docs, profiles, fixtures, lockfiles, coverage files, or git history during the scan. Other agents already have local edits in `.coverage`, `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, and `tests/unit/test_material_packages.py`; preserve them and do not revert unrelated work.

## Baseline Verified

Command run:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Current output confirms:

- Overall Japanese demo narration: `47/51`
- `meeting-control-map-demo`: `18/22`
- First missing Japanese step: `control-map-background`
- Remaining missing control-map steps: `control-map-background`, `control-map-settings`, `control-map-leave`, `control-map-summary`
- Japanese Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- `questionAliases.ja` remains `3/27` entrypoints and `9` aliases

Working-tree note: current tests already appear partly prepared for this slice, with `48/51`, `19/22`, and `control-map-settings` expectations plus a focused `test_meeting_control_map_has_japanese_background_narration`. The package YAML still lacks `localizedText.ja` on `control-map-background`, so those test edits are likely parallel implementation prep. Reconcile with them; do not overwrite or revert them.

## Target Step Shape

`meeting-control-map-demo` -> `control-map-background` currently has Chinese localized narration but no Japanese localized narration:

```yaml
  - id: control-map-background
    title: Background settings
    action:
      entrypointId: ringcentral.video.more.background
      operation: open
    narration:
      text: Background settings protect presentation quality and privacy. You can turn effects off, blur the room,
        use a built-in image or video background, or upload your own.
      localizedText:
        zh: 背景设置关系到展示效果和隐私。你可以关闭效果、模糊房间、选择内置图片或视频背景，也可以上传自己的背景。
      placement: during
      actionOffsetMs: 400
```

Add only `localizedText.ja` under this step. Preserve the English text, Chinese text, step order, `entrypointId`, `operation: open`, `placement: during`, and `actionOffsetMs: 400`.

## Expected Coverage After Adding Background

After adding only `localizedText.ja` to `control-map-background`:

- Overall Japanese demo narration: `47/51` -> `48/51`
- `meeting-control-map-demo`: `18/22` -> `19/22`
- First missing Japanese step: `control-map-background` -> `control-map-settings`
- Remaining missing control-map steps should be `control-map-settings`, `control-map-leave`, and `control-map-summary`
- Japanese Q&A should remain `12/12` questions and `12/12` answers
- `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases
- `--require-complete` for Japanese should still fail because later `meeting-control-map-demo` steps remain untranslated

## Focused Tests To Update/Add

`tests/unit/test_material_packages.py`:

- If not already covered by parallel edits, update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`:
  - `report.demo_localized_steps`: `47` -> `48`
  - `meeting-control-map-demo.localized_steps`: `18` -> `19`
  - first missing step: `control-map-background` -> `control-map-settings`
  - keep total demo steps `51`, control-map total `22`, Q&A counts, alias counts, and `required_localization_complete is False`
- Add or keep `test_meeting_control_map_has_japanese_background_narration` after the notes-focused test.
- Update adjacent focused tests that assert the first missing control-map step, especially notes and any later control-map Japanese tests, so they expect `control-map-settings`.
- In the background focused test, keep `control-map-notes` localized and assert `control-map-settings` remains without Japanese narration.
- Reuse the existing `meeting-controls-tour` background settings test as the closest safety pattern, but target `meeting-control-map-demo` and the `control-map-background` step.

`tests/unit/test_cli.py`:

- In both Japanese localization-report tests, update or keep:
  - `Localization report: 47/51 demo steps` -> `Localization report: 48/51 demo steps`
  - `- meeting-control-map-demo: 18/22 narration localized` -> `- meeting-control-map-demo: 19/22 narration localized`
  - `missing: control-map-background` -> `missing: control-map-settings`
- Keep `missing: explain-leave` absent.
- Keep localized Q&A counts and `questionAliases.ja present on 3/27 entrypoints (9 aliases)` unchanged.
- Keep `test_localization_report_require_complete_fails_for_japanese_demo_gap` exit code `1`.

`tests/unit/test_diagnostics.py`:

- In `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`, update or keep `47/51 demo steps` -> `48/51 demo steps`.
- Keep status `FAIL`, detail `required ja localization incomplete`, and Q&A detail assertions unchanged.

`tests/unit/test_package_demo.py`:

- No new executor behavior should be needed. Existing settings-cleanup coverage already exercises `ringcentral.video.more.background` opening More, opening Background, and closing the Settings dialog. Add only if route behavior changes, which this slice should avoid.

## Route And Action Assertions For Background

The focused background test should lock the settings route and no-change boundary:

```python
assert step.action.entrypoint_id == "ringcentral.video.more.background"
assert step.action.operation == "open"
assert step.narration.placement == "during"
assert step.narration.action_offset_ms == 400
assert "ja" in step.narration.localized_text
assert report.flow_by_id["meeting-control-map-demo"].missing_step_ids[0] == (
    "control-map-settings"
)
```

Also assert:

- `background_entrypoint.question_aliases` does not gain `ja`
- global Japanese alias coverage remains `3` entrypoints and `9` aliases
- `[open_step.target for open_step in background_entrypoint.open_steps] == ["More", "Background"]`
- first open step remains `action == "clickWindowControl"`, `target == "More"`, `match["occurrence"] == "3"`, and `match["controlType"] == "button"`
- second open step remains `action == "clickWindowControl"`, `target == "Background"`, and `match["cleanup"] == "settings"`
- presenter notes still mention Settings dialog tabs, `Off`, `Blur`, built-in static backgrounds, video backgrounds, upload, `Mirror my video`, and closing the Settings dialog before continuing
- previous step `control-map-notes` remains localized and uses `ringcentral.video.more.notes`
- next step `control-map-settings` remains without Japanese narration and becomes the first missing step

## Safe Japanese Text Constraints

Use natural Japanese product-demo narration consistent with the existing `meeting-controls-tour` background narration, but keep this control-map step concise.

Required semantic content:

- Mention `Background`.
- Explain that Background opens the Settings dialog directly on the Background tab.
- Mention presentation quality, appearance, and privacy.
- Mention options: `Off`, `Blur`, built-in image/static backgrounds, video backgrounds, upload, and `Mirror my video`.
- State that the tour displays/explains choices only.
- State that AiPresenter does not change effects, select Blur, choose or upload a background, apply a video background, or toggle mirror unless the user explicitly asks.
- Mention closing the Settings dialog after explanation or before continuing.

Suggested Japanese text:

```yaml
        ja: Background は Settings ダイアログの Background タブを開き、表示品質とプライバシーに関わる背景の見え方を確認する場所です。ここには Off、Blur、内蔵画像、動画背景、アップロード、Mirror my video などの候補があります。ツアーでは選択肢を表示して説明するだけで、ユーザーが明確に求めるまで背景効果を変更せず、Blur を選ばず、画像や動画背景を選択またはアップロードしません。説明後は Settings ダイアログを閉じます。
```

Positive text assertions can include:

- `Background`
- `背景`
- `プライバシー`
- `見え方`
- `Off`
- `Blur`
- `画像`
- `動画背景`
- `アップロード`
- `Mirror my video`
- `候補`
- `表示して説明`
- `変更せず`
- `選ばず`
- `閉じます`

Negative assertions should reject execution or unsafe promise language:

- `Blur にします`
- `背景を変更します`
- `背景を選択します`
- `背景を選びます`
- `画像をアップロードします`
- `動画背景を適用します`
- `Mirror my video をオンにします`
- `クリックします`
- `自動`

Do not add Japanese `questionAliases` for background in this slice. Plain Japanese background questions should remain future alias work unless explicitly assigned.

## Source Index Update If Needed

Current `docs/knowledge/ringcentral-video/source-index.md` says Japanese coverage includes the overview through `more/recording/notes` steps of `meeting-control-map-demo`.

If the implementation assignment includes source-index maintenance, update only the localization coverage sentence so it advances from coverage through `more/recording/notes` to coverage through `more/recording/notes/background`, while keeping remaining control-map narration and other entrypoint aliases marked as future work.

Expected wording concept:

- Before: `.../share/reactions/raise-hand/more/recording/notes steps of meeting-control-map-demo`
- After: `.../share/reactions/raise-hand/more/recording/notes/background steps of meeting-control-map-demo`

Do not imply full `meeting-control-map-demo` Japanese coverage until all 22 steps are localized.

## Verification Commands

Focused red/green pytest command for the implementation round:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_notes_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_background_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Expected localization report after implementation:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected key lines:

```text
Localization report: 48/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
- meeting-control-map-demo: 19/22 narration localized
  missing: control-map-settings, control-map-leave, control-map-summary
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

Implementation diff should be limited to one `localizedText.ja` block for `control-map-background`, directly necessary test expectation updates, and the source-index coverage sentence if included by the implementation assignment.

## Safe Implementation Constraints

- Do not localize `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change English or Chinese narration.
- Do not change `operationEntrypoints`, `openSteps`, presenter notes, action placement, offsets, cleanup, aliases, Q&A, profiles, source code, or tests beyond directly assigned implementation files.
- Do not choose Blur, select any image, apply a video background, upload a custom background, toggle `Mirror my video`, open unrelated settings, or leave the meeting.
- Do not add screenshots, logs, fixtures, or review artifacts that capture participant names, meeting identifiers, account details, camera previews, room details, custom background filenames, uploaded images, recording state, transcript content, note content, or private messages.
- Treat Background as a privacy and appearance surface: explain where the choices are, close the Settings dialog, and require explicit user intent before any future change to the local visual state.
