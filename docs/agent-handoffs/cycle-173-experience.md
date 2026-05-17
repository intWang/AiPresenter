# Cycle 173 经验沉淀：性能缓存边界与后续优化候选

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle173 经验沉淀 subagent

## 范围与约束

本文件只沉淀 Cycle173 的经验，不修改源码、测试、YAML 或 `.coverage`，不 stage，不 commit。

本轮参考材料：

- `docs/agent-handoffs/cycle-173-demand-analysis.md`
- `docs/agent-handoffs/cycle-173-technical-scan.md`
- `docs/agent-handoffs/cycle-173-risk-scan.md`
- 当前工作区 diff：`src/ai_presenter/cli.py`、`tests/unit/test_cli.py`、`.coverage`

当前 diff 显示本轮实现集中在 CLI `voices` 命令的语音资产探测缓存：新增 `VoiceAssetAvailabilityCache`，在一次 `voices` invocation 内复用 profile voice 列表检查与 selected voice 检查的结果；测试新增 `test_voices_reuses_profile_asset_checks_for_selected_route`，确认 `--language en-US --tone friendly` 的 selected voice 不再重复触发底层资产检查，而是复用同一路由的 profile 检查结果。

## 本轮性能缓存经验

本轮最有价值的判断不是“缓存能让命令更快”，而是“缓存必须贴着已有行为的边界长出来”。语音资产探测可能访问 SAPI voice listing、Piper 模型文件、模块可用性等本地状态；这些检查比字符串匹配重，适合在短生命周期内复用。但它们同时依赖 profile、provider、voice route 和本地环境，不能被提升成不受约束的全局事实。

本轮选择把缓存放在 CLI `voices` 命令内，是一个低风险切片：

- 只影响一次命令调用中的重复资产检查。
- 保留 `check_voice_asset_availability(...)` 作为无状态 API。
- 不改变 profile voice 支持判断、输出文案、exit code 或 provider 注入点。
- 不触碰 question routing、RingCentral package YAML、doctor 诊断语义和 controller runtime 行为。

当前实现使用 `(profile.id, profile.providers.speech, route)` 作为 key，比单纯 `(language, tone)` 更接近真实成本来源：同一 speech provider 与 route 下，不同 voice settings 可能最终落到同一资产探测路径，因此 profile 列表和 selected voice 可以复用结果。这个选择比 route-level 以下的底层枚举缓存更保守，也比 language/tone 级缓存更有实际收益。

## 为什么缓存应保持 command-scoped

语音资产可用性不是长期稳定配置。SAPI voice、Piper 模型文件、环境变量、可导入模块、profile YAML 都可能在一个开发会话中变化。若缓存做成进程级或模块级状态，后续命令、测试或 UI 运行可能读到过期结果，表现为“明明安装/删除了资产，doctor 或 voices 仍旧报告旧状态”。

command-scoped 缓存的好处是边界清楚：

- 生命周期等于一次 CLI invocation，天然避免跨命令 stale state。
- 测试隔离简单，不需要全局 reset hook。
- 不会污染 controller 的 readiness cache，也不会让 doctor 的单次诊断带上 CLI 历史。
- 可以缓存 `None`、OK、FAIL 全量结果，而不是只缓存布尔状态，避免 fake/openai 或无资产检查路线重复探测。

后续如果要把缓存抽到 `runtime.voice_assets`，也应保持“显式创建、显式传入”的对象级缓存，而不是隐式全局单例。也就是说，缓存对象可以复用，缓存生命周期必须由调用方控制。

## 如何避免影响 routing / doctor / controller

本轮经验是：性能缓存必须和行为路由分层。语音资产检查属于 voice/profile 能力探测，不属于 RingCentralVideo question matching，也不属于 answer-only 安全策略。

保持 routing 安全的原则：

