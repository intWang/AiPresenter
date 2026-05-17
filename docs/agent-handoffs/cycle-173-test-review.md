# Cycle 173 测试 Review：voices 资产可用性缓存

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle173 测试 review subagent

## 范围与边界

本次只审查当前 diff 中的 CLI voice asset cache 变更：

- `src/ai_presenter/cli.py`
- `tests/unit/test_cli.py`

按要求只写入本文档，未修改源码、测试、YAML 或 `.coverage`，未 stage/commit。开始 review 时工作区已有 `.coverage` dirty 以及其他 Cycle173 handoff 文档，已保持不触碰。

## Diff 摘要

`cli.py` 新增 `VoiceAssetAvailabilityCache`，并在 `voices` 命令中复用 profile catalog 阶段已经做过的资产检查结果。缓存 key 为：

```python
(profile.id, profile.providers.speech, route)
```

其中 `route` 来自 `resolve_speech_provider_name(profile, voice)`。`voices --profile ... --language ... --tone ...` 的 selected voice 检查会复用同 profile、同 speech provider、同最终 route 的 catalog 检查结果。

`test_cli.py` 新增 `test_voices_reuses_profile_asset_checks_for_selected_route`，用 monkeypatch 记录 asset checker 调用，证明 selected `en-US/friendly` 会复用 catalog 阶段 `en/professional` 的 `windows-sapi-en` route 检查，而不会再次调用 asset checker。

## 测试覆盖评价

覆盖是针对本次性能/重复检查优化的核心路径的：同一个 `voices` invocation 内，profile catalog 先检查默认 tone，再 selected voice 用不同 tone 但同 route 时复用结果。这个测试能防止 selected path 回退到重复探测本地 SAPI/Piper 资产。

现有 voices 测试组还保留了这些邻近行为：

- 无 profile 时只打印 catalog，不触发 profile/runtime voice 检查。
- profile catalog 会报告 supported/unsupported languages。
- 本地资产状态会显示在 profile catalog 中。
- selected incompatible voice 仍非零退出。
- selected missing assets 仍非零退出。

覆盖缺口不构成阻塞，但建议后续若继续改 cache，可以补一个更直接的“不同 route 不复用”单测，例如同一 profile 下 `en` 与 `zh` 分别检查 `windows-sapi-en` 和 `windows-sapi-zh`，并断言两次 checker 调用都保留。当前新增测试已经隐含这一点，因为 calls 是 `en` 和 `zh` 两次，但它的主断言重点在 selected `en/friendly` 不新增第三次调用。

## profile / route 缓存风险

我没有看到当前 diff 会造成错误 profile 或 route 串用的阻塞风险。

原因：

- cache 是 `voices()` 命令内的局部对象，每次 CLI invocation 新建，不会跨命令、跨测试、跨进程保留状态。
- key 包含 `profile.id`，避免同一进程内未来若复用 cache 时不同 profile 直接串用。
- key 包含 `profile.providers.speech` 与解析后的 `route`，能区分 `windows-sapi-zh` 配置下的英文 fallback route `windows-sapi-en` 与中文 route `windows-sapi-zh`。
- 当前 `check_voice_asset_availability()` 的行为本身只基于最终 route 选择 Zira、Huihui、any SAPI、Piper 或 none；tone 不影响资产可用性，所以 selected tone 复用 catalog 默认 tone 的 route-level 检查是合理的。

需要注意的非阻塞前提：如果未来 asset checker 开始依赖 profile 内更细粒度的资产配置，例如 profile-specific Piper voice path、per-language voice name 或 tone-specific voice asset，当前 key 就需要扩展。以现在代码看，`profile.id + speech + route` 足够。

## 对 doctor / controller 的影响

没有发现对 `doctor` 或 `controller` 的行为影响。

- `VoiceAssetAvailabilityCache` 只在 `voices()` 内实例化并调用。
- `doctor` 走 diagnostics 模块的 voice preflight / asset check，不经过这个 CLI cache。
- `controller` 使用自己的 `_ControllerVoiceReadinessCache`，key 是 canonical `voice.language` 与 `voice.tone`，本 diff 没改 controller runtime。

因此本次 cache 优化不会改变 doctor 的验证输出，也不会改变 controller 切换 voice 时的 readiness 缓存/刷新语义。

## 已知 focused 验证

主会话给出的 focused 验证结果：

- 4 voices tests passed
- 14 mixed focused tests passed

我本次 review 未重复运行测试，避免在并行工作区里刷新 `.coverage` 或 pytest cache。当前结论基于 diff 和相关实现只读审查。

## 建议最终验证命令

收口前建议主会话运行：

```powershell
git diff --check -- src/ai_presenter/cli.py tests/unit/test_cli.py docs/agent-handoffs/cycle-173-test-review.md
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_cli.py::test_voices_lists_language_tone_choices tests\unit\test_cli.py::test_voices_profile_reports_supported_and_unsupported_languages tests\unit\test_cli.py::test_voices_profile_reports_local_asset_status tests\unit\test_cli.py::test_voices_reuses_profile_asset_checks_for_selected_route tests\unit\test_cli.py::test_voices_targeted_missing_assets_exits_nonzero tests\unit\test_cli.py::test_doctor_accepts_language_and_tone_voice_preflight tests\unit\test_controller.py::test_controller_voice_readiness_cache_reuses_canonical_voice tests\unit\test_controller.py::test_controller_voice_readiness_cache_reuses_prior_voice_after_switching_back
```

最终合并前再跑完整套件，并确认不要把既有 dirty `.coverage` 纳入提交：

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
git status --short
git diff --cached --name-status
```

## 阻塞问题

未发现阻塞问题。

本次 diff 的行为边界清晰：只优化 `voices` 命令内的重复 asset probe；缓存生命周期局限在单次命令调用；当前 key 足以避免 profile/speech/route 串用；doctor/controller 不受影响。建议作为非阻塞增强补充一个“不同 route 不复用”的更显式断言，但不要求阻塞当前变更。
