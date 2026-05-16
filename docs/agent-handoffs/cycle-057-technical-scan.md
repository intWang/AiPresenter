# Cycle 057 Technical Scan: RingCentral Video Meeting Basics JA Narration

Date: 2026-05-16

## Scope

This scan prepares the handoff for adding Japanese `localizedText.ja` narration to the three-step `meeting-basics-demo` flow in `packages/ringcentral-video.yaml`.

Only this handoff document was edited. The scan read:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/ringcentral-video/source-index.md`

## YAML Update Needed

Target file: `packages/ringcentral-video.yaml`

Flow: `meeting-basics-demo`

Current step ids and English narration:

| Step id | Entrypoint | Operation | English narration |
| --- | --- | --- | --- |
| `show-mic` | `ringcentral.video.toolbar.audio` | `point` | The microphone control shows whether local audio is muted and lets the presenter quickly recover before speaking. |
| `show-participants` | `ringcentral.video.toolbar.participants` | `open` | The Participants panel is the fastest way to confirm who is in the room and whether the meeting is still empty. |
| `show-chat` | `ringcentral.video.toolbar.chat` | `open` | Chat supports side-channel collaboration while the spoken demo continues. |

Each step already has `localizedText.zh`. Add a sibling `ja` value under the same `localizedText` mapping for all three steps. Do not change ids, actions, placement, or `actionOffsetMs`.

Suggested Japanese narration, keeping product control names stable:

```yaml
ja: マイクのコントロールでは、ローカル音声がミュート中かどうかを確認できます。発言前にすばやく状態を戻せます。
```

```yaml
ja: Participants パネルは、誰が会議室にいるか、また会議がまだ空の状態かを確認する一番速い方法です。
```

```yaml
ja: Chat は、音声でのデモを続けながら補足情報を共有できる、文字ベースの協作用チャネルです。
```

## Test Updates Needed

Target file: `tests/unit/test_material_packages.py`

- `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage` is already aligned with the intended post-change state in this checkout:
  - `report.demo_localized_steps == 7`
  - `report.flow_by_id["meeting-basics-demo"].localized_steps == 3`
  - `report.flow_by_id["meeting-basics-demo"].total_steps == 3`
- The short-flow structural test already includes `meeting-basics-demo` step ids under the Chinese localized narration test. No JA-specific short-flow assertion exists there.
- After adding YAML JA strings, this test file should pass without further changes unless another branch still has the older `4/51` assertions.

Target file: `tests/unit/test_cli.py`

Update Japanese localization-report assertions in:

- `test_localization_report_outputs_japanese_vbg_and_qa_coverage`
- `test_localization_report_require_complete_fails_for_japanese_demo_gap`

Expected output changes:

- Add or assert `- meeting-basics-demo: 3/3 narration localized`.
- Overall localized demo-step total should become `7/51`.
- Existing `- vbg-blur-demo: 4/4 narration localized` remains unchanged.
- Existing `- meeting-controls-tour: 0/22 narration localized` remains unchanged.
- Existing `missing: meeting-overview` remains valid because the next missing flow is still `meeting-controls-tour`.
- Q&A lines stay `12/12`.
- `questionAliases.ja present on 0/27 entrypoints (0 aliases)` stays unchanged.
- `--require-complete` for Japanese should still fail with `Localization coverage incomplete for ja.`

Target file: `tests/unit/test_diagnostics.py`

Update `test_diagnostics_require_localization_reports_japanese_qa_complete_but_demo_missing`:

- Change the detail expectation from `4/51 demo steps` to `7/51 demo steps`.
- Keep status `FAIL`.
- Keep `required ja localization incomplete`.
- Keep `12/12 Q&A questions` and `12/12 Q&A answers`.

## Localization Report And Diagnostics Impact

Japanese Q&A coverage is already complete at `12/12` questions and `12/12` answers. Adding these three JA narration strings only affects demo narration coverage.

Expected Japanese localization report after the YAML update:

- Demo narration: `7/51` localized
- `vbg-blur-demo`: `4/4`
- `meeting-basics-demo`: `3/3`
- `meeting-controls-tour`: `0/22`
- `meeting-control-map-demo`: still unlocalized for JA
- Required localization remains incomplete

Expected diagnostics with `require_localization=True` and `localization_language="ja"`:

- `localization` check remains `FAIL`
- Detail should report `required ja localization incomplete`
- Detail should report `7/51 demo steps`
- Q&A detail remains `12/12 Q&A questions` and `12/12 Q&A answers`

## Validation Commands

Run the focused tests after the YAML and assertion updates:

```powershell
pytest tests/unit/test_material_packages.py -q
pytest tests/unit/test_cli.py -q
pytest tests/unit/test_diagnostics.py -q
```

Optional focused CLI smoke checks:

```powershell
python -m ai_presenter.cli localization-report --package ringcentral-video --language ja
python -m ai_presenter.cli localization-report --package ringcentral-video --language ja --require-complete
```

The second command should still exit non-zero because Japanese demo narration is not complete across all 51 demo steps.

## Notes And Risks

- Keep Japanese strings under `localizedText.ja`, not `localizedText.jp`.
- Preserve product labels such as `Participants` and `Chat` if consistency with existing English UI labels is preferred.
- Do not add Japanese `questionAliases` in this cycle; source index currently records `questionAliases.ja` as future work and report output should remain `0/27 entrypoints (0 aliases)`.
- Source index currently says Japanese coverage is complete for Q&A and the four-step virtual background blur demo. After this change, update that line in a later documentation cycle to include the three-step meeting basics demo.
- If a branch still contains the old material-package JA assertions, update them from `4` to `7` and add the `meeting-basics-demo` flow count assertions shown above.
