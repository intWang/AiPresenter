# Cycle 172 Technical Scan: Meeting Info Privacy Localization Routing

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle172 technical-scan subagent

## Scope

本轮只读扫描代码和文档，并只写入本文件：

- `docs/agent-handoffs/cycle-172-technical-scan.md`

未修改源码、测试、资料包 YAML、`.coverage`、git staging 或提交。工作区扫描时只看到 `.coverage` 为 tracked dirty，按要求未触碰。

## 当前实现概览

`src/ai_presenter/runtime/questions.py` 的问题路由顺序是：先标准化问题，再查 Q&A exact/safety/fuzzy 匹配，然后才落到 entrypoint 匹配；最终 `can_operate` 由 `questionPolicy`、`openSteps` 和 risky words 决定。

和上一轮 meeting info privacy routing 相关的当前状态：

- `_match_meeting_info_privacy_qa()` 已在通用 Q&A 候选循环前执行。
- Meeting information 隐私 matcher 会避开位置类查询，例如 `where is meeting link` 继续返回 Meeting information entrypoint answer。
- 英文和中文的 copy/paste/read/share meeting ID/link 类请求已经能命中 privacy Q&A。
- `_BROAD_QA_FRAGMENT_TOKENS = {"secure", "security", "status", "verify"}` 避免单个宽泛词被 encryption-status Q&A 捕获。
- `_is_package_entrypoint_alias_lookup()` 会阻止大多数 package alias 抢 Q&A，但对 Meeting information 的私密动作词和裸 `meeting id/link`、`会议号/会议链接` 留出 privacy Q&A 通路。

`src/ai_presenter/runtime/voice.py` 目前支持 runtime language `en/zh/ja/es` 和 tone `professional/conversational/concise/friendly/coach/formal/support/careful`。本地化 Q&A answer 命中时直接返回 authored localized answer；不会再额外套 tone 前缀。这一点已经被中文 careful/privacy tone 相关测试覆盖。

`packages/ringcentral-video.yaml` 的 RingCentral Video 资料包当前关键数量：

- `questionAliases`: 165 个 package-owned aliases。
- Q&A prompts: 220 个。
- localized Q&A coverage: `16/16` questions 和 `16/16` answers。
- Meeting information privacy Q&A 有英文多条动作型 prompt，西语/日语/中文各有一条主 localized question，并且三种语言都有 localized answer。

## 扫描到的测试覆盖

重点测试文件和已覆盖行为：

- `tests/unit/test_questions.py`
  - `test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first` 覆盖英文 read/copy/share/paste meeting link、meeting ID、dial-in、host、meeting information/details。
  - `test_chinese_meeting_link_short_question_uses_privacy_qa` 覆盖裸中文 `会议链接` 命中 privacy Q&A。
  - `test_chinese_meeting_info_action_requests_use_privacy_qa` 覆盖中文 `复制/粘贴/贴上/分享/读出` + `会议链接/会议号`。
  - `test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable` 只断言日文 meeting ID/link 请求非 operable 且不落到 invite/add-coworkers；没有断言命中 privacy Q&A。
  - `test_ringcentral_bare_status_words_do_not_match_encryption_status` 覆盖 `status/security/secure/verify` 不误入 encryption-status Q&A。
  - `test_ringcentral_encryption_status_questions_stay_meeting_info_answer_only` 覆盖多条英文 encryption/security/status copy/share 问句保持 answer-only。
  - `test_ringcentral_sensitive_prompt_routing_is_tone_invariant` 覆盖敏感路由不随 tone 改变。
- `tests/unit/test_diagnostics.py`
  - 断言 RingCentral package Q&A prompt 数为 `220`，alias overlap 也按 `220` 统计。
  - `qa alias substring risk` 当前为 INFO，数量为 `11`。
- `tests/unit/test_cli.py`
  - localization-report 断言 zh/ja/es 资料包完整度。
  - language alias normalization 覆盖 `Spanish`、`es-MX`、`es-419`、`Español`、`zh-CN`。

## 候选改进点

首选小步：补齐日文和西语 Meeting information 隐私动作路由，让 “读/复制/分享/粘贴 meeting ID/link” 类本地化问题命中现有 privacy Q&A，而不是返回 no-match。

只读探针结果显示，以下请求当前都是 no-match、non-operable、无 interrupt：

