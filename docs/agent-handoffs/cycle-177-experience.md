# Cycle 177 Experience Handoff: Presenter Meta Orchestration Sentinels

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Scope: write only `docs/agent-handoffs/cycle-177-experience.md`

## Sources Read

- `docs/agent-handoffs/cycle-177-demand-analysis.md`
- `docs/agent-handoffs/cycle-177-risk-scan.md`
- `docs/agent-handoffs/cycle-177-technical-scan.md`
- `docs/agent-handoffs/cycle-177-technical-development.md`
- Recent experience handoffs for format and continuity:
  - `docs/agent-handoffs/cycle-176-experience.md`
  - `docs/agent-handoffs/cycle-175-experience.md`
  - `docs/agent-handoffs/cycle-170-experience.md`
- Current working diff for:
  - `.coverage`
  - `tests/unit/test_controller.py`
  - `tests/unit/test_controller_session.py`
- `git status --short`, `git diff --name-status`, and `git diff --stat`

Workspace context: `.coverage`, `tests/unit/test_controller.py`, and
`tests/unit/test_controller_session.py` were already dirty, and the three
Cycle177 scan docs were already untracked. Treat all of that as other-agent
work. This pass only writes the experience handoff named above.

## When To Add Orchestration Sentinels

Runtime guards are necessary but not enough when the visible failure can happen
above the router. Cycles 174-176 established the lower-level rule: pure
Presenter expression prompts are answer-only, non-operable, and no-interrupt.
Cycle177's lesson is to add orchestration sentinels after that runtime rule is
stable, because the controller can still accidentally wrap an answer-only result
into `question-answer-demo`, and the session can still accidentally create an
interrupt step.

Use this pattern when a prompt family already has route-level coverage but the
user-visible risk is "the meeting UI moved anyway." Keep the controller/session
tests representative, not exhaustive. The runtime suite owns the broad language,
tone, pacing, detail, familiarity, mixed-intent, and localized prompt taxonomy.
The orchestration suite should prove propagation of the existing contract:

- no `entrypoint_id`
- `can_operate is False`
- no interrupt step
- no idle `question-answer-demo`
- no queued interrupt during an already running demo

This sequencing keeps source behavior and test intent crisp. First prove the
router classifies correctly; then prove higher layers respect that answer-only
shape.

## Controller No-Demo Patterns

For idle controllers, use a runner spy and assert it never runs. The useful
assertion cluster is:

- `result.demonstration_status == "text_only"`
- `result.demonstration_message == ""`
- `result.entrypoint_id is None`
- `result.can_operate is False`
- `result.answer_text.startswith("Presenter settings:")`
- `controller.is_running is False`
- `controller.last_error is None`
- runner calls stay empty
- `control.pop_interrupt() is None`
- `control.is_stop_requested is False`

For running controllers, start the normal `meeting-control-map-demo`, submit the
Presenter meta prompt while the runner is held open, then release and join the
thread. The important no-demo assertions are that captured calls remain exactly
`["meeting-control-map-demo"]`, `question-answer-demo` is absent, and
`control.pop_interrupt() is None`.

Use a compatible profile and voice setting for localized prompts. The current
tests use `_controller_inputs()` and `PresenterVoiceSettings(language="zh")`,
which is useful because an accidental demo-start branch should fail as a real
orchestration regression, not be hidden behind an unrelated voice/profile
validation error. Use Unicode escapes for Chinese prompts in test source to
avoid Windows console and source-encoding ambiguity.

## Threading-Safe Test Pattern

Threaded controller tests should never wait for an interrupt that must not
exist. Hold the runner with `threading.Event`, submit the prompt, inspect the
control queue from the test thread, release the runner, and join with a bounded
timeout. A regression that queues an interrupt should be visible after
`submit_question(...)` through `control.pop_interrupt()`.

Keep the threaded prompt matrix small. One English and one Chinese
representative prompt are enough at the controller layer because the route
matrix is already covered elsewhere. If a future slice adds more threaded
cases, release the runner in a `finally` block before joining so assertion
failures do not leave a live controller thread behind.

## Session Interrupt Contract

`ControllerSession.answer_question(...)` returns the routing result; it does not
by itself guarantee that a later layer will refuse to operate. The session
contract is completed by `ControllerSession.create_interrupt_step(response)`.
For Presenter meta responses, the durable session assertion is:

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `response.answer_text.startswith("Presenter settings:")`
- `session.create_interrupt_step(response) is None`

Do not assert that a language, tone, pacing, detail, or familiarity preference
was persistently changed. The current behavior answers the user's style request
safely; it does not mutate durable Presenter voice state. Also avoid asserting
localized answer prose here. The stable contract is no interrupt, not exact
copy.

## Current Diff Lessons

The current diff already follows the Cycle177 scan direction:

- `tests/unit/test_controller.py` adds idle no-demo coverage for English and
  Chinese Presenter meta prompts.
- `tests/unit/test_controller.py` adds a running-demo sentinel that proves the
  existing demo is not stopped, no interrupt is queued, and
  `question-answer-demo` is not started.
- `tests/unit/test_controller_session.py` adds a session no-interrupt sentinel
  for the same representative prompt pair.
- `docs/agent-handoffs/cycle-177-technical-development.md` reports that the
  focused controller/session tests and Ruff checks passed for the current test
  slice; re-run them before any integration step rather than relying on that
  report alone.
- `.coverage` is still dirty as binary coverage data and should remain
  unrelated unless a future owner explicitly refreshes coverage artifacts.

The reusable experience is not the exact prompts. It is the shape of the
protection: once runtime says "answer-only," every orchestration layer that can
move UI needs a small sentinel proving it preserves "answer-only."

## Next-Cycle Backlog

- Run the focused Cycle177 tests with coverage and cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_answers_meta_prompt_without_question_demo_when_idle tests\unit\test_controller.py::test_presenter_controller_answers_meta_prompt_without_queuing_running_demo tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_presenter_meta_answer
```

- Run the existing runtime meta sentinels if any routing code changes:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents
```

- Run style and whitespace checks only on owned paths for the implementation
  slice:

```powershell
.\.venv\Scripts\python.exe -B -m ruff check tests\unit\test_controller.py tests\unit\test_controller_session.py
git diff --check -- tests\unit\test_controller.py tests\unit\test_controller_session.py docs\agent-handoffs\cycle-177-experience.md
```

- Review the running-controller test for thread cleanup if future edits add
  earlier assertions, exceptions, or more prompt cases. Prefer a `finally`
  release/join pattern for any larger threaded expansion.
- Keep controller/session prompt coverage narrow unless a real orchestration
  regression appears. Add broader phrase coverage in `tests/unit/test_questions.py`.
- Do not move Presenter expression prompts into `packages/ringcentral-video.yaml`
  or claim persistent Presenter voice state without explicit state mutation and
  tests.
- Do not stage or commit `.coverage`, scan handoffs, or unrelated work unless a
  future assignment explicitly owns that integration step.

## Status

Cycle177 experience handoff complete. The key lesson is to add small
controller/session sentinels after runtime answer-only guards, so Presenter
language, tone, pacing, detail, and familiarity requests cannot become demo
starts or queued interrupts.

Changed file path:

- `docs/agent-handoffs/cycle-177-experience.md`
