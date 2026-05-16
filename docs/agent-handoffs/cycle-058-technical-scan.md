# Cycle 058 Technical Scan: RingCentral Video JA Toolbar Aliases

Date: 2026-05-16

Scope: prepare the next implementation pass for adding `questionAliases.ja` to three RingCentral Video toolbar entrypoints only: audio, participants, and chat. Keep privacy Q&A routing ahead of entrypoint alias routing.

## Files Scanned

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `docs/knowledge/ringcentral-video/source-index.md`

No code, test, YAML, or git changes were made in this scan.

## Current Entrypoint Alias Shape

All three target entrypoints already have `questionAliases` with only `zh`. Add a sibling `ja` list under the same `questionAliases` mapping.

### `ringcentral.video.toolbar.audio`

Current:

```yaml
questionAliases:
  zh:
  - 麦克风
  - 静音
  - 声音
```

Recommended:

```yaml
  ja:
  - マイク
  - ミュート
  - 音声
```

Rationale: mirrors the existing Chinese "microphone / mute / audio" intent. Note that `音声` also appears in the existing Japanese audio/video readiness Q&A, so routing tests should confirm that Q&A still wins for readiness/privacy-style questions.

### `ringcentral.video.toolbar.participants`

Current:

```yaml
questionAliases:
  zh:
  - 参会者
  - 参会人列表
  - 谁在会议里
```

Recommended:

```yaml
  ja:
  - 参加者
  - 参加者一覧
  - 誰が参加していますか
```

Rationale: mirrors "participants / participant list / who is in the meeting" without adding host-control or people-management verbs that could blur into safety Q&A.

### `ringcentral.video.toolbar.chat`

Current:

```yaml
questionAliases:
  zh:
  - 聊天
  - 聊天室
  - 消息
  - 聊天在哪里
```

Recommended:

```yaml
  ja:
  - チャット
  - メッセージ
  - チャットはどこ
```

Rationale: keep this to three aliases so the round is small and countable. Do not add `チャット内容` as an alias; that phrase belongs to the privacy-sensitive Q&A: `チャット内容や参加者名を読み上げられますか`.

## Localization Status Counts

After adding the three `ja` alias lists above:

- `entrypoints_with_aliases`: `3`
- `entrypoint_total`: `27`
- `alias_total`: `9`
- CLI report line should become: `questionAliases.ja present on 3/27 entrypoints (9 aliases)`

Unchanged JA localization numbers:

- `Localization report: 7/51 demo steps`
- localized questions: `12/12`
- localized answers: `12/12`
- `required_localization_complete` stays `False` because demo narration coverage is still partial.

Update targets:

- `tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`

Note: in this checkout, `test_material_packages.py` already appears to expect `3` and `9`, while `test_cli.py` still expects the old `0/27` report string. Recheck the target branch before editing.

## Question Routing Tests

Runtime order in `src/ai_presenter/runtime/questions.py` is:

1. `_answer_question()` normalizes the prompt.
2. `_match_qa()` runs first.
3. Only if no Q&A matches, `_match_entrypoint()` tries package-owned aliases and then the legacy alias table.

Add or update tests in `tests/unit/test_questions.py`:

1. Add a JA package-owned alias routing test with the legacy table disabled:

```python
def test_ringcentral_japanese_questions_match_package_aliases_without_legacy_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    expected = {
        "マイク": "ringcentral.video.toolbar.audio",
        "参加者一覧": "ringcentral.video.toolbar.participants",
        "チャットはどこ": "ringcentral.video.toolbar.chat",
    }

    for question, entrypoint_id in expected.items():
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language="ja"),
        )
        assert response.entrypoint_id == entrypoint_id
```

2. Strengthen the existing Japanese privacy-sensitive Q&A test for chat/participants so alias matches cannot steal it:

```python
response = answer_question(
    package=package,
    question="チャット内容や参加者名を読み上げられますか",
    voice=PresenterVoiceSettings(language="ja", tone="professional"),
)

assert response.entrypoint_id is None
assert response.can_operate is False
assert "チャットメッセージ" in response.answer_text
assert "参加者名" in response.answer_text
assert "明示的" in response.answer_text
assert "確認" in response.answer_text
assert not response.answer_text.startswith("Chat panel:")
```

The existing parametrized privacy test already checks `can_operate is False` and answer fragments; it should either add `entrypoint_id is None` for all no-related-entrypoint privacy Q&A items or add a focused new test for the chat privacy prompt.

3. Optional but useful: add a similar guard for audio readiness, because the proposed alias `音声` appears inside `音声とビデオの準備を確認するにはどうすればいいですか`. Expected behavior is Q&A answer, `entrypoint_id == "ringcentral.video.toolbar.audio"` from the Q&A related entrypoint, and `can_operate is False`.

## Validation Commands

Run the focused tests first:

```powershell
pytest tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage `
  tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage `
  tests/unit/test_cli.py::test_localization_report_require_complete_fails_for_japanese_demo_gap `
  tests/unit/test_questions.py::test_ringcentral_japanese_privacy_sensitive_questions_match_localized_answers
```

Run the new JA alias routing test once added:

```powershell
pytest tests/unit/test_questions.py::test_ringcentral_japanese_questions_match_package_aliases_without_legacy_table
```

Then run the report manually:

```powershell
python -m ai_presenter.cli localization-report --package ringcentral-video --language ja
```

Expected report still shows `7/51 demo steps`, but the alias line should show `questionAliases.ja present on 3/27 entrypoints (9 aliases)`.

## Notes

- Keep this round limited to the three requested toolbar entrypoints; do not opportunistically add JA aliases to audio-menu, video, share, notes, recording, or other entrypoints.
- The source index currently says `questionAliases.ja` remain future work. That remains broadly true after this small slice, but the exact report count should become `3/27`.
- Avoid aliases that name private content directly, especially `チャット内容`, because those should continue to route through privacy Q&A rather than opening or describing the Chat panel.
