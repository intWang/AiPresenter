# Cycle 148 Demand Analysis: Renderer-Level Acceptance Draft Boundary

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## 用户价值

Cycle147 已经把 `acceptance-draft` 的 CLI 成功路径守成 draft 起点，而不是 live acceptance evidence。本轮价值是把同一条边界下沉到 renderer-level unit tests：即使未来有人绕过 CLI 直接调用 `render_manual_acceptance_draft`，flow 和 mixed flow+entrypoint 输出也必须继续包含：

- `Draft only`
- `not acceptance evidence`
- `No live RingCentral action has been performed by this helper.`

这能防止 renderer 模板漂移成“看起来像已经验收”的记录，同时保留它作为人工验收前草稿的便利性：可以预填 package、flow、entrypoint、checklist、隐私提醒和待填写字段，但不能暗示已经执行 RingCentral live workflow、已经观察结果，或已经可写入 `acceptance-runs.md`。

## 最小范围

本轮实现优先 test-only，目标文件是 `tests/unit/test_acceptance_manual_record.py`。

建议增加一个本地 helper，例如 `assert_acceptance_draft_boundary(draft: str) -> None`，集中断言三条 renderer boundary 文案。然后把该 helper 接入至少这些成功路径：

- `test_manual_acceptance_draft_prefills_flow_steps`
- `test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps`

现有 entrypoint 成功路径 `test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance` 已经直接断言 boundary，可选择改用同一个 helper 以减少重复，但不要扩大行为变更范围。

如果实现者采用 TDD，可先临时破坏 `src/ai_presenter/acceptance/manual_record.py` 中任一 boundary 文案确认测试红灯，再恢复源码并确认 `src` 无残留 diff。

## 不碰范围

- 不改 `src/ai_presenter/acceptance/manual_record.py` 的生产逻辑，除非测试红灯证明当前 renderer 已经缺失要求文案。
- 不改 CLI 行为；Cycle147 已覆盖 CLI stdout/file output 成功路径。
- 不改 `acceptance-runs.md`，不创建或追加 live acceptance evidence。
- 不声明已执行 RingCentral live action，不声明 acceptance passed/accepted/validated。
- 不改 package YAML、runtime、locator/state/privacy/evidence matrix。
- 不改 `package`/依赖文件，不改 `.coverage`，不为了清理工作树 revert 他人改动。

## 验收标准

实现完成后应满足：

- `tests/unit/test_acceptance_manual_record.py` 的 flow renderer 输出受同一组 draft-only boundary 断言保护。
- mixed flow+entrypoint renderer 输出受同一组 draft-only boundary 断言保护。
- 断言明确覆盖 `Draft only`、`not acceptance evidence`、`No live RingCentral action has been performed by this helper.`。
- 合法模板字段不被误伤，例如 `acceptance`、`Pass/fail` 仍可存在；避免用过宽 negative regex。
- 本轮不产生 `src` diff，除非发现真实缺陷并按最小范围修复。
- 不修改 `.coverage`，不 stage `.coverage`。

建议 focused 验证：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
rg -n "[ \t]+$" docs\agent-handoffs\cycle-148-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-148-demand-analysis.md
git diff -- src\ai_presenter\acceptance\manual_record.py
git status --short
```

其中本需求分析子任务只需验证 handoff 文档本身：

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-148-demand-analysis.md
git diff --check -- docs\agent-handoffs\cycle-148-demand-analysis.md
```

## 实现 Handoff Prompt

你是 Cycle148 实现子任务。仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`。

目标：为 renderer-level acceptance draft boundary 增加 test-only 守护。Cycle147 已守护 CLI 成功路径；本轮要让 `tests/unit/test_acceptance_manual_record.py` 的 flow 和 mixed renderer 输出也统一守住 `Draft only` / `not acceptance evidence` / `No live RingCentral action has been performed by this helper.`，避免未来绕过 CLI 直接调用 renderer 时漂移。

请先阅读：

- `docs/agent-handoffs/cycle-147-experience.md`
- `docs/agent-handoffs/cycle-148-demand-analysis.md`
- `tests/unit/test_acceptance_manual_record.py`
- `src/ai_presenter/acceptance/manual_record.py`

实施边界：

- test-only 优先，主要修改 `tests/unit/test_acceptance_manual_record.py`。
- 建议抽一个 `assert_acceptance_draft_boundary` helper，并用于 flow 与 mixed 成功路径。
- 可把 entrypoint 成功路径也改用 helper，但不要扩大到无关测试重排。
- 不改 `acceptance-runs.md`，不声明 live acceptance。
- 不碰 `.coverage`，不要 revert 他人改动。

验收：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_acceptance_manual_record.py
git diff --check -- tests\unit\test_acceptance_manual_record.py
git diff -- src\ai_presenter\acceptance\manual_record.py
git status --short
```
