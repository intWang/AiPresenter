# Cycle 177 Risk Scan: Controller/Session Meta Prompt No-Demo Sentinels

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle177 risk-scan handoff

## Scope And Boundary

This pass reviewed Presenter meta routing, `PresenterController.submit_question(...)`,
session interrupt creation, and related tests. Per assignment, it writes only this file:

- `docs/agent-handoffs/cycle-177-risk-scan.md`

No source, tests, package YAML, knowledge docs, `.coverage`, staging, or commits
were modified by this pass. The workspace already had `.coverage` dirty before
the scan and it was not touched.

Reviewed anchors:

- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/voice.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_session.py`
- Cycle175/176 risk, technical, and test handoffs for Presenter meta routing

Candidate slice: add controller/session sentinel tests proving pure Presenter
meta prompts do not create a `question-answer-demo`, do not enqueue a question
interrupt, and stay text-only at the orchestration layer.

## Current Behavior To Preserve

Runtime routing already covers the core invariant:

- `_answer_question(...)` runs Q&A before Presenter meta detection.
- Pure Presenter meta prompts return `QuestionResponse(entrypoint_id=None, can_operate=False)`.
- `create_question_interrupt_step(...)` returns `None` when there is no
  entrypoint or the response is not operable.
- `PresenterController.submit_question(...)` starts or queues
  `question-answer-demo` only after `create_question_interrupt_step(...)`
  returns a `DemoStep`.

Existing `tests/unit/test_questions.py` covers the runtime route matrix for
English and Chinese meta prompts, mixed RingCentralVideo intents, bare Chinese
safety/status words, and mojibake rejection. Existing controller tests cover
safe question demos, queued interrupts, indexed `question-answer-demo` lookup,
and risky answer-only questions, but they do not directly sentinel pure
Presenter meta prompts at the controller/session layer.

## Must-Have Tests

Add exactly focused orchestration sentinels. Do not broaden the runtime route
matrix in this slice unless a failure proves the runtime layer regressed.

### 1. Controller idle pure meta prompt does not start question demo

Suggested home: `tests/unit/test_controller.py`.

Suggested name:

- `test_presenter_controller_answers_meta_prompt_without_question_demo_when_idle`

Shape:

- Build the normal `_controller_inputs()` profile/package.
- Use a runner spy that appends `(package.app_id, flow_id, voice)`.
- Submit one English pure meta prompt such as `Answer in Chinese` or
  `Be more concise`.
- Assert:
  - `result.demonstration_status == "text_only"`
  - `result.entrypoint_id is None`
  - `result.can_operate is False`
  - the runner spy was not called
  - `controller.is_running is False`
  - `controller.last_error is None`

This directly protects the `submit_question(...)` branch that would otherwise
wrap the answer into a `question-answer-demo`.

### 2. Controller Chinese pure meta prompt uses compatible voice/profile and still does not demo

Suggested home: `tests/unit/test_controller.py`, either as a second case in the
same parametrized test or a small separate test.

Shape:

- Use `_controller_inputs()` because `ringcentral-video-bind-speaker` uses a
  local SAPI route that resolves Chinese output to `windows-sapi-zh`.
- Set `voice=PresenterVoiceSettings(language="zh", tone="friendly")` on the
  controller or via `set_voice(...)`.
- Submit one high-confidence Chinese meta prompt already covered by
  `test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls`.
- Assert the same no-demo fields as above.

This prevents a false pass where an incompatible profile raises during
`_start_target(...)` and masks a bad demo-start attempt.

### 3. Session pure meta response does not create an interrupt step

Suggested home: `tests/unit/test_controller_session.py`.

Suggested name:

- `test_session_does_not_create_interrupt_for_presenter_meta_answer`

Shape:

- Select a material package target.
- Optionally parametrize English and Chinese voice/prompt pairs using a
  compatible profile for Chinese.
- Call `session.answer_question(...)`.
- Assert:
  - `response.entrypoint_id is None`
  - `response.can_operate is False`
  - `session.create_interrupt_step(response) is None`

This locks the session-level sentinel without duplicating the full runtime
route matrix.

## Risks And Test Design Notes

### 1. Flaky Threading Tests

High risk if the slice tries to prove the running-demo queue path with another
event loop. Existing controller tests already use `threading.Event` for the
safe queued interrupt path. A meta no-demo sentinel does not need a live runner:
if the response has no interrupt, the idle path must not call `_start_target(...)`
at all.

Recommendation: make the must-have controller test idle and deterministic. If
a future cycle adds a running-demo meta sentinel, keep it optional, release the
runner in `finally`, never wait for an interrupt that should not appear, and
assert `control.pop_interrupt() is None` after `submit_question(...)`.

### 2. Over-Constraining Generic No-Match Behavior

Medium risk. The desired behavior is not "every unknown prompt must have this
exact answer." It is "known Presenter meta prompts must stay answer-only and
must not become a question demo."

Avoid adding controller/session assertions for generic text like
`quantum waffle`, or exact no-match prose. The existing runtime tests already
cover blank/no-match behavior. Keep the controller assertions on the fields and
runner calls that define orchestration safety.

### 3. Mixing Runtime Route Tests With Controller Orchestration

Medium-high risk. `tests/unit/test_questions.py` is the right layer for route
ordering, Chinese phrase matrices, mixed prompts, bare words, and mojibake.
`tests/unit/test_controller.py` should not replay that matrix.

Recommendation: use one English and one Chinese representative prompt in
controller tests. Trust the runtime suite for prompt taxonomy; assert only that
the controller does not translate a text-only response into
`question-answer-demo`.

### 4. Chinese Voice/Profile Compatibility

Medium risk. `PresenterController.submit_question(...)` validates profile voice
only when it starts a target. A pure text-only meta response will not hit that
validation path. If a test uses an incompatible Chinese voice/profile, a bad
future implementation could fail with voice validation instead of revealing
that it attempted to start a demo.

Recommendation: for Chinese controller no-demo sentinels, use a profile that
can validate Chinese if the demo-start branch is accidentally reached. The
existing `_controller_inputs()` profile is acceptable because Chinese resolves
to `windows-sapi-zh`; an OpenAI profile is also acceptable but adds unnecessary
fixture variation.

### 5. `.coverage` Churn

Medium risk and already present in this workspace. The tree has `.coverage`
dirty before Cycle177. Do not run default coverage-enabled test commands for
this slice.

Recommendation: run focused tests with `--no-cov`, `-p no:cacheprovider`,
`-B`, and `PYTHONDONTWRITEBYTECODE=1`. Do not stage or commit `.coverage`.

## Suggested Focused Verification

If the future implementation adds only the controller/session tests above:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_answers_meta_prompt_without_question_demo_when_idle tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_presenter_meta_answer
git diff --check -- tests\unit\test_controller.py tests\unit\test_controller_session.py
git status --short -- .coverage tests\unit\test_controller.py tests\unit\test_controller_session.py
```

