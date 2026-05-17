# Cycle174 风险/测试扫描：Presenter 元请求防误路由

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle174 风险/测试扫描 subagent

## 范围与边界

本轮只读代码/文档，并只写入本文档：

- `docs/agent-handoffs/cycle-174-risk-scan.md`

未修改源码、测试、YAML、`.coverage`，未 stage 或 commit。开始扫描时工作区已有 `.coverage` dirty，按要求保持未触碰。

主要参考：

- Cycle173 提交 `2f49dec`：`perf: cache voices asset checks`
- Cycle172 handoffs：meeting-info 隐私 routing 已锁定，重点是 Q&A-first、answer-only、no-interrupt
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/voice.py`
- `src/ai_presenter/packages/models.py`
- `packages/ringcentral-video.yaml`
- `tests/unit/test_questions.py`
- `tests/unit/test_voice.py`
- `tests/unit/test_controller.py`
- `tests/unit/test_controller_session.py`

## 当前 routing 形状

Presenter 问答的关键顺序是：

1. `_match_qa()` 先匹配 exact Q&A，再匹配 recording、notes/transcript、meeting-info privacy 等安全分流。
2. `_is_meeting_info_location_lookup()` 允许“在哪里找 meeting ID/link/host information”走 meeting-info entrypoint，但 entrypoint 自身是 `questionPolicy: answerOnly`。
3. `_match_entrypoint_alias()` 和 token scoring 只在 Q&A 未命中后兜底。
4. `_can_operate()` 用 `questionPolicy == answerOnly`、`openSteps` 和 `_RISKY_ENTRYPOINT_WORDS` 决定是否能生成可执行 interrupt。
5. `PresenterVoiceSettings(language/tone)` 影响回答/旁白渲染、语音 provider 校验和日志标签，不应该改变 route choice。

Cycle174 如果要做“Presenter 元请求防误路由”，最容易出问题的地方不是新增一个 meta intent，而是把这个 intent 插入得太早、太宽或太像普通 entrypoint alias。防线应是：元请求可以回答“Presenter 能/不能做什么、如何安全处理”，但不能抢走已有安全 Q&A，也不能把 answer-only 面板变成可操作 demo。

## 最容易破坏的既有 routing

### 1. Meeting information / meeting-info 隐私边界

最高风险。`packages/ringcentral-video.yaml` 中 `ringcentral.video.top.meeting-info` 同时包含 meeting title、host、meeting ID、copy link、dial-in、encryption 和 E2EE option，且 `questionPolicy: answerOnly`。Cycle172 已把多语言隐私动作请求锁到 privacy Q&A，避免读取、复制、分享真实 meeting values。

容易破坏的方式：

- 新增 “Presenter can/can you/show/read/share” 元请求规则时，把 “meeting information / meeting ID / meeting link” 识别成普通功能说明或可执行打开。
- 为了识别元请求，把 `copy/read/share` 这类 action token 提前归类为“询问能力”，从而绕过 `_match_meeting_info_privacy_qa()`。
- 把 location lookup 和 private-action lookup 合并，导致“会议链接在哪里”与“复制会议链接”走同一条回答。
- 用 localized title/purpose 扩大匹配面，导致西语、日语或中文片段越过 Q&A-first。

需要保住的行为：

- “meeting information”“where is the meeting ID/link” 返回 `ringcentral.video.top.meeting-info`，但 `can_operate is False`。
- “read/copy/share meeting ID/link/dial-in/host info” 返回隐私 Q&A，`can_operate is False`，并且 `create_question_interrupt_step(...) is None`。
- 答案不得包含真实 URL、domain、sample meeting ID、host name、dial-in 或“已复制/已朗读/已分享”的完成态。

### 2. Host controls / Participants 管理边界

高风险。host controls Q&A 是一个安全解释问题，不是直接执行管理动作。它应说明 Participants 面板可用于 attendee count、search、invite、host/moderator control areas，同时不 mute/remove/lock/change security/read names。

容易破坏的方式：

- 元请求里出现 “host”“control”“manage participants” 时，被误路由到 meeting-info，因为 meeting-info 也含 `host`。
- 把 “can Presenter control all UI / operate host controls” 当作普通 controls overview，导致可操作或过度承诺。
- 用 “security settings” 扩宽 encryption/meeting security 的 token 后，抢走 host controls Q&A 或把它误导到 meeting-info encryption。

需要保住的行为：

- “where are host controls for participants” 命中 host controls Q&A，`entrypoint_id is None`，`can_operate is False`。
- 中文 host controls 问法返回中文 guidance。
- 日文 host signal/control 请求不应路由到 raise hand、participants 或其它可操作入口。

### 3. Full screen / View layout

中高风险。Full screen 现有设计是 route 到 `ringcentral.video.top.views`，用于解释 local view/layout menu。它不是控制屏幕共享、焦点、成员关系、音视频状态，也不应该因为“full screen”像操作指令就变成 destructive 或 answer-only。

容易破坏的方式：

- 元请求把 “show / enter / exit / leave full screen” 识别为 Presenter 能力询问后返回 no-match 或通用安全回答，破坏已有 view layout 路由。
- 把 “leave full screen mode” 的 `leave` 纳入 risky entrypoint word 后错误打到 Leave meeting 或阻断 Views。
- 把 “show full screen” 当成屏幕共享、presentation control 或 OS full-screen command。

需要保住的行为：

- Full screen 相关英文 aliases 继续命中 `ringcentral.video.top.views`。
- 该 route 可解释 view layout menu，但回答不声称 AiPresenter 已切换布局、进入/退出全屏、改变共享、音视频、成员或主持人状态。

### 4. Encryption / security status

高风险。Encryption Q&A 关联 meeting-info，但应是 answer-only：可以指向 Meeting information 并概括可见状态，不能断言会议已加密、已启用、已关闭，也不能复制/分享 security status。

容易破坏的方式：

- 元请求把 “is this meeting secure / can you verify security / share security status / copy status” 识别成“能力/元请求”，绕过 encryption Q&A。
- 把 broad tokens `secure/security/status/verify` 放开，导致 bare “security” 误命中 encryption。
- 把 “open encryption settings / change encryption settings / leave encryption off” 当作可操作 setting route。

需要保住的行为：

- 具体 encryption/security status 问题命中 meeting-info answer-only，`entrypoint_id == ringcentral.video.top.meeting-info`，`can_operate is False`，无 interrupt。
- bare “status/security/secure/verify” 不应误命中 encryption status。
- 多语言 encryption 问题继续返回本地化 answer-only。

### 5. Language / tone rendering 与 route 不变量

中高风险。Cycle173 刚做 voice asset cache，下一轮若在元请求里处理 “Presenter should speak/act/respond in X tone/language”，容易把 voice setting 和 route intent 混在一起。

容易破坏的方式：

- 根据 tone 改变 route，例如 `careful/privacy/safe` tone 下把本该路由的 location question 改成 no-match，或把普通 entrypoint 问题强制安全回答。
- 根据 language alias 改变 route，例如 `zh-CN` 与 `zh` 在 localized narration、Q&A answer、日志或 provider routing 中不一致。
- 对日语/西语 localized answer 添加英文 tone prefix，或对中文 careful tone 破坏现有中文前缀/替换逻辑。
- 元请求把 “Presenter tone/language” 当作 package entrypoint 问题，污染 `_match_entrypoint_alias()` 或 token scoring。

需要保住的行为：

- 同一敏感 prompt 在 professional/friendly/careful/support 等 tone 下 route 不变，只是渲染不同。
- `zh-CN`、`ja-JP`、`es-MX` 等 alias 规范化后使用 canonical language key。
- 日语/西语本地化文本不加英文 prefix；中文安全语气不出现 `Safety note`。

## 推荐 focused tests

做 Presenter 元请求防误路由时，建议先加或扩以下 focused tests，再实现。

### 元请求新防线

新增测试建议放在 `tests/unit/test_questions.py`：

- `test_presenter_meta_requests_do_not_steal_meeting_info_privacy_routes`
  - 输入如 “Can Presenter read the meeting link?”、“Can you copy meeting information?”、“Presenter 能朗读会议号吗”
  - 期望命中 meeting-info privacy Q&A，`entrypoint_id == ringcentral.video.top.meeting-info`，`can_operate is False`，无 interrupt
- `test_presenter_meta_requests_do_not_operate_host_controls`
  - 输入如 “Can Presenter mute all participants?”、“Can Presenter manage host controls?”
  - 期望 answer-only host/participants guidance，不能命中 participants interrupt
- `test_presenter_meta_requests_preserve_full_screen_view_layout_route`
  - 输入如 “Can Presenter show full screen?”、“Where is full screen?”、“Leave full screen mode”
  - 期望仍为 `ringcentral.video.top.views`，不要误到 Leave meeting
- `test_presenter_meta_requests_preserve_encryption_answer_only`
  - 输入如 “Can Presenter verify encryption?”、“Can you share security status?”、“Can Presenter change encryption settings?”
  - 期望 meeting-info answer-only，无 interrupt
- `test_presenter_meta_routing_is_language_and_tone_invariant`
  - 同一组敏感问题在 `PresenterVoiceSettings(language="en", tone="professional")`、`tone="privacy"`、`language="zh-CN"`、`language="ja-JP"`、`language="es-MX"` 下 route/can_operate 不漂移

### 已有高信号回归组

如果只跑一组窄测试，优先：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests\unit\test_questions.py::test_chinese_meeting_link_short_question_uses_privacy_qa tests\unit\test_questions.py::test_japanese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_spanish_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_spanish_meeting_info_location_requests_use_entrypoint_answer tests\unit\test_questions.py::test_meeting_info_privacy_gate_does_not_depend_on_risky_words
```

