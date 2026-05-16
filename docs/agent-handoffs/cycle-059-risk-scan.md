# Cycle 059 Risk Scan: Alias Substring Diagnostics

## Scope

本轮审视候选 diagnostics/doctor warning/info：检测 package-owned alias 作为隐私/安全 Q&A prompt 子串时的风险。该功能不改变 runtime question matching，只作为诊断层提示。

目标边界：

- 不影响正常 runtime Q&A 优先级和 entrypoint alias matching。
- 不重复制造现有 `qa alias overlap` exact prompt equals alias 的噪声。
- 不让当前健康的 RingCentral Video 包因为朴素子串扫描直接变成 warning，除非命中代表不可接受风险。

## Current Diagnostics Context

- `diagnose_configuration()` 当前对 material package 依次追加 `question aliases`、`qa questions`、`qa alias overlap`、`explainer coverage`。
- `question aliases` 只检查 normalized alias 跨 entrypoint duplicate。
- `qa questions` 只检查 Q&A prompt 跨 Q&A item duplicate。
- `qa alias overlap` 只检查 Q&A prompt normalized value 与 package-owned alias normalized value 完全相等，且 alias entrypoint 不在该 Q&A item 的 `relatedEntrypointIds` 中时才 WARN。
- 现有单测明确要求当前 RingCentral 包为健康状态：
  - `question aliases`: `OK`, `62 package-owned aliases have no cross-entrypoint duplicates`
  - `qa questions`: `OK`, `71 Q&A question prompts have no cross-item duplicates`
  - `qa alias overlap`: `OK`, `71 Q&A question prompts have no unsafe package-owned alias overlaps`

## Probe Result

用当前包数据模拟“alias normalized value 是 Q&A normalized prompt 的真子串”后，RingCentral Video 当前包会产生明显命中：

- 总 alias 数：62
- 总 Q&A prompt candidate 数：71
- substring 命中：41
- 其中 alias entrypoint 不在 Q&A item `relatedEntrypointIds` 内的命中：13

这些 13 条并不全部等价于必须 WARN。代表性命中包括：

- `ringcentral.video.toolbar.chat` alias `Chat`/`chat` 类词出现在“能否读聊天内容/meeting messages”的隐私边界 Q&A 中。
- `ringcentral.video.toolbar.participants` alias `Participants`/participant 类词出现在“能否读 participant names”和 host controls Q&A 中。
- `ringcentral.video.more.recording` alias `recording` 类词出现在 post-meeting recordings Q&A 中。
- `ringcentral.video.more.notes` alias `transcript` 类词出现在 live transcription/post-meeting transcript Q&A 中。
- 另有 audio/network/invite 等语义相邻命中，其中一部分是同域相关、低风险或应由 Q&A exact/fragment 覆盖的提示。

结论：朴素“任意 unsafe 子串即 WARN”会把当前 RingCentral 健康包变成多条 warning，噪声过高，也会与 Cycle 058 已接受的 alias 风险边界发生冲突。

## Risk List

- **High: 朴素 substring WARN 会误伤健康 RingCentral 包。** 当前 RingCentral 包已有 41 条 alias-in-Q&A 子串命中，其中 13 条按 `relatedEntrypointIds` 会被标成 unsafe。若直接 WARN，doctor 会从现有 OK 变成 noisy，并让新增诊断看起来像 package regression。
- **High: 隐私/安全 Q&A 与入口词天然共享词根。** Chat、Participants、recording、transcript、screen share 等隐私/安全 Q&A 必然包含对应功能名。仅凭子串关系无法区分“危险遮蔽”与“Q&A 正在描述该功能的安全边界”。
- **Medium: 与 exact overlap 检查重复或语义冲突。** 现有 `qa alias overlap` 已处理 exact prompt equals alias。新增 substring 检查若不排除 exact match，会重复报同一风险；若 detail 文案也使用 “shadows” 语义，用户会难以区分 exact collision 与 weaker substring signal。
- **Medium: `relatedEntrypointIds` 缺失会放大误报。** RingCentral 若干安全 Q&A 没有关联 entrypoint，原因可能是 answer-only 边界说明，而不是包漏配。把“alias entrypoint not related”直接当作 unsafe 会把 answer-only 安全说明全部推向 warning。
- **Medium: 短 alias 和多语言 prompt 容易制造跨语义命中。** 中文、日文短词如 audio、chat、participant、recording、transcript 的本地化词很短，常出现在更长 Q&A 中。substring 检查需要最小长度、语言、风险词上下文等降噪条件。
- **Low: Info 过多也会稀释 doctor 输出。** 即使降级为 INFO，如果每个包输出几十条 detail，也会遮蔽真正需要修复的 duplicate/exact overlap warning。