- 不改 `runtime/questions.py` 的 Q&A-first 顺序、安全 matcher、entrypoint alias scoring。
- 不把 `localizedTitles`、`localizedPurposes` 或展示文案纳入 matcher 候选。
- 不让缓存结果影响 `entrypoint_id`、`can_operate`、interrupt step 或 privacy answer 文案。
- 不因为“更快”而提前构建、共享或重排 package matcher 索引。

保持 doctor 安全的原则：

- `diagnose_configuration(...)` 目前仍应按诊断调用现场做检查，避免复用 CLI `voices` 历史结果。
- 若 doctor 未来扩展为多 voice 资产诊断，可以在 doctor invocation 内创建自己的短生命周期缓存。
- diagnostics count、QA alias overlap、localization completeness 等报告不应因语音资产缓存发生变化。

保持 controller 安全的原则：

- controller 已有 `_ControllerVoiceReadinessCache`，它服务运行时 voice readiness，不应和 CLI 缓存混用。
- CLI 缓存不应写入 controller state，也不应改变 `PresenterVoiceSettings`、profile selection 或 runtime voice switch 行为。
- 如果未来要统一缓存实现，应统一“接口形状”，不要统一“状态实例”；每个调用域仍保留自己的 cache owner。

## 本轮可复用的工程判断

性能优化优先选择可证明的重复路径，而不是先追 wall-clock。当前测试用 monkeypatch 记录底层 `check_voice_asset_availability` 调用次数，比固定毫秒阈值更稳定，也更能说明行为边界。

缓存 key 设计要从“成本来源”倒推，而不是从函数参数机械复制。本轮 key 包含 profile、speech provider 和 route，能解释为什么 selected voice 与 profile voice 列表可以复用，同时避免不同 profile 或 provider 串味。

保留无状态底层函数是降低风险的关键。缓存包装层只负责“是否复用”，不负责“如何判断资产可用”；这让现有测试、monkeypatch、provider 注入点和后续 doctor/controller 调用都能继续以原方式工作。

## 下一轮候选优化

1. 把 `VoiceAssetAvailabilityCache` 下沉到 `runtime.voice_assets`，但仍由 CLI/doctor/controller 各自显式创建实例。验收重点是缓存 `None`、OK、FAIL，保留所有依赖注入点，并证明现有 CLI 输出不变。

2. 为 CLI `voices` 增加更细的缓存测试：覆盖同 route 复用、不同 route 分离、不同 profile 分离、`None` 结果复用、FAIL 结果复用。不要使用 wall-clock 断言。

3. 若发现 SAPI/Piper 底层枚举仍重复，可考虑在一次资产检查批处理中复用更底层的 listing/resolver 结果。但这应是独立切片，因为 route-level 缓存和 provider-internal 缓存的失效边界不同。

4. 对 matcher 增加结构性诊断，而不是全局路由缓存。候选方向包括：短 token 风险、substring overlap、localized action/location 交叉风险、Q&A-first 顺序哨兵。避免把 matcher 优化与行为修正混在同一轮。

5. 对 RingCentralVideo 资料包做 repo-local 导航文档，而不是 active skill 或 runtime prompt。下一轮若沉淀资料包熟悉度，应继续区分 source evidence、repo tests、live acceptance 和 answer-only safety。

## 交接提醒

当前工作区不是干净状态，已有 `.coverage`、`src/ai_presenter/cli.py`、`tests/unit/test_cli.py` 改动，以及 Cycle173 handoff 文档。后续 agent 不要回滚这些改动，也不要把 `.coverage` 纳入提交。

若下一轮继续性能缓存，请优先验证：

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_profile_reports_local_asset_status tests\unit\test_cli.py::test_voices_reuses_profile_asset_checks_for_selected_route tests\unit\test_cli.py::test_voices_targeted_missing_assets_exits_nonzero
```

若下一轮触碰 routing、package 或 diagnostics，请先跑 Cycle173 risk scan 中列出的 focused route tests，并用 `git diff --check` 做收口检查。
