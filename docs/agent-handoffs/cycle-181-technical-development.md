# Cycle 181 Technical Development: Localized Participant Privacy

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/runtime/questions.py`
  - Added localized participant disclosure terms for zh/ja/es.
  - Added localized identity terms for names, roles, who-is, host, moderator, and coordinator phrasing.
  - Added localized panel/list location terms so safe navigation remains operable.
- `tests/unit/test_questions.py`
  - Added localized identity prompts that must remain answer-only.
  - Added localized safe panel/list prompts that must remain operable.
  - Reclassified Chinese `谁在会议里` as privacy guidance instead of a package-alias operation.
- `tests/unit/test_controller.py`
  - Added Chinese safe and sensitive mixed-meta controller regressions for idle/running paths.
- `tests/unit/test_controller_session.py`
  - Added Chinese safe and sensitive session interrupt regressions.

No package YAML changes were made.

## Behavior Added

Localized identity prompts now resolve to the existing participant privacy Q&A:

- Chinese: `列出参会者`, `谁在会议里`, `读参会人名字`, `谁是主持人或协管员`
- Japanese: `参加者名を読んで`, `参加者の名前を教えて`, `参加者一覧に誰がいますか`, `ホストまたはモデレーターは誰ですか`
- Spanish: `Muestrame los participantes`, `Lista los participantes`, `Muestrame el panel de participantes con nombres`, `Quien esta en la reunion?`, `Quien es host o moderador?`

These return:

- `entrypoint_id is None`
- `can_operate is False`
- no question interrupt
- localized privacy guidance

Localized panel/list navigation remains operable when identity intent is absent:

- `参会人列表在哪里`
- `打开参会人列表`
- `参加者一覧はどこですか`
- `参加者パネルを開いて`
- `Muestrame el panel de participantes`
- `Donde esta la lista de participantes?`

## Implementation Notes

The change stays inside `_match_participant_privacy_qa()` inputs. The matcher still uses the Cycle 180 rule:

- If a disclosure prompt includes panel/list location terms but no identity terms, let entrypoint matching handle it.
- If identity terms are present, return the participant privacy Q&A before aliases can match.

This preserves `participants` and explicit panel navigation while blocking roster disclosure.
