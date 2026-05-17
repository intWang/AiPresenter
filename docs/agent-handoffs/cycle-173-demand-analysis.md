# Cycle 173 需求分析：Presenter 元请求、技能沉淀与 RingCentralVideo 熟悉度

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle173 demand-analysis subagent

## 范围与约束

本轮只读代码和文档，只写入本文件：

- `docs/agent-handoffs/cycle-173-demand-analysis.md`

未修改源码、测试、YAML、`.coverage`，未 stage，未 commit。读取前工作区只有 `.coverage` dirty；当前 HEAD 为 `a7d1c81`，提交主题是 `test: localize meeting info privacy routing`。

重点阅读材料：

- Cycle170-Cycle172 handoff 文档
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- 最近提交日志与只读 `rg` 结果

## 近期脉络

Cycle170-Cycle172 的主线非常集中：Meeting information、encryption/security status、read/copy/share/paste 类隐私动作，以及多语言 meeting-info 私密值请求，都必须 Q&A-first、answer-only、non-operable、无 interrupt，且不能从静态包文本声称实时会议状态或暴露会议 ID、链接、拨入、host 等值。

Cycle172 已把西语/日语 meeting-info 动作型隐私请求补齐到本地化路由，并处理了 `host controls` 误入 meeting-info 的回归。下一轮如果继续只扩 prompt，收益会变窄，风险仍然集中在 matcher 过宽、薄 entrypoint answer、localized caveat 漂移和诊断计数维护。

维护手册还提示了更上层的方向：运行时 presenter skills、package YAML、durable knowledge、handoff、Codex home skills 是不同层。当前不应直接安装或改全局技能；更稳妥的是先把可复用经验沉淀在 repo-local 文档/测试边界，再决定是否升级为技能。

## 最值得推进的 3 个需求

### 1. Presenter 元请求防误路由

用户在 demo 中会自然说：

- `Switch to careful tone`
- `Use privacy tone`
- `Be more concise`
- `Make this more executive`
- `Answer in Chinese`
- `Answer in English`
- `Explain this for a beginner`
- `I am new to RingCentral Video`
- `I know RingCentral Video well, be concise`

这些是对 AiPresenter 的语言、语气、详略、受众熟悉度要求，不是 RingCentralVideo 控件操作。Cycle172 demand/experience 已记录过高风险现象：类似话语可能误路由到 Views、More、Video settings 或 Reactions，并且有的会变成 `can_operate=True`。这会直接损害控制器信任感：用户只是想让讲解更谨慎、更短、更适合新手，系统却像要点击会议 UI。

用户价值：

- 让控制器更“听得懂人话”，减少演示中误触 RingCentral 控件的恐惧。
- 为后续真正的语言/语气切换打入口边界：先识别为 presenter-meta，再决定是否只是回答、更新 controller state，或走未来的设置流程。
- 把 RingCentralVideo 熟悉度变成产品语义：新手讲细一点、熟练用户少讲基础，而不是错误进入 Video settings。

为什么现在做：

- 这是当前已有的可操作误路由，不是低价值 no-match。
- 可以先做小而精的英文 exact/high-confidence guard，不改 package YAML 大量 prompt，不引入语义分类器。
- 能同时覆盖用户要求的 UI 体验、语言/语气扩展、RingCentralVideo 熟悉度三条线。

### 2. RingCentralVideo 资料包熟悉度与知识导航

RingCentralVideo 知识文档已经形成一组资料包：source index、evidence index、runtime safety routing、privacy matrix、locator/state/acceptance/runbook。问题是这些资料对维护 agent 很有价值，但对“下一轮该先读什么、怎么判断能不能动某个 route、怎样避免 live acceptance 过度声明”仍需要人工拼装。

需求形态可以是 repo-local 维护产物，而不是运行时功能：

- 给 RingCentralVideo 资料包补一个“下一轮任务入口图”：按需求类型指向 source/evidence/privacy/runtime safety/acceptance。
- 把常见判断转成清单：是 answer-only、repo-tested、observed、accepted，还是 blocked。
- 明确“资料熟悉”不等于“可执行信心”：没有 dated live acceptance 的 route 不能声称 accepted。

用户价值：

- 新 subagent 更快进入状态，少重复翻 10 份文档。
- 降低把官方文档、repo tests、live evidence 混为一谈的风险。
- 为未来 `RingCentral evidence reviewer` 或 `AiPresenter maintenance steward` 技能候选提供真实使用样本。

风险：

- 纯文档如果写得太泛，会变成另一个过期索引。
- 如果误写成 runtime skill 或全局 Codex skill，会越过维护手册边界。

适合的验收：

- 新文档或维护手册小节只链接现有知识源，不复制大量内容。
- 明确 evidence levels 和“不声称 live accepted”的语言。
- `rg` 能定位 source/evidence/privacy/runtime safety/acceptance 五类入口。

### 3. Matcher 增长后的性能与可维护性护栏

