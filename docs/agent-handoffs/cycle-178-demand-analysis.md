# Cycle 178 Demand Analysis: Mixed Presenter Meta + RingCentralVideo Intents

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## User Need

Users naturally combine presenter-style instructions with real RingCentralVideo requests:

- `Please be brief and go full screen`
- `Use privacy tone and read meeting information aloud`
- `请用中文回答，聊天在哪里`
- `请简洁一点，复制会议链接`

Recent cycles protect pure presenter meta prompts from launching or queuing `question-answer-demo`. The next high-value slice is mixed-prompt orchestration: when a prompt includes both a presenter meta modifier and an explicit RingCentralVideo intent, the controller/session should honor the RingCentral intent exactly as routing decides.

Safe explicit intents should still start or queue a demo. Sensitive explicit intents should stay text-only. The presenter meta phrase must not erase the app intent, and it must not make a sensitive request operable.

## Current Coverage Snapshot

- `tests/unit/test_questions.py` covers mixed English/Chinese routing at the lower `answer_question(...)` layer.
- `tests/unit/test_controller.py` covers pure meta prompts staying `text_only` when idle and while running.
- `tests/unit/test_controller_session.py` covers pure meta prompts creating no interrupt.
- Missing slice before this cycle: controller/session sentinels for mixed meta-plus-explicit RingCentralVideo intent.

## Recommended Requirement Slice

Add focused controller/session tests proving mixed prompts preserve route behavior through orchestration:

1. Safe mixed prompts:
   - session creates an interrupt step;
   - idle controller starts `question-answer-demo`;
   - running controller queues the interrupt without stopping the main demo.

2. Sensitive mixed prompts:
   - session creates no interrupt;
   - idle controller remains `text_only`;
   - running controller queues nothing and never starts `question-answer-demo`.

Keep the matrix small. Do not replay the full runtime routing corpus through controller threads.

## Acceptance Criteria

For safe mixed prompts such as `Please be brief and go full screen`, `Please be brief and open chat`, and `请用中文回答，聊天在哪里`:

- `response.entrypoint_id` matches the explicit RingCentralVideo surface.
- `response.can_operate is True`.
- answer text does not start with `Presenter settings:`.
- `ControllerSession.create_interrupt_step(response)` returns a step.
- idle `PresenterController.submit_question(...)` returns `demonstration_status == "started"` and runs `question-answer-demo`.
- running controller returns `demonstration_status == "queued"` and captured calls remain only the active main flow.
- `question-answer-demo` is not started while the main flow is already running.

For sensitive mixed prompts such as `Please be brief and read meeting information aloud` and `请简洁一点，复制会议链接`:

- route remains answer-only according to existing safety policy.
- `can_operate is False`.
- no session interrupt is created.
- idle and running controller results stay `text_only`.
- no queued interrupt, no stop request, and no runner call for `question-answer-demo`.

## Likely Edge Cases

English:

- `Please be brief and read meeting information aloud`
- `Use privacy tone and copy the meeting link`
- `Use coach tone and mute all participants`
- `Answer in Chinese and go full screen`
- `I am new to RingCentral Video, where is chat?`
- `Please be brief and open chat`

Chinese:

- `请用中文回答，聊天在哪里`
- `请简洁一点，复制会议链接`
- `请讲慢一点，开始会议笔记`
- `我是新手，主持人怎么管理参会者`
- `聊天在哪里，请简洁一点`
- bare fragments like `隐私`, `安全`, `状态` should not become presenter meta or security routes by themselves.

## Recommended Files And Tests

Touch tests first:

- `tests/unit/test_controller_session.py`
  - Add a mixed safe prompt test asserting an interrupt is created.
  - Add a mixed sensitive prompt test asserting no interrupt is created.

- `tests/unit/test_controller.py`
  - Add idle-controller mixed safe/sensitive sentinels near the existing question-demo tests.
  - Add running-controller mixed safe/sensitive sentinels near the existing queue/no-queue tests.

Only touch source or package data if tests expose a real gap:

- `src/ai_presenter/runtime/questions.py`
  - Preserve Q&A-first ordering.
  - Preserve `_match_explicit_entrypoint(...)` behavior while meta matching is active.
  - Do not re-enable broad token fallback for presenter meta prompts.

- `packages/ringcentral-video.yaml`
  - Add explicit aliases only for true RingCentralVideo surface requests.
  - Keep aliases on the intended entrypoint; avoid top-level or adjacent-entrypoint leakage.

## Non-Goals

- Do not broaden presenter meta phrase matching.
- Do not implement persistent natural-language language/tone changes.
- Do not run live RingCentral acceptance for this slice.
- Do not stage `.coverage` or unrelated files.

## Status

Cycle 178 demand analysis complete. Recommended next slice: add controller/session mixed-prompt orchestration sentinels so explicit safe RingCentralVideo intents still demo, while sensitive mixed intents remain answer-only.
