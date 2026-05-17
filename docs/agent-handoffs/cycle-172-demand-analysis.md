# Cycle 172 需求分析：Presenter 元请求与隐私路由边界

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle172 demand-analysis subagent

## 范围

本轮只读近期交接文档、项目文档、`packages/ringcentral-video.yaml`、RingCentral Video 知识文档，以及少量只读路由探针。只写本文件：

- `docs/agent-handoffs/cycle-172-demand-analysis.md`

没有修改源码、测试、包 YAML、`.coverage`、暂存区或提交。工作区进入分析时已有 ` M .coverage`，按要求不触碰。

重点阅读：

- Cycle168-Cycle171 demand / technical / risk / experience / review handoff
- `README.md`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `presenter/soul.md`
- `presenter/memory.md`
- `presenter/skills/ringcentral-safety.md`
- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py` 中的当前匹配边界

## 近期上下文

Cycle168-Cycle171 的主线是 RingCentral Video 问答路由安全：

- Cycle168：把会议安全/lock/settings 类 host-control 问法固定到 answer-only。
- Cycle169：把 full screen 相关短语路由到 Views，避免 Screen sharing / Leave 误路由。
- Cycle170：新增 encryption/security status Q&A，指向 Meeting information，但不声称当前会议已加密、已启用、已验证或安全。
- Cycle171：加固 Meeting information 隐私请求，新增专用 matcher，让英文和中文的 read/copy/share/paste 会议号、链接、URL 等请求进入隐私 Q&A；裸 `status/security/secure/verify` 保持 no-match，避免变成静态安全断言。
- 上一轮提交 `a0ee47d` 已把 Chinese meeting-info privacy action forms 纳入专用 matcher，主题是 harden meeting info privacy routing。

这说明当前最稳定的工程策略是：精确短语优先、Q&A answer-only 优先、敏感值不读不复制、状态不从静态包文本推断、不要把元意图或隐私意图落到可操作 UI 控件。

## 用户需求候选

### 1. Presenter 元请求不要误触 RingCentral 控件

用户会在 demo 中自然说：

- `Switch to careful tone`
- `Be more concise`
- `Make this more executive`
- `Answer in Chinese`
- `Can you explain this for a beginner?`
- `I am new to RingCentral Video`
- `I know RingCentral Video well, be concise`

只读探针显示几个高风险误路由：

| 用户话语 | 当前观察 |
| --- | --- |
| `Switch to careful tone` | 路由到 `ringcentral.video.top.views`，`can_operate=True` |
| `Be more concise` | 路由到 `ringcentral.video.toolbar.more`，`can_operate=True` |
| `Make this more executive` | 路由到 `ringcentral.video.toolbar.more`，`can_operate=True` |
| `I am new to RingCentral Video` | 路由到 `ringcentral.video.settings.video`，`can_operate=True` |
| `I know RingCentral Video well, be concise` | 路由到 `ringcentral.video.settings.video`，`can_operate=True` |
| `Can you explain this for a beginner?` | 命中 Reactions/Raise hand 安全 Q&A，语义不对 |

用户价值：这些不是 RingCentral Video 控件问题，而是对 AiPresenter 的语言、语气、详细程度、用户熟悉度的元指令。误路由到 Views、More、Video settings 会让控制器看起来“不听人话”，甚至可能排队打开错误 UI。

涉及重点：

- 语言类型：`Answer in Chinese`、`Use English`、`用中文讲`。
- 语气类型：`careful`、`privacy`、`friendly`、`concise`、`executive` 等。
- RingCentralVideo 熟悉度：新手、熟练用户、少讲基础、讲得更细。
- Q&A/技能边界：这是 presenter / controller / voice 层意图，不应由 RingCentral package entrypoint 匹配处理。

建议方向：在 app-control 匹配前增加一个很小的 presenter-meta intent guard，先覆盖高置信英文短语。返回 answer-only / non-operable，提示用户可通过 controller 的 language/tone selectors 或下一句自然指令调整讲解风格；不要点击任何 RingCentral UI。

### 2. 西班牙语、日语的 Meeting information 动作式隐私问法补齐

Cycle171 已覆盖英文和中文 meeting-info private action forms，但只读探针显示西班牙语、日语类似请求多为 no-match：

- Spanish: copy/read/share meeting link or meeting ID
- Japanese: copy/read/share meeting link or meeting ID

当前 no-match 是安全的，但不够有用。包里已有 zh/ja/es localized Q&A answers，`language-lifecycle.md` 也说明西班牙语 package localization 已较完整，OpenAI-backed Spanish runtime 可用。用户用西班牙语或日语问“复制会议链接 / 读会议 ID”时，理想行为应与英文、中文一致：Meeting information privacy Q&A、`can_operate=False`、无 interrupt、不暴露值。

用户价值：提升非中英文隐私问答一致性，避免“英文/中文安全且有用，其他语言只有 no-match”的体验断层。

风险：日语 token/fragment 匹配比中文更复杂，西班牙语存在冠词、重音、`link/enlace/ID` 变体。若直接加宽 matcher，可能影响 Invite、Share、Meeting information 位置查询。适合作为单独语言 wedge，先 exact Q&A prompts 或非常小的 localized action/content fragment 列表，配负向测试。

### 3. Matcher 增长后的性能和可维护性

RingCentral Video Q&A prompt 数从早期知识文档中的 84 增长到 Cycle171 后约 220，近期几轮大量依赖 exact prompts、专用 safety matcher、负向路由测试和诊断计数。仓库已有 `qa-matcher-candidate-precompute` 设计和计划，目标是在 `MaterialPackage` 上预计算 Q&A / entrypoint matcher candidates，避免 live controller 中每次 question 都重复构造候选和 token sets。

用户价值：对 live controller 更稳，减少每次问答的重复工作，也降低未来包继续扩张时的性能和回归风险。

风险：这是基础设施改动，要求“行为完全不变”。虽然已有计划，但相比 Cycle172 的产品价值小切口，它更像技术债优化；如果本轮做，需要强行为回归测试，而不是 wall-clock 性能断言。

## 推荐本轮小切口

推荐目标：**Presenter 元请求路由保护：语言、语气、熟悉度请求 answer-only，不进入 RingCentral 控件匹配。**

选择理由：

- 它直接覆盖用户给出的重点维度：语言类型、语气类型、RingCentralVideo 熟悉度、Q&A/技能边界。
- 当前已经存在可操作误路由，不只是“不够好”的 no-match。`Switch to careful tone`、`Be more concise`、`I am new to RingCentral Video` 这类话语不应打开 Views、More 或 Video settings。
- 切口可以很小：先做精确高置信英文短语，不改包 YAML 大面积别名，不引入语义匹配，不改变真实 language/tone 设置。
- 它能保护 controller 体验：用户在演示中调整讲解方式时，AiPresenter 应回答“我会按这个方式讲/请使用控制器选择器”，而不是执行 app 操作。

## 可测验收标准

建议本轮只覆盖英文 exact prompts，保持实现可控：

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
- 不返回 `View layout menu:`、`More actions:`、`More video settings:`、`Network quality:`、`Reactions:` 等 RingCentral 控件答案前缀
- 不改变实际 `PresenterVoiceSettings.language` 或 `tone`；本轮只是防误路由和 answer-only 引导
- answer 文案说明这是 presenter 语言/语气/讲解深度请求，不是 RingCentral Video 控件操作
- 现有敏感路由不变：Meeting information privacy、encryption status、full screen Views、host/security answer-only、tone-invariant routing 继续通过

推荐聚焦测试：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_presenter_meta_requests_do_not_route_to_app_controls tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_questions.py::test_ringcentral_full_screen_questions_route_to_view_layout tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first
```

