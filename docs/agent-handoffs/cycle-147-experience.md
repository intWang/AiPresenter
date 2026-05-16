# Cycle 147 Experience: Acceptance Draft Boundary Guard

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## 主题/用户价值

本轮价值是把 `acceptance-draft` 固定为人工验收记录的草稿起点，而不是验收证据本身。成功生成的 stdout 和 `--output` 文件越完整，越需要同时保留三层边界：

- `Draft only`
- `not acceptance evidence`
- `No live RingCentral action has been performed by this helper.`

这能让后续操作者得到 package、flow、entrypoint、checklist、隐私提醒和待填写字段的便利，同时不会误读为已经执行过 RingCentral live workflow、已经观察到结果，或已经可以写入 `acceptance-runs.md`。

## 子代理衔接

需求分析把范围压在 successful draft 的输出契约上：守住 draft-only / not-evidence / no-live-action，不扩展到 live acceptance、package YAML、runtime 或 evidence ledger。

技术扫描确认生产实现已经由 renderer 统一输出边界文案，CLI stdout 和 file output 复用同一份 markdown；缺口主要是 CLI 层成功路径的测试契约不完整。

风险扫描补齐了措辞边界：draft 可以描述 intended target、intended steps 和待填写字段，但不能暗示 observed、validated、executed、passed 或 accepted。

实现子任务选择 test-only：在 `tests/unit/test_cli.py` 增加 `assert_acceptance_draft_boundary`，覆盖 entrypoint stdout、flow stdout 和 file output，并用临时破坏 renderer 的方式确认红灯有效。

评审确认无 findings，且最终 `src/ai_presenter/acceptance/manual_record.py` 与 `src/ai_presenter/cli.py` 无 diff。

## 经验规则

Successful draft paths 要统一守护同一组边界，不要只在一个 renderer 或一个 stdout 测试里检查。至少 entrypoint stdout、flow stdout、file output 都要包含 draft-only、not-evidence、no-live-action 三句话。

`acceptance-draft --output` 的成功消息只能表达写入了 draft file，不能说 evidence、acceptance run、ledger 或 live action 已完成。拒绝写入 `acceptance-runs.md` 的保护不能为了测试便利而放松。

临时破坏 renderer 做 TDD 红灯是有效手段，但恢复后必须显式确认没有 `src` 残留 diff。尤其本轮临时动过 `src/ai_presenter/acceptance/manual_record.py`，收尾时要跑：

```powershell
git diff -- src\ai_presenter\acceptance\manual_record.py src\ai_presenter\cli.py
```

Negative words 要避免误伤合法字段。`accepted` 不会误伤 `acceptance`，`passed` 不会误伤 `Pass/fail` 或 `pass/fail`，但后续如果改成更宽的正则或词干匹配，必须重新检查这些合法 acceptance template 字段。

不要用 no-open-step refusal、blocked target 或 `validation-targets` draft command 代替 successful draft guard。它们是相关边界，但本轮核心是“成功生成的草稿本身不能像证据”。

## 下轮建议

下一轮可以二选一做一个窄切口。

方案一：在 `tests/unit/test_acceptance_manual_record.py` 增加 renderer-level helper，把 flow 和 mixed renderer unit tests 也接入同一组 draft-only boundary 断言。这样即使未来绕过 CLI 使用 renderer，也有同等保护。

方案二：补一个 acceptance-draft output refusal path 守护，确认写入 `acceptance-runs.md`、已存在文件、no-open-step entrypoint 等拒绝路径不会创建 output file，也不会输出任何 evidence-like 成功措辞。

优先级上，如果后续改动集中在文案模板或 renderer，选方案一；如果后续改动集中在 CLI `--output` 行为，选方案二。

## 验证/提交注意

提交前建议跑完整验证，而不只跑本轮 focused tests：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q
.\.venv\Scripts\ruff.exe check --no-cache .
.\.venv\Scripts\python.exe -m mypy .
git diff --check
git diff -- src\ai_presenter\acceptance\manual_record.py src\ai_presenter\cli.py
git status --short
```

不要 stage `.coverage`，也不要为了清理工作树 revert 他人改动。若 `.coverage` 已 dirty，记录现状并在提交时排除即可。
