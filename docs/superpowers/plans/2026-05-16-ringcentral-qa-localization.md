# RingCentral Q&A Localization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand RingCentralVideo Chinese Q&A and package-owned aliases using existing package schema, without changing runtime logic or route safety.

**Architecture:** Keep all behavior in package-authored content. Use `localizedQuestions.zh`, `localizedAnswers.zh`, and `questionAliases.zh`; verify through package-loading and question-answer tests.

**Tech Stack:** YAML package content, Pydantic package loader, pytest, ruff.

---

## File Structure

- Modify `packages/ringcentral-video.yaml`: add localized Q&A and selected Chinese aliases.
- Modify `tests/unit/test_material_packages.py`: add package-content coverage.
- Modify `tests/unit/test_questions.py`: add localized answer and package-owned alias behavior coverage.
- Create `docs/agent-handoffs/cycle-022-implementation.md`: implementation handoff.

## Task 1: Add Failing Content Tests

**Files:**

- Modify: `tests/unit/test_material_packages.py`
- Modify: `tests/unit/test_questions.py`

- [ ] **Step 1: Add package-content tests**

Add to `tests/unit/test_material_packages.py`:

```python
def test_ringcentral_all_qa_items_have_chinese_localized_questions_and_answers() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    entrypoint_ids = {entrypoint.id for entrypoint in package.operation_entrypoints}

    for item in package.qa:
        assert item.localized_questions.get("zh"), item.question
        assert item.localized_answers.get("zh", "").strip(), item.question
        assert set(item.related_entrypoint_ids) <= entrypoint_ids
```

```python
def test_ringcentral_package_owns_chinese_aliases_for_question_routes() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    aliases_by_entrypoint: dict[str, set[str]] = {}
    for alias in package.entrypoint_question_aliases:
        if alias.language != "zh":
            continue
        aliases_by_entrypoint.setdefault(alias.entrypoint_id, set()).add(alias.alias)

    expected_aliases = {
        "ringcentral.video.main.add-coworkers": {"加同事", "邀请同事", "拉人入会"},
        "ringcentral.video.toolbar.participants": {"参会者", "参会人列表", "谁在会议里"},
        "ringcentral.video.toolbar.audio": {"麦克风", "静音", "声音"},
        "ringcentral.video.toolbar.audio-menu": {"音频设置", "换麦克风", "换扬声器"},
        "ringcentral.video.toolbar.video": {"摄像头", "开视频", "关视频"},
        "ringcentral.video.toolbar.video-menu": {"视频设置", "换摄像头", "摄像头菜单"},
        "ringcentral.video.top.network-quality": {"网络质量", "连接质量", "卡顿"},
        "ringcentral.video.top.meeting-info": {"会议信息", "会议号", "会议链接"},
        "ringcentral.video.more.notes": {"笔记", "转录", "会议笔记"},
        "ringcentral.video.more.recording": {"录制", "录像", "记录会议"},
    }

    for entrypoint_id, aliases in expected_aliases.items():
        assert aliases <= aliases_by_entrypoint.get(entrypoint_id, set())
```

- [ ] **Step 2: Add question behavior tests**

Add to `tests/unit/test_questions.py`:

```python
def test_ringcentral_localized_shared_screen_qa_returns_chinese_answer() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="你能说明共享屏幕内容吗",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.share"
    assert response.can_operate is False
    assert "共享内容" in response.answer_text
    assert "approved observation" not in response.answer_text
```

```python
def test_ringcentral_localized_invite_qa_returns_chinese_answer_and_stays_non_operable() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="我是第一个人怎么邀请同事入会",
        voice=PresenterVoiceSettings(language="zh", tone="friendly"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.invite"
    assert response.can_operate is False
    assert "Add coworkers" in response.answer_text
    assert "不要朗读" in response.answer_text
```

```python
def test_ringcentral_localized_audio_video_readiness_qa_returns_chinese_answer() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="开会前怎么确认声音视频",
        voice=PresenterVoiceSettings(language="zh", tone="coach"),
    )

    assert response.entrypoint_id == "ringcentral.video.toolbar.audio"
    assert response.can_operate is False
    assert "麦克风" in response.answer_text
    assert "摄像头" in response.answer_text
```

```python
def test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    monkeypatch.setattr(questions_module, "_ENTRYPOINT_ALIASES", {})

    expected = {
        "谁在会议里": "ringcentral.video.toolbar.participants",
        "换麦克风": "ringcentral.video.toolbar.audio-menu",
        "换摄像头": "ringcentral.video.toolbar.video-menu",
        "网络质量": "ringcentral.video.top.network-quality",
        "会议号在哪里": "ringcentral.video.top.meeting-info",
        "会议笔记在哪里": "ringcentral.video.more.notes",
        "怎么录制会议": "ringcentral.video.more.recording",
        "邀请同事": "ringcentral.video.main.add-coworkers",
    }

    for question, entrypoint_id in expected.items():
        response = answer_question(
            package=package,
            question=question,
            voice=PresenterVoiceSettings(language="zh"),
        )
        assert response.entrypoint_id == entrypoint_id
```

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Expected: new tests fail because Q&A localization and package-owned aliases are missing.

## Task 2: Update RingCentral Package Content

**Files:**

- Modify: `packages/ringcentral-video.yaml`

- [ ] **Step 1: Add missing Chinese aliases**

For the target entrypoints listed in the design, add or extend `questionAliases.zh` with the expected aliases from tests. Preserve existing English fields, route ids, titles, purposes, and `openSteps`.

