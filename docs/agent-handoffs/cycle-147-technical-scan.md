# Cycle 147 Technical Scan: acceptance-draft Draft-Only Boundary

Date: 2026-05-17
Cycle: 147
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

本次只扫描 `acceptance-draft` 的 draft-only / not-evidence / no-live-action 边界。未改源码、测试、package 或 `.coverage`。当前工作区已有 `.coverage` dirty，应继续忽略，不要 stage、revert 或 normalize。

阅读范围：

- `src/ai_presenter/acceptance/manual_record.py`
- `src/ai_presenter/cli.py`
- `tests/unit/test_acceptance_manual_record.py`
- `tests/unit/test_cli.py` acceptance-draft tests
- `docs/agent-handoffs/cycle-146-experience.md`

## Existing Implementation Coverage

`manual_record.render_manual_acceptance_draft(...)` 已经在所有成功 draft 输出开头写入三层边界：

- `> Draft only: this is not acceptance evidence until filled after the manual run and appended to acceptance-runs.md.`
- `> No live RingCentral action has been performed by this helper.`
- `Proof-Order Reminder` 中再次声明 draft-only fields 是 placeholders，pass/fail、failures、recovery、evidence files、locator updates 必须等实际观察后填写。

`manual_record.build_acceptance_target_summary(...)` 已经在 target resolve 后调用 `_reject_direct_no_step_entrypoint(...)`。这会拒绝直接对没有 executable open steps 的 entrypoint 生成 acceptance draft，错误文案包含 separate confirmation workflow / before live execution。这个位置是当前最小生产守护点，已经覆盖 direct entrypoint 的 no-live-action 边界。

`cli.acceptance_draft(...)` 当前只是加载 package、组装 `AcceptanceDraftRequest`、调用 `render_manual_acceptance_draft(...)`。如果传 `--output`，它把 renderer 生成的同一份 markdown 写入文件；因此 stdout 与 file output 的 draft-only 文案来源一致。

`cli._write_acceptance_draft_output(...)` 已有 file-output 专属保护：

- 拒绝写到 `acceptance-runs.md`，要求 separate draft file，并由人工完成证据后 append。
- 拒绝覆盖已存在文件。
- no-open-step entrypoint 在 renderer 前置拒绝，CLI 测试已覆盖失败时不创建 output file。

`validation_targets.acceptance_draft_command(...)` 只是生成后续人工 draft 命令；`render_validation_target_lines(...)` 已在 header 输出 `Note: repo-derived planning list only; not live acceptance evidence.`，且 blocked target 不输出 draft command。Cycle 146 文档建议本轮聚焦 `acceptance-draft` 本身，而不是再改 validation-targets。

## Existing Test Coverage

`tests/unit/test_acceptance_manual_record.py`：

- `test_manual_acceptance_draft_prefills_entrypoint_context_without_claiming_acceptance` 已断言 entrypoint draft 包含 `Draft only`、`not acceptance evidence`、`No live RingCentral action has been performed by this helper.`，并断言不包含 `Accepted`。
- `test_manual_acceptance_draft_prefills_flow_steps` 只覆盖 flow context，没有断言 draft-only / not-evidence / no-live-action 文案。
- `test_manual_acceptance_draft_prefills_mixed_flow_and_entrypoint_steps` 覆盖 flow + entrypoint + checklist context 和 intended steps，没有断言边界文案。
- `test_manual_acceptance_draft_rejects_no_open_step_entrypoint` 覆盖 direct no-open-step entrypoint 拒绝，但只看错误路径，不看 successful draft 的 no-live-action 文案。

`tests/unit/test_cli.py` acceptance-draft：

- `test_acceptance_draft_outputs_entrypoint_template` 已断言 stdout entrypoint path 包含 `Draft only`，但没有断言 `not acceptance evidence` 和 `No live RingCentral action has been performed by this helper.`。
- `test_acceptance_draft_outputs_flow_template` 覆盖 flow path 的成功输出，但没有断言任何 draft-only boundary。
- `test_acceptance_draft_can_write_to_output_file` 覆盖 file output 成功写入，并断言文件内有 `Draft only`，但没有断言 `not acceptance evidence`、no-live-action 文案，也没有断言 CLI stdout 只是写入提示而非 acceptance claim。
- `test_acceptance_draft_rejects_no_open_step_entrypoint` 和 `test_acceptance_draft_refusal_does_not_write_output_file` 覆盖 no-open-step / blocked direct path，不生成 draft，不写文件。
- `test_acceptance_draft_rejects_acceptance_runs_output_file` 覆盖 file-output 不允许直接写 `acceptance-runs.md`。

Cycle 146 experience 已明确把本轮推荐收窄为 successful draft 的 focused guard：断言 draft helper 继续是 draft-only / not acceptance evidence，且不出现 `accepted`、`passed`、`live validated` 等结论性措辞。

## Gaps

当前缺口主要是测试契约不够完整，不是生产实现缺失：

