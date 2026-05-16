# Cycle 061 Technical Scan: `explain-report-issue` JA Narration

## Scope

- Target flow: `meeting-controls-tour`
- Target step: `explain-report-issue`
- Target field for the implementation round: `narration.localizedText.ja`
- This scan only prepares the handoff. Do not change code, tests, YAML, or git in this round.

## English Source

Step `explain-report-issue` currently narrates:

> Report opens the troubleshooting dialog for audio, video, screen sharing, joining, notes, transcript, or other issues. It blocks the meeting controls, so I close it before moving on.

Relevant behavior notes from the entrypoint:

- `ringcentral.video.top.report-issue` opens a foreground dialog.
- The dialog blocks other meeting controls until closed.
- Do not pick an issue category during a feature tour unless the user wants to file a report.
- Close with the dialog X before continuing; Escape was not reliable in testing.

## Suggested JA Narration

Recommended YAML insertion under `narration.localizedText` for `explain-report-issue`:

```yaml
        ja: Report は、音声、ビデオ、画面共有、参加、Notes、transcript、その他の問題を報告するためのトラブルシューティングダイアログを開きます。表示された内容だけを根拠にし、原因は決めつけません。このダイアログは会議コントロールをふさぐため、説明が終わったら閉じます。
```

Rationale:

- Keeps product/control label `Report` in English, matching nearby localized narration style.
- Covers the original categories without adding a promise to file or submit a report.
- Adds the safety boundary required by the unit test: do not infer the exact cause.
- Mentions closing the blocking dialog before continuing.
- Avoids `送信`, because the tour should not imply submitting a report.

## Expected Count Updates

Current baseline for JA localization report:

- Overall demo narration: `11/51 demo steps`
- `meeting-controls-tour`: `4/22 narration localized`
- First missing step: `explain-report-issue`

After adding only this `localizedText.ja` entry:

- Overall demo narration should become `12/51 demo steps`
- `meeting-controls-tour` should become `5/22 narration localized`
- First missing step should advance to `explain-add-coworkers`
- Q&A should remain `12/12` localized questions and `12/12` localized answers
- Japanese aliases should remain `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Tests in the scanned tree already contain post-update expectations for the report-issue step:

- `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage` expects `12/51` and `meeting-controls-tour: 5/22`.
- `test_meeting_controls_tour_has_japanese_report_issue_narration` expects the JA text to include `Report`, `原因`, `決めつけません`, and `閉じます`, and not include `送信`.

CLI/diagnostic tests that still describe the old baseline should be updated by the implementation round if this candidate is accepted:

- `tests/unit/test_cli.py`
  - `test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - `test_localization_report_require_complete_fails_for_japanese_demo_gap`
- `tests/unit/test_diagnostics.py`
  - `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`

## Verification Commands

Run after the YAML and expected-count test updates are made:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider tests/unit/test_material_packages.py -k "japanese or localization_status"
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider tests/unit/test_cli.py -k "localization_report"
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider tests/unit/test_diagnostics.py -k "localization"
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider tests/unit/test_material_packages.py tests/unit/test_cli.py tests/unit/test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected CLI report after the implementation:

```text
Localization report: 12/51 demo steps
- meeting-controls-tour: 5/22 narration localized
  missing: explain-add-coworkers
```

## Notes

- Keep this candidate to one YAML localization entry unless the implementation round also updates tests to match the new baseline.
- Do not add a Japanese `questionAliases` entry for Report issue in this candidate; alias counts are expected to stay unchanged.
- Do not edit `docs/knowledge/ringcentral-video/source-index.md` in the implementation unless the owner explicitly includes source-index maintenance. It currently describes JA coverage as the first four top-bar steps of `meeting-controls-tour`; after this change, that statement becomes stale and should eventually say the first five steps.
- The next likely JA narration candidate after this one is `explain-add-coworkers`.
