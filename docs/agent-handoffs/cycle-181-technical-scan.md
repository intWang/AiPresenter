# Cycle 181 Technical Scan: Localized Participant Routing

Date: 2026-05-17

## Files Inspected

- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_session.py`
- `docs/agent-handoffs/cycle-180-*`

## Findings

- Participant privacy detection lives in `_match_participant_privacy_qa()` and is called before contained Q&A and entrypoint fallback.
- Cycle 180 constants were English-focused: disclosure terms, identity terms, and panel/button location terms did not cover zh/ja/es.
- Package aliases include localized participant list/panel wording, so substring matching can turn identity requests into `ringcentral.video.toolbar.participants` operations.
- The existing privacy Q&A `Can the presenter read meeting messages or participant names?` already has localized answers for zh/ja/es and can be reused.

## Behavior Before This Cycle

- `列出参会者` and `谁在会议里` routed to the Participants panel with `can_operate=True`.
- `读参会人名字` was safe but fell through to the generic no-match answer.
- `参加者名を読んで` routed to the Participants panel with `can_operate=True`.
- Spanish `Muestrame el panel de participantes con nombres` could route through the panel alias unless identity intent was recognized first.
- Safe panel prompts such as `参会者在哪里`, `参加者一覧はどこですか`, and `panel de participantes` remained valid navigation requests.

## Recommended Implementation

- Extend runtime participant privacy terms for localized disclosure and identity intent.
- Extend panel/list location terms for localized safe navigation.
- Keep the existing rule: panel/list wording is safe only when identity terms are absent.
- Do not change YAML aliases or Q&A count expectations.

## Verification Slice

Use the focused participant/controller/session slice:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py -k "localized_participant_identity or participants_panel_location_requests or chinese_questions_match_package_aliases_without_legacy_table or safe_mixed_meta_question or sensitive_mixed_meta_question or safe_mixed_presenter_meta_answer or sensitive_mixed_presenter_meta_answer"
```
