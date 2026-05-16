# RingCentral Demo Localization Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Localize `meeting-controls-tour` in Chinese and guard all RingCentral demo flows against missing Chinese narration.

**Architecture:** Use existing package `narration.localizedText.zh` content and existing `render_narration_text()` selection. Add an all-flow test in the package test module. No runtime, schema, route, CLI, or controller changes.

**Tech Stack:** YAML material package, Pydantic loader, presenter voice renderer, pytest, ruff.

---

## File Structure

- Modify `packages/ringcentral-video.yaml`: add `localizedText.zh` to 22 `meeting-controls-tour` steps.
- Modify `tests/unit/test_material_packages.py`: add all-flow Chinese narration coverage and a render assertion for a long-tour step.
- Create `docs/agent-handoffs/cycle-025-implementation.md`: implementation handoff.

## Task 1: Add Failing All-Flow Localization Tests

**Files:**

- Modify: `tests/unit/test_material_packages.py`

- [ ] **Step 1: Add an all-flow coverage test**

Add this test near the existing demo-flow localization tests:

```python
def test_all_ringcentral_demo_flow_steps_have_chinese_localized_narration() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    for flow in package.demo_flows:
        for step in flow.steps:
            step.narration.text.encode("ascii")
            zh_text = step.narration.localized_text["zh"]
            assert zh_text.strip(), f"{flow.id}:{step.id}"
            assert has_cjk(zh_text), f"{flow.id}:{step.id}"
```

- [ ] **Step 2: Add a long-tour render assertion**

Add this test after the all-flow coverage test:

```python
def test_meeting_controls_tour_renders_chinese_narration_text() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    flow = package.demo_flow_by_id("meeting-controls-tour")
    step = next(step for step in flow.steps if step.id == "explain-share")

    rendered = render_narration_text(
        step.narration,
        PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert rendered == step.narration.localized_text["zh"].strip()
    assert "Share" in rendered
    assert has_cjk(rendered)
```

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_all_ringcentral_demo_flow_steps_have_chinese_localized_narration tests\unit\test_material_packages.py::test_meeting_controls_tour_renders_chinese_narration_text
```

Expected: fail because `meeting-controls-tour` has no `localizedText.zh`.

## Task 2: Add `meeting-controls-tour` Chinese Narration

**Files:**

- Modify: `packages/ringcentral-video.yaml`

- [ ] **Step 1: Add localized text to overview and top-bar steps**

Add `localizedText.zh` under each step's `narration.text`:

- `meeting-overview`:

```yaml
      localizedText:
        zh: RingCentral Video 的会议窗口可以分成三块：上方看会议身份、连接状态、视图和问题反馈；下方管理音频、视频、共享、成员、聊天、互动和安全操作；中间是实时会议画面。
```

- `explain-meeting-info`:

```yaml
      localizedText:
        zh: 先看 info 按钮。它会打开主持人、会议 ID、复制链接、拨入信息和加密状态；这些值默认属于敏感信息，我只说明位置，不主动朗读。
```

- `explain-network-quality`:

```yaml
      localizedText:
        zh: 接着是 Network quality。会议不稳定时，可以从这里查看共享、视频和音频的丢包、抖动和延迟。
```

- `explain-view-layout`:

```yaml
      localizedText:
        zh: Views 用来调整你看到会议的布局，比如 Gallery view 或 Full screen；它只改变本地显示，不会影响通话里的其他人。
```

- `explain-report-issue`:

```yaml
      localizedText:
        zh: Report 会打开故障反馈窗口，适合处理音频、视频、屏幕共享、入会、笔记、转录或其他问题。它会挡住会议控制区，所以讲完后需要关闭。
```

- [ ] **Step 2: Add localized text to people and communication steps**

- `explain-add-coworkers`:

```yaml
      localizedText:
        zh: 进入成员相关控制。空会议里的 Add coworkers 会打开邀请窗口，可以搜索同事、复制会议链接或发送邀请。
```

- `explain-invite`:

```yaml
      localizedText:
        zh: 工具栏里的 Invite 是活跃会议中邀请他人的常规入口，可以继续添加同事或复制会议详情。
```

- `explain-participants`:

```yaml
      localizedText:
        zh: Participants 会打开参会人列表。这里可以确认谁在会议里，也能进入邀请、锁定会议、静音和更多成员操作。
```

- `explain-chat`:

```yaml
      localizedText:
        zh: Chat 会打开消息面板，支持发给所有人的消息和私聊。聊天内容默认保持隐私，除非用户明确要求读取。
