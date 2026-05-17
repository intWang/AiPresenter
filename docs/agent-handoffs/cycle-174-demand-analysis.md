# Cycle 174 需求分析：Presenter 元请求防误路由

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle174 demand-analysis subagent

## 范围与约束

本轮只读代码和文档，只写入本文件：

- `docs/agent-handoffs/cycle-174-demand-analysis.md`

未修改源码、测试、YAML、`.coverage`，未 stage，未 commit。读取前工作区已有 `.coverage` dirty，按边界没有触碰。当前 HEAD 为 `2f49dec`，Cycle173 已提交主题为 voices asset cache。

重点阅读：

- `docs/agent-handoffs/cycle-172-demand-analysis.md`
- `docs/agent-handoffs/cycle-172-experience.md`
- `docs/agent-handoffs/cycle-173-demand-analysis.md`
- `docs/agent-handoffs/cycle-173-technical-development.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/session.py`
- `src/ai_presenter/runtime/voice.py`
- `README.md`
- `presenter/soul.md`
- `presenter/skills/ringcentral-safety.md`

## 背景判断

当前问答路由的安全主线已经比较清楚：`answer_question(...)` 先做 Q&A-first，再做 entrypoint alias / token 匹配；`_can_operate(...)` 再依据 `questionPolicy: answerOnly`、`openSteps` 和 risky words 决定是否可操作；`create_question_interrupt_step(...)` 只有在 `entrypoint_id` 存在且 `can_operate=True` 时才会排队执行。

问题在于 Presenter 元请求不属于 RingCentral Video 控件问题，却会被后面的 entrypoint alias/token 匹配吞掉。Cycle172 的只读探针已经观察到高风险误路由：`Switch to careful tone` 可落到 Views，`Be more concise` / `Make this more executive` 可落到 More，`I am new to RingCentral Video` 可落到 Video settings，且部分结果 `can_operate=True`。这和用户真实意图相反：用户是在调整 AiPresenter 的语言、语气、讲解详细度或受众熟悉度，不是在要求打开 RingCentral 控件。

Cycle173 的实现主题转向 `voices` asset cache，没有落地这个元请求 guard。因此 Cycle174 最值得做的小切口仍是：在 app-control 匹配前识别高置信 Presenter 元请求，让它们 answer-only、non-operable、无 interrupt。

## 需求场景

### 1. 语言切换请求：回答语言，不是会议控件

典型话语：

- `Answer in Chinese`
- `Answer in English`
- `Use Chinese`
- `Respond in English`
- 后续可扩展到 `用中文讲`、`用英文回答`

用户意图：调整 Presenter 的回答语言或后续讲解语言。

期望行为：

- 不匹配 RingCentral Video 的任何 entrypoint。
- 不打开 Meeting information、Settings、Video settings、Translation 或其它语言相关 UI。
- 当前小切口只做防误路由和引导，不声称已经持久切换语言，除非实现同时更新了 `ControllerSession.set_voice(...)` 或 controller state。
- 回答应说明这是 Presenter 语言请求，不是 RingCentral Video 控件操作；可以提示控制器已有 language selector，或说“我会按这个方向回答”。

安全原因：`runtime.voice.PresenterVoiceSettings` 已支持 `en/zh/ja/es` 和语言别名，但问答文本框里的自然语言请求目前不是 voice-setting API。把语言词误当 RingCentral 控件会破坏用户信任，也可能排队错误 UI 操作。

### 2. 语气和详略请求：表达风格，不是 Views/More/Reactions

典型话语：

- `Switch to careful tone`
- `Use privacy tone`
- `Use a friendlier tone`
- `Be more concise`
- `Make this more executive`
- `Answer more carefully`

用户意图：改变 Presenter 的口吻、简洁程度或风险边界表达。

期望行为：

- `entrypoint_id is None`，`can_operate is False`，无 interrupt。
- 不返回 `View layout menu:`、`More actions:`、`Reactions:`、`Network quality:` 等 RingCentral 控件答案前缀。
- `careful/privacy/safety` 仍只是风格或元请求，不得改变 `questionPolicy`、`can_operate`、Q&A-first precedence 或 route safety。
- 若本轮不做真实 tone state 更新，文案不能说“已切换”，只能说“我会按更谨慎/更简洁的方式回答”或“可通过控制器 tone selector 调整”。

安全原因：`runtime-safety-routing.md` 已明确 tone 是 style-only。用户说“更谨慎”时，系统不应借此打开 Views 或 More；这类误路由尤其危险，因为 More 下挂 Recording、Notes、Settings 等高风险面。

### 3. RingCentral Video 熟悉度请求：讲解深度，不是 Video settings

典型话语：

- `I am new to RingCentral Video`
- `Explain this for a beginner`
- `Can you explain this for a beginner?`
- `I know RingCentral Video well, be concise`
- `Skip the basics`

用户意图：声明自己对 RingCentral Video 的熟悉度，要求 Presenter 调整解释层级。

期望行为：