- [ ] **Step 2: Localize existing Q&A**

For `Can the presenter describe shared-screen content?`, add:

```yaml
  localizedQuestions:
    zh:
    - 你能说明共享屏幕内容吗
    - 能读共享的文档吗
    - 共享屏幕内容可以讲吗
  localizedAnswers:
    zh: 只有在共享内容来自已批准的观察来源，并且用户明确允许时，Presenter 才会说明它。默认策略是避免推断或朗读私人共享内容；可以安全解释 Share 入口本身。
```

For `How can I bring people into the meeting?`, add:

```yaml
  localizedQuestions:
    zh:
    - 怎么邀请同事入会
    - 我是第一个人怎么邀请同事入会
    - 怎么复制会议邀请
  localizedAnswers:
    zh: 如果会议里只有你，可以用 Add coworkers；在工具栏里也可以用 Invite 添加同事或复制会议邀请。Presenter 不要朗读私人邀请链接、邮箱、姓名或建议列表，除非用户明确要求并且内容已验证。
```

- [ ] **Step 3: Add four new Q&A entries**

Add the following Q&A entries under `qa:`:

```yaml
- question: Can the presenter read chat or participant names?
  localizedQuestions:
    zh:
    - 你能读聊天内容吗
    - 能说出参会人名字吗
    - 参会者和聊天内容能讲吗
  answer: The presenter can explain where Chat and Participants are and summarize visible counts when verified. It should not read chat messages, participant names, roles, or private tabs unless the user explicitly asks and the content is verified.
  localizedAnswers:
    zh: Presenter 可以说明 Chat 和 Participants 在哪里，也可以在已验证时概括可见人数。默认不要朗读聊天消息、参会人姓名、角色或私人标签页，除非用户明确要求并且内容已经验证。
  relatedEntrypointIds:
  - ringcentral.video.toolbar.chat
  - ringcentral.video.toolbar.participants
- question: How do I make sure my audio and camera are ready?
  localizedQuestions:
    zh:
    - 怎么检查麦克风和摄像头
    - 开会前怎么确认声音视频
    - 声音和视频怎么准备
  answer: Check the microphone and camera state first, then use the audio or video menu for device recovery. Do not toggle real meeting media unless the user intends to change the state.
  localizedAnswers:
    zh: 先确认麦克风和摄像头当前状态，再用音频或视频菜单处理设备选择和恢复。不要在真实会议里随意切换麦克风或摄像头，除非用户明确要改变状态。
  relatedEntrypointIds:
  - ringcentral.video.toolbar.audio
  - ringcentral.video.toolbar.audio-menu
  - ringcentral.video.toolbar.video
  - ringcentral.video.toolbar.video-menu
- question: How do I troubleshoot choppy audio or video?
  localizedQuestions:
    zh:
    - 声音或视频卡顿怎么办
    - 怎么看网络质量
    - 连接质量在哪里看
  answer: Open Network quality to inspect packet loss, jitter, latency, or related meeting diagnostics. Use Report issue only as an escalation path, and avoid guessing exact causes without observed values.
  localizedAnswers:
    zh: 打开 Network quality 查看丢包、抖动、延迟或相关会议诊断。Report issue 适合升级反馈；在没有观察到具体数值前，不要猜测准确原因。
  relatedEntrypointIds:
  - ringcentral.video.top.network-quality
  - ringcentral.video.top.report-issue
- question: Where are notes, transcripts, and recording controls?
  localizedQuestions:
    zh:
    - 笔记和转录在哪里
    - 怎么录制会议
    - 会议笔记和录制在哪里
  answer: Notes opens the notes and transcript panel. Recording is a meeting-state change from More, so it requires explicit confirmation, role awareness, and participant consent before use.
  localizedAnswers:
    zh: Notes 会打开笔记和转录面板。Recording 是 More 里的会议状态变更操作，使用前需要明确确认、了解角色权限，并考虑参会者同意。
  relatedEntrypointIds:
  - ringcentral.video.more.notes
  - ringcentral.video.more.recording
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Expected: focused material package and question tests pass.

## Task 3: Verify And Record Handoff

**Files:**

- Create: `docs/agent-handoffs/cycle-022-implementation.md`

- [ ] **Step 1: Run verification commands**

Run:

```powershell
.\.venv\Scripts\python -m ruff check --no-cache tests\unit\test_material_packages.py tests\unit\test_questions.py
.\.venv\Scripts\python -m mypy --no-incremental src tests
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_material_packages.py tests\unit\test_questions.py docs\agent-handoffs\cycle-022-implementation.md
```

Expected:

- Ruff passes.
- Mypy passes.
- Full pytest passes.
- Diff check is clean except possible existing CRLF warnings.

- [ ] **Step 2: Write implementation handoff**

Create `docs/agent-handoffs/cycle-022-implementation.md` with:

```markdown
# Cycle 022 Implementation Handoff

## Summary

- Expanded RingCentralVideo package Q&A localization.
- Added package-owned Chinese aliases for selected P0/P1 routes.
- Preserved runtime matching, schema, route safety, and operability behavior.

## Changed Paths

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`

## TDD Evidence

- RED:
- GREEN:

## Verification

- Ruff:
- Mypy:
- Full pytest:
- Diff check:

## Notes

- No live RingCentralVideo interaction was performed.
- No runtime logic or package schema changed.
- Invite, Share, Recording, and Leave remain non-operable.
```

- [ ] **Step 3: Return worker status**

Return `DONE` with changed paths, exact test summaries, and any concerns.