若实现不改包 YAML，则 diagnostics / doctor prompt counts 不应变化。

## 风险

- 元请求词过宽会吞掉真实 RingCentral 控件问题。例如 `view tone`、`more`、`video`、`language` 单词不能作为广义禁用词。
- 不能假装已经切换语言或语气，除非 controller / CLI 确实持久化了新的 `PresenterVoiceSettings`。本轮只建议 answer-only 防误路由。
- `beginner` / `expert` 类熟悉度请求可能既是元请求，也可能是“给我一个 overview”。建议只覆盖明确的自然句，不碰裸 `beginner`、`overview`、`RingCentral Video`。
- 如果选择用 package Q&A 实现，会增加 Q&A counts，并把 presenter 元语义放进 RingCentral package。更干净的方向是 runtime guard 或 controller 层 guard，但需保持 no package count drift。

## 不做项

- 不新增真实语言/语气切换能力。
- 不新增 controller UI。
- 不更改 voice provider、profile、SAPI/Piper/OpenAI 支持矩阵。
- 不加入 broad semantic classifier。
- 不更改 Meeting information、encryption status、host/security、full-screen 已有路由。
- 不扩展西班牙语/日语隐私动作词；这是下一候选需求。
- 不执行 RingCentral live acceptance。

## 推荐本轮目标

**落地一个精确的 Presenter 元请求防误路由小切口：让语言、语气、讲解详细度、RingCentralVideo 熟悉度相关的高置信请求保持 answer-only、non-operable、无 interrupt，并明确不进入 RingCentral Video 控件匹配。**
