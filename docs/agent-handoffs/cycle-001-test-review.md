# Cycle 001 Test Review Handoff

Date: 2026-05-16

## Verdict

approved_with_risks

No blocking findings were found in the review scope. The implemented behavior matches the core Cycle 001 intent, and the required focused tests, ruff check, and full no-coverage pytest pass.

## Commands Run

- `.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_controller.py tests\unit\test_questions.py tests\unit\test_material_runtime.py`
  - Result: passed, `43 passed in 6.32s`.
- `.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\runtime\controller.py src\ai_presenter\runtime\questions.py tests\unit\test_controller.py tests\unit\test_questions.py`
  - Result: passed, `All checks passed!`.
- `.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests`
  - Result: passed, `361 passed, 1 warning in 10.33s`.
  - Warning: pywinauto emitted `UserWarning: Revert to STA COM threading mode`.

## Spec Coverage Checklist

- [x] Running safe question queues to `DemoControl`, not stop/restart.
  - `PresenterController.submit_question()` calls `self._control.enqueue_interrupt(interrupt)` for `is_running and not is_stopping` and returns `queued` at `src/ai_presenter/runtime/controller.py:257`.
  - Regression coverage asserts no stop request, one original flow call, and queued question step at `tests/unit/test_controller.py:147`.
- [x] Idle safe question still starts `question-answer-demo`.
  - Idle path calls `_start_target(question_target, voice)` and returns `started` at `src/ai_presenter/runtime/controller.py:273`.
  - Regression coverage asserts `question-answer-demo` is started at `tests/unit/test_controller.py:271`.
- [x] Risky/non-operable questions remain text-only.
  - `create_question_interrupt_step()` returns `None` when `entrypoint_id is None or not response.can_operate` at `src/ai_presenter/runtime/session.py:92`.
  - Controller risky question coverage asserts `text_only`, `can_operate is False`, and no runner calls at `tests/unit/test_controller.py:308`.
  - Chinese invite/share/leave tests assert matched but non-operable at `tests/unit/test_questions.py:47` and `tests/unit/test_questions.py:60`.
- [x] Real Chinese questions are covered, and mojibake input is not treated as a supported alias.
  - Real Chinese coverage includes chat, invite, share, leave, and background at `tests/unit/test_questions.py:34`.
  - Mojibake negative coverage asserts no match at `tests/unit/test_questions.py:95`.
- [x] Alias matching avoids the obvious `设置背景` vs generic `设置` mis-match.
  - Alias matcher selects the longest contained alias at `src/ai_presenter/runtime/questions.py:221`.
  - `怎么设置背景` is covered as background settings at `tests/unit/test_questions.py:80`.
- [x] Controller status helper is used consistently by Tk `submit_question`.
  - `describe_question_result()` covers queued, started, risky/text-only, and no-match outcomes at `src/ai_presenter/runtime/controller.py:108`.
  - Tk `submit_question()` sets status through that helper at `src/ai_presenter/runtime/controller.py:633`.

## Findings

No blocking findings.

## Residual Risks

- Low: `tests/unit/test_material_runtime.py` proves queued interrupts run before a flow step and that direct interrupts do not advance the cursor, but it does not encode the exact acceptance sequence `main step -> queued interrupt -> next main step` after an interrupt arrives mid-flow. The implementation appears consistent with that behavior because `MaterialDemoRuntime.run_next()` checks interrupts before consuming `_next_index`, but a dedicated test would make this contract easier to defend.
- Low: `submit_question()` checks `is_running` and `is_stopping` separately before enqueueing. A narrow race could enqueue just as stopping begins; current behavior should be benign because `DemoControl.reset()` clears queued interrupts, but it is not directly stress-tested.

## Next Test Suggestions

- Add a material runtime unit test for `run_next()` once, then enqueue, then `run_next()` twice, expecting `["one", "interrupt", "two"]`.
- Add a controller test for safe question submission during the stopping window if the controller grows stronger concurrency guarantees.
