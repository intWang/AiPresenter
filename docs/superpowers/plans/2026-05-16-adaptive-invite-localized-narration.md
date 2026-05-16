# Adaptive Invite Localized Narration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure active-meeting RingCentral invite rewrites use correct Chinese narration instead of stale package-localized empty-room text.

**Architecture:** Keep the fix inside `runtime.adaptive_demo`. When adaptive logic rewrites invite narration, update both English `text` and `localized_text` with active-meeting content. Tests exercise the adjusted step and rendered Chinese output.

**Tech Stack:** Python dataclasses/Pydantic models, existing presenter voice renderer, pytest, ruff, mypy.

---

## File Structure

- Modify `src/ai_presenter/runtime/adaptive_demo.py`: add localized active-meeting invite narration and reuse it in both adaptive branches.
- Modify `tests/unit/test_adaptive_demo.py`: add localized stale-text regression tests.
- Create `docs/agent-handoffs/cycle-024-implementation.md`: implementation handoff with verification evidence.

## Task 1: Add Failing Localized Adaptive Tests

**Files:**

- Modify: `tests/unit/test_adaptive_demo.py`

- [ ] **Step 1: Import voice rendering helpers**

Add imports:

```python
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_narration_text
```

- [ ] **Step 2: Extend the test helper to accept localized text**

Update `make_step()`:

```python
def make_step(
    step_id: str,
    entrypoint_id: str,
    text: str = "Original narration.",
    localized_text: dict[str, str] | None = None,
) -> DemoStep:
    return DemoStep(
        id=step_id,
        title="Step",
        action=DemoStepAction(entrypointId=entrypoint_id, operation="open"),
        narration=DemoStepNarration(
            text=text,
            localizedText=localized_text or {},
            placement="during",
            actionOffsetMs=350,
        ),
    )
```

- [ ] **Step 3: Add Add coworkers stale-localized-text regression**

Add this test after the existing Add coworkers rewrite test:

```python
def test_rewrites_add_coworkers_localized_narration_for_active_meeting() -> None:
    stale_chinese = "空会议里的 Add coworkers 是最快的拉人入口。"
    step = make_step(
        "control-map-add-coworkers",
        "ringcentral.video.main.add-coworkers",
        "Add coworkers opens the invite dialog from the empty room.",
        localized_text={"zh": stale_chinese},
    )

    adjusted = adjust_ringcentral_demo_step(step, MeetingState(participant_count=2))

    assert adjusted is not None
    assert adjusted.action.entrypoint_id == "ringcentral.video.toolbar.invite"
    zh_text = adjusted.narration.localized_text["zh"]
    assert zh_text != stale_chinese
    assert "Invite" in zh_text
    assert "已经有人在会议中" in zh_text
    assert adjusted.narration.placement == "during"
    assert adjusted.narration.action_offset_ms == 350

    rendered = render_narration_text(
        adjusted.narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )
    assert rendered == zh_text
    assert stale_chinese not in rendered
```

- [ ] **Step 4: Add toolbar Invite stale-localized-text regression**

Add this test after the toolbar Invite rewrite test:

```python
def test_rewrites_toolbar_invite_localized_narration_for_active_meeting() -> None:
    stale_chinese = "Invite 会打开空会议邀请流程。"
    step = make_step(
        "explain-invite",
        "ringcentral.video.toolbar.invite",
        "The Invite button brings someone into the empty meeting.",
        localized_text={"zh": stale_chinese},
    )

    adjusted = adjust_ringcentral_demo_step(step, MeetingState(participant_count=3))

    assert adjusted is not None
    zh_text = adjusted.narration.localized_text["zh"]
    assert zh_text != stale_chinese
    assert "Invite" in zh_text
    assert "已经有人在会议中" in zh_text
    assert adjusted.narration.placement == "during"
    assert adjusted.narration.action_offset_ms == 350

    rendered = render_narration_text(
        adjusted.narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )
    assert rendered == zh_text
    assert stale_chinese not in rendered
```

- [ ] **Step 5: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_adaptive_demo.py::test_rewrites_add_coworkers_localized_narration_for_active_meeting tests\unit\test_adaptive_demo.py::test_rewrites_toolbar_invite_localized_narration_for_active_meeting
```

Expected: fail because adjusted narration still preserves stale `localized_text["zh"]`.

## Task 2: Implement Localized Adaptive Narration

**Files:**

- Modify: `src/ai_presenter/runtime/adaptive_demo.py`

- [ ] **Step 1: Add localized narration constant**

Add below `_ACTIVE_MEETING_INVITE_NARRATION`:

```python
_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION = {
    "zh": "因为已经有人在会议中，Invite 用来继续添加参会人，或复制会议详情，而不会改变当前对话。"
}
```

- [ ] **Step 2: Add a helper for adaptive narration copies**

Add:

```python
def _active_meeting_invite_narration(narration: DemoStepNarration) -> DemoStepNarration:
    return narration.model_copy(
        update={
            "text": _ACTIVE_MEETING_INVITE_NARRATION,
            "localized_text": dict(_ACTIVE_MEETING_INVITE_LOCALIZED_NARRATION),
        }
    )
```

Also import `DemoStepNarration` from `ai_presenter.packages.models`.

- [ ] **Step 3: Use the helper in both adaptive branches**

Replace each inline `step.narration.model_copy(update={"text": _ACTIVE_MEETING_INVITE_NARRATION})` with:

```python
"narration": _active_meeting_invite_narration(step.narration)
```

- [ ] **Step 4: Run targeted tests and verify GREEN**

Run the same targeted command from Task 1 Step 5.

Expected: both tests pass.

## Task 3: Focused Verification And Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-024-implementation.md`

- [ ] **Step 1: Run adaptive, voice, and runtime factory tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_adaptive_demo.py tests\unit\test_voice.py tests\unit\test_runtime_factory.py
```

Expected: pass.

- [ ] **Step 2: Run ruff on touched code/tests**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache src\ai_presenter\runtime\adaptive_demo.py tests\unit\test_adaptive_demo.py
```

Expected: `All checks passed!`

- [ ] **Step 3: Run diff check**

Run:

```powershell
git diff --check -- src\ai_presenter\runtime\adaptive_demo.py tests\unit\test_adaptive_demo.py docs\agent-handoffs\cycle-024-implementation.md
```

Expected: exit 0. LF-to-CRLF warnings are acceptable if no whitespace errors are reported.

- [ ] **Step 4: Write implementation handoff**

Create `docs/agent-handoffs/cycle-024-implementation.md` with:

```markdown
# Cycle 024 Implementation Handoff

Date: 2026-05-16
Role: implementation subagent
Scope: adaptive invite localized narration fix.

## Summary

- Added Chinese active-meeting Invite narration for adaptive demo rewrites.
- Updated both Add coworkers-to-Invite and toolbar Invite adaptive branches to replace stale localized text.
- Added tests proving Chinese render output no longer uses stale empty-room text.

## Verification

- RED: [exact failing command and output]
- GREEN: [exact passing command and output]
- Focused tests: [exact output]
- Ruff: [exact output]
- Diff check: [exact output]

## Notes

- No package YAML, schema, controller, CLI, route, provider, or live RingCentralVideo behavior was changed.
```

- [ ] **Step 5: Do not commit**

This long-running workspace is accumulating multiple cycles. Do not stage or commit unless the main session explicitly asks.
