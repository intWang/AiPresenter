# Timing Telemetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add redaction-safe timing logs for question answering and package action execution.

**Architecture:** Keep telemetry local and dependency-free. Add helper functions to `runtime.logging`, then instrument `runtime.questions` and `runtime.package_demo` with `perf_counter` and metadata-only log fields.

**Tech Stack:** Python logging, pytest `caplog`, monkeypatchable `perf_counter`.

---

### Task 1: Timing Helper And Instrumentation

**Files:**
- Modify: `src/ai_presenter/runtime/logging.py`
- Modify: `tests/unit/test_runtime_logging.py`
- Modify: `src/ai_presenter/runtime/questions.py`
- Modify: `tests/unit/test_questions.py`
- Modify: `src/ai_presenter/runtime/package_demo.py`
- Modify: `tests/unit/test_package_demo.py`
- Create: `docs/agent-handoffs/cycle-007-implementation.md`

- [ ] **Step 1: Add failing logging helper tests**

In `tests/unit/test_runtime_logging.py`, add:

```python
from ai_presenter.runtime.logging import elapsed_ms, log_timed_event


def test_elapsed_ms_returns_milliseconds() -> None:
    assert elapsed_ms(1.25, 1.5) == 250.0


def test_log_timed_event_redacts_secret_fields(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("ai_presenter.test.telemetry")

    with caplog.at_level(logging.INFO, logger="ai_presenter.test.telemetry"):
        log_timed_event(
            logger,
            "demo_event",
            duration_ms=12.34,
            status="ok",
            api_key="sk-secret",
            package="demo",
            omitted=None,
        )

    message = caplog.records[-1].getMessage()
    assert "demo_event" in message
    assert "duration_ms=12.34" in message
    assert "status=ok" in message
    assert "api_key=***REDACTED***" in message
    assert "sk-secret" not in message
    assert "omitted=" not in message
```

Also import `pytest` at the top of the file.

- [ ] **Step 2: Run logging tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_logging.py
```

Expected: import failures for missing helper functions.

- [ ] **Step 3: Implement logging helpers**

In `src/ai_presenter/runtime/logging.py`, add:

```python
def elapsed_ms(start: float, end: float) -> float:
    return round((end - start) * 1000, 2)


def log_timed_event(
    logger: logging.Logger,
    event: str,
    *,
    duration_ms: float,
    status: str,
    **fields: object,
) -> None:
    parts = [event, f"status={status}", f"duration_ms={duration_ms:.2f}"]
    for key, value in fields.items():
        if value is None:
            continue
        parts.append(f"{key}={redact_value(value)}")
    logger.info(" ".join(parts))
```

- [ ] **Step 4: Add failing question telemetry test**

In `tests/unit/test_questions.py`, add imports `logging` and `questions_module`:

```python
import logging
from ai_presenter.runtime import questions as questions_module
```

Add:

```python
def test_answer_question_logs_timing_without_question_text(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    times = iter([1.0, 1.123])
    monkeypatch.setattr(questions_module, "perf_counter", lambda: next(times))

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.questions"):
        response = answer_question(
            package=package,
            question="How do I protect my real background?",
            voice=PresenterVoiceSettings(),
        )

    message = caplog.records[-1].getMessage()
    assert response.entrypoint_id == "ringcentral.video.settings.background"
    assert "question_answered" in message
    assert "duration_ms=123.00" in message
    assert "package=ringcentral-video" in message
    assert "entrypoint=ringcentral.video.settings.background" in message
    assert "can_operate=False" in message
    assert "How do I protect" not in message
    assert response.answer_text not in message
```

Run it and verify it fails because no timing log exists:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_answer_question_logs_timing_without_question_text
```

- [ ] **Step 5: Instrument `answer_question`**

In `src/ai_presenter/runtime/questions.py`:

- Import `logging`, `perf_counter`, and the timing helpers.
- Add `logger = logging.getLogger("ai_presenter.runtime.questions")`.
- Move existing answer logic into `_answer_question(...)`.
- Wrap `answer_question(...)` with timing, logging `status=ok` or `status=error`.
- Log only metadata: package, language, tone, entrypoint, can_operate.

- [ ] **Step 6: Add failing package action telemetry tests**

In `tests/unit/test_package_demo.py`, import `logging` and `package_demo_module`:

```python
import logging
from ai_presenter.runtime import package_demo as package_demo_module
```

Add:

```python
def test_package_action_executor_logs_action_duration(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter([2.0, 2.05])
    monkeypatch.setattr(package_demo_module, "perf_counter", lambda: next(times))
    driver = RecordingDemoDriver()
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.package_demo"):
        executor.execute_action("ringcentral.video.toolbar.more-control", operation="open")

    message = caplog.records[-1].getMessage()
    assert "package_action_executed" in message
    assert "status=ok" in message
    assert "duration_ms=50.00" in message
    assert "package=ringcentral-video" in message
    assert "entrypoint=ringcentral.video.toolbar.more-control" in message
    assert "operation=open" in message


def test_package_action_executor_logs_action_failure_duration(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter([3.0, 3.025])
    monkeypatch.setattr(package_demo_module, "perf_counter", lambda: next(times))
    driver = RecordingDemoDriver()
    driver.fail_controls.update({"Raise hand", "Lower hand"})
    executor = PackageActionExecutor(
        package=make_package(),
        driver=driver,
        handle=make_handle(),
        clear_before_action=False,
        action_hold_seconds=0,
    )

    with caplog.at_level(logging.INFO, logger="ai_presenter.runtime.package_demo"):
        with pytest.raises(PackageActionExecutionError):
            executor.execute_action("ringcentral.video.toolbar.raise-hand-alternate", operation="open")

    message = caplog.records[-1].getMessage()
    assert "package_action_executed" in message
    assert "status=error" in message
    assert "duration_ms=25.00" in message
    assert "entrypoint=ringcentral.video.toolbar.raise-hand-alternate" in message
```

Run both tests and verify RED:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_package_demo.py::test_package_action_executor_logs_action_duration tests\unit\test_package_demo.py::test_package_action_executor_logs_action_failure_duration
```

- [ ] **Step 7: Instrument package action execution**

In `src/ai_presenter/runtime/package_demo.py`:

- Import `logging`, `perf_counter`, and timing helpers.
- Add `logger = logging.getLogger("ai_presenter.runtime.package_demo")`.
- Wrap `execute_action(...)` with timing and log `package_action_executed` in a `finally`.
- Preserve existing behavior and exceptions.
- Do not log target UI text beyond package/entrypoint/operation metadata.

- [ ] **Step 8: Run focused telemetry tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_runtime_logging.py tests\unit\test_questions.py tests\unit\test_package_demo.py
```

Expected: focused suites pass.

- [ ] **Step 9: Write implementation handoff**

Create `docs/agent-handoffs/cycle-007-implementation.md` with actual RED/GREEN commands, files changed, privacy notes, and remaining risks.

- [ ] **Step 10: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full suite passes with only the known `pywinauto` STA COM threading warning.