Host controls / Participants：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_host_controls_question_returns_participants_guidance tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route tests\unit\test_questions.py::test_ringcentral_localized_host_controls_question_returns_chinese_guidance tests\unit\test_questions.py::test_ringcentral_japanese_host_signal_control_requests_stay_non_operable tests\unit\test_questions.py::test_exact_qa_match_uses_precomputed_question_index tests\unit\test_questions.py::test_exact_qa_match_uses_trimmed_index_before_entrypoint_alias_fallback
```

Full screen / View layout：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_full_screen_questions_route_to_view_layout tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table
```

Encryption / security：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_bare_status_words_do_not_match_encryption_status tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_ringcentral_localized_encryption_status_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant
```

Language / tone rendering：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_voice.py::test_voice_settings_normalize_language_aliases tests\unit\test_voice.py::test_voice_settings_normalize_expanded_tones tests\unit\test_voice.py::test_render_presenter_text_applies_chinese_careful_tone_without_english_prefix tests\unit\test_voice.py::test_render_presenter_text_keeps_japanese_text_without_english_prefix tests\unit\test_voice.py::test_render_presenter_text_keeps_spanish_text_without_english_prefix tests\unit\test_voice.py::test_language_alias_prefers_canonical_localized_narration_key tests\unit\test_questions.py::test_ringcentral_chinese_safety_qas_keep_authored_text_under_careful_tone tests\unit\test_questions.py::test_answer_question_logs_canonical_language_for_language_alias
```

