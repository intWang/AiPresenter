# Cycle 062 Technical Scan: meeting-controls-tour / explain-add-coworkers JA narration

## Scope

Scan only for the next implementation pass. The proposed implementation should add Japanese `localizedText.ja` narration to one step:

- Package: `packages/ringcentral-video.yaml`
- Flow: `meeting-controls-tour`
- Step: `explain-add-coworkers`
- Entrypoint: `ringcentral.video.main.add-coworkers`
- Operation: `open`

Do not change runtime behavior, open steps, action offsets, aliases, Q&A, or unrelated docs as part of the narration slice unless the implementation owner explicitly expands scope.

## Local Context Read

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- Cycle 060 and 061 handoffs, especially:
  - `docs/agent-handoffs/cycle-061-review.md`
  - `docs/agent-handoffs/cycle-061-summary.md`
  - `docs/agent-handoffs/cycle-061-technical-scan.md`

Current verified baseline from `.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja`:

- `Localization report: 12/51 demo steps`
- `meeting-controls-tour: 5/22 narration localized`
- first missing step: `explain-add-coworkers`
- Q&A remains complete: `12/12` localized questions and `12/12` localized answers
- Japanese aliases remain partial: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Targeted baseline tests also pass:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Result observed during scan: `3 passed`.

## Source Step

Current English narration:

```yaml
text: Moving into people controls, Add coworkers opens the invite dialog from the empty meeting view. You can
  search for a coworker, copy the meeting link, or send an invite.
```

Current Chinese narration:

```yaml
zh: 进入成员相关控制。空会议里的 Add coworkers 会打开邀请窗口，可以搜索同事、复制会议链接或发送邀请。
```

Relevant entrypoint notes for `ringcentral.video.main.add-coworkers`:

- The dialog includes a name/email field, suggestions, Copy meeting link, Cancel, and Invite.
- Functionally similar to the toolbar Invite control.
- The callout only appears in an empty-room "first one here" state; skip it when participant tiles or a Participants badge count show other attendees are already present.
- Close with dialog X or Cancel before touching other controls; the dialog blocks the toolbar.

## Recommended Japanese Wording

Recommended insertion under `narration.localizedText`:

```yaml
        ja: 人に関する操作に移ります。空の会議画面にある Add coworkers は招待ダイアログを開き、同僚の検索、会議リンクのコピー、招待の送信に使えます。名前、メールアドレス、候補、非公開の招待リンクは、ユーザーが明示的に求め、表示内容が確認されている場合を除き読み上げません。
```

Rationale:

- Preserves visible UI label `Add coworkers`.
- Covers the same action surface as English and Chinese.
- Adds privacy guardrails from existing package notes and Q&A: do not read names, email addresses, suggestions, or private invite links by default.
- Does not imply that an invite is sent automatically; it says the dialog can be used for invite sending.
- Keeps the step explain/open-only and compatible with the existing blocking modal cleanup.

## Expected Count Changes

After adding only this `localizedText.ja` entry:

- Overall Japanese demo narration: `12/51` -> `13/51`
- `meeting-controls-tour`: `5/22` -> `6/22`
- First missing `meeting-controls-tour` step should advance from `explain-add-coworkers` to `explain-invite`
- Q&A counts should remain `12/12` questions and `12/12` answers
- Japanese alias counts should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`
- `--require-complete` for Japanese should still fail because the package remains partially localized.

## Tests To Update/Add

Update existing expected counts:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - `report.demo_localized_steps == 13`
  - `report.flow_by_id["meeting-controls-tour"].localized_steps == 6`
  - keep `report.demo_total_steps == 51`
  - keep `meeting-controls-tour` total at `22`
  - keep Q&A and alias expectations unchanged

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expected line: `Localization report: 13/51 demo steps`
  - expected line: `- meeting-controls-tour: 6/22 narration localized`
  - missing assertion should become `missing: explain-invite`
  - keep Q&A and alias lines unchanged

- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expected line: `Localization report: 13/51 demo steps`
  - expected line: `- meeting-controls-tour: 6/22 narration localized`
  - missing assertion should become `missing: explain-invite`
  - keep exit code `1`
  - keep `Localization coverage incomplete for ja.`

- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - expected detail should include `13/51 demo steps`
  - keep `required ja localization incomplete`
  - keep `12/12 Q&A questions` and `12/12 Q&A answers`

Add a focused material-package test for this step, analogous to the existing report issue test:

```python
def test_meeting_controls_tour_has_japanese_add_coworkers_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-add-coworkers")

    ja_text = step.narration.localized_text["ja"]
    assert ja_text.strip()
    assert has_cjk(ja_text)
    assert "Add coworkers" in ja_text
    assert "会議リンク" in ja_text
    assert "読み上げません" in ja_text
    assert "名前" in ja_text
    assert "メールアドレス" in ja_text
```

Do not add Japanese `questionAliases` for `ringcentral.video.main.add-coworkers` in this pass unless the task is explicitly broadened; expected alias counts above assume no alias change.

## Expected CLI Output Changes

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected relevant output after implementation:

```text
Language: ja
- meeting-controls-tour: 6/22 narration localized
  missing: explain-invite, explain-participants, explain-chat, explain-microphone, explain-audio-menu, explain-camera, explain-camera-menu, explain-share, explain-reactions, explain-raise-hand, explain-more, explain-recording, explain-notes, explain-background-settings, explain-settings, explain-leave
- localized questions: 12/12
- localized answers: 12/12
questionAliases.ja present on 3/27 entrypoints (9 aliases)
Localization report: 13/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

For:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected result after implementation:

- Exit code: `1`
- Includes `Localization report: 13/51 demo steps`
- Includes `- meeting-controls-tour: 6/22 narration localized`
- Includes `missing: explain-invite`
- Includes `Localization coverage incomplete for ja.`

## Verification Commands

Run targeted tests with the project venv:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_meeting_controls_tour_has_japanese_add_coworkers_narration tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap tests\unit\test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing
```

Optional broader package-localization sweep:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py -k "japanese or localization_status or add_coworkers"
```

CLI smoke checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

## Notes For Implementer

- Keep the YAML insertion under `localizedText.ja`, not `localizedText.jp`.
- Preserve existing `zh`, `placement: during`, and `actionOffsetMs: 400`.
- Keep product/UI labels in English where they match the visible UI: `Add coworkers`, and optionally `Invite` only if mentioned.
- The invite dialog can expose names, email addresses, suggestions, and private meeting links. The Japanese text should avoid reading those values aloud by default.
- The step opens a modal, so do not change cleanup or action flow in a narration-only pass.
