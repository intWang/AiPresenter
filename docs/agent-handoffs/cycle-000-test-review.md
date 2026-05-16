# Cycle 000 Test Review

日期：2026-05-16（Asia/Shanghai）

角色：第 0 周期测试 review subagent  
写入范围：仅本文件；业务代码未修改。

## 1. 已运行测试和检查

说明：`pyproject.toml` 默认 `pytest` 配置带 `pytest-cov`、`term-missing` 和 `--cov-fail-under=80`。本轮受“除 handoff 外不写文件”的约束，未运行会生成仓库覆盖率文件的 coverage 模式；改用禁用 pytest cache/bytecode 的只读式测试命令，并记录覆盖盲区。

| 命令 | 结果 | 关键输出摘要 |
| --- | --- | --- |
| `$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests` | 通过 | `354 passed, 1 warning in 11.20s`；warning 来自 `pywinauto`: `Revert to STA COM threading mode` |
| `.\.venv\Scripts\python -m ruff check --no-cache .` | 通过 | `All checks passed!` |
| `.\.venv\Scripts\python -m mypy --no-incremental src tests` | 通过 | `Success: no issues found in 70 source files` |
| `.\.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run` | 通过 | `Loaded profile: ringcentral-video`; `Dry run complete.` |
| `.\.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run` | 通过 | profile/package/flow 均加载成功；`Dry run complete.` |
| `.\.venv\Scripts\ai-presenter controller --profile ringcentral-video --package ringcentral-video --flow meeting-control-map-demo --dry-run` | 通过 | profile/package/flow 均加载成功；`Controller dry run complete.` |
| `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` | 通过 | `8 ok, 0 warnings, 0 failed`；自动发现 RingCentralDevelop `config.ini`，且 `DisableAffinityMask=true` |
| 从 `$env:TEMP` 运行 `<repo>\.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run` | 通过 | 证明 profile id 可从非 repo 工作目录解析 |
| `.\.venv\Scripts\ai-presenter run --profile profiles\ringcentral-video-openai.example.yaml --dry-run` | 通过 | OpenAI 示例 profile 可加载；未调用真实 OpenAI |
| `.\.venv\Scripts\ai-presenter flows --package ringcentral-video` | 通过 | 列出 4 个 flow：`vbg-blur-demo`, `meeting-basics-demo`, `meeting-controls-tour`, `meeting-control-map-demo` |
| `.\.venv\Scripts\ai-presenter entrypoints --package ringcentral-video --area "Meeting toolbar"` | 通过 | 列出 13 个 Meeting toolbar entrypoints |

测试规模：`tests/unit` 有 29 个测试文件、298 个测试函数；`tests/integration` 有 2 个测试文件、34 个测试函数。参数化后本次 pytest 共执行 354 个 case。

## 2. 当前测试覆盖能力地图

- 配置和 CLI：profile/package 路径解析、dry-run、doctor、flows、entrypoints、OpenAI profile 环境校验、RingCentral `DisableAffinityMask` 诊断。
- Provider 层：fake/OpenAI/Codex CLI/Piper/Windows SAPI provider 注册、输入校验、OpenAI prompt/response contract、Piper 命令构造、Windows SAPI WAV 输出路径；大多使用 fake client 或 fake runner。
- 音频输出：WAV 解码、speaker/virtual mic/both 路由、PortAudio 错误包装、单路失败继续和双路失败抛错；真实设备未播放。
- RingCentral 状态识别：UI 文本解析 mic/camera/participant/dialog/warning，process/window class 绑定判断，低置信度抑制，prejoin dialog 误报防护。
- Presenter loop：事件检测、状态合并、冷却/去重、空 narration/speech/media output 失败时不提交状态，observation sources 传递。
- Windows desktop driver：focus、wait for window、capture bounds、visible windows/controls、stale UI 控件容错、依赖缺失报错；全部由 fake 控件和 monkeypatch 驱动。
- Material package 和同步 demo：`packages/ringcentral-video.yaml` schema、entrypoint 唯一性、flow 引用合法性、open step 支持范围、cleanup、audio/action placement、manual directive skip/focus/say。
- Controller/session/questions：线程状态、start/pause/end、running app scan 状态、safe question interrupt、risky question text-only、chat history formatting、English/Chinese voice settings。
- 语言/语气：Chinese localized narration 选择、concise 取首句、conversational 前缀、SAPI rate 映射、Piper profile 中文 fallback 到 Windows SAPI。

RingCentral 资料包当前结构：`ringcentral-video` 支持 5 个 profile、27 个 operation entrypoints、4 个 demo flows、3 条 QA、21 个 explainer 节点覆盖 27/27 entrypoints。只有 `meeting-control-map-demo` 的 22/22 steps 具备 `localizedText.zh`；另外 3 个 flows 的中文本地化为 0。

## 3. 主要测试缺口

### UI

- Tk controller 真实 UI 没有自动化 smoke：当前 dry-run 不打开 `root.mainloop()`，unit tests 只覆盖 `PresenterController`、`ControllerSession` 和部分状态函数，没有验证 widget 创建、菜单回调、按钮布局、文本框追加、Return 键提交、状态刷新和错误展示。
- 没有截图或视觉布局检查：`720x500` 固定尺寸下，长 package/app/window label、中文回答、多轮 chat history 是否溢出只能靠人工看。
- 没有真实用户路径级 UI 测试：Start/Pause/Resume/End、切换 Running desktop app、Refresh/Scan、语言/语气切换、Submit 问题目前没有通过 UI 事件驱动串起来。

### 性能

