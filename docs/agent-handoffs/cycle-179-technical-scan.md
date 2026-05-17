# Cycle 179 Technical Scan

Date: 2026-05-17

No edits made by this scan.

## Current Behavior

- Mixed presenter-meta routing is Q&A-first, then presenter-meta detection. Meta prompts use explicit entrypoint matching only, not the full token scorer.
- Safe mixed prompts already work for Chat and Network quality in question/session/controller tests.
- `Please be brief and show network quality` routes to `ringcentral.video.top.network-quality`, `can_operate=True`, and allows interrupt/demo.
- `Please be brief and show participants` produces no entrypoint and stays a presenter-settings answer only.
- `Please be brief and show participants panel` routes to `ringcentral.video.toolbar.participants`, `can_operate=True`, and allows interrupt/demo.
- `Please be brief and show Notes and Transcript` routes to answer-only safety Q&A with no interrupt.
- `Please be brief and open notes and transcript` routes to `ringcentral.video.more.notes`, `can_operate=False`, and creates no interrupt.

## Probes To Run

```powershell
.\.venv\Scripts\pytest.exe -q --no-cov tests/unit/test_questions.py tests/unit/test_controller.py tests/unit/test_controller_session.py -k "presenter_meta_modifiers_do_not_steal or mixed_meta_question or mixed_presenter_meta_answer or notes_question_policy or participants_matches_participants_entrypoint or network_quality_question_remains_operable"
```

The scan agent observed `35 passed, 454 deselected`. Without `--no-cov`, the focused slice passes tests but exits nonzero because repo coverage falls below `fail_under=80`.

## Test Patterns

- Unit routing matrix lives in `tests/unit/test_questions.py`.
- Session interrupt gating lives in `tests/unit/test_controller_session.py`.
- Controller queued/started/text-only orchestration lives in `tests/unit/test_controller.py`.
- Production interrupt creation is only `entrypoint_id` plus `can_operate`.
- Controller turns safe interrupts into `queued` while running or `started` while idle.

## Production Needs

No production change is needed for the Network Quality and Notes/Transcript slice.

Do not add support for plain `Please be brief and show participants` in this cycle. Participants has dual intent: opening the panel is safe, but listing names or roles is answer-only privacy territory. If a later cycle supports that phrase, prefer a precise package alias only after adding privacy regression tests.

Preserve Notes/Transcript answer-only behavior. It is protected by `questionPolicy: answerOnly` and safety Q&A terms.

## Risks

- Broadening meta routing with full token scoring could make sensitive prompts operable by accident.
- Participants has dual intent and needs a separate privacy-adjacent pass.
- Notes/Transcript has location, content, and state-changing intents; keep show/read/start/copy/export transcript text-only unless explicitly scoped and verified.