- 不把 `new`、`video`、`RingCentral Video`、`beginner`、`concise` 这些词路由到 `ringcentral.video.settings.video`、Views、Reactions 或 More。
- 回答应把熟悉度视为讲解策略：新手多解释概念和位置，熟练用户少讲基础、直接给操作边界。
- 当前小切口不需要新增长期用户画像或记忆写入；只需安全地 answer-only，避免排队 RingCentral 操作。

安全原因：熟悉度请求常发生在 live demo 中，用户并没有要求打开设置。误入 Video settings 属于高噪声、高困惑的行为，也会让后续真正的 Video settings 请求更难测试。

## 推荐本轮小切口

推荐目标：**Presenter 元请求防误路由：高置信语言、语气、详略、RingCentralVideo 熟悉度请求在 RingCentral 控件匹配前被拦截，返回 answer-only、non-operable、无 interrupt。**

建议实现形态：

- 优先在 `src/ai_presenter/runtime/questions.py` 的 `_answer_question(...)` 里、Q&A/entrypoint 匹配前增加小型 presenter-meta guard。
- 先覆盖英文 exact 或高置信短语，不做 broad semantic classifier。
- 不改 `packages/ringcentral-video.yaml`，避免把 Presenter 元语义塞进 RingCentral package，也避免 Q&A/localization/diagnostics count 漂移。
- 不改变真实 `PresenterVoiceSettings` 状态；状态更新可以作为后续 controller/voice 专项。

为什么这是本轮最合适的小切口：

- 用户给出的例子全部属于这个需求面。
- 已有观察显示当前会产生 `can_operate=True` 的错误控件匹配，不只是 no-match 体验问题。
- 改动可小、可测、可回归，不需要 live RingCentral acceptance。
- 它保护后续语言/语气扩展：先把“元请求”和“App 控件请求”分层，再谈真正状态切换。

## 验收标准

建议至少覆盖这些英文 prompt：

- `Switch to careful tone`
- `Use privacy tone`
- `Use a friendlier tone`
- `Be more concise`
- `Make this more executive`
- `Answer in Chinese`
- `Answer in English`
- `Explain this for a beginner`
- `Can you explain this for a beginner?`
- `I am new to RingCentral Video`
- `I know RingCentral Video well, be concise`

每个 prompt 应满足：

- `response.entrypoint_id is None`
- `response.can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- answer 文案说明这是 Presenter 语言/语气/详略/熟悉度请求，不是 RingCentral Video 控件操作
- 不出现 RingCentral 控件答案前缀，例如 `View layout menu:`、`More actions:`、`More video settings:`、`Network quality:`、`Reactions:`、`Meeting information:`
- 不声称已真正切换 language/tone，除非本轮同时实现并测试了状态更新

回归保持：

- `full screen` 相关问题仍应路由到 Views。
- Meeting information privacy、encryption/security status、Notes/Transcript privacy、Recording safety、host/security answer-only 路由不变。
- `participants`、`chat`、`network quality` 等真实控件位置问题仍可按既有规则匹配。
- 如果不改 YAML，package Q&A prompt count、localization count、doctor/diagnostics count 不应变化。

建议聚焦验证命令由实现轮决定；为了不改写 `.coverage`，可使用 `--no-cov -p no:cacheprovider -B` 风格运行 focused tests。

## 风险

- 过宽拦截会吞掉真实控件请求。不要把裸 `more`、`video`、`view`、`language`、`beginner`、`privacy` 当作通用 meta trigger。
- `RingCentral Video` 出现在熟悉度请求里，但也会出现在真实产品问题里。建议必须有 `new to`、`beginner`、`know ... well`、`skip basics` 等明确熟悉度框架。
- `careful/privacy/safety` 容易和安全 Q&A 混淆。它们作为 tone/meta 请求时不应改变安全策略；作为 Meeting information / recording / transcript 安全问题时仍应走既有 Q&A-first guard。
- 不能假装已持久化设置。若只在 question answer 层拦截，文案必须避免“已切换为中文/已切换为 careful tone”。
- 不建议用 package Q&A 实现本需求。那会把 Presenter 层行为绑定到 RingCentralVideo 包，并增加 localization/diagnostics 维护成本。
- 多语言元请求很有价值，但本轮若同时做中文、日语、西语，会放大 matcher 面。建议先英文高置信句，下一轮再扩。

## 不做项

- 不新增真实语言/语气持久切换。
- 不新增 controller UI 或 selector 行为。
- 不修改 voice provider、profile、SAPI/Piper/OpenAI 支持矩阵。
- 不新增 LLM intent classifier 或宽泛语义分类器。
- 不修改 RingCentralVideo package aliases、entrypoints、demo flows、Q&A YAML。
- 不改变 Meeting information、encryption status、full screen Views、Notes/Transcript、Recording、host/security 等既有安全路由。
- 不执行 live RingCentral acceptance。
- 不安装或修改 Codex home skill；技能沉淀先保持 repo-local 文档/测试边界。

## 推荐目标

Cycle174 推荐落地：**Presenter 元请求防误路由小切口**。把 `Be more concise`、`Answer in Chinese`、`Switch to careful tone`、`I am new to RingCentral Video` 等高置信元请求安全回答为 answer-only，不进入 RingCentral 控件匹配，不排队任何 RingCentral 操作。
