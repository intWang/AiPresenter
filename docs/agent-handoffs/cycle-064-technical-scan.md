# Cycle 064 Technical Scan: meeting-controls-tour / explain-participants JA narration

## Scope

Scan only for the next implementation pass. The proposed implementation should add Japanese `localizedText.ja` narration to one step:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-participants`
- Entrypoint: `ringcentral.video.toolbar.participants`
- Operation: `open`

Do not change runtime behavior, open steps, action offsets, aliases, Q&A, flow order, YAML structure outside this step, or unrelated docs as part of this narration slice unless the implementation owner explicitly expands scope.

## Local Context Read

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- Recent handoffs:
  - `docs/agent-handoffs/cycle-062-summary.md`
  - `docs/agent-handoffs/cycle-063-technical-scan.md`
  - `docs/agent-handoffs/cycle-063-implementation.md`
  - `docs/agent-handoffs/cycle-063-review.md`
  - `docs/agent-handoffs/cycle-063-summary.md`

Current verified baseline from:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

- `Localization report: 14/51 demo steps`
- `meeting-controls-tour: 7/22 narration localized`
- first missing `meeting-controls-tour` step: `explain-participants`
- Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- Japanese aliases remain partial: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Important current-tree note: the focused Cycle 064 tests already appear to be advanced to the expected post-implementation state. The package YAML has not yet been advanced for `explain-participants`, so the implementation owner should expect the advanced tests to fail until the YAML gets the Japanese narration.

## Source Step

Current English narration:

```yaml
text: Participants opens the roster panel. From here you can confirm who is in the room and access people
  controls such as invite, lock, mute, and more options.
```

Current Chinese narration:

```yaml
zh: Participants 会打开参会人列表。这里可以确认谁在会议里，也能进入邀请、锁定会议、静音和更多成员操作。
```

Relevant entrypoint notes for `ringcentral.video.toolbar.participants`:

- Use this to answer questions about attendee count and meeting control.
- Do not identify participants unless the UI text is verified and allowed.
- Observed panel has Participant and Chat tabs, search, invite, lock, mute, raise-hand, and more controls.
- Toggle the Participants button or close the side panel before opening Chat.

Relevant prior slices:

- Cycle 062 localized `explain-add-coworkers`, with privacy language for names, email addresses, suggestions, and private invite links.
- Cycle 063 localized `explain-invite`, and confirmed Japanese coverage at `14/51`, `meeting-controls-tour: 7/22`, first missing `explain-participants`.
- Cycle 064 should treat Participants as its own roster privacy slice because it can expose participant names, roles, counts, and host controls.

## Recommended Japanese Wording

Recommended insertion under `narration.localizedText`:

```yaml
        ja: Participants は参加者一覧パネルを開きます。ここでは会議にいる人数を確認し、招待、会議のロック、ミュート、その他の参加者操作に進めます。名前や役割は、ユーザーが明示的に求め、表示内容が確認されるまで読み上げません。説明したらパネルを閉じ、ユーザーの明確な指示なしに他の参加者をミュートしません。
```

Rationale:

- Preserves visible UI label `Participants`.
- Covers roster count with `人数`, matching the current test expectation.
- Covers private roster fields with `名前` and `役割`.
- Keeps the key safety rule: do not read identities or roles unless the user explicitly asks and visible content is verified.
- Mentions closing the side panel before moving on.
- Says the presenter does not mute other participants without explicit instruction.
- Avoids implying AiPresenter locks the meeting, changes participant state, removes people, or reads a roster by default.

## Expected Count Changes

After adding only this `localizedText.ja` entry:

- Overall Japanese demo narration: `14/51` -> `15/51`
- `meeting-controls-tour`: `7/22` -> `8/22`
- First missing `meeting-controls-tour` step should advance from `explain-participants` to `explain-chat`
- Q&A counts should remain `12/12` questions and `12/12` answers
- Japanese alias counts should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`
- `--require-complete` for Japanese should still fail because the package remains partially localized.

## Tests To Update/Add

The current test files already contain the expected Cycle 064 assertions. If the implementation owner is working from this tree, no test edits should be needed; the YAML narration should turn the existing red tests green.

Existing expected test coverage to preserve:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - expects `report.demo_localized_steps == 15`
  - expects `report.flow_by_id["meeting-controls-tour"].localized_steps == 8`
  - keeps `report.demo_total_steps == 51`
  - keeps `meeting-controls-tour` total at `22`
  - keeps Q&A and alias expectations unchanged

- `tests/unit/test_material_packages.py::test_meeting_controls_tour_has_japanese_participants_narration`
  - asserts Japanese text exists and contains CJK
  - asserts `Participants`
  - asserts `参加者`
  - asserts `人数`
  - asserts `名前`
  - asserts `役割`
  - asserts `読み上げません`
  - asserts `閉じます`
  - asserts `ミュートしません`

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expects `Localization report: 15/51 demo steps`
  - expects `- meeting-controls-tour: 8/22 narration localized`
  - expects `missing: explain-chat`
  - keeps Q&A and alias lines unchanged

- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expects exit code `1`
  - expects `Localization report: 15/51 demo steps`
  - expects `- meeting-controls-tour: 8/22 narration localized`
  - expects `missing: explain-chat`
  - keeps `Localization coverage incomplete for ja.`

- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - expects diagnostic detail to include `15/51 demo steps`
  - keeps `required ja localization incomplete`
  - keeps `12/12 Q&A questions` and `12/12 Q&A answers`

If applying this scan to a branch that does not already have the participant-focused test, add it with the assertions listed above. Do not add Japanese `questionAliases` for new entrypoints in this pass; `ringcentral.video.toolbar.participants` already has Japanese aliases, and expected alias counts above assume no alias change.

## Expected CLI Output Changes

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected relevant output after implementation:

```text
Language: ja
- meeting-controls-tour: 8/22 narration localized
  missing: explain-chat, explain-microphone, explain-audio-menu, explain-camera, explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
Localization report: 15/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected result after implementation:

- Exit code: `1`
- Includes `Localization report: 15/51 demo steps`
- Includes `- meeting-controls-tour: 8/22 narration localized`
- Includes `missing: explain-chat`
- Includes `Localization coverage incomplete for ja.`

## Verification Commands

Run targeted tests with the project venv:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_participants_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional broader package-localization sweep:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k "japanese or localization_status or participants"
```

CLI smoke checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Optional doctor localization preflight:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --language ja --require-localization
```

Expected doctor result remains nonzero because Japanese localization is still incomplete, but the localization detail should move to `15/51 demo steps`.

## Notes For Implementer

- Keep the YAML insertion under `localizedText.ja`, not `localizedText.jp`.
- Preserve existing `zh`, `placement: during`, and `actionOffsetMs: 350`.
- Keep product/UI labels in English where they match visible UI: `Participants`.
- This step opens a side panel, not a modal. Keep the narration about closing the panel, but do not change cleanup or operation behavior in a narration-only pass.
- The Participants panel may show private names, roles, and controls that affect other people. Default narration should describe capabilities and verified counts, not read identities or perform host actions.
- Do not imply AiPresenter will invite, lock, mute, remove, raise hands, or use more participant options unless the user explicitly asks and the visible context is verified.