```

- [ ] **Step 3: Add localized text to media and sharing steps**

- `explain-microphone`:

```yaml
      localizedText:
        zh: 现在看媒体控制。Mute 是麦克风的主要隐私开关；发言前，最先应该确认这里的状态。
```

- `explain-audio-menu`:

```yaml
      localizedText:
        zh: 麦克风箭头会打开音频设备菜单，可以切换麦克风和扬声器、离开电脑音频、使用电话音频，或进入更多音频设置。
```

- `explain-camera`:

```yaml
      localizedText:
        zh: Start video 会打开本地摄像头；开启后，同一个按钮会变成 Stop video，用来关闭视频。
```

- `explain-camera-menu`:

```yaml
      localizedText:
        zh: 摄像头箭头会打开摄像头选择，并提供进入更多视频设置的入口，包括背景配置。
```

- `explain-share`:

```yaml
      localizedText:
        zh: Share 会打开屏幕或应用窗口选择器，也可以共享系统音频。但在你确认要展示哪个内容前，我不会点击最终的 Share 按钮。
```

- [ ] **Step 4: Add localized text to interaction, advanced, and closeout steps**

- `explain-reactions`:

```yaml
      localizedText:
        zh: React 适合轻量反馈，比如爱心、点赞、庆祝、鼓掌、微笑和 Be right back，不需要打断正在说话的人。
```

- `explain-raise-hand`:

```yaml
      localizedText:
        zh: Raise hand 表示你想获得发言机会，而不用打断别人。它是开关，所以展示后会再把手放下。
```

- `explain-more`:

```yaml
      localizedText:
        zh: 最后是 More，它是更深层会议工具的扩展菜单。当前版本里 Notes 已在工具栏上，More 主要保留 Start recording、Background 和 Settings。
```

- `explain-recording`:

```yaml
      localizedText:
        zh: Start recording 会改变会议状态，所以在导览里只解释入口；开始或停止录制前都需要先询问并确认。
```

- `explain-notes`:

```yaml
      localizedText:
        zh: Notes 会打开 Notes and Transcript 面板。这里可以启动会议笔记，也可能涉及录制相关操作，所以这些动作继续由用户控制。
```

- `explain-background-settings`:

```yaml
      localizedText:
        zh: Background 会打开视觉呈现设置，可以关闭效果、模糊房间、选择内置背景、使用视频背景或上传自己的背景。
```

- `explain-settings`:

```yaml
      localizedText:
        zh: Settings 是完整配置区域，包含音频、视频、背景、翻译、入会偏好和通用会议偏好。
```

- `explain-leave`:

```yaml
      localizedText:
        zh: Leave 会离开会议，是破坏性控制；Presenter 只说明它的作用，不会在没有明确确认时点击。
```

- [ ] **Step 5: Run targeted tests and verify GREEN**

Run the same targeted command from Task 1 Step 3.

Expected: both tests pass.

## Task 3: Focused Verification And Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-025-implementation.md`

- [ ] **Step 1: Run package-focused tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_voice.py tests\unit\test_questions.py
```

Expected: pass.

- [ ] **Step 2: Run ruff on touched tests**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache tests\unit\test_material_packages.py tests\unit\test_voice.py tests\unit\test_questions.py
```

Expected: `All checks passed!`

- [ ] **Step 3: Run diff check**

Run:

```powershell
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py docs\agent-handoffs\cycle-025-implementation.md docs\superpowers\specs\2026-05-16-ringcentral-demo-localization-coverage-design.md docs\superpowers\plans\2026-05-16-ringcentral-demo-localization-coverage.md
```

Expected: exit 0. LF-to-CRLF warnings are acceptable if no whitespace errors are reported.

- [ ] **Step 4: Write implementation handoff**

Create `docs/agent-handoffs/cycle-025-implementation.md` with:

```markdown
# Cycle 025 Implementation Handoff

Date: 2026-05-16
Role: implementation subagent
Scope: RingCentral demo-flow Chinese localization closure.

## Summary

- Added `localizedText.zh` to all 22 `meeting-controls-tour` steps.
- Added an all-flow Chinese narration coverage guard.
- Added a render assertion for a newly localized long-tour step.
- Left runtime, schema, CLI, controller, routes, providers, and open steps unchanged.

## Verification

- RED: [exact failing command and output]
- GREEN: [exact passing command and output]
- Focused tests: [exact output]
- Ruff: [exact output]
- Diff check: [exact output]

## Notes

- No live RingCentralVideo interaction was performed.
- This cycle makes every current RingCentral demo flow Chinese-narration complete.
```

- [ ] **Step 5: Do not commit**

This workspace is accumulating many optimization cycles. Do not stage or commit unless the main session explicitly asks.
