# Cycle 145 Experience: validation-targets Evidence Boundary

Date: 2026-05-17
Cycle: 145
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## 本轮主题和用户价值

本轮主题是守护 `validation-targets` CLI 的证据边界：它可以帮助操作者从
RingCentral Video 的 checklist 和 evidence index 中选择下一步人工验证目标，
但不能被误读为 live RingCentral acceptance evidence。

用户价值在于降低后续代理和操作者的误判风险。`validation-targets` 输出的是
repo-derived planning list，`acceptance-draft` 输出的是未来手工记录的草稿命令；
二者都不执行 RingCentral 操作、不记录 acceptance run，也不证明当前 build 已被
RingCentral live 接受。把这个边界固定在 CLI 和 renderer 输出测试里，可以防止
后续重构把 planning、draft、Repo-tested、Observed 或 checklist 行误提升成
Accepted 证据。

## 子代理衔接方式

本轮衔接是一个窄范围、多阶段交接：

- demand analysis 先定义用户价值、最小实现面和 no-go 边界，明确不要改 package、
  profile、runtime、acceptance run 或 `.coverage`。
- technical scan 读取现有实现和测试，发现生产 renderer 已经有非证据 note，
  缺口在测试未 pin 住该 note。
- risk scan 约束风险语言，列出不可声称的 live acceptance、provider readiness、
  privacy 和 evidence-level 误读。
- implementation 按扫描建议做 test-only guard，并用临时破坏生产 note 的方式验证
  红灯，再恢复生产 note，确保最终没有 `src` diff。
- review 检查 diff 范围、断言覆盖面和证据措辞，结论为 no findings / go。

这种衔接方式的关键是：前置文档把“不要做什么”说清楚，技术扫描把“最小可测试点”
落到具体测试，实施只守住已存在行为，review 再从 evidence boundary 角度复核。

## 经验规则

- CLI planning output 不是 live acceptance evidence。即使输出 target、priority、
  checklist path、evidence level、validate/cleanup/privacy 字段，也只能说明
  planning source 可追踪，不能说明 RingCentral route 已执行或已通过。
- `acceptance-draft` command 不是 acceptance evidence。它只是准备
  `acceptance-runs.md` 手工记录模板的 helper；只有带日期、环境、动作、结果、恢复和
  隐私说明的实际 manual/live run 记录，才可能支持 Accepted claim。
- renderer output 不是 live acceptance evidence。即使 renderer 被 CLI 复用、输出
  统一 note，也只是 repo-derived 文本渲染，不是运行时 acceptance engine。
- TDD 红灯可以通过临时破坏生产 note 验证测试有效性，但必须恢复该破坏，并在最终状态
  确认没有 `src` diff。红灯记录要说明破坏点、失败测试和恢复动作，避免临时改动残留。
- 证据措辞要精确。优先使用 `repo-derived planning list only; not live acceptance
  evidence`、`draft only`、`template/helper` 等边界词，避免单独使用 `validated`、
  `verified`、`ready`、`safe` 这类容易被误读成 live acceptance 的词。
- `.coverage` 可能是并行代理或本地测试留下的 dirty artifact；本类经验/交接任务不要
  stage、revert、normalize 或覆盖它。

## 下轮建议

建议选择一个具体、窄、可测试的后续守护点：

1. 为 `validation-targets` 增加 source checklist / evidence path traceability
   守护。测试可断言 list/detail 输出继续包含
   `validation-checklist-index.md` 和 `evidence-index.md`，并且仍同时包含非证据 note。
   价值是让 planning list 的来源更可追踪，同时不把来源文件误当成证明。
2. 继续守护 `acceptance-draft` 的 draft-only 边界。测试可集中在
   `acceptance-draft` 成功模板输出和拒绝未知 target 的路径，断言输出包含 draft-only
   语义，且不出现 pass/accepted/current live evidence 之类结论性措辞。
3. 如果要扩展 renderer 覆盖，优先选一个 blocked target 或 unknown target 的输出
   边界，确认它们仍是 catalog/planning diagnostics，不提供 draft command，也不暗示
   可以执行 live route。

推荐优先级是第 1 项：source checklist / evidence path traceability。它和 Cycle 145
已有 guard 自然相邻，测试面小，可用现有 fixture 和 CLI runner 完成，不需要源码行为
变更。

## 验证/提交注意

提交前建议完整跑：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src tests
git diff --check
git status --short
```

如果只做 docs-only 经验沉淀，至少跑当前文档的尾随空白和 diff check：

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-145-experience.md
git diff --check -- docs\agent-handoffs\cycle-145-experience.md
```

提交或 staging 时只纳入本轮有意修改的文档和已确认的代码/测试文件；不要 stage
`.coverage`，也不要因为它 dirty 而 revert。
