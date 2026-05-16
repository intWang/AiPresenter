# Cycle 059 Demand Analysis: Diagnostics Guardrail for Alias Substring Routing Risk

## 需求判断

建议新增 diagnostics 护栏，检测 package-owned `questionAliases` 作为隐私/安全 Q&A prompt 子串时的潜在路由风险。

当前 runtime 的实际行为仍然安全：`answer_question()` 先执行 Q&A 匹配，再进入 entrypoint alias 匹配；第058轮新增的日语 meeting-basics aliases 在现有 `ringcentral-video` 包下也通过了 `qa alias overlap` exact 检查。但现有 doctor 只覆盖三类结构性问题：

- `question aliases`: normalized alias 是否跨 entrypoint 重复。
- `qa questions`: normalized Q&A prompt 是否跨 Q&A item 重复。
- `qa alias overlap`: normalized Q&A prompt 是否与 package-owned alias 完全相同，且 alias 指向无关 entrypoint。

它不会发现短 alias 出现在较长隐私/安全 Q&A prompt 内部的风险，例如 Chat / Participants 类短 alias 被未来用户变体或新增 Q&A prompt 包含时，可能绕过 answer-only 安全文案，落到 `_match_package_entrypoint_alias()` 的 substring fallback。第058轮风险扫描已经把这个缺口标成 diagnostics 覆盖不足，因此第059轮适合把它收敛为 doctor 预警，而不是等到 runtime 行为被扩 alias 推到边界后再补。

## 用户价值

这个护栏的价值主要是提前暴露“看似无害的本地化 alias”对隐私/安全问答路由的影响。

对包维护者来说，它能在新增 Chat、Participants、Recording、Notes、Transcript、Invite 等敏感入口 alias 时，及时提示 alias 是否出现在 answer-only 的安全边界 Q&A 中，尤其是多语言短词和片假名/汉字短语。对最终用户来说，它减少了隐私问题被误当成“打开面板”请求的概率，避免 AiPresenter 在会议中打开聊天、参与者、记录、字幕等可能含有敏感信息的界面。

该需求也能让 doctor 继续承担“扩展前预检”的角色：当前 runtime Q&A 优先级是最后防线，diagnostics 应该成为更早、更便宜的内容质量门禁。

## 建议范围

建议新增一个独立 diagnostics check，名称可用 `qa alias substring overlap` 或 `qa alias substring risk`，放在 `_diagnose_material_package()` 的 package 检查序列中，紧邻现有 `_diagnose_qa_alias_overlaps()`。

建议检测逻辑：

- 遍历 package-owned `entrypoint_question_aliases` 和 `qa_question_candidates`。
- 检测 `alias.normalized_alias in candidate.normalized_question`，但排除完全相等的情况；完全相等仍由现有 `qa alias overlap` 覆盖。
- 仅在 alias 指向的 entrypoint 不属于 Q&A item 的 `related_entrypoint_ids` 时报警；如果 Q&A 明确关联同一入口，视为可解释 overlap。
- 优先以 `WARN` 呈现，因为当前 runtime Q&A 优先，风险是未来扩 alias / prompt 变体导致的路由脆弱性，不是现有必现故障。
- detail 中应包含 normalized alias、Q&A label、Q&A language、alias language、alias entrypoint id，以及“runtime exact Q&A still wins, but alias fallback may route variants”这一类可操作解释。
- 当前 RingCentral package 应保持 OK，以避免第058轮已提交内容被新护栏误判为当前失败。

建议测试范围：

- `tests/unit/test_diagnostics.py` 增加子串风险单测：例如 alias `chat` 出现在 Q&A `can ai read chat messages` 中，且 Q&A 无 related entrypoint 或 related entrypoint 不含 `demo.chat`，应 WARN。
- 增加允许场景：alias 是 prompt 子串但 Q&A `relatedEntrypointIds` 包含该 alias entrypoint，应 OK。
- 增加 exact overlap 不重复报警的场景，避免同一问题同时被 `qa alias overlap` 和新 check 报两次。
- `tests/unit/test_cli.py` 增加 doctor 输出覆盖，确认 CLI 能呈现新 WARN，且 warning 计数正确。
- 更新 RingCentral doctor 期望，确认现有 `ringcentral-video` 仍为 OK，并更新 package aliases / Q&A prompt 计数时只反映真实数据变化。

## 非目标

本轮不建议修改 runtime matching 顺序。Q&A 优先是当前安全行为的核心，需求目标是预检内容风险，而不是改变用户问答路由。

本轮不建议修改 `packages/ringcentral-video.yaml`。第058轮的日语 meeting-basics aliases 已经落地，本需求是给未来扩展加护栏。

本轮不建议把所有 alias 子串命中升为 FAIL。很多入口定位类 Q&A 会自然包含入口名，强制失败会制造噪音；先用 WARN 并结合 related entrypoint 过滤更符合 doctor 现有风格。

本轮不建议引入复杂的隐私分类模型或语言特定 NLP。第一阶段只做 normalized substring + related entrypoint 关系判断，足以覆盖第058轮指出的缺口。

## 验收口径

可以按以下标准验收：

- doctor 对 package-owned alias 的 exact overlap 和 substring overlap 分别给出清晰、非重复的诊断。
- 新增子串风险样例会产生 `WARN`，输出能定位到 alias、Q&A item、语言和被 shadow 的 entrypoint。
- Q&A item 显式关联同一 entrypoint 时不报警。
- 当前 `packages/ringcentral-video.yaml` 在 doctor 中仍不产生新增 WARN。
- CLI doctor 的 warning / failed 计数正确；新增 WARN 不导致 exit code 变为失败。
- 单测覆盖 diagnostics helper 和 CLI 输出，建议最小命令为：
  - `pytest tests/unit/test_diagnostics.py -k "qa_alias"`
  - `pytest tests/unit/test_cli.py -k "doctor"`

## 后续建议

下一轮可先实现最小 diagnostics WARN，不碰 runtime 和 YAML。实现后再用第058轮列出的日语 Chat / Participants 隐私问法做一次手工或单测探针，确认 doctor 能捕获未来短 alias 扩展风险。

如果后续发现 WARN 噪音较高，可以再细化策略：只对 answer-only Q&A、敏感 entrypoint、或包含 privacy/action 词的 prompt 报警；但第一版不必过度设计，先让 doctor 看见“短 alias 嵌入安全 Q&A”的结构性风险。

## Files Changed

- `docs/agent-handoffs/cycle-059-demand-analysis.md`
