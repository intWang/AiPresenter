# Cycle 146 Experience: validation-targets Source Traceability

Date: 2026-05-17
Cycle: 146
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## 本轮主题和用户价值

本轮主题是守护 `validation-targets` 的 source traceability：CLI list/detail
和 renderer 输出都要继续显示 checklist 与 evidence index 的来源路径：

- `docs/knowledge/ringcentral-video/validation-checklist-index.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`

用户价值是让操作者能从 planning list 反查目标、证据等级、主缺口和下一步手工验证材料来自哪里，同时不把这些路径误读成 live RingCentral acceptance proof。路径让输出可审计；真正的接受证据仍然只能来自带日期、环境、动作、结果、恢复和隐私说明的 acceptance run 记录。

本轮最终落点是 test-only guard。生产 renderer 已经输出共享 header：
`Package:`、`Checklist:`、`Evidence:` 和
`Note: repo-derived planning list only; not live acceptance evidence.`。实现任务只需要把这个契约固定在 CLI list/detail 与 renderer 单元测试里。

## 子代理衔接

本轮衔接链路比较顺：

- demand analysis 先限定用户价值和最小范围：守住 source path 可追溯，不改 package、profile、runtime、acceptance run 或 `.coverage`。
- technical scan 读取当前 renderer/CLI 行为，判断生产实现已经满足路径输出，缺口主要是测试没有同时 pin 住 `Checklist:` 与 `Evidence:`。
- risk scan 把语言边界讲清楚：source path 是 traceability pointer，不是 proof；checklist/evidence index/draft command 都不能升级成 Accepted claim。
- implementation 按扫描建议做 test-only guard，并用临时破坏 renderer `Evidence:` 输出的方式验证红灯，然后恢复生产实现。
- review 发现路径断言硬编码了 Windows 反斜杠，指出应使用 `Path(...)` 生成期望值或只断言 label/file name。
- rereview 确认 P2 已关闭：测试改为通过 `Path("docs/knowledge/...")` 派生显示路径，且 `src/ai_presenter/acceptance/validation_targets.py` 最终无 diff。

这个链路的关键经验是：需求与风险文档先把边界讲窄，技术扫描再确认是否真的需要改生产代码，review 用跨平台视角检查测试契约是否可移植。

## 经验规则

- `traceability path` 是指针，不是 proof。`validation-checklist-index.md` 指向验证 procedure；`evidence-index.md` 指向证据等级导航和摘要。它们帮助定位材料，但不证明当前 RingCentral build 已经 live accepted。
- `acceptance-draft` 不是 acceptance evidence。它只是生成未来人工记录的草稿命令；不能因为 detail 输出里有 draft command，就暗示 route 已运行、已通过或当前可安全执行。
- CLI/renderer 测试可以守护路径可见性，但必须继续守护非证据 note。只断言文件名出现不够；应确保输出附近仍有 `repo-derived planning list only; not live acceptance evidence` 这类边界语义。
- 跨平台路径断言要用 `Path` 生成。不要硬编码 `docs\knowledge\...` 这类 Windows 分隔符；优先用 `str(Path("docs/knowledge/..."))` 或断言 `Checklist:`/`Evidence:` label 加文件名。
- TDD 临时破坏生产实现后，必须恢复并确认无 `src` diff。红灯可以通过临时改 renderer label、路径或 fallback 验证测试有效性，但最终必须运行 `git diff -- src\ai_presenter\acceptance\validation_targets.py` 并确认无输出。
- `.coverage` 是易被并行测试污染的 artifact。经验/交接任务不要 stage、revert、normalize 或覆盖它；提交时只纳入有意修改的文档、源码或测试文件。

## 下轮建议

优先选择一个具体、窄、可测试的小守护：

1. `acceptance-draft` draft-only boundary。为成功生成草稿的路径补一个 focused guard，断言输出继续包含 draft-only / not acceptance evidence 语义，并且不出现 `accepted`、`passed`、`live validated` 这类结论性措辞。价值是防止 draft helper 被误读为执行结果。
2. `validation-targets` none-evidence fallback。为 `render_validation_target_lines(...)` 构造 `evidence_text=None`、`evidence_path=None` 的 catalog，断言 header 显示 `Evidence: none`，同时目标 evidence level 保持 `unknown` 或等价的非证明状态。价值是守住没有 evidence source 时的显式降级，而不是静默省略 header。

推荐优先级：如果下轮继续围绕 acceptance 边界，选 `acceptance-draft` draft-only boundary；如果下轮继续围绕 renderer 纯输出契约，选 `validation-targets` none-evidence fallback。两者都不需要 live RingCentral、package YAML、runtime/provider 或 acceptance run 修改。

## 验证/提交注意

完整提交前建议跑：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src tests
git diff --check
git status --short
```

本类 docs-only 经验沉淀至少跑当前文件的尾随空白和 diff check：

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-146-experience.md
git diff --check -- docs\agent-handoffs\cycle-146-experience.md
```

提交或 staging 时不要纳入 `.coverage`。如果曾做 TDD 红灯临时破坏生产实现，还要额外确认：

```powershell
git diff -- src\ai_presenter\acceptance\validation_targets.py
```
