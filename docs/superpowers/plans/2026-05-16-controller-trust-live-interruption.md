# Controller Trust And Live Interruption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make safe controller questions behave as true queued interruptions during an active demo, add deterministic Chinese question input for RingCentral Video, and expose clearer question outcome/status helpers.

**Architecture:** Reuse `DemoControl.enqueue_interrupt()` and `MaterialDemoRuntime` instead of adding a second flow cursor. Keep question matching deterministic with a small auditable alias layer in `runtime.questions`. Keep Tk changes modest by adding pure controller helper functions and using them from existing callbacks.

**Tech Stack:** Python 3.10+, Typer/Tkinter runtime, Pydantic material package models, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/controller.py`
  - Add `queued` question status.
  - Return richer `QuestionSubmitResult` fields.
  - Queue safe question interrupt steps on the active `DemoControl` while a demo is running.
  - Add pure formatter helpers for question outcome and voice labels.
  - Wire queued status into the existing Tk callback.
- Modify `src/ai_presenter/runtime/questions.py`
  - Add deterministic Chinese phrase aliases for common RingCentral Video entrypoints.
  - Keep existing English token scoring unchanged after alias lookup.
- Modify `tests/unit/test_controller.py`
  - Replace stop-and-restart interrupt expectations with queue-based expectations.
  - Add status helper tests.
- Modify `tests/unit/test_questions.py`
  - Add Chinese question input cases and risky-control assertions.
- Modify `docs/agent-handoffs/cycle-001-implementation.md`
  - Summarize the implementation decisions, tests, and next gaps after code changes.

---

### Task 1: Queue Safe Questions During Active Demos

**Files:**
- Modify: `tests/unit/test_controller.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing tests for queue-based interrupts**

Update `tests/unit/test_controller.py`.

Replace the old expectation in `test_presenter_controller_interrupts_current_demo_for_safe_question` with a queue assertion:

```python
def test_presenter_controller_queues_safe_question_without_stopping_running_demo() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    interrupt_seen = threading.Event()
    release = threading.Event()
    calls: list[str] = []
    queued_steps: list[str] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
        captured_flow_id: str,
        *,
        control: DemoControl,
        voice: PresenterVoiceSettings | None = None,
    ) -> None:
        calls.append(captured_flow_id)
        started.set()
        while not release.is_set():
            interrupt = control.pop_interrupt()
            if interrupt is not None:
                queued_steps.append(interrupt.id)
                interrupt_seen.set()
            release.wait(timeout=0.01)

    controller = PresenterController(
        profile=profile,
        material_package=package,
        flow_id="meeting-control-map-demo",
        control=control,
        runner=runner,
    )

    controller.start()
    assert started.wait(timeout=1)

    result = controller.submit_question("chat")
    assert interrupt_seen.wait(timeout=1)
    release.set()
    controller.join(timeout=1)

    assert result.demonstration_status == "queued"
    assert result.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert result.can_operate is True
    assert control.is_stop_requested is False
    assert calls == ["meeting-control-map-demo"]
    assert queued_steps == ["question-answer"]
```

Update `test_presenter_controller_end_clears_pending_question_demo` so it proves queued interrupts do not survive a reset:

```python
def test_presenter_controller_end_clears_queued_question_before_next_run() -> None:
    profile, package = _controller_inputs()
    control = DemoControl()
    started = threading.Event()
    release = threading.Event()
    calls: list[str] = []

    def runner(
        captured_profile: DesktopAppProfile,
        captured_package: MaterialPackage,
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
    result = controller.submit_question("chat")
    assert result.demonstration_status == "queued"

    controller.end()
    release.set()
    controller.join(timeout=1)

    control.reset()
    assert control.pop_interrupt() is None
    assert calls == ["meeting-control-map-demo"]
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_controller.py
```

Expected: fail because `QuestionDemonstrationStatus` does not include `queued`, `QuestionSubmitResult` does not expose `entrypoint_id`/`can_operate`, and running questions still request stop/start a pending target.

- [ ] **Step 3: Implement queue-based running-question behavior**

In `src/ai_presenter/runtime/controller.py`, change the status literal and result model:

```python
QuestionDemonstrationStatus = Literal["text_only", "interrupting", "queued", "started"]

@dataclass(frozen=True)
class QuestionSubmitResult:
    answer_text: str
    demonstration_status: QuestionDemonstrationStatus = "text_only"
    demonstration_message: str = ""
    entrypoint_id: str | None = None
    can_operate: bool = False
```

Update `submit_question()` so running safe questions enqueue instead of stopping:

```python
        if interrupt is None:
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
            )
        question_target = _target_with_question_flow(target, interrupt)
        if self.is_running and not self.is_stopping:
            self._control.enqueue_interrupt(interrupt)
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_status="queued",
                demonstration_message="I queued that for the next safe step.",
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
            )
        if self._start_target(question_target, voice):
            return QuestionSubmitResult(
                answer_text=response.answer_text,
                demonstration_status="started",
                demonstration_message="Demonstrating it now.",
                entrypoint_id=response.entrypoint_id,
                can_operate=response.can_operate,
            )
```

