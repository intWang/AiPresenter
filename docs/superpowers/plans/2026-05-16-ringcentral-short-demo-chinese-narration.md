# RingCentral Short Demo Chinese Narration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add native Chinese narration to RingCentralVideo's short blur and meeting-basics demo flows.

**Architecture:** Use existing package `narration.localizedText.zh` content and existing `render_narration_text()` runtime selection. Keep this cycle package-content-only apart from tests and handoff docs.

**Tech Stack:** YAML material packages, Pydantic package loader, presenter voice renderer, pytest, ruff.

---

## File Structure

- Modify `packages/ringcentral-video.yaml`: add `localizedText.zh` to seven existing demo steps.
- Modify `tests/unit/test_material_packages.py`: add focused coverage for short-flow Chinese localization and rendering.
- Create `docs/agent-handoffs/cycle-023-implementation.md`: implementation handoff with RED/GREEN evidence.

## Task 1: Add Failing Short-Flow Localization Tests

**Files:**

- Modify: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Add imports for narration rendering**

Add these imports near the existing package loader import:

```python
from ai_presenter.runtime.voice import PresenterVoiceSettings
from ai_presenter.runtime.voice import render_narration_text
```

- [ ] **Step 2: Add a small CJK helper**

Add this helper near `EXECUTABLE_DEMO_STEP_OPERATIONS`:

```python
def has_cjk(text: str) -> bool:
    return any("\u4e00" <= character <= "\u9fff" for character in text)
```

- [ ] **Step 3: Add target-flow localized content coverage**

Add this test after `test_meeting_control_map_demo_is_directed_and_complete()`:

```python
def test_short_ringcentral_demo_flows_have_chinese_localized_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    expected_step_ids = {
        "vbg-blur-demo": [
            "open-video-settings",
            "open-background-panel",
            "select-blur",
            "verify-meeting-video",
        ],
        "meeting-basics-demo": [
            "show-mic",
            "show-participants",
            "show-chat",
        ],
    }

    for flow_id, step_ids in expected_step_ids.items():
        flow = package.demo_flow_by_id(flow_id)
        assert [step.id for step in flow.steps] == step_ids
        for step in flow.steps:
            step.narration.text.encode("ascii")
            zh_text = step.narration.localized_text["zh"]
            assert zh_text.strip()
            assert has_cjk(zh_text)
```

- [ ] **Step 4: Add a render-path assertion**

Add this test immediately after the target-flow coverage:

```python
def test_short_ringcentral_demo_flow_renders_chinese_narration_text() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("vbg-blur-demo")
    step = next(step for step in flow.steps if step.id == "select-blur")

    rendered = render_narration_text(
        step.narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert rendered == step.narration.localized_text["zh"].strip()
    assert "Blur" in rendered
    assert has_cjk(rendered)
```

- [ ] **Step 5: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_short_ringcentral_demo_flows_have_chinese_localized_narration tests\unit\test_material_packages.py::test_short_ringcentral_demo_flow_renders_chinese_narration_text
```

Expected: fail because the seven target steps do not yet have `localizedText.zh`.

## Task 2: Add Short-Flow Chinese Narration Content

**Files:**

- Modify: `packages/ringcentral-video.yaml`

- [ ] **Step 1: Add `localizedText.zh` to `vbg-blur-demo`**

Add the following localized text under each target step's existing `narration.text`:

```yaml
      localizedText:
        zh: 我先从摄像头控制进入 Settings，这样可以调整视频呈现方式，而不需要改变会议里其他人的状态。
```

For `open-background-panel`:

```yaml
      localizedText:
        zh: Background 面板集中管理模糊、内置虚拟背景和自定义背景上传，是保护真实环境和提升展示效果的入口。
```

For `select-blur`:

```yaml
      localizedText:
        zh: 选择 Blur 会保留演示者本人，同时弱化真实房间细节，适合在不暴露环境的情况下继续开会。
```

For `verify-meeting-video`:

```yaml
      localizedText:
        zh: 回到会议画面后，确认本地视频仍然开启，并且背景已经被模糊处理。
```

- [ ] **Step 2: Add `localizedText.zh` to `meeting-basics-demo`**

For `show-mic`:

```yaml
      localizedText:
        zh: 麦克风按钮显示当前是否静音。发言前先看这里，可以快速确认自己是否会被听到。
```

For `show-participants`:

```yaml
      localizedText:
        zh: Participants 面板用来确认谁在会议里，也能判断会议是否还处于空房间状态。
```

For `show-chat`:

```yaml
      localizedText:
        zh: Chat 是文字协作通道，适合发送链接和补充信息；聊天内容默认保持隐私，除非用户明确要求读取。
```

- [ ] **Step 3: Run focused tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_short_ringcentral_demo_flows_have_chinese_localized_narration tests\unit\test_material_packages.py::test_short_ringcentral_demo_flow_renders_chinese_narration_text
```

Expected: both tests pass.

## Task 3: Focused Verification And Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-023-implementation.md`

- [ ] **Step 1: Run focused package tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py
```

Expected: pass.

- [ ] **Step 2: Run ruff on touched test file**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache tests\unit\test_material_packages.py
```

Expected: `All checks passed!`

- [ ] **Step 3: Run diff check for touched files**

Run:

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py docs\agent-handoffs\cycle-023-implementation.md
```

Expected: exit 0. Existing LF-to-CRLF working-copy warnings are acceptable if there are no whitespace errors.

- [ ] **Step 4: Write implementation handoff**

Create `docs/agent-handoffs/cycle-023-implementation.md` with:

```markdown
# Cycle 023 Implementation Handoff

Date: 2026-05-16
Role: implementation subagent
Scope: package-content-only RingCentral short demo Chinese narration.

## Summary

- Added `localizedText.zh` to all `vbg-blur-demo` and `meeting-basics-demo` steps.
- Added tests proving target-flow Chinese coverage and Chinese render-path behavior.
- Left runtime, schema, CLI, controller, routes, and open steps unchanged.

## Verification

- RED: [exact failing command and output]
- GREEN: [exact passing command and output]
- Focused package tests: [exact output]
- Ruff: [exact output]
- Diff check: [exact output]

## Notes

- No live RingCentralVideo interaction was performed.
- `meeting-control-map-demo` was already localized; `meeting-controls-tour` remains a later-cycle candidate.
```

- [ ] **Step 5: Do not commit**

This long-running workspace is accumulating multiple uncommitted cycles. Do not stage or commit unless the main session explicitly asks.
