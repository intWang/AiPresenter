# Cycle 063 Technical Scan: meeting-controls-tour / explain-invite JA narration

## Scope

Scan only for the next implementation pass. The proposed implementation should add Japanese `localizedText.ja` narration to one step:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-invite`
- Entrypoint: `ringcentral.video.toolbar.invite`
- Operation: `open`

Do not change runtime behavior, open steps, action offsets, aliases, Q&A, flow order, or unrelated docs as part of this narration slice unless the implementation owner explicitly expands scope.

## Local Context Read

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- Recent handoffs:
  - `docs/agent-handoffs/cycle-062-technical-scan.md`
  - `docs/agent-handoffs/cycle-062-implementation.md`
  - `docs/agent-handoffs/cycle-062-review.md`
  - `docs/agent-handoffs/cycle-062-summary.md`

Current verified baseline from:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

- `Localization report: 13/51 demo steps`
- `meeting-controls-tour: 6/22 narration localized`
- first missing `meeting-controls-tour` step: `explain-invite`
- Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- Japanese aliases remain partial: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Focused target tests are already advanced to the expected Cycle 063 post-implementation state, so they currently fail against the YAML baseline. Observed scan command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_invite_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Result observed during scan: `5 failed`. Failures are consistent with the missing `localizedText.ja` on `explain-invite`: actual coverage is still `13/51`, `meeting-controls-tour` is still `6/22`, and `step.narration.localized_text["ja"]` raises `KeyError`.

## Source Step

Current English narration:

```yaml
text: The Invite button in the toolbar opens the same invite flow. It is the regular place to bring someone
  into an active meeting.
```

Current Chinese narration:

```yaml
zh: 工具栏里的 Invite 是活跃会议中邀请他人的常规入口，可以继续添加同事或复制会议详情。
```

Relevant entrypoint notes for `ringcentral.video.toolbar.invite`:

- Useful when the presenter needs to explain how to bring people into an active room.
- Avoid reading private invite links aloud unless explicitly requested.
- Opens the same Invite others dialog as Add coworkers, with search, suggestions, Copy meeting link, Cancel, and Invite.
- Close using the dialog X or Cancel before continuing.

Relevant prior slice:

- Cycle 062 localized `explain-add-coworkers`, the empty-meeting invite entrypoint.
- Cycle 063 should treat `explain-invite` as the active-meeting toolbar entrypoint, even though it opens the same dialog.
- Keep privacy language consistent with Cycle 062: do not read names, email addresses, suggestions, or private invite links unless the user explicitly asks and visible content is verified.

## Recommended Japanese Wording

Recommended insertion under `narration.localizedText`:

```yaml
        ja: ツールバーの Invite は、進行中の会議で参加者を招待する通常の入口です。Add coworkers と同じ Invite ダイアログを開き、同僚の検索、会議情報のコピー、招待の準備に使えます。名前、メールアドレス、候補、非公開の招待リンクは、ユーザーが明示的に求め、表示内容が確認されるまで読み上げません。説明したら、このダイアログを閉じます。
```

Rationale:

- Preserves visible UI label `Invite`.
- Names the toolbar context, which distinguishes this step from the empty-meeting `Add coworkers` callout.
- Keeps `Add coworkers` in the narration to clarify that the same dialog is reused.
- Uses active-meeting language: `進行中の会議`.
- Covers copying meeting details without reading private invite links aloud.
- Avoids the word `送信`, matching the current test guard that this narration should not imply an invite is sent automatically.
- Explicitly closes the blocking dialog after explanation.

## Expected Count Changes

After adding only this `localizedText.ja` entry:

- Overall Japanese demo narration: `13/51` -> `14/51`
- `meeting-controls-tour`: `6/22` -> `7/22`
- First missing `meeting-controls-tour` step should advance from `explain-invite` to `explain-participants`
- Q&A counts should remain `12/12` questions and `12/12` answers
- Japanese alias counts should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`
- `--require-complete` for Japanese should still fail because the package remains partially localized.

## Tests To Update/Add

The test files appear to already contain the Cycle 063 expected assertions. If the implementation owner is working from this current tree, no additional test edits should be needed; the YAML narration should turn the existing red tests green.

Existing expected test coverage to preserve:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - expects `report.demo_localized_steps == 14`
  - expects `report.flow_by_id["meeting-controls-tour"].localized_steps == 7`
  - keeps `report.demo_total_steps == 51`
  - keeps `meeting-controls-tour` total at `22`
  - keeps Q&A and alias expectations unchanged

- `tests/unit/test_material_packages.py::test_meeting_controls_tour_has_japanese_invite_narration`
  - asserts Japanese text exists and contains CJK
  - asserts `Invite`
  - asserts `ツールバー`
  - asserts `進行中の会議`
  - asserts `会議情報`
  - asserts `読み上げません`
  - asserts `閉じます`
  - asserts `送信` is not present

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expects `Localization report: 14/51 demo steps`
  - expects `- meeting-controls-tour: 7/22 narration localized`
  - expects `missing: explain-participants`
  - keeps Q&A and alias lines unchanged

- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expects exit code `1`
  - expects `Localization report: 14/51 demo steps`
  - expects `- meeting-controls-tour: 7/22 narration localized`
  - expects `missing: explain-participants`
  - keeps `Localization coverage incomplete for ja.`

- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - expects diagnostic detail to include `14/51 demo steps`
  - keeps `required ja localization incomplete`
  - keeps `12/12 Q&A questions` and `12/12 Q&A answers`

If applying this scan to a branch that does not already have the invite-focused test, add it with the assertions listed above. Do not add Japanese `questionAliases` for `ringcentral.video.toolbar.invite` in this pass unless scope is explicitly broadened; expected alias counts above assume no alias change.

## Expected CLI Output Changes

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected relevant output after implementation:

```text
Language: ja
- meeting-controls-tour: 7/22 narration localized
  missing: explain-participants, explain-chat, explain-microphone, explain-audio-menu, explain-camera, explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
Localization report: 14/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected result after implementation:

- Exit code: `1`
- Includes `Localization report: 14/51 demo steps`
- Includes `- meeting-controls-tour: 7/22 narration localized`
- Includes `missing: explain-participants`
- Includes `Localization coverage incomplete for ja.`

## Verification Commands

Run targeted tests with the project venv:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_invite_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional broader package-localization sweep:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k "japanese or localization_status or invite"
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

Expected doctor result remains nonzero because Japanese localization is still incomplete, but the localization detail should move to `14/51 demo steps`.

## Notes For Implementer

- Keep the YAML insertion under `localizedText.ja`, not `localizedText.jp`.
- Preserve existing `zh`, `placement: during`, and `actionOffsetMs: 350`.
- Keep product/UI labels in English where they match visible UI: `Invite`, and optionally `Add coworkers` when explaining dialog reuse.
- This step opens the active-meeting toolbar Invite dialog. It should not imply that AiPresenter sends an invite, selects a person, enters an address, copies or reads a private link, or reads suggestions by default.
- The invite dialog is modal/blocking, so do not change cleanup or action flow in a narration-only pass.