Keep the existing `_switch_to_target_after_current_step()` path available for legacy/internal use, but normal safe questions should no longer use it.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_controller.py
```

Expected: all controller unit tests pass.

---

### Task 2: Add Deterministic Chinese Question Aliases

**Files:**
- Modify: `tests/unit/test_questions.py`
- Modify: `src/ai_presenter/runtime/questions.py`

- [ ] **Step 1: Write failing tests for Chinese input**

Add these tests to `tests/unit/test_questions.py`:

```python
def test_chinese_chat_question_matches_chat_entrypoint() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="聊天在哪里",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.chat"
    assert response.can_operate is True


def test_chinese_invite_question_matches_but_stays_non_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="怎么邀请别人",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.can_operate is False


def test_chinese_share_and_leave_questions_remain_text_only() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    share = answer_question(
        package=package,
        question="怎么共享屏幕",
        voice=PresenterVoiceSettings(language="zh"),
    )
    leave = answer_question(
        package=package,
        question="怎么离开会议",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert share.entrypoint_id == "ringcentral.video.toolbar.share"
    assert share.can_operate is False
    assert leave.entrypoint_id == "ringcentral.video.toolbar.leave"
    assert leave.can_operate is False


def test_chinese_background_question_matches_background_settings() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="怎么设置背景",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id in {
        "ringcentral.video.settings.background",
        "ringcentral.video.more.background",
    }
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_questions.py
```

Expected: Chinese questions fail because the current matcher does not extract meaningful non-Latin tokens.

- [ ] **Step 3: Implement alias matching**

In `src/ai_presenter/runtime/questions.py`, add aliases near the constants:

```python
_ENTRYPOINT_ALIASES: dict[str, tuple[str, ...]] = {
    "ringcentral.video.toolbar.chat": ("聊天", "聊天室", "消息"),
    "ringcentral.video.toolbar.participants": ("参会者", "参与者", "成员", "人员", "谁在会议"),
    "ringcentral.video.toolbar.invite": ("邀请", "邀请别人", "拉人", "加人"),
    "ringcentral.video.toolbar.share": ("共享屏幕", "分享屏幕", "屏幕共享", "共享"),
    "ringcentral.video.toolbar.audio": ("麦克风", "静音", "取消静音", "声音"),
    "ringcentral.video.toolbar.video": ("摄像头", "相机", "视频开关", "开启视频"),
    "ringcentral.video.more.settings": ("设置", "会议设置"),
    "ringcentral.video.settings.background": ("背景", "虚拟背景", "模糊背景", "设置背景"),
    "ringcentral.video.more.recording": ("录制", "录像", "记录会议"),
    "ringcentral.video.more.notes": ("笔记", "转录", "字幕记录"),
    "ringcentral.video.toolbar.react": ("回应", "表情", "反应", "点赞"),
    "ringcentral.video.toolbar.raise-hand": ("举手", "举手发言"),
    "ringcentral.video.top.network-quality": ("网络", "网络质量", "连接质量"),
    "ringcentral.video.top.meeting-info": ("会议信息", "会议号", "会议链接"),
    "ringcentral.video.toolbar.leave": ("离开会议", "退出会议", "结束会议"),
}
```

Add a helper and call it before token matching:

```python
def _match_entrypoint_alias(
    package: MaterialPackage,
    normalized_question: str,
) -> OperationEntrypoint | None:
    if not normalized_question:
        return None
    for entrypoint_id, aliases in _ENTRYPOINT_ALIASES.items():
        if any(alias in normalized_question for alias in aliases):
            try:
                return package.entrypoint_by_id(entrypoint_id)
            except KeyError:
                continue
    return None
```

Then start `_match_entrypoint()` with:

```python
    alias_match = _match_entrypoint_alias(package, normalized_question)
    if alias_match is not None:
        return alias_match
```

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_questions.py
```

Expected: all question tests pass.

---

### Task 3: Add Controller Outcome Helpers And UI Wiring

**Files:**
- Modify: `tests/unit/test_controller.py`
- Modify: `src/ai_presenter/runtime/controller.py`

- [ ] **Step 1: Write failing tests for helper output**

Add tests to `tests/unit/test_controller.py`:

```python
from ai_presenter.runtime.controller import describe_question_result
from ai_presenter.runtime.controller import render_voice_label


def test_describe_question_result_distinguishes_queued_started_and_risky() -> None:
    queued = QuestionSubmitResult(
        answer_text="Chat: Open chat.",
        demonstration_status="queued",
        demonstration_message="I queued that for the next safe step.",
        entrypoint_id="ringcentral.video.toolbar.chat",
        can_operate=True,
    )
    started = QuestionSubmitResult(
        answer_text="Chat: Open chat.",
        demonstration_status="started",
        demonstration_message="Demonstrating it now.",
        entrypoint_id="ringcentral.video.toolbar.chat",
        can_operate=True,
    )
    risky = QuestionSubmitResult(
        answer_text="Leave meeting: Leave or end the meeting.",
        entrypoint_id="ringcentral.video.toolbar.leave",
        can_operate=False,
    )

    assert describe_question_result(queued) == "Queued safe demo: ringcentral.video.toolbar.chat"
    assert describe_question_result(started) == "Demonstrating: ringcentral.video.toolbar.chat"
    assert describe_question_result(risky) == "Answered only: ringcentral.video.toolbar.leave is not safe to operate automatically"


def test_render_voice_label_uses_controller_labels() -> None:
    assert render_voice_label(PresenterVoiceSettings()) == "English / Professional"
    assert (
        render_voice_label(PresenterVoiceSettings(language="zh", tone="conversational"))
        == "Chinese / Conversational"
    )
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_controller.py
```

Expected: fail because the helper functions are missing.

- [ ] **Step 3: Implement helper functions and Tk status wiring**

In `src/ai_presenter/runtime/controller.py`, add helper constants and functions near the existing pure helpers:

```python
_LANGUAGE_LABELS = {"en": "English", "zh": "Chinese"}
_TONE_LABELS = {
    "professional": "Professional",
    "conversational": "Conversational",
    "concise": "Concise",
}


def render_voice_label(voice: PresenterVoiceSettings) -> str:
    return f"{_LANGUAGE_LABELS[voice.language]} / {_TONE_LABELS[voice.tone]}"


def describe_question_result(result: QuestionSubmitResult) -> str:
    if result.demonstration_status == "queued" and result.entrypoint_id is not None:
        return f"Queued safe demo: {result.entrypoint_id}"
    if result.demonstration_status == "started" and result.entrypoint_id is not None:
        return f"Demonstrating: {result.entrypoint_id}"
    if result.entrypoint_id is not None and not result.can_operate:
        return f"Answered only: {result.entrypoint_id} is not safe to operate automatically"
    if result.entrypoint_id is None:
        return "Answered only: no matching safe control"
    return f"Answered only: {result.entrypoint_id}"
```

In the Tk `submit_question()` callback, update status for queued and text-only cases:

```python
            status.set(describe_question_result(result))
            if result.demonstration_message:
                append_chat("AiPresenter", result.demonstration_message)
```

Remove or adapt the old status-only branches for `started` and `interrupting` so `queued` is visible.

- [ ] **Step 4: Run controller tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_controller.py
```

Expected: all controller unit tests pass.

---

### Task 4: Documentation, Cycle Handoff, And Verification

**Files:**
- Create: `docs/agent-handoffs/cycle-001-implementation.md`
- Modify: `docs/runbooks/ringcentral-manual-acceptance.md`

- [ ] **Step 1: Update manual acceptance checklist**

In `docs/runbooks/ringcentral-manual-acceptance.md`, add Cycle 001 checks under Controller Acceptance:

```markdown
- [ ] While `meeting-control-map-demo` is running, ask `chat`; verify the controller reports a queued safe demo and the original flow continues after Chat.
- [ ] Switch language to Chinese and ask `聊天在哪里`; verify the answer maps to Chat.
- [ ] Ask `怎么离开会议`; verify the controller answers only and does not click Leave.
```

- [ ] **Step 2: Create implementation handoff**

Create `docs/agent-handoffs/cycle-001-implementation.md`:

```markdown
# Cycle 001 Implementation Handoff

Date: 2026-05-16

## Scope

Implemented controller trust improvements: queued safe question interrupts, deterministic Chinese RingCentral question aliases, and clearer controller question outcome helpers.

## Changed Files

- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_questions.py`
- `docs/runbooks/ringcentral-manual-acceptance.md`

## Verification

Record exact command output here after running verification.

## Notes For Next Cycle

RingCentral knowledge package hardening and performance telemetry remain the best next candidates.
```

- [ ] **Step 3: Run focused and full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -q tests\unit\test_controller.py tests\unit\test_questions.py tests\unit\test_material_runtime.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\python -m ruff check --no-cache .
.\.venv\Scripts\python -m mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter controller --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run
```

Expected:

- Focused tests pass.
- Full no-coverage tests pass.
- Ruff passes.
- Mypy passes.
- Controller dry-run loads profile/package/flow and completes.

- [ ] **Step 4: Fill verification results in handoff**

Update `docs/agent-handoffs/cycle-001-implementation.md` with exact pass/fail summaries from Step 3.

---

## Self-Review Checklist

- Spec coverage: all Cycle 001 design goals map to Tasks 1-4.
- Placeholder scan: no incomplete implementation placeholders are present in this plan.
- Type consistency: `QuestionDemonstrationStatus`, `QuestionSubmitResult`, `PresenterVoiceSettings`, and helper names are consistent across tasks.
- Safety: risky controls remain answer-only.
- User workflow: running safe questions queue, idle safe questions still demonstrate immediately.