- 没有性能预算或回归基线：`WindowsDesktopDriver.list_visible_controls`、UIA tree walk、RingCentral adapter 文本解析、22-step synchronized flow、controller 500ms refresh loop 都没有 duration 断言。
- 当前并发测试依赖少量 `time.sleep(0.05)` 和 `Event.wait(timeout=1)`，能测正确性，但不能发现 “能跑但明显卡顿”。
- 没有长会话资源测试：线程结束、音频 sink stop、controller 多次 start/end、Piper/OpenAI 慢响应、RingCentral capture 失败重试是否泄漏没有覆盖。

### 语言/语气

- 语言质量仍是结构性断言：测试会检查中文存在、不是空串、不是固定前缀，但不会判断是否自然、是否像翻译腔、是否符合 `soul.md` 的“conversational and prepared”目标。
- 语气差异断言偏浅：professional/conversational/concise 主要通过前缀、首句截断和 SAPI rate 间接体现；没有 golden 样例验证同一问题在不同 tone 下的具体表达边界。
- 中文覆盖不完整：只有 `meeting-control-map-demo` 全量中文，`vbg-blur-demo`、`meeting-basics-demo`、`meeting-controls-tour` 没有 zh localized narration。
- OpenAI narration/speech 的真实端到端语气没有自动验收；当前覆盖主要是 fake client contract，不证明真实模型输出、TTS 音色、语速和中文可懂度。

### RingCentralVideo 自动化资料包

- Package schema 和 flow 顺序覆盖强，但缺少产品漂移检测：没有把真实 RingCentral UIA text/control snapshots 固化成 fixtures，无法提前发现按钮 label、menu item、window class、control type 改名。
- `openSteps` 可执行性是 fake desktop 级别验证，未对真实 RingCentral 窗口确认 “More -> Notes -> cleanup side panel” 等复合路径。
- 高风险动作只能解释不能点击的策略有部分测试（recording/leave），但 share final chooser、start/stop recording、leave confirmation、chat/private content 不泄露等仍主要靠手动验收。
- QA 只有 3 条，无法覆盖资料包 27 个 entrypoints 的自然问法、中文问法、模糊问法和风险边界。

## 4. 下一轮实现前最应该补的 5 个测试

1. `tests/unit/test_controller_ui.py`  
   意图：在 fake `tkinter` 或抽出的 controller view factory 上做 UI wiring smoke，验证 Target/Voice/Question/Chat widgets 创建，Start/Pause/End/Refresh/Scan/Submit 回调能正确更新 status、chat history、voice settings 和 controller/session 调用。

2. `tests/integration/test_controller_acceptance_flow.py`  
   意图：用 fake desktop + fake runner 串起 runbook 的 controller 验收路径：Material package mode start/pause/resume/end；切到 Running desktop app、refresh、scan、start；问 `chat` 触发 safe demo；问 risky control 保持 text-only；切中文和 conversational tone 后回答进入对应语言/语气。

3. `tests/integration/test_ringcentral_observation_fixtures.py` 配套 `tests/fixtures/ringcentral/*.json`  
   意图：从真实 RingCentralVideo 采集脱敏 UI text/control snapshots，回放 prejoin、in-meeting、More menu、Chat/Participants side panel、connection warning、permission dialog 等场景，验证 adapter、entrypoint target 和 cleanup 不随产品文案小改动失效。

4. `tests/unit/test_language_tone_quality.py`  
   意图：建立小型 golden corpus，覆盖 English/Chinese + professional/conversational/concise；断言中文不含机械翻译残留、concise 不丢安全边界、conversational 不变得啰嗦，且所有 RingCentral demo flow 要么提供 zh localized text、要么显式标记暂不支持。

5. `tests/performance/test_runtime_budgets.py`  
   意图：用 synthetic large UI tree 和 fake media/provider 设置预算，例如 adapter 解析、visible control filtering、22-step timeline dry run、controller scan/package generation应在固定阈值内完成；同时加 repeated start/end 或 repeated question interrupt 的线程收敛断言。

## 5. 不可自动化风险和手动验收策略

- 真实 RingCentralVideo/Windows UI：自动测试无法可靠保证焦点、权限弹窗、UIA accessibility tree、DPI、多显示器、窗口遮挡、RingCentral 版本差异。手动验收按 `docs/runbooks/ringcentral-manual-acceptance.md` 的 Smoke Checklist 执行，重点记录：Video tab 被选中、Start 被点击、绑定 `RingCentralVideoClass`、只有 in-meeting 控件可见后才认为 joined、mic/camera/participants 只触发一条 narration。
- 高风险会议动作：录制、离开、最终共享、读取聊天或参会者隐私内容不能让自动化无确认执行。手动验收时只验证入口说明、弹窗出现和 cleanup，不点击最终确认；检查日志和屏幕录制证明没有越权动作。
- 音频设备：virtual mic 和 speaker 依赖 VB-CABLE/VoiceMeeter、Windows 默认设备、PortAudio、采样率和 RingCentral 输入选择。手动验收需要同时确认本地 speaker 可听、RingCentral 接收到 virtual mic、失败时日志指出具体 sink。
- OpenAI/Piper/Windows SAPI：真实模型、TTS 音色、语速、中文自然度和 API/key/成本无法由 fake tests 证明。手动验收使用 OpenAI profile 和 Piper profile 各跑一次短句与一次 1-iteration demo，保留模型/env、输出设备和听感记录。
- 性能和稳定性：30 秒 bind timeout、500ms controller refresh、长会议期间观察循环和音频播放容易受机器状态影响。手动验收建议跑一段 10-15 分钟控制器会话，观察 CPU、线程结束、日志增长、窗口焦点恢复和 narration 是否重复/漏报。
