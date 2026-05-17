# Cycle 177 Demand Analysis: Controller/Session Presenter Meta Sentinels

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle177 demand-analysis handoff

## Scope And Boundary

This pass writes only this handoff:

- `docs/agent-handoffs/cycle-177-demand-analysis.md`

No source, test, package YAML, coverage, staging, or commit changes were made.
The working tree already had `.coverage` dirty before this handoff; treat it as
unrelated existing work.

## Sources Reviewed

- Cycle174-176 handoffs under `docs/agent-handoffs/`, especially demand,
  technical-development, test-review, technical-scan, and risk-scan notes.
- Current runtime Presenter meta routing tests in `tests/unit/test_questions.py`.
- Current controller/session tests:
  - `tests/unit/test_controller_session.py`
  - `tests/unit/test_controller.py`
  - focused status/view-model context in `tests/unit/test_controller_view_model.py`
- Current orchestration code paths:
  - `src/ai_presenter/runtime/questions.py`
  - `src/ai_presenter/runtime/session.py`
  - `src/ai_presenter/runtime/controller.py`

## User Need

Cycles 174 and 175 established the runtime guard: pure Presenter expression
requests are answer-only, non-operable, and no-interrupt. Cycle176 promoted that
rule into the RingCentral Video runtime safety knowledge docs.

The remaining user need is controller/session confidence. A user may ask
AiPresenter to answer in a different language, use a different tone, be more
concise, speak more slowly, or explain at a beginner level while the controller
is idle or while a demo is already running. Those prompts are about AiPresenter's
answer style. They should stay text-only through the higher-level controller and
session APIs too; they must not enqueue an interrupt into an active demo and must
not start the synthetic `question-answer-demo` flow when idle.

This matters because the visible user failure is not only a bad route in
`answer_question(...)`. It is the controller moving the meeting UI after a
language/tone/detail request. The next slice should prove the orchestration layer
honors the runtime guard.

## Current Coverage Snapshot

`tests/unit/test_questions.py` already has strong runtime sentinels:

- English pure meta prompts such as `Answer in Chinese`, `Switch to careful
  tone`, `Be more concise`, and `I am new to RingCentral Video` return
  `entrypoint_id is None`, `can_operate is False`, and no question interrupt.
- Chinese pure meta prompts such as `请用中文回答`, `请简洁一点`, `请讲慢一点`,
  and `我是新手，请讲简单一点` have the same no-entrypoint/no-interrupt shape.
- Mixed meta plus RingCentralVideo prompts preserve Q&A-first and explicit
  control behavior.

`tests/unit/test_controller_session.py` currently covers:

- safe app questions creating an interrupt step, for example `chat`;
- risky or answer-only RingCentral paths producing no interrupt, for example
  `leave meeting` and Notes/transcript policy;
- active voice settings and temporary scanned packages.

It does not yet include a Presenter meta session sentinel.

`tests/unit/test_controller.py` currently covers:

- running controllers queueing safe `chat` interrupts without stopping the main
  demo;
- idle controllers starting a safe `question-answer-demo` for `chat`;
- risky `leave meeting` answers staying `text_only`;
- Spanish OpenAI and indexed question-flow start behavior.

It does not yet prove that English or Chinese Presenter meta prompts avoid both
the running-demo queue path and the idle `question-answer-demo` start path.

## Recommended Scope

Recommended next implementation slice: add focused controller/session tests only.
No runtime behavior change is expected if the existing guard is working.

Add one small session-level sentinel near the existing interrupt tests in
`tests/unit/test_controller_session.py`:

- select the RingCentral Video material package target;
- submit representative English and Chinese pure Presenter meta prompts through
  `ControllerSession.answer_question(...)`;
- assert the response is answer-only and
  `ControllerSession.create_interrupt_step(response) is None`.

Add two controller-level sentinels near the existing question-demo tests in
`tests/unit/test_controller.py`:

- idle controller: submit English and Chinese pure Presenter meta prompts and
  assert `demonstration_status == "text_only"`, no entrypoint, no operation
  permission, no demonstration message, no runner call, and no
  `question-answer-demo` start;
- running controller: start the ordinary `meeting-control-map-demo`, submit the
  same meta prompts, and assert the result stays `text_only`, no interrupt is
  queued, the only runner call remains the original flow, and
  `question-answer-demo` never appears in captured calls.

