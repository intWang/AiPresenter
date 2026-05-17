# Cycle172 风险扫描：语言、语气与 RingCentral Video 问答扩展

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle172 测试/风险 review subagent

## 范围与边界

本轮只读代码和文档，并只写入本文件：

- `docs/agent-handoffs/cycle-172-risk-scan.md`

未修改源码、测试、YAML、暂存区、提交或 `.coverage`。开始审查时工作区已有 `.coverage` dirty，保持未触碰。

重点查看：

- `tests/unit/test_questions.py`
- `src/ai_presenter/runtime/questions.py`
- `packages/ringcentral-video.yaml`
- Cycle169-171 的测试/风险/开发 handoff 与最近提交 `de46eea`、`a3fc826`、`a0ee47d`

## 最近三轮方向

Cycle169 把 Full screen 系列 prompt 放进 `ringcentral.video.top.views` 的 package-owned aliases，并用 focused tests 确认它们路由到 Views，而不是 Share 或 Leave。这个方向是“安全但可操作的位置入口”：Views 改本地布局，测试允许 `can_operate=True` 和 interrupt。

Cycle170 把 encryption/security status 问题收束到 Meeting information 的 answer-only Q&A。测试方向是 Q&A-first、无 interrupt、不过度声称 live encryption state，并避免误入 Share、Leave、Settings、Network、RingCentralDevelop 等相邻 surface。

Cycle171 继续加固 meeting info privacy routing。当前 `a0ee47d` 已把旧风险点 `share secure`、`share verify`、`copy status`、`copy security` 等拉回 encryption-status Q&A；同时新增 meeting info action prompt 的 privacy Q&A 保护。测试方向已经从“路由正确”扩展到“答案不能包含 URL、域名、样例 ID、copied/read/dialed 结果声称”。

## 当前实现关键点

`src/ai_presenter/runtime/questions.py` 的问答路由顺序是风险核心：

1. `_match_qa()` 先查 exact Q&A，再查 recording、notes/transcript、meeting-info privacy 等安全特判。
2. 如果不是 Q&A，再走 package-owned entrypoint aliases 和 legacy aliases。
3. `_can_operate()` 最后用 `questionPolicy: answerOnly`、`openSteps` 和 `_RISKY_ENTRYPOINT_WORDS` 决定是否可操作。

这意味着扩展语言或语气时，风险不只在某个 alias 是否命中，还在它是命中 Q&A 还是命中 entrypoint。相同 entrypoint 可以是安全 Q&A，也可能退化成薄的 entrypoint answer。

## Cycle172 最容易引入的风险

1. **把敏感动作 prompt 加成 entrypoint alias，而不是 Q&A prompt。**
   例如 read/copy/share/show/open meeting ID、link、dial-in、host、captions、transcript、participant names。如果放进 `questionAliases`，即使 `answerOnly` 阻止执行，也可能返回薄的入口说明，而不是隐私 Q&A。

2. **位置查询和价值请求边界变模糊。**
   当前 `meeting information`、`where is the meeting link` 这类位置查询仍返回 `Meeting information:` 入口答案，并列出 meeting ID、copy link 等字段类别；而 `复制会议链接`、`read dial-in details` 会走 privacy Q&A。继续扩展时要明确：哪些是“告诉我在哪里”，哪些是“读/复制/分享具体值”。

3. **多语言覆盖不均。**
   英文 meeting-info privacy Q&A 有大量 action prompts；中文通过 runtime privacy matcher 和少量测试覆盖了短问、复制、粘贴、分享、读出。日文目前更偏“非可操作/不误入 invite”的保护，`会議IDを読んで` 这类价值请求没有被强制断言为 localized privacy Q&A。它今天是安全 no-match，但后续新增 alias 时容易漂到 Meeting information 或 Invite。

4. **语气渲染可能稀释安全 caveat。**
   `render_presenter_text()` 在 localized authored answers 存在时通常不改写，但非 localized fallback 会受 tone 影响。继续扩展 `tone="friendly"|"coach"|"privacy"` 时，要固定 route、`can_operate`、interrupt 和关键 caveat，而不是只看 answer 文案好不好听。

5. **Broad token guard 仍是局部规则。**
   `_BROAD_QA_FRAGMENT_TOKENS` 只挡 exact broad words 在一个 fragment path 上的误匹配。它适合当前 `status/security/secure/verify`，但若未来加入新的单词级 Q&A 或 localized broad token，仍需测试先行。

6. **answerOnly 容易被误解为完整隐私保护。**
   `questionPolicy: answerOnly` 能阻止 interrupt/operation，但不能保证答案不泄露或不过度承诺。敏感问答仍需要断言：不读值、不复制、不分享、不声称已验证/已打开/已启用/已关闭。

## 推荐验收测试组合

Focused tests 先跑最小高信号组合：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_ringcentral_bare_status_words_do_not_match_encryption_status tests\unit\test_questions.py::test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests\unit\test_questions.py::test_chinese_meeting_link_short_question_uses_privacy_qa tests\unit\test_questions.py::test_chinese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

如果 Cycle172 触碰 localized Q&A 或 alias 数量，再加：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_japanese
```

最终全量命令建议：

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
```

提交前还应跑 touched files 的 whitespace 检查：

```powershell
git diff --check -- src/ai_presenter/runtime/questions.py packages/ringcentral-video.yaml tests/unit/test_questions.py tests/unit/test_cli.py tests/unit/test_diagnostics.py tests/unit/test_material_packages.py docs/agent-handoffs/cycle-172-risk-scan.md
```

## 本轮适合修的薄弱点

最适合 Cycle172 做的薄弱点：把日文 meeting info 价值请求从“只保证非可操作/不误入 invite”提升为“明确命中 Meeting information privacy Q&A”。

建议最小 slice：

- 在 `packages/ringcentral-video.yaml` 的 `How should AiPresenter handle meeting IDs and links safely?` 下增加 3-5 个日文 localizedQuestions，例如读会议 ID、复制会议链接、复制邀请链接、读 meeting link。
- 在 `tests/unit/test_questions.py` 中把 `test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable` 加强为断言：
  - `entrypoint_id == "ringcentral.video.top.meeting-info"`
  - `can_operate is False`
  - `create_question_interrupt_step(...) is None`
  - answer 使用日文 privacy Q&A，而不是 `Meeting information:`
  - 不包含 URL/domain/sample ID，也不出现 copied/read/dialed outcome claim
- 不改 runtime matcher，除非测试证明 package Q&A prompt 无法覆盖该 slice。

这个修复很薄，但价值高：它补齐了 Cycle171 已经在英文/中文建立的隐私语义，把日文从“安全地找不到或不执行”推进到“安全且有用地回答”。

## 风险结论

Cycle172 可以继续扩展语言、语气和 RingCentralVideo 问答，但验收必须把“route、operability、interrupt、answer wording、localized caveat”当成一个整体看。当前最大风险不是自动执行错误操作，而是新增 prompt 后从 privacy Q&A 漂到薄 entrypoint answer，或 localized/tone 文案丢掉不读、不复制、不分享、不声称已验证的边界。