- 日文：`会議IDを読んで`
- 日文：`会議リンクをコピーして`
- 日文：`招待リンクをコピーして`
- 日文：`会議リンクを共有して`
- 日文：`会議IDを読み上げて`
- 西语：`lee el ID de la reunión`
- 西语：`copia el enlace de la reunión`
- 西语：`comparte el enlace de la reunión`
- 西语：`pega el enlace de la reunión`

这不是一个会触发操作的安全 blocker，因为当前结果仍是 non-operable 且无 interrupt。但它会让已经存在的日文/西语 localized privacy answer 无法用于自然动作问句，用户体验比英文/中文弱。

## 建议实现方案

涉及文件：

- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`
- 如选择资料包 exact prompts 路线，还会涉及 `packages/ringcentral-video.yaml`、`tests/unit/test_diagnostics.py`、`tests/unit/test_cli.py`

推荐实现方式是 runtime matcher 小步扩展，而不是先改 YAML prompt 数量：

1. 在 `_PRIVATE_MEETING_INFO_ACTION_TOKENS` 中加入日文和西语动作词片段。
   - 日文候选：`コピー`、`共有`、`読ん`、`読み上げ`。
   - 西语候选：`lee`、`leer`、`copia`、`copiar`、`comparte`、`compartir`、`pega`、`pegar`。
2. 在 `_PRIVATE_MEETING_INFO_CONTENT_FRAGMENTS` 中加入日文和西语私密内容片段。
   - 日文候选：`会議id`、`会議 id`、`会議リンク`、`招待リンク`。
   - 西语候选：`id de la reunion`、`enlace de la reunion`。`normalize_question_prompt()` 会去掉拉丁重音，所以 `reunión` 会标准化为 `reunion`。
3. 保持 `_LOCATION_LOOKUP_TERMS` gate 不变，避免 `where/dónde/どこ` 类位置查询被 privacy Q&A 抢走。
4. 新增测试时复用现有 `answer_question(...)` + `create_question_interrupt_step(...)` 模式，断言：
   - `entrypoint_id == "ringcentral.video.top.meeting-info"`。
   - `can_operate is False`。
   - `create_question_interrupt_step(...) is None`。
   - 日文 answer 包含 localized privacy 关键词，例如 `非公開` 或 `正確な ID`。
   - 西语 answer 包含 localized privacy 关键词，例如 `detalles privados` 或 `contenido visible esté verificado`。
   - answer 不包含 `Meeting information:`、`https://`、`ringcentral.com`、`123456789`。

候选测试：

- 新增或扩展 `tests/unit/test_questions.py::test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable`，把断言从“非 operable”提升为“命中 localized privacy Q&A”。
- 新增 `test_ringcentral_spanish_meeting_info_action_requests_use_privacy_qa`，覆盖 `lee/copia/comparte/pega` + `ID/enlace de la reunión`。
- 可选新增 `test_ringcentral_meeting_info_location_queries_stay_entrypoint_answers`，明确保护 `where is meeting link`、`会议号在哪里`、日文 `会議情報の場所...` 这类位置查询不被新词抢走。

## 潜在回归

- 日文 `会議リンク`/`招待リンク` 加入 content fragments 后，如果动作词过宽，可能把正常“在哪里”类查询误路由到 privacy Q&A。保持 location gate 并加 location regression 可以降低风险。
- 西语 action token 如果只加 `id` 或 `link` 这样过短/过泛的词，会增加误判。建议用较长 phrase，如 `id de la reunion`、`enlace de la reunion`。
- 如果改 YAML 添加 exact localized prompts，Q&A prompt 数会从 `220` 增加，需要同步更新 diagnostics 和 CLI 的硬编码数量；这会扩大改动面。runtime matcher 路线不会改变资料包统计。
- 当前 PowerShell 控制台会把部分 CJK 输出显示成 mojibake；测试里应继续使用 Unicode escape 或直接 UTF-8 文件内容，避免诊断时误读。

## 首选方案

优先做 runtime matcher + focused tests：在 `src/ai_presenter/runtime/questions.py` 扩展 Meeting information privacy 的日文/西语 action/content fragments，并在 `tests/unit/test_questions.py` 增加日文、西语自然动作问句覆盖。这个小步不改资料包 prompt 数量，不需要调整 diagnostics/CLI 计数，能直接提高语言覆盖并减少 localized privacy answer 的漏用。
