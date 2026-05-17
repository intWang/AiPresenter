# Cycle 172 经验沉淀：AiPresenter / RingCentralVideo

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle172 experience subagent

## 范围与边界

本轮只读取以下材料并沉淀经验：

- `docs/agent-handoffs/cycle-172-demand-analysis.md`
- `docs/agent-handoffs/cycle-172-technical-scan.md`
- `docs/agent-handoffs/cycle-172-risk-scan.md`
- 当前工作区 diff

本文件是唯一写入文件：

- `docs/agent-handoffs/cycle-172-experience.md`

未修改源码、测试、YAML、`.coverage`，未 stage，未 commit。读取时工作区已有 `.coverage`、`src/ai_presenter/runtime/questions.py`、`tests/unit/test_questions.py` 变更，以及三份 Cycle172 handoff 未跟踪文件；本沉淀不回滚、不接管这些改动。

## 本轮经验

Cycle172 的核心经验是：RingCentralVideo 的问答扩展不能只看“是否可操作”，还要同时固定 route、operability、interrupt、answer wording 和 localized caveat。一个问题即使当前是 no-match、non-operable，也可能代表体验缺口；但一旦扩展，风险会从“找不到答案”转为“命中了错误 surface、薄 entrypoint answer，或丢失隐私边界”。

当前 diff 走的是 runtime matcher 小步扩展路线：在 `src/ai_presenter/runtime/questions.py` 中扩展 Meeting information privacy 的日语/西语 action tokens、content fragments 和西语 location lookup terms；在 `tests/unit/test_questions.py` 中新增日语、西语 action requests 命中 localized privacy Q&A 的断言。这个方向延续了 Cycle171 的 Q&A-first 隐私保护：读、复制、分享、粘贴会议 ID、会议链接、拨入信息、host 信息等价值请求，应返回 Meeting information privacy Q&A，`can_operate=False`，无 interrupt，不暴露具体值。

这轮也再次暴露 AiPresenter 与 RingCentralVideo 的边界：用户说“Answer in Chinese”“Be more concise”“I am new to RingCentral Video”时，语义上是在调整 presenter 语言、语气、详略或熟悉度，不是在操作 RingCentral Video。此类 presenter-meta 请求如果落到 Views、More、Video settings，就会让控制器显得像误解了用户。因此下一步若处理元请求，应优先在 runtime/controller 层做精确 guard，让它 answer-only、non-operable，而不是把 presenter 行为塞进 RingCentral package 的 entrypoint aliases。

## 语言扩展时的 matcher 原则

语言扩展要遵守“动作词 + 私密内容片段 + 位置查询 gate”的三段式约束。只出现 `id`、`link`、`security`、`status`、`video` 这类宽泛 token，不应成为命中依据；必须同时看到足够明确的动作意图和足够明确的私密内容对象。

动作词要窄：例如日语的 copy/share/read 片段，西语的 `lee/copiar/comparte/pega` 等，可以作为候选；但不能把单字、常见名词或 UI surface 名称当成动作。内容片段要长：优先使用 `id de la reunion`、`enlace de la reunion`、`会议链接`、`会議リンク` 这类 phrase，而不是 `id`、`url`、`link` 单点触发。

位置查询必须继续让位给 entrypoint answer。`where is meeting link`、中文“在哪里”、西语 `donde/ubicacion` 这类问题是在问入口位置，不是在要求读出、复制或分享具体值。新增语言 matcher 时，应配套负向用例，确认位置查询不会被 privacy Q&A 抢走。

敏感 answer 的验收不能只断言 `answerOnly`。还要断言没有 interrupt、不包含 URL/domain/sample ID、不声称已复制/已读取/已分享/已验证、不把静态包文案推断成 live meeting state。tone 和 localization 都不能稀释这些 caveat。

## 不改 YAML prompt 数量的适用条件

当目标是扩大已有安全 matcher 的语言覆盖，并且已有 localized Q&A answer 可复用时，优先不改 YAML prompt 数量。runtime matcher 能避免 Q&A prompt count 从当前固定值继续漂移，也避免同步修改 diagnostics、CLI localization/doctor 里的硬编码统计。

适合不改 YAML 的情况：

- 语义已经存在于包内 Q&A，只是自然语言动作问法漏匹配。
- 可以用小型、可审查的 action/content fragment 覆盖。
- 需要保持 `tests/unit/test_diagnostics.py` 中 RingCentral Q&A prompt count 不变。
- 变更目标是 routing guard，而不是新增知识内容。
- 期望最小化对 package localization lifecycle 的影响。

应该考虑改 YAML 的情况：

- 新增的是知识内容或正式 authored prompt，而不是 matcher 漏洞。
- 需要让 material package 自身表达新的用户可见问法。
- runtime matcher 已经变得过宽或难以解释。
- 多语言问题需要由 localization report 追踪为包内容覆盖，而非路由补丁。

本轮 diff 属于“不改 YAML prompt 数量”的典型场景：日语/西语隐私 answer 已存在，缺的是 action-form 问句进入 privacy Q&A 的通道。

## 下一轮候选优化

1. Presenter-meta guard：覆盖语言、语气、详略、熟悉度等高置信短句，确保 `Answer in Chinese`、`Be more concise`、`Switch to careful tone`、`I am new to RingCentral Video` 不再进入 RingCentral app controls。

2. Meeting information location regressions：补充英文、中文、日语、西语“在哪里/where/donde/ubicacion”类位置查询测试，固定它们继续返回 entrypoint 位置说明，而不是 privacy Q&A。

3. Sensitive wording assertions：把日语/西语隐私测试从“包含 localized caveat”扩展到“不包含 URL、domain、sample ID、copied/read/shared outcome claim”，与英文/中文隐私测试保持同一标准。

4. Matcher candidate precompute：当 Q&A prompts 和 matcher fragments 继续增长时，重新评估 `MaterialPackage` 侧预计算候选，目标是行为不变、减少 live question routing 的重复构造成本。

5. Prompt-count contract cleanup：若未来必须改 YAML prompt 数量，集中更新 diagnostics/CLI 统计断言，并在 handoff 中明确说明为什么这次不能继续走 runtime matcher。

## 给下一轮的提醒

不要把“安全 no-match”误认为“体验完成”。对 RingCentralVideo 这类演示控制场景，理想状态是安全且有用：敏感值不读、不复制、不分享，但用户仍能得到清楚的隐私说明和正确入口。

也不要把 `answerOnly` 误认为完整安全边界。真正要守住的是：不执行、不打断、不泄露、不虚构 live state、不把 presenter 元指令当成 app 控件操作。