- Entrypoint stdout path：已有 `Draft only`，缺少对完整 not-evidence 和 no-live-action 文案的 CLI 层断言。
- Flow stdout path：只断言 flow 内容，缺少 draft-only / not-evidence / no-live-action 边界断言。
- File output path：只断言文件内 `Draft only`，缺少文件内 not-evidence / no-live-action 断言；也可以补一条 stdout 写入提示不含 acceptance 结论。
- Renderer unit：entrypoint path 已较好；flow 或 mixed path 可补边界断言，但最小收益低于 CLI 层，因为 renderer 文案已由 entrypoint test pin 住，而 CLI 的 flow/file 成功路径还没有 pin。
- Negative wording：只有 renderer entrypoint test 断言 `Accepted` 不出现；CLI successful paths 没有防止 `accepted`、`passed`、`live validated` 等结论性措辞的 focused guard。

## Recommended Minimal Guard

建议 test-only 修改，不改 `src`。

首选最小测试位置是 `tests/unit/test_cli.py`，因为它直接覆盖用户可见 entrypoint、flow、file output 三条路径。生产 renderer 已经输出正确文案，新增断言应当直接绿；TDD 红灯可用临时破坏 renderer 文案确认测试有效，然后恢复。

推荐新增一个小 helper，避免三条路径重复断言：

```python
def assert_acceptance_draft_boundary(text: str) -> None:
    assert "Draft only" in text
    assert "not acceptance evidence" in text
    assert "No live RingCentral action has been performed by this helper." in text
    lowered = text.casefold()
    assert "accepted" not in lowered
    assert "passed" not in lowered
    assert "live validated" not in lowered
```

注意：如果直接对整份 draft 断言 `"passed" not in lowered`，当前内容没有 `passed`，可行；`pass/fail` 不会触发该词。`accepted` 也不会误伤 `acceptance`，因为 `accepted` 是独立词形。

推荐测试名和断言：

- `test_acceptance_draft_outputs_entrypoint_template`
  - 在现有测试里追加 `assert_acceptance_draft_boundary(result.stdout)`。
  - 这个 path 覆盖 direct entrypoint stdout。
- `test_acceptance_draft_outputs_flow_template`
  - 在现有测试里追加 `assert_acceptance_draft_boundary(result.stdout)`。
  - 这个 path 覆盖 flow-only stdout。
- `test_acceptance_draft_can_write_to_output_file`
  - 对 `text = output_path.read_text(...)` 追加 `assert_acceptance_draft_boundary(text)`。
  - 可追加 `assert "acceptance evidence" not in result.stdout.casefold()` 或更窄地保持现有 `Wrote acceptance draft` 提示；stdout 不应承载 acceptance claim。

如果想把 guard 独立成新测试，推荐：

- `test_acceptance_draft_entrypoint_stdout_keeps_draft_only_boundary`
- `test_acceptance_draft_flow_stdout_keeps_draft_only_boundary`
- `test_acceptance_draft_output_file_keeps_draft_only_boundary`

但当前已有三条相同路径的测试，直接增强现有测试更小。

## Need To Modify Src?

不需要。当前 `src/ai_presenter/acceptance/manual_record.py` 已经是单一文案来源，`src/ai_presenter/cli.py` 对 stdout 和 file output 都复用 renderer 字符串。最小 guard 只需补测试断言。

只有在团队希望复用边界文案常量，或让 CLI 写入提示也显示 `draft only` 时，才需要改 `src`。本轮主题是守住 draft-only boundary，现有实现已经满足，风险更低的做法是 test-only。

## TDD Red-Light Method

建议红灯方式：

1. 先在 `tests/unit/test_cli.py` 增加 helper 和三处断言。
2. 临时破坏 `src/ai_presenter/acceptance/manual_record.py` 中其中一句边界文案，例如把 `not acceptance evidence` 改成 `not final evidence`，或删除 `No live RingCentral action has been performed by this helper.`。
3. 跑目标测试，确认新增断言失败，失败点应指向 entrypoint/flow/file output 的 boundary helper。
4. 恢复 `manual_record.py`，确认 `git diff -- src\ai_presenter\acceptance\manual_record.py` 无输出。
5. 重新跑目标测试，确认通过。

不要用写入 `acceptance-runs.md` 或 no-open-step entrypoint 来制造红灯；这些是已有保护，不直接验证 successful draft 文案。

## Validation Commands

本 handoff 文档本身：

```powershell
rg -n "[ \t]+$" docs\agent-handoffs\cycle-147-technical-scan.md
git diff --check -- docs\agent-handoffs\cycle-147-technical-scan.md
```

后续实现本建议时的 focused verification：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_cli.py -k acceptance_draft
git diff --check -- tests\unit\test_cli.py
git diff -- src\ai_presenter\acceptance\manual_record.py src\ai_presenter\cli.py
```

如果实现者还补 renderer unit guard：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider tests\unit\test_acceptance_manual_record.py
git diff --check -- tests\unit\test_acceptance_manual_record.py
```
