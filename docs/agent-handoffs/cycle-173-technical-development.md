# Cycle 173 Technical Development: voices 资产检查命令级缓存

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle173 technical-development handoff subagent

## 目标

本轮技术开发目标是做一个性能小切口：降低 `ai-presenter voices --profile ... --language ... --tone ...` 在同一次命令执行中对同一路由语音资产的重复检查。

具体问题是：`voices` 命令先打印 profile 支持的语音列表，再打印 selected voice 的兼容性和资产状态。当 selected voice 解析到的实际 speech route 已经在 profile 列表阶段检查过时，原逻辑仍会再次调用 `check_voice_asset_availability(...)`。对本地 SAPI / Piper / OpenAI 等 provider 资产探测来说，这类重复检查会增加 CLI 延迟，也可能重复触发较重的环境探测。

本 handoff subagent 只读了当前 diff、相关 `src/ai_presenter/cli.py` 与 `tests/unit/test_cli.py` 片段，并只写入本文件：

- `docs/agent-handoffs/cycle-173-technical-development.md`

未修改源码、测试、YAML、`.coverage`，未 stage、commit，也未回滚任何并发工作区改动。

## 改动

主会话当前 diff 中观察到的代码改动：

- `src/ai_presenter/cli.py`
  - 新增 `VoiceAssetAvailabilityCache`。
  - 缓存 key 为 `(profile.id, profile.providers.speech, route)`，其中 `route` 来自 `resolve_speech_provider_name(profile, voice)`。
  - `voices(...)` 命令内创建一个命令级 `asset_cache`。
  - profile 列表阶段和 selected voice 阶段都通过 `asset_cache.get(loaded_profile, voice)` 读取资产检查结果。

- `tests/unit/test_cli.py`
  - 新增 `test_voices_reuses_profile_asset_checks_for_selected_route`。
  - 测试 monkeypatch `ai_presenter.cli.check_voice_asset_availability` 记录调用的 `(language, tone)`。
  - 执行 `voices --profile ringcentral-video-bind-speaker --language en-US --tone friendly`。
  - 断言 selected friendly voice 没有额外触发资产检查，调用列表保持为 profile 列表阶段的 `("en", "professional")` 和 `("zh", "professional")`。

当前工作区另有 `.coverage` 已修改，以及 Cycle173 其他 handoff 文档未跟踪；本 subagent 没有触碰这些文件。

## TDD 证据

主会话报告的 TDD 证据：

- RED：新增测试最初失败，`calls` 多出 selected voice 对应的 `("en", "friendly")`，证明 selected 阶段确实重复执行了资产检查。
- GREEN：实现命令级缓存后，相关 `voices` 4 tests passed。
- 宽 focused：14 passed，包含 Cycle172 routing sentinels。

本 handoff subagent 没有重跑 pytest。原因是用户明确要求只读当前 diff / 相关源码测试并只写 handoff 文档；重跑测试可能改写 `.coverage`，超出本次边界。

## 实现要点

`VoiceAssetAvailabilityCache` 是一个很小的命令级缓存对象，不是全局缓存：

- 生命周期限定在一次 `voices(...)` 调用内。
- 缓存值保存 `check_voice_asset_availability(profile, voice)` 的返回结果，包括 `None`、`OK`、`WARN`、`FAIL` 等结果形态。
- key 使用 profile id、配置的 speech provider、实际 resolved route，而不是直接使用 selected voice 的 language/tone。

选择 route 作为 key 的关键点在于：不同输入 voice 可能解析到同一个实际 speech route。例如 `ringcentral-video-bind-speaker` 下，`en-US/friendly` selected voice 与 profile 列表阶段默认 English / Professional 都可能走 `windows-sapi-en`。缓存按 route 复用后，selected 阶段能复用列表阶段已经完成的资产检查。

实现仍保留 selected voice 自己的 `validate_profile_voice(...)` 和 `resolve_speech_provider_name(...)` 输出，因此命令输出的兼容性判断和 route 文案没有被绕过；只复用较重的资产可用性检查结果。

## 为什么只接入 voices

本次只接入 `ai-presenter voices`，是因为重复调用发生在这个命令的单次控制流内：同一个 loaded profile 先枚举支持语言，再检查 selected voice。缓存的收益明确、作用域小，且测试可以稳定证明 selected route 的重复资产检查被消除。

其他 CLI 命令没有同样的“先枚举再检查同一路由 selected voice”的结构：

- `demo` / `controller` 主要做运行前 voice validation，不直接做资产 availability preflight。
- `doctor` 的资产检查属于 diagnostics 聚合逻辑，职责在 `ai_presenter.runtime.diagnostics`，不适合从 CLI 层强行塞入 `voices` 专用缓存。
- `localization-report`、`validation-targets`、`acceptance-draft` 等命令有惰性导入与无 provider 加载边界，不能为了一个局部性能优化扩大 provider 资产检查耦合。

因此本轮把优化限制在 `voices` 命令内部，避免把命令级状态扩散到共享 runtime 或其它 CLI path。

## 不改无状态 API

本轮没有修改 `check_voice_asset_availability(...)` 的无状态 API，也没有在 `runtime.voice_assets` 中加入全局缓存。

原因：

- 资产可用性可能依赖当前机器、环境变量、已安装语音、provider 配置和文件系统状态。全局缓存容易跨命令、跨测试或跨配置污染结果。
- 无状态函数便于测试 monkeypatch，也符合现有 CLI 惰性导入边界。
- 这次性能问题只在同一次 `voices` 命令内出现，命令级缓存已经足够覆盖。
- 不改 runtime API 可以降低 blast radius，避免影响 `doctor` diagnostics、未来运行时 preflight 或其它调用方。

换句话说，缓存是 call-site optimization，不是 provider availability 模型的语义变更。

## 风险

- 缓存 key 目前使用 `(profile.id, profile.providers.speech, route)`。如果未来同一个 profile/provider/route 下资产检查还依赖 voice tone、具体 voice alias 或其它未进入 route 的参数，当前复用可能过宽。就当前实现观察，资产检查目标是 speech route 可用性，因此这个 key 与本轮测试意图一致。
- 缓存保存失败结果；同一次命令内如果外部环境在执行过程中发生变化，selected 阶段会复用列表阶段的旧结果。不过 CLI 单次执行窗口很短，这个风险可接受。
- `VoiceAssetAvailabilityCache.get(...)` 内部会再次 resolve route；调用方 selected 阶段也 resolve route 用于输出，因此存在轻量重复解析。但重复解析成本远低于资产探测，也能让 cache 自己保持 key 构造完整。
- 本轮没有跑 full suite；主会话报告了 targeted / focused 绿色，但集成前仍应由主会话或合并负责人做最终验证。

## 后续建议

- 合并前跑一次相关 CLI suite 或 full pytest，并确认 `.coverage` 不被误 stage。
- 如果未来发现 `doctor` 或 diagnostics 内也存在同一次报告中的重复资产检查，应在 diagnostics 层单独设计局部缓存，不要复用 `voices` 的 CLI helper。
- 如果 voice asset availability 开始依赖 tone、speaker name 或 provider-specific voice id，应同步收窄 cache key，并补充针对同 route 不同 voice metadata 的回归测试。
- 保持 `check_voice_asset_availability(...)` 无状态，除非后续有明确跨命令缓存需求、失效策略和测试隔离方案。
