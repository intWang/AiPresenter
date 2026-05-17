# Cycle 177 Technical Scan: Presenter Meta Controller Guards

Date: 2026-05-17

## Scope

- Inspected `src/ai_presenter/runtime/controller.py`.
- Inspected `src/ai_presenter/runtime/session.py`.
- Inspected `tests/unit/test_controller.py`.
- Inspected `tests/unit/test_controller_session.py`.
- Checked related Presenter meta classifier coverage in `tests/unit/test_questions.py`.
- Ran a read-only probe with `.\.venv\Scripts\python.exe` to confirm current runtime behavior.
- Did not modify source, tests, or git staging.

## Current Baseline

Presenter meta requests already resolve as answer-only at the question-routing layer:

- `answer_question(...)` returns `entrypoint_id=None` and `can_operate=False`.
- `create_question_interrupt_step(...)` returns `None` when there is no operable entrypoint.
- `PresenterController.submit_question(...)` returns `QuestionSubmitResult` with
  `demonstration_status="text_only"` before any start/queue branch when the interrupt is `None`.
- Existing `tests/unit/test_questions.py` covers the classifier and interrupt helper directly for
  English and Chinese meta prompts, but the controller/session integration path is not locked yet.

This slice should be tests-only. No production code is expected.

## Exact Tests To Add

Add the following near the existing safe/risky question tests in `tests/unit/test_controller.py`.
It reuses the current `_controller_inputs()` helper, `DemoControl`, `PresenterController`,
`PresenterVoiceSettings`, and the existing `pytest` import.

```python
@pytest.mark.parametrize(
    ("question", "voice"),
    [
        ("Please be brief", PresenterVoiceSettings(language="en")),
        ("\u8bf7\u7528\u4e2d\u6587\u56de\u7b54", PresenterVoiceSettings(language="zh")),
    ],
)
def test_presenter_controller_answers_presenter_meta_request_without_starting_demo_when_idle(
    question: str,
    voice: PresenterVoiceSettings,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
        voice=voice,
    )

    result = controller.submit_question(question)
    controller.join(timeout=1)

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id is None
    assert result.can_operate is False
    assert result.answer_text.startswith("Presenter settings:")
    assert controller.is_running is False
    assert calls == []
    assert control.pop_interrupt() is None
    assert control.is_stop_requested is False
```

Add the running-controller companion beside
`test_presenter_controller_queues_safe_question_without_stopping_running_demo`.
It reuses that test's `threading.Event` runner shape but intentionally does not pop interrupts
inside the runner, so a regression leaves a queued step visible after the submit.

```python
@pytest.mark.parametrize(
    ("question", "voice"),
    [
        ("Please be brief", PresenterVoiceSettings(language="en")),
        ("\u8bf7\u7528\u4e2d\u6587\u56de\u7b54", PresenterVoiceSettings(language="zh")),
    ],
)
def test_presenter_controller_answers_presenter_meta_request_without_queuing_running_demo(
    question: str,
    voice: PresenterVoiceSettings,
) -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    release = threading.Event()
    calls: list[str] = []

    def runner(
        _profile: DesktopAppProfile,
        _package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        release.wait(timeout=1)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)
    controller.set_voice(voice)

    result = controller.submit_question(question)
    release.set()
    controller.join(timeout=1)

    assert result.demonstration_status == "text_only"
    assert result.demonstration_message == ""
    assert result.entrypoint_id is None
    assert result.can_operate is False
    assert result.answer_text.startswith("Presenter settings:")
    assert control.pop_interrupt() is None
    assert control.is_stop_requested is False
    assert calls == ["meeting-control-map-demo"]
    assert "question-answer-demo" not in calls
```

Add the following near the existing interrupt-step tests in
`tests/unit/test_controller_session.py`. It reuses `load_desktop_profile()`,
`load_material_package(...)`, `MaterialPackageTarget`, `ControllerSession`, and
`PresenterVoiceSettings`; no new imports are needed.

```python
@pytest.mark.parametrize(
    ("question", "voice"),
    [
        ("Please be brief", PresenterVoiceSettings(language="en")),
        ("\u8bf7\u7528\u4e2d\u6587\u56de\u7b54", PresenterVoiceSettings(language="zh")),
    ],
)
def test_session_does_not_create_interrupt_for_presenter_meta_requests(
    question: str,
    voice: PresenterVoiceSettings,
) -> None:
    session = ControllerSession()
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    session.select_target(
        MaterialPackageTarget(
            profile=load_desktop_profile(),
            package=package,
            flow_id="meeting-control-map-demo",
        )
    )
    session.set_voice(voice)

    response = session.answer_question(question)

    assert response.entrypoint_id is None
    assert response.can_operate is False
    assert response.answer_text.startswith("Presenter settings:")
    assert session.create_interrupt_step(response) is None
```

## Fixtures And Patterns To Reuse

- `tests/unit/test_controller.py::_controller_inputs()` loads
  `profiles/ringcentral-video-bind-speaker.yaml` plus `packages/ringcentral-video.yaml`.
- `test_presenter_controller_starts_safe_question_demo_when_idle` shows the idle runner-call
  assertion pattern; invert it here with `calls == []`.
- `test_presenter_controller_queues_safe_question_without_stopping_running_demo` shows the
  `threading.Event` pattern for keeping a controller running while submitting a question.
- `test_presenter_controller_answers_risky_question_without_demo` is the nearest
  `text_only` controller precedent.
- `tests/unit/test_controller_session.py::test_session_does_not_create_interrupt_for_risky_answer`
  is the closest session-side no-interrupt precedent.
- Use Unicode escapes for Chinese prompts in the new tests, matching
  `tests/unit/test_questions.py`, to avoid Windows console/source-encoding ambiguity.

## Focused Commands

Run only the new/nearby tests first, avoiding default coverage and cache churn:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller.py::test_presenter_controller_answers_presenter_meta_request_without_starting_demo_when_idle tests\unit\test_controller.py::test_presenter_controller_answers_presenter_meta_request_without_queuing_running_demo tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_presenter_meta_requests
```

Then include the existing lower-level Presenter meta sentinels:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_chinese_presenter_meta_requests_do_not_route_to_ringcentral_controls tests\unit\test_questions.py::test_presenter_meta_modifiers_do_not_steal_ringcentral_intents tests\unit\test_questions.py::test_chinese_presenter_meta_modifiers_do_not_steal_ringcentral_intents
```

Lint only the touched tests:

```powershell
.\.venv\Scripts\python.exe -B -m ruff check tests\unit\test_controller.py tests\unit\test_controller_session.py
```

Before handoff, confirm the slice stayed tests-only:

```powershell
git diff -- tests\unit\test_controller.py tests\unit\test_controller_session.py
git status --short
```

## Risks

- If a future change makes Presenter meta produce an `entrypoint_id`, the idle controller will
  start `question-answer-demo`; the first controller test catches that.
- If a future change enqueues an interrupt while a normal demo is running, the running-controller
  test catches it through `control.pop_interrupt() is None` and unchanged `calls`.
- Do not assert localized Chinese answer text here. Current Presenter meta answer is the stable
  `"Presenter settings:"` runtime guard text rendered through voice styling.
- Keep this out of `packages/ringcentral-video.yaml`; Presenter expression requests are runtime
  guards, not app aliases or Q&A facts.
- Avoid running default pytest without `--override-ini addopts= --no-cov` unless intentionally
  refreshing `.coverage`.

## Status

Technical scan complete. Source and tests were inspected only. This handoff is the only intended
file change.

Changed file: `docs/agent-handoffs/cycle-177-technical-scan.md`