RingCentralVideo Q&A 和 localized prompt 数量持续增长，近期又加入多语言隐私动作词、location lookup、专用 safety matcher。当前代码已经有 `MaterialPackage` 侧的预计算候选与相关测试，说明纯“预计算候选”不是全新空白；下一步更值得做的是性能/可维护性护栏，而不是盲目追 wall-clock。

需求可以聚焦在两类：

- 结构性护栏：当新增 prompt、alias、localized matcher fragment 时，诊断报告能指出高风险短 token、substring overlap、localized location/action 交叉风险。
- 轻量 timing/trace：在 controller question path 或 debug 日志里保留 question routing 的候选数量、命中阶段、总耗时，帮助后续判断卡顿来自 matcher、UIA、TTS 还是操作清理。

用户价值：

- package 继续扩张时，路由行为更可解释，不靠人工 route probe 追错。
- 性能讨论从“感觉慢”转为有结构证据。
- 维护者能区分行为回归和性能回归。

风险：

- 如果做成 wall-clock 单测，容易 flaky。
- 如果在同一轮改 matcher 行为和性能统计，问题定位会变难。

适合的验收：

- 优先结构性测试和诊断输出，不以固定毫秒阈值作为唯一标准。
- 不改变已有 route、`can_operate`、interrupt、diagnostics count 语义，除非该轮明确声明。

## 推荐本轮小切口

推荐目标：**Presenter 元请求防误路由：语言、语气、详略与 RingCentralVideo 熟悉度请求 answer-only，不进入 RingCentral 控件匹配。**

这是本轮最小、最有用户价值的切口。它不需要新增真实语言/语气切换，不需要改 controller UI，不需要 live RingCentral acceptance，也不需要继续扩大多语言 privacy prompt 面。它只先保护高置信元请求，避免误触 Views、More、Video settings、Reactions 等 app controls。

## 用户价值

- 演示中用户可以自然要求“讲短一点”“用中文回答”“按新手解释”，系统不会误以为要操作会议按钮。
- 控制器体验更稳定：answer-only、non-operable、无 queued interrupt，降低错误点击风险。
- 为后续语言/语气扩展留下正确分层：本轮识别元意图，未来再决定是否更新 `PresenterVoiceSettings` 或 controller state。
- 提升 RingCentralVideo 资料包熟悉度表达：用户熟悉度是讲解策略，不是 RingCentralVideo 控件。

## 建议验收标准

建议先覆盖英文 exact/high-confidence prompts：

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

- `entrypoint_id is None`
- `can_operate is False`
- `create_question_interrupt_step(package, response) is None`
- 不返回 `View layout menu:`、`More actions:`、`More video settings:`、`Network quality:`、`Reactions:`、`Meeting information:` 等 RingCentral 控件答案前缀
- answer 文案说明这是 presenter 语言/语气/详略/熟悉度请求，不是 RingCentralVideo 控件操作
- 不声称已经真正切换语言或语气，除非实现确实更新了 controller/runtime voice state；本轮推荐只做 answer-only 防误路由
- 现有 Meeting information privacy、encryption status、full screen Views、host/security、localized meeting-info privacy 路由继续通过

若实现选择 runtime/controller guard 而非 package Q&A：

- package Q&A prompt counts、localization counts、doctor/diagnostics count 不应变化。
- 测试应证明该 guard 只拦截高置信自然句，不拦截真实 RingCentral 控件查询。

## 风险

- 元请求识别过宽会吞掉真实控件请求。例如不要把裸 `more`、`video`、`view`、`language`、`beginner` 当作元请求。
- 不能把 tone 当安全策略。`careful/privacy` 是风格或元请求，不应改变 `questionPolicy`、`can_operate` 或 route safety。
- 不能假装完成持久化设置。本轮如果不改 voice/controller state，答案应说“我会按这个方向回答”或“可以通过控制器选择器调整”，不要说“已切换”。
- 如果用 package YAML Q&A 实现，会把 presenter 元语义塞进 RingCentral package，并带来 count/localization 维护成本；更干净的方向是 runtime/controller 层的小 guard。
- 多语言元请求如 `用中文讲` 很有价值，但本轮若一起做中文/日语/西语，matcher 面会扩大；建议先英文 exact 验证分层。

## 不做项

- 不新增真实语言切换、语气持久化、profile/provider 支持矩阵。
- 不新增 controller UI。
- 不改 OpenAI/SAPI/Piper/Codex provider 行为。
- 不新增 broad semantic classifier 或 LLM intent classifier。
- 不改 RingCentralVideo package 的控件 aliases。
- 不改 Meeting information、encryption status、host/security、full-screen、localized meeting-info privacy 既有路由。
- 不执行 live RingCentral acceptance。
- 不安装或修改 Codex home skill；技能沉淀先保留在 repo-local 文档和后续候选设计里。

## 后续候选排序

1. 本轮推荐：Presenter 元请求防误路由。
2. 下一候选：RingCentralVideo 知识导航/资料包熟悉度清单，作为 repo-local skill candidate 的使用样本。
3. 再下一候选：matcher 增长后的结构性诊断和轻量 timing/trace，避免继续靠人工 route probe 发现回归。
