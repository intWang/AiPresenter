# Cycle 174 技术扫描：Presenter 元请求防误路由

日期：2026-05-17

## 扫描范围

- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/runtime/controller.py`
- `src/ai_presenter/runtime/session.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_session.py`
- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`

Cycle 173 已提交 `2f49dec`。本次只读扫描代码/文档，只写本 handoff；没有修改源码、测试、YAML、`.coverage`，也没有 stage/commit。工作树已有 `.coverage` 修改，应继续视为他人或既有改动。

## 当前行为锚点

`src/ai_presenter/runtime/questions.py` 的 `_answer_question(...)` 当前顺序是：

1. `normalize_question_prompt(question)`
2. `_match_qa(package, normalized)`
3. `_match_entrypoint(package, normalized)`
4. 根据 `_can_operate(...)` 决定 `QuestionResponse.can_operate`

`src/ai_presenter/runtime/session.py` 的 `create_question_interrupt_step(...)` 只在 `entrypoint_id is not None` 且 `can_operate=True` 时创建 demo interrupt。

`src/ai_presenter/runtime/controller.py` 的 `PresenterController.submit_question(...)` 会把 `answer_question(...)` 的结果交给 `create_question_interrupt_step(...)`。如果返回 step，运行中会 `enqueue_interrupt(...)`，空闲时会启动 `question-answer-demo`。

`src/ai_presenter/runtime/voice.py` 已把 language/tone 定义为 presenter voice 设置：`en/zh/ja/es` 和 `professional/conversational/concise/friendly/coach/formal/support/careful`。`runtime-safety-routing.md` 已明确 tone/language 只能影响 phrasing，不应改变 route、`can_operate` 或 interrupt。

## 问题形态

需要防住的不是 RingCentralVideo 控件请求，而是对 Presenter 本身的表达方式请求：

- 语言：`answer in Chinese`、`use English`、`请用中文回答`
- 语气：`use a friendly tone`、`be more formal`、`语气温和一点`
- 详略：`be concise`、`give more detail`、`简单说`、`详细一点`
- 熟悉度：`explain like I'm new`、`assume I know RingCentral`、`面向新手讲`

风险点在于这些请求常会同时包含控件词，例如 `answer chat more concisely`、`用中文解释 participants`、`be friendly when explaining meeting information`。按当前 `questions.py` 的 alias-first entrypoint 路径，这类输入可能命中 `chat`、`participants`、`meeting information` 等 RingCentralVideo 控件，再由 `can_operate=True` 的控件生成 interrupt。目标要求它们必须 answer-only、non-operable、无 interrupt，且不要进入 RingCentralVideo 控件匹配。

## 首选方案

首选在 `src/ai_presenter/runtime/questions.py` 内新增一个早期短路：

- 新增 helper：`_match_presenter_meta_request(normalized_question: str) -> bool`
- 新增 answer renderer：`_presenter_meta_answer(voice: PresenterVoiceSettings) -> QuestionResponse`
- 在 `_answer_question(...)` 里，紧跟 `normalized = normalize_question_prompt(question)` 之后、`_match_qa(...)` 之前调用。

建议伪代码：

```python
normalized = normalize_question_prompt(question)
if _match_presenter_meta_request(normalized):
    return QuestionResponse(
        answer_text=_render_text(_PRESENTER_META_ANSWERS[voice.language], voice),
        entrypoint_id=None,
        can_operate=False,
    )
```

这样可以保证元请求不会进入 `_match_qa(...)`、`_match_entrypoint(...)`、package-owned aliases、legacy aliases 或 token fallback。`entrypoint_id=None` 也会让 `create_question_interrupt_step(...)` 自然返回 `None`。

## 匹配策略

推荐保守启发式，不引入 NLP 或 YAML schema：

- 必须命中“Presenter 表达意图”动词/结构之一：`answer/respond/say/speak/explain/tell/use/be/make/keep`，以及中文 `回答/说/讲/解释/用/语气/口吻/风格`。
- 同时命中至少一个元请求维度：
  - language：复用或镜像 `voice.py` 的 language aliases，如 `english/chinese/japanese/spanish/espanol/español/中文/日本語`
  - tone：复用或镜像 `voice.py` 的 tone aliases，如 `professional/conversational/concise/friendly/coach/formal/support/careful/warm/brief/privacy`
  - detail/familiarity：`concise/brief/short/detail/detailed/simple/simpler/beginner/new/expert/familiar`，中文 `简洁/简短/详细/简单/新手/熟悉/专业`
- 对纯控件位置请求保持不匹配：`where is chat`、`participants`、`network quality` 不应因为普通词被误识别为元请求。

首轮不建议把 `language`、`tone` 的别名表从 `voice.py` 移出来做公共常量；那会扩大 API 面。可以先在 `questions.py` 放小型元请求词表，测试锁定行为。如果后续多个模块需要复用，再抽到 `voice.py` 或新模块。

## 候选实现文件与位置

首选：

- `src/ai_presenter/runtime/questions.py`
  - `_answer_question(...)`：在 Q&A 和 entrypoint 匹配前短路。
  - 常量区：新增 `_PRESENTER_META_*` 词表和 `_PRESENTER_META_ANSWERS`。
  - helper 区：放在 `_match_qa(...)` 前或 `_meaningful_tokens(...)` 附近，保持 routing helper 集中。

备选但不推荐：

- `src/ai_presenter/runtime/session.py`
  - 可以在 `ControllerSession.answer_question(...)` 前拦截，但 `PresenterController.submit_question(...)` 直接调用 `answer_question(...)`，会漏掉 controller 路径。
- `src/ai_presenter/runtime/controller.py`
  - 可以在 `submit_question(...)` 拦截，但 CLI/会话层直接问答不会受保护，且问题本质属于 routing。
