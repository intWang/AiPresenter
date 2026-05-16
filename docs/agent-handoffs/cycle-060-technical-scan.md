# Cycle 060 Technical Scan: Meeting Controls Tour JA Narration

Date: 2026-05-16

## Scope

Prepare the next low-risk implementation pass for adding Japanese `localizedText.ja` narration to the first four `meeting-controls-tour` steps in `packages/ringcentral-video.yaml`.

Only this handoff document was edited. The scan read:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/ringcentral-video/source-index.md`

## Recommended Slice

Use the requested four-step slice:

1. `meeting-overview`
2. `explain-meeting-info`
3. `explain-network-quality`
4. `explain-view-layout`

This is safer than extending into `explain-report-issue` in the same pass. `Report issue` opens a foreground troubleshooting dialog that blocks other meeting controls and has stricter cleanup notes, while the first four steps are narrative, private-value-safe, or layout-only.

## YAML Update Needed

Target file: `packages/ringcentral-video.yaml`

Flow: `meeting-controls-tour`

Add a sibling `ja` value under each step's existing `narration.localizedText` mapping. Do not change ids, actions, placement, or `actionOffsetMs`.

| Step id | Entrypoint | Operation | English narration | Suggested `localizedText.ja` |
| --- | --- | --- | --- | --- |
| `meeting-overview` | `ringcentral.video.overview` | `explain` | RingCentral Video is organized around the live meeting canvas. The top bar covers meeting identity, connection health, layout, and reporting. The bottom toolbar covers audio, video, sharing, people, chat, reactions, and safety actions. | RingCentral Video はライブ会議キャンバスを中心に構成されています。上部バーでは会議の識別情報、接続状態、表示レイアウト、問題報告を確認できます。下部ツールバーでは音声、ビデオ、共有、参加者、Chat、リアクション、安全に関わる操作を扱います。 |
| `explain-meeting-info` | `ringcentral.video.top.meeting-info` | `open` | First, the info button opens meeting details: host, meeting ID, copy link, dial-in information, and encryption status. I treat those values as private unless you ask for them. | まず info ボタンで会議の詳細を開きます。ここには主催者、会議 ID、リンクのコピー、ダイヤルイン情報、暗号化状態が表示されます。これらの値は、ユーザーから求められない限り非公開情報として扱います。 |
| `explain-network-quality` | `ringcentral.video.top.network-quality` | `open` | Next is network quality. This is where you check packet loss, jitter, and latency for sharing, video, and audio when the meeting feels unstable. | 次は Network quality です。会議が不安定に感じるときに、共有、ビデオ、音声それぞれのパケットロス、ジッター、遅延を確認する場所です。 |
| `explain-view-layout` | `ringcentral.video.top.views` | `open` | Views changes how you see the meeting. It includes Gallery view and Full screen, so it affects layout without changing anyone in the call. | Views では会議の見え方を切り替えます。Gallery view や Full screen が含まれ、通話中の参加者やメディア状態を変えずに表示レイアウトだけを調整します。 |

## Test Count Updates

Current Japanese localization baseline:

- Overall demo narration: `7/51`
- `vbg-blur-demo`: `4/4`
- `meeting-basics-demo`: `3/3`
- `meeting-controls-tour`: `0/22`
- Q&A questions: `12/12`
- Q&A answers: `12/12`
- `required_localization_complete` remains `False`

After adding the recommended four strings:

- Overall demo narration should become `11/51`
- `meeting-controls-tour` should become `4/22`
- `vbg-blur-demo` remains `4/4`
- `meeting-basics-demo` remains `3/3`
- Q&A counts remain `12/12`
- `required_localization_complete` remains `False`

Update these assertions after the YAML change:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - `report.demo_localized_steps == 11`
  - `report.flow_by_id["meeting-controls-tour"].localized_steps == 4`
  - keep `report.flow_by_id["meeting-controls-tour"].total_steps == 22`
- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - expected line: `Localization report: 11/51 demo steps`
  - expected line: `- meeting-controls-tour: 4/22 narration localized`
  - the first missing step should move from `meeting-overview` to `explain-report-issue`
- `tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap`
  - expected line: `Localization report: 11/51 demo steps`
  - expected missing line should mention `explain-report-issue`
- `tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`
  - detail should report `11/51 demo steps`

## Validation Commands

Run focused tests:

```powershell
pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage -q
pytest tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap -q
pytest tests/unit/test_diagnostics.py::test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing -q
```

Run report smoke checks:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
```

Expected: the first command reports `11/51 demo steps` and `meeting-controls-tour: 4/22`; the second command still exits non-zero with `Localization coverage incomplete for ja.`

## Notes

- Keep Japanese strings under `localizedText.ja`, not `localizedText.jp`.
- Preserve product UI labels such as `RingCentral Video`, `info`, `Network quality`, `Views`, `Gallery view`, `Full screen`, and `Chat` to match observed UI and existing package style.
- Do not add or change `questionAliases.ja` in this pass; the current alias coverage is already tracked separately and this slice is narration-only.
- Do not localize `explain-report-issue` unless the implementation owner intentionally expands the slice. That step opens a blocking dialog and is a better next boundary after confirming the first top-bar slice.
- The source index already records that Japanese coverage includes Q&A, `vbg-blur-demo`, and `meeting-basics-demo`; after this implementation, a later docs pass can mention that the first four `meeting-controls-tour` steps are also localized.