If the test is parametrized and pytest node IDs change, run the two files
focused instead:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py tests\unit\test_controller_session.py
```

No runtime routing test expansion is required for this candidate slice. If the
implementation changes `src/ai_presenter/runtime/questions.py`, then also run
the existing Presenter meta routing sentinels in `tests/unit/test_questions.py`.

## No-Go Conditions

Do not accept the Cycle177 sentinel slice if it:

- Starts a real thread just to prove the idle no-demo path.
- Adds broad generic no-match assertions unrelated to Presenter meta prompts.
- Re-implements the full English/Chinese runtime route matrix in controller
  tests.
- Uses an incompatible Chinese voice/profile combination that can hide an
  accidental demo-start attempt behind a validation error.
- Touches source, package YAML, knowledge docs, or `.coverage` for a test-only
  sentinel slice.
- Stages or commits unrelated dirty files.

## Recommendation

Proceed with a small test-only sentinel slice when source/test edits are
allowed: one controller idle no-demo test covering English and Chinese pure meta
prompts, plus one session no-interrupt test. Keep the runtime route suite as the
source of truth for prompt taxonomy. Avoid adding a new running-thread test
unless a real bug is found in the queue path.

## Status

Status: risk scan complete; source, tests, package YAML, knowledge docs,
`.coverage`, staging, and commits were not modified by this pass.

Changed file path:

- `docs/agent-handoffs/cycle-177-risk-scan.md`
