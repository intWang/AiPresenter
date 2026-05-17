# Cycle 177 Test Review: Presenter Meta Controller Sentinels

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle177 test-review handoff

## Findings

No blocking findings.

- `tests/unit/test_controller.py:585` covers the idle controller path for English and Chinese Presenter meta prompts. It asserts the response remains `text_only`, has no entrypoint, cannot operate, starts no runner, leaves the controller stopped, records no error, and leaves `DemoControl` without interrupt or stop state.
- `tests/unit/test_controller.py:634` covers the running controller path. The normal `meeting-control-map-demo` runner stays active while the meta prompt is submitted, and the test asserts no queued interrupt, no stop request, no `question-answer-demo`, and no extra runner call.
- `tests/unit/test_controller_session.py:159` covers the session interrupt path. It verifies `ControllerSession.answer_question(...)` returns an answer-only response and that `session.create_interrupt_step(response)` stays `None`.
- Chinese voice/profile compatibility looks acceptable for this slice. The tests use `profiles/ringcentral-video-bind-speaker.yaml`, whose speech provider is `windows-sapi-en`; `resolve_speech_provider_name(...)` maps Chinese voice output on local SAPI-capable profiles to `windows-sapi-zh`, and `ControllerSession.set_voice(...)` validates that path before answering. The idle controller meta path also never reaches `_start_target(...)`, so it cannot accidentally validate or start a demo for answer-only text.
- The answer text checks are narrow enough for the current guard contract but intentionally tied to the English `Presenter settings:` sentinel. This is not a blocker for Cycle177 because the runtime guard text currently uses that prefix for both English and Chinese voice rendering, but future localized Presenter-meta copy should update these assertions to a semantic helper or a less English-specific sentinel.
- No production or YAML files are modified in the reviewed diff. The workspace is not globally clean: `.coverage` is modified and several Cycle177 handoff docs are untracked. I left those untouched because they are outside this assigned review.

## Verification Performed

- Reviewed the working diff for:
  - `tests/unit/test_controller.py`
  - `tests/unit/test_controller_session.py`
- Reviewed related runtime boundaries in:
  - `src/ai_presenter/runtime/controller.py:368`
  - `src/ai_presenter/runtime/session.py:88`
  - `src/ai_presenter/runtime/questions.py:224`
  - `src/ai_presenter/runtime/voice.py:223`
- Ran focused pytest without default coverage, cache, or bytecode writes:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_answers_meta_prompt_without_question_demo_when_idle tests\unit\test_controller.py::test_presenter_controller_answers_meta_prompt_without_queuing_running_demo tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_presenter_meta_answer
```

Result: `6 passed in 3.97s`.

- Ran lint on the reviewed test files:

```powershell
.\.venv\Scripts\python.exe -B -m ruff check tests\unit\test_controller.py tests\unit\test_controller_session.py
```

Result: `All checks passed!`

- Ran whitespace check:

```powershell
git diff --check -- tests\unit\test_controller.py tests\unit\test_controller_session.py
```

Result: exit code 0. Git also reported the existing LF-to-CRLF warnings for the two test files.

## Residual Risks

- The running-controller test uses the existing `threading.Event` plus `release.wait(timeout=1)` pattern. It is low risk and passed locally, but an extreme CI stall longer than the runner's one-second wait could let the runner exit before the question submission. A future hardening pass could use a `try/finally` release with an unbounded wait after `started.set()`.
- The tests prove the controller/session propagation contract for one English prompt and one Chinese prompt. Broader Presenter meta phrase taxonomy remains covered at the question-routing layer rather than replayed through controller threads.
- The `Presenter settings:` assertion deliberately tracks the current guard text. If Presenter meta answers become fully localized, these tests may fail for wording rather than behavior.
- I did not run the full unit suite. This review focused on the Cycle177 tests-only diff and nearby lint/whitespace checks.

## Recommendation

Accept the Cycle177 tests-only diff. The new coverage locks the intended no-demo/no-interrupt contract across idle controller, running controller, and session interrupt boundaries without touching production code or package YAML.

Status: test review complete. No source, test, staging, or commit changes were made by this pass; only this assigned handoff file was written.

Changed file path:

- `docs/agent-handoffs/cycle-177-test-review.md`