## Mitigations

- 将新增检查命名为独立诊断，例如 `qa alias substring risk`，不要复用 `qa alias overlap`，以免与 exact collision 混淆。
- exact match 继续只由 `qa alias overlap` 负责；substring 检查必须排除 `alias.normalized_alias == candidate.normalized_question`。
- 默认 severity 建议为 `INFO`，且仅汇总计数和首个代表样例；不要让当前 RingCentral 包因为该弱信号产生 `WARN`。
- 若要产生 `WARN`，建议必须同时满足更强条件：
  - Q&A prompt 属于 privacy/security/action-risk 上下文，如 read names/messages/content、recording、transcript、post-meeting artifacts、host controls、mute/remove/lock 等。
  - alias 明显短且容易截走 answer-only prompt，或 alias entrypoint 可执行动作可能改变会议状态。
  - Q&A item 没有关联该 entrypoint，且该 prompt 不是已知健康包的安全边界说明。
- 对 RingCentral 当前命中应优先作为 `INFO` 或 debug-style summary：提示维护者“这些 alias 出现在安全 Q&A prompt 中，请用 runtime regression 覆盖”，而不是断言包有错误。
- 输出应聚合，避免一条 collision 一个 check。建议格式类似：`N alias substrings appear in privacy/security Q&A prompts; review first: '<alias>' in '<prompt>' maps to <entrypoint>`。
- 可以按 Q&A item 去重，而不是按 alias/prompt pair 全量报出。RingCentral 当前 41 个 pair 如果直接展开会太吵。
- detail 中明确说明“不改变 runtime matching”，并建议补 runtime regression，而不是暗示 doctor 已证明 runtime 会误路由。

## Must Verify

- `pytest tests/unit/test_diagnostics.py -k "question_aliases or qa_alias_overlap or substring"`。
- 当前 RingCentral 包的既有健康断言必须继续成立：
  - `question aliases` 仍为 OK，计数仍为 62。
  - `qa questions` 仍为 OK，计数仍为 71。
  - `qa alias overlap` 仍为 OK，计数仍为 71。
- 新增 substring diagnostics 若接入 `diagnose_configuration()`，必须新增 RingCentral fixture 断言：当前包不能产生 `WARN`，最多产生聚合 `INFO`。
- 必须覆盖 exact 与 substring 的边界：
  - Q&A prompt exactly equals alias 且不相关：仍由 `qa alias overlap` WARN。
  - Q&A prompt contains alias as proper substring：不触发 exact overlap；按新规则 INFO 或条件性 WARN。
  - Q&A prompt contains alias and Q&A `relatedEntrypointIds` includes alias entrypoint：应 OK 或低噪声 INFO，不应 WARN。
- 必须覆盖聚合行为：多个 substring 命中只产生一个诊断 check，detail 带计数和首个样例，不逐条刷屏。
- 必须验证 `format_diagnostic_report()` 统计不把 INFO 当 WARN/FAIL；如果当前 status 类型只有 `OK/WARN/FAIL`，则需要先决定是否引入 INFO，或把弱信号留在 OK detail/独立可选 verbose 输出中。

## Recommendation

建议推进，但不要以朴素 substring WARN 形态推进。

更安全的推进方式是先做聚合型弱信号：保留 exact overlap 的 WARN 语义，新增 substring 检查只作为 INFO 或非失败性 summary，用来提醒维护者为隐私/安全 prompt 加 runtime regression。当前 RingCentral 包已经包含真实的 chat/participants/recording/transcript 安全边界 Q&A；这些命中说明“值得审查”，但不足以证明包不健康。

若当前 diagnostics 状态模型暂不支持 INFO，不建议用 WARN 承载该候选功能。可以先补内部 helper 和单测，或将结果折叠为 OK check detail，等 INFO 状态设计明确后再暴露到 doctor。

## Files Changed

- `docs/agent-handoffs/cycle-059-risk-scan.md`