Keep the prompt matrix small at the controller layer. The runtime tests already
own broad phrase coverage; controller/session tests should prove propagation of
the no-interrupt/no-demo contract.

## Candidate Prompts

Recommended session prompt matrix:

- `Answer in Chinese`
- `Switch to careful tone`
- `Be more concise`
- `I am new to RingCentral Video`
- `请用中文回答`
- `请简洁一点`
- `请讲慢一点`
- `我是新手，请讲简单一点`

Recommended controller prompt matrix:

- `Answer in Chinese`
- `请用中文回答`

Optional controller expansion, if the implementation wants tone/detail coverage
without much extra cost:

- `Switch to careful tone`
- `请简洁一点`

Negative controls should remain the existing controller tests rather than new
work:

- `chat` still queues while running and starts `question-answer-demo` when idle.
- `leave meeting` still answers text-only because it is a risky control route.

## Acceptance Criteria

For each session-level Presenter meta prompt:

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `response.answer_text` uses the existing `Presenter settings:` framing or an
  equivalent explicit Presenter-settings framing
- `session.create_interrupt_step(response) is None`
- the answer text does not use RingCentral control prefixes such as `Chat:`,
  `Participants:`, `Meeting information:`, `More actions:`, `More video
  settings:`, `View layout menu:`, `Network quality:`, or `Reactions:`

For each idle-controller Presenter meta prompt:

- `controller.submit_question(prompt).demonstration_status == "text_only"`
- `entrypoint_id is None`
- `can_operate is False`
- `demonstration_message == ""`
- the runner is not called
- `question-answer-demo` is not present in captured flow IDs
- the controller is not left running after the submit call

For each running-controller Presenter meta prompt:

- the main demo has started before submitting the prompt
- the result stays `text_only`
- `entrypoint_id is None`
- `can_operate is False`
- no interrupt is observed or queued through `DemoControl`
- captured flow IDs contain only the original `meeting-control-map-demo`
- `question-answer-demo` is not present in captured flow IDs
- the test releases and joins the running thread cleanly

Focused verification for the future implementation cycle:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller_session.py tests\unit\test_controller.py::test_presenter_controller_queues_safe_question_without_stopping_running_demo tests\unit\test_controller.py::test_presenter_controller_starts_safe_question_demo_when_idle tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo
```

After adding the new tests, include their exact test node IDs in the focused
command. Run `git diff --check` before handoff.

## Non-Goals

- Do not modify `src/ai_presenter/runtime/questions.py` unless a new sentinel
  exposes an actual regression and the implementation cycle explicitly expands
  from tests to a fix.
- Do not modify `packages/ringcentral-video.yaml`.
- Do not add new Presenter meta fragments or broaden runtime phrase matching.
- Do not implement persistent natural-language language, tone, pacing, detail,
  or familiarity state mutation.
- Do not change controller UI, view-model labels, voice readiness, profile
  validation, SAPI/Piper/OpenAI behavior, or demo runner behavior.
- Do not replace the existing runtime routing tests in `test_questions.py`; this
  slice complements them at the controller/session layer.
- Do not run live RingCentral acceptance.
- Do not stage or commit `.coverage` or unrelated files.

## Risk Notes

- Controller tests can become flaky if they wait for an interrupt that should
  never arrive. Prefer capturing queued steps in the runner loop, submitting the
  meta prompt, releasing the thread, joining, and then asserting the captured
  queue list stayed empty.
- Keep controller prompt coverage narrow. Re-testing the entire runtime phrase
  list through threads would slow the suite and obscure the intent.
- Avoid asserting that the language or tone was persistently changed. The
  current guard returns an answer; it does not mutate `PresenterVoiceSettings`.
- If Chinese prompts are tested with a Chinese voice setting, use a compatible
  profile setup already present in the controller/session tests. The test goal is
  no demo orchestration, not voice-provider validation.
- If the answer text is localized in a later slice, the sentinel should preserve
  the semantic framing rather than freezing English-only wording forever.

## Status

Cycle177 demand analysis complete. Recommended next slice: add focused
controller/session sentinel tests proving English and Chinese Presenter meta
requests stay text-only and never enqueue or start `question-answer-demo`.

Changed file path:

- `docs/agent-handoffs/cycle-177-demand-analysis.md`