- `src/ai_presenter/runtime/voice.py`
  - 适合保存 voice settings 和 rendering，不适合决定用户问题是否应进入 app 控件匹配。
- `packages/ringcentral-video.yaml`
  - 不推荐。元请求是 Presenter 级别，不属于 RingCentralVideo package；用 YAML Q&A 会改变 counts 和 localization 诊断，也不能保护临时 running-app package。

## 测试建议

主测试放在 `tests/unit/test_questions.py`，因为目标是 routing 和 interrupt 边界。

建议新增测试名：

- `test_presenter_meta_language_request_stays_answer_only_without_entrypoint`
  - 输入：`answer in Chinese`
  - 断言：`entrypoint_id is None`、`can_operate is False`、`create_question_interrupt_step(package, response) is None`
- `test_presenter_meta_tone_request_with_control_word_does_not_route_to_control`
  - 输入：`answer chat more concisely`
  - 断言：不等于 `ringcentral.video.toolbar.chat`，`entrypoint_id is None`，无 interrupt
- `test_presenter_meta_detail_request_with_participants_word_does_not_interrupt`
  - 输入：`be more detailed when explaining participants`
  - 断言：不进入 `ringcentral.video.toolbar.participants`，无 interrupt
- `test_presenter_meta_chinese_style_request_with_control_word_stays_answer_only`
  - 输入：`请用更简洁的语气回答聊天`
  - 断言：`entrypoint_id is None`、`can_operate is False`、无 interrupt
- `test_presenter_meta_guard_does_not_block_plain_control_lookup`
  - 输入：`chat` 或 `where is chat`
  - 断言：仍命中 `ringcentral.video.toolbar.chat`，保持现有 `can_operate=True`

可选补充：

- `tests/unit/test_controller.py`
  - 新增 `test_presenter_controller_answers_presenter_meta_request_without_demo`
  - monkeypatch runner 记录 calls，输入 `answer chat more concisely`，断言 `demonstration_status == "text_only"`、`calls == []`
- `tests/unit/test_controller_session.py`
  - 新增 `test_session_does_not_create_interrupt_for_presenter_meta_request`
- `tests/unit/test_voice.py`
  - 不需要为首选方案新增测试，除非决定把元请求词表/API 放进 `voice.py`。
- `tests/unit/test_cli.py`
  - 不需要修改。CLI language/tone flags 已有覆盖，元请求是运行时问题 routing，不是 CLI 参数解析。

## 误判风险

主要 false positive：

- `use chat`、`use participants` 这类口语命令。如果只靠 `use`，可能把真实控件请求误判为元请求。因此 `use` 必须和 language/tone/detail/familiarity 词同时出现。
- `briefing` 当前是 `formal` tone alias，但用户可能问 `where is briefing notes`。建议首轮仅在有 presenter 表达意图时才把 tone alias 当元请求。
- `support` 既是 tone alias，也可能是产品支持概念。不要让单词 `support` 单独触发；需要 `use support tone` 或 `be supportive` 之类结构。
- `privacy/safety` 是 careful tone alias，同时也是安全 Q&A 关键词。必须确保 `privacy` 单独不会绕过已有 meeting-info、notes、recording safety Q&A；只有 `use a privacy tone`、`answer in a safer tone` 这类表达方式请求才短路。

主要 false negative：

- 复杂自然语言如 `could you adapt the explanation for executives` 可能首轮不识别。这是可接受的小步边界；未识别时现有安全策略仍会用 `_can_operate(...)` 和 `questionPolicy` 限制高风险控件。
- 西语/日语元请求首轮如果词表较小，可能仍 no-match 或命中安全 Q&A。建议先覆盖英文和中文高频表达，后续按真实需求扩展。

## 是否要改 YAML

不建议改 YAML。

理由：

- 元请求属于 Presenter 表达策略，不属于 RingCentralVideo 控件或知识包。
- 改 `packages/ringcentral-video.yaml` 会影响 localization counts、doctor Q&A prompt 数、alias overlap 诊断。
- YAML Q&A 只保护 RingCentralVideo package，不能保护 `build_temporary_package(...)` 生成的 running-app 临时包。
- 目标明确要求“不进入 RingCentralVideo 控件匹配”，早期 runtime short-circuit 比 package Q&A 更直接。

## 推荐验证命令

实现后建议跑聚焦测试：

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_controller.py::test_presenter_controller_queues_safe_question_without_stopping_running_demo tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo tests\unit\test_controller_session.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice.py tests\unit\test_cli.py::test_controller_passes_language_and_tone_to_runtime tests\unit\test_cli.py::test_demo_passes_language_and_tone_to_runtime
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\questions.py tests\unit\test_questions.py tests\unit\test_controller.py tests\unit\test_controller_session.py
git diff --check
```

如果只改 `questions.py` 和 `test_questions.py`，第一条可缩小到 `tests\unit\test_questions.py` 加 controller/session sentinel。

## 首选切片

首选切片：只改 `src/ai_presenter/runtime/questions.py` 和 `tests/unit/test_questions.py`。

完成标准：

- 语言/语气/详略/熟悉度类 Presenter 元请求返回 `QuestionResponse(entrypoint_id=None, can_operate=False)`。
- `create_question_interrupt_step(...)` 对这些响应返回 `None`。
- 含控件词的元请求不命中 RingCentralVideo entrypoint，例如 `answer chat more concisely` 不进入 `ringcentral.video.toolbar.chat`。
- 普通控件请求仍保持现有行为，例如 `chat` 或 `where is chat` 仍能命中 chat。
- 不改 YAML，不改 CLI，不改 voice settings API。