Controller interrupt/no-interrupt：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_controller_session.py::test_session_creates_interrupt_step_for_safe_answer tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_risky_answer tests\unit\test_controller_session.py::test_session_does_not_create_interrupt_for_notes_question_policy tests\unit\test_controller.py::test_presenter_controller_queues_safe_question_without_stopping_running_demo tests\unit\test_controller.py::test_presenter_controller_answers_risky_question_without_demo
```

## 最终验证命令

开发完成后的推荐收口：

```powershell
git diff --check
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_voice.py tests\unit\test_controller_session.py tests\unit\test_controller.py
```

如果改了 package YAML、diagnostics、localized metadata 或 CLI 输出：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
```

最终全量：

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
```

提交前确认没有误纳 `.coverage` 或本轮外文件：

```powershell
git status --short
git diff --cached --name-status
git diff -- .coverage
```

## No-go 条件

出现以下任一情况，不建议合入 Cycle174：

- meeting-info private action 请求可操作，或生成 `create_question_interrupt_step(...)`。
- meeting ID/link/dial-in/host/encryption status 答案包含真实值、示例 URL/domain/ID，或声称已复制、已朗读、已分享。
- “where are host controls for participants” 被路由到 meeting-info、participants interrupt、security/encryption 或 no-match。
- host controls、mute all、remove participant、lock/unlock meeting、change security settings 任何请求变成可操作。
- Full screen aliases 不再命中 `ringcentral.video.top.views`，或误命中 Leave meeting / Share / OS full-screen。
- encryption/security status 请求不再是 meeting-info answer-only，或 bare `security/status/secure/verify` 开始误命中 encryption。
- language/tone 改变同一敏感 prompt 的 route、entrypoint_id 或 can_operate。
- 日语/西语 localized answer 被加英文 prefix；中文 careful/privacy tone 出现英文 `Safety note`。
- 新增 meta matcher 位于 Q&A safety matchers 之前，且没有精确测试证明不会抢 meeting-info、host controls、fullscreen、encryption。
- 为了元请求支持而把 `localizedTitles` / `localizedPurposes` 加入 runtime match candidates。
- `.coverage`、无关源码、测试或 YAML 被误改、误 stage。

## 风险结论

Cycle174 的核心风险是“元请求”这个词太宽：它很容易把用户对 Presenter 能力边界的询问，误处理成普通 entrypoint location 或操作请求。最危险的是 meeting-info 隐私 routing，其次是 host controls 和 encryption/security 的 answer-only 边界；Full screen 风险主要在误打到 Leave/Share 或被元请求 no-match；language/tone 风险主要在渲染层反向污染 routing。

建议实现策略是保守插入：元请求 matcher 必须在已有 exact/safety Q&A 后面，或只处理明确不属于既有安全 Q&A/entrypoint alias 的问题。任何改动都应先用 focused tests 固定 `entrypoint_id`、`can_operate`、`create_question_interrupt_step` 和本地化 answer，再做最小实现。
