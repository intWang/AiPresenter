# Cycle 173 技术扫描

日期：2026-05-17

## 扫描范围

- `src/ai_presenter/runtime`
- `src/ai_presenter/cli.py`
- `tests/unit`
- `docs/knowledge/ringcentral-video`

Cycle 172 提交 `a7d1c81` 已把 meeting-info 的隐私 routing 固定到 `src/ai_presenter/runtime/questions.py` 和 `tests/unit/test_questions.py`。本轮扫描没有修改源码、测试、YAML 或 `.coverage`；工作树中已有 `.coverage` 改动，应继续视为他人/既有改动。

## 首选改进点：抽出 CLI 语音资产探测缓存

优先级：P1，小步可实现。

`PresenterController` 里已经有 `_ControllerVoiceReadinessCache`，会按规范化后的 `(language, tone)` 缓存 voice readiness，并有单元测试覆盖别名复用、切回复用、refresh 失效、`None` 结果缓存。CLI 侧仍直接调用 `check_voice_asset_availability(...)`：

- `src/ai_presenter/cli.py` 的 `voices` 命令在传入 `--profile` 时会遍历全部 presenter languages，并为每个 supported voice 调一次资产检查。
- 同一命令在指定 `--language/--tone` 时还会再对 selected voice 调一次资产检查。
- `src/ai_presenter/runtime/diagnostics.py` 的 `_diagnose_voice_assets(...)` 也直接调用资产检查。
- `src/ai_presenter/runtime/voice_assets.py` 的 SAPI 检查会调用 `list_installed_sapi_voices()`，Piper 检查会解析本地模型和模块可用性；这些调用比纯字符串校验更适合缓存。

小步方案：在 `runtime.voice_assets` 增加一个轻量缓存类或函数包装，例如 `VoiceAssetAvailabilityCache`。

建议行为：

- 以 `(profile.id, profile.providers.speech, normalized_language, normalized_tone)` 为缓存 key，或如果只在单个 profile 命令作用域内使用，则以 `(voice.language, voice.tone)` 为 key。
- 缓存 `VoiceAssetAvailability | None`，不要只缓存 OK/FAIL，避免 fake/openai 路由重复走检查。
- 保留现有 `check_voice_asset_availability(...)` 函数作为无状态 API，新增缓存包装供 CLI 使用，降低兼容风险。
- 在 `cli.voices(...)` 内创建一次命令级缓存；语言循环和 selected voice 复用同一个缓存。
- 可选第二步：`diagnostics.diagnose_configuration(...)` 仍保持单次检查；如果后续 doctor 扩展为多 voice 诊断，再复用同一个缓存类。

## 涉及文件

实现文件：

- `src/ai_presenter/runtime/voice_assets.py`：新增缓存类或命令级 helper。
- `src/ai_presenter/cli.py`：`voices` 命令使用缓存对象，避免同一 profile/voice 重复资产探测。

候选测试：

- `tests/unit/test_voice_assets.py`：新增缓存单元测试，覆盖同一 canonical voice 只调用一次 checker，`None` 结果也缓存，不同 tone/language 分开缓存。
- `tests/unit/test_cli.py`：新增或扩展 `voices` 命令测试，让 monkeypatch 的 `check_voice_asset_availability` 记录调用；执行 `voices --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` 时，profile language 列表里的 Chinese / Professional 与 selected Chinese / Friendly 是否应分开取决于 key 设计。如果按 language+tone 缓存，两者不同；如果按资产 route 缓存，则两者可复用同一 SAPI listing。建议本轮先按 voice key，实现保守。
- `tests/unit/test_controller.py`：无需改动，但可作为缓存行为测试风格参考。

验证命令：

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_voice_assets.py tests\unit\test_cli.py::test_voices_profile_reports_local_asset_status tests\unit\test_cli.py::test_voices_targeted_missing_assets_exits_nonzero
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\runtime\voice_assets.py src\ai_presenter\cli.py tests\unit\test_voice_assets.py tests\unit\test_cli.py
git diff --check
```

## 风险与边界

- 不要把缓存做成进程级永久状态。SAPI 声音、Piper 模型文件、环境状态可能在长会话中变化；本轮建议只做命令级或对象级缓存。
- `voice_assets` 当前支持依赖注入 `sapi_voice_lister`、`piper_asset_resolver`、`piper_module_checker`。缓存包装也应保留这些注入点，否则测试会变脆。
- 如果 key 只按 language/tone，SAPI/Piper 的底层资产枚举仍可能在 English 和 Chinese 两个不同 voice 间重复。更激进的 route-level 缓存收益更大，但要更仔细处理不同 voice 对同一路由的不同需求。本轮不建议一步做大。
- 不要改变 `validate_profile_voice(...)` 的错误边界；缓存只负责资产探测，不负责语言/语气支持判定。
- 不要触碰 RingCentral Video YAML、question routing 或 `runtime-safety-routing.md` 的 safety 规则。Cycle172 刚锁定 meeting-info 隐私 routing，本轮性能缓存不需要进入该高敏区域。

## 备选改进点

1. Controller 问题体验：`submit_question()` 里若 running app 未 scan，会把提示写入 chat 和 status。可以把提示文案通过 view model 统一，但这会触碰 UI/controller 行为，风险略高于缓存。
2. 语言/语气边界：`runtime-safety-routing.md` 已明确 tone 是 style-only，`tests/unit/test_questions.py` 已有敏感 prompt tone-invariant 哨兵。继续扩展边界测试有价值，但 Cycle172 刚做隐私 routing，容易引入回归压力。
3. RingCentralVideo 知识资料包导航：`source-index.md`、`evidence-index.md`、`runtime-safety-routing.md` 的互链已较完整；可以新增“快速入口”小节，但这是文档体验，不如缓存改进有直接运行时收益。

## 推荐 Cycle173 切片

首选切片：新增 `VoiceAssetAvailabilityCache`，只在 `ai-presenter voices` 命令内使用，保留现有无状态检查函数和所有 provider 注入点。

完成标准：

- 同一 CLI invocation 内重复请求同一 canonical voice 不重复调用底层资产检查。
- `None`、OK、FAIL 三类结果都能缓存。
- 现有 `voices` 输出不变。
- 不修改 RingCentral package YAML、question routing 或 knowledge safety docs。
