# Cycle173 风险/测试扫描：下一轮 UI、性能、技能沉淀与资料包导航

日期：2026-05-17
仓库：`C:\Users\rcadmin\Documents\Repos\AiPresenter`
角色：Cycle173 风险/测试扫描 subagent

## 范围与边界

本轮只读代码和文档，并只写入本文件：

- `docs/agent-handoffs/cycle-173-risk-scan.md`

未修改源码、测试、YAML、`.coverage`，未 stage 或 commit。开始扫描时工作区已有 `.coverage` dirty，按要求保持未触碰。

主要参考：

- Cycle172 提交 `a7d1c81`：`test: localize meeting info privacy routing`
- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/ai-presenter-maintenance.md`
- `docs/knowledge/language-lifecycle.md`

## 当前状态判断

Cycle172 已把日文/西语 action-style Meeting information 隐私问句纳入 runtime matcher，并补了西语 location lookup 回归。当前路由顺序仍是 Q&A 优先：`_match_qa()` 先查 exact Q&A，再查 recording、notes/transcript、meeting-info privacy 等安全 matcher，之后才落到 entrypoint alias 和 token scoring。这个顺序是近期 routing/language/doc changes 的安全核心。

几个关键实现点：

- `questions.py` 中 `_PRIVATE_MEETING_INFO_ACTION_TOKENS`、`_PRIVATE_MEETING_INFO_CONTENT_FRAGMENTS`、`_PRIVATE_MEETING_INFO_LOCATION_FRAGMENTS` 已承担多语言隐私动作和位置查询分流。
- `_PRIVATE_MEETING_INFO_LOCATION_FRAGMENTS` 已显式把 bare `host` / `ホスト` 从位置查询片段里排除，避免 `where are host controls for participants` 被误导到 Meeting information。
- package model 的 `localizedTitles` / `localizedPurposes` 不进入 match candidates；它们只用于展示，不应影响 alias ordering、Q&A precedence 或 safety gating。
- maintenance playbook 明确要求：package YAML、runtime presenter skills、durable knowledge、handoffs、Codex home skills 是不同层；资料包和 active presenter skill 都是行为变更，需要对应测试。

## 下一轮最容易引入的风险

1. **资料包导航把“展示文案”误当“匹配语义”。**

   如果下一轮做资料包导航、entrypoints 展示或本地化 UI，最容易把 `localizedTitles` / `localizedPurposes` 纳入搜索或路由候选。这样会推翻当前边界：展示元数据只负责 answer label，不参与 matching。风险表现是西语/日文标题片段开始抢路由，或者资料包导航为了“更好搜”引入新的 broad alias，导致 Q&A-first 安全问答被 entrypoint answer 覆盖。

2. **UI 下一步可能把 answer-only 入口变成可操作入口。**

   `can_operate` 现在由 `questionPolicy == answerOnly`、`openSteps` 和 `_RISKY_ENTRYPOINT_WORDS` 控制。UI 如果为了提升体验，给 answer-only entrypoint 加按钮、快捷跳转、自动 interrupt 或 controller action，最危险的是 Meeting information、Notes and Transcript、Recording、Leave/End、Invite、Share、Participants host/security 这些面板被误认为“只是打开位置”。这些入口里很多文本答案允许说明位置，但不允许读值、复制、分享、开启、关闭或代用户执行。

3. **性能优化可能改变 matcher 的可变性和顺序。**

   package model 已经缓存 entrypoint aliases、Q&A candidates、normalized Q&A map 和 entrypoint match candidates。如果下一轮做性能缓存或预计算，最大风险不是慢，而是缓存 invalidation 与 match order 漂移：`with_demo_flow()`、测试里动态构造 `MaterialPackage`、monkeypatch legacy aliases、以及 YAML 热加载都可能依赖当前构造时索引。优化若把全局 cache 绑到路径或 app_id，而不是稳定内容签名，可能造成跨测试、跨语言、跨资料包串味。

4. **技能沉淀把 repo-local 经验提升成 active behavior。**

   `docs/knowledge/ai-presenter-maintenance.md` 只是维护指南，不是 presenter runtime skill，也不是 Codex home skill。下一轮若把经验沉淀成 `presenter/skills/*.md` 或 `.codex` skill，风险会从文档变成 active prompt 行为：模型可能开始过度承诺“已验证”“已接受”“可操作”，或者改变 live demo 中的隐私边界。尤其要避免把 handoff 里的阶段性结论当成 evergreen truth。

5. **语言生命周期叙述继续有 overclaim 风险。**

   `docs/knowledge/language-lifecycle.md` 明确区分 package-local localization、runtime voice support 和 live acceptance。下一轮如果做资料包导航或 UI badge，容易把 `localization-report --require-complete` 展示成“语言可运行”“语音可用”或“RingCentral live accepted”。这类文案风险高于代码风险，因为用户会据此执行真实演示。

## 推荐 focused tests

如果下一轮触碰 routing、language、资料包导航、entrypoint 展示或 UI action gating，先跑高信号路由组：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_japanese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_spanish_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_spanish_meeting_info_location_requests_use_entrypoint_answer tests\unit\test_questions.py::test_ringcentral_host_controls_question_returns_participants_guidance tests\unit\test_questions.py::test_ringcentral_careful_tone_preserves_privacy_question_route tests\unit\test_questions.py::test_ringcentral_sensitive_prompt_routing_is_tone_invariant tests\unit\test_questions.py::test_ringcentral_participant_identity_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

如果触碰 `localizedTitles`、`localizedPurposes`、entrypoints CLI 或资料包导航：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_is_not_part_of_match_candidates tests\unit\test_questions.py::test_ringcentral_spanish_display_metadata_fragments_do_not_create_matches tests\unit\test_material_packages.py::test_entrypoint_localized_title_and_purpose_do_not_affect_match_candidates tests\unit\test_material_packages.py::test_entrypoint_title_and_purpose_counts_do_not_gate_required_localization tests\unit\test_cli.py::test_entrypoints_language_marker_contract_is_documented tests\unit\test_cli.py::test_package_language_alias_normalization_is_documented
```

如果触碰 package YAML、aliases、Q&A、diagnostics 或 localization counts：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_loads_ringcentral_video_app_material_package tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

如果触碰 active presenter skill、soul/memory 或 packaged skill parity：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_presenter_context.py tests\unit\test_presenter_skill_packaging.py tests\unit\test_profile_runner.py
```

如果触碰 runtime performance/cache/index construction，至少补跑：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_material_packages.py::test_material_package_builds_qa_question_index_from_localized_questions tests\unit\test_material_packages.py::test_material_package_copy_rebuilds_private_indexes tests\unit\test_questions.py::test_package_owned_equal_length_aliases_keep_source_order tests\unit\test_questions.py::test_longest_package_owned_alias_wins tests\unit\test_questions.py::test_package_owned_alias_takes_precedence_over_legacy_alias_table
```

最终收口命令建议：

```powershell
git diff --check
```

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
```

提交前必须确认 `.coverage` 未被纳入：

```powershell
git status --short
git diff --cached --name-status
git diff -- .coverage
```

## 适合本轮修的薄弱点

最适合本轮修的薄弱点：**为 Meeting information location lookup 增补日文/中文位置查询回归，明确“在哪里找 ID/link/host information”只返回 entrypoint 位置说明，不命中 privacy Q&A，也不产生 interrupt。**

理由：

- Cycle172 已补西语 location tests，但日文/中文只覆盖了动作型隐私请求和部分短问句；location 维度还不够对称。
- 这个 slice 很薄：只加测试，通常不需要改 runtime。若测试暴露偏差，再做最小词表或 location fragment 修正。
- 它直接保护下一轮资料包导航和 UI 入口展示，因为导航工作最可能新增“位置、入口、在哪里、場所、どこ、ubicación”类文案。

建议新增或扩展的断言：

- `会议号在哪里`、`会议链接入口在哪`
- `会議IDの場所はどこですか`、`会議リンクはどこにありますか`
- 期望 `entrypoint_id == "ringcentral.video.top.meeting-info"`
- `can_operate is False`
- `create_question_interrupt_step(...) is None`
- answer 包含位置/入口说明，不包含 localized privacy Q&A 的“私人会议详情 / 非公開 / detalles privados”
- answer 不包含 URL、domain、sample ID、`copied/read/dialed` 结果声称

这比继续扩更多同义词更稳：它先把位置查询和隐私动作查询的分界线钉住，下一轮做 UI/导航/性能时有清晰护栏。

## 风险结论

Cycle173 下一轮最大的风险不是单个问句没有匹配，而是为了 UI、性能或导航便利把现有分层打平：展示文案进入 matcher、answer-only 入口变成可操作入口、缓存改变路由顺序、repo-local 维护指南升级成 active prompt 行为。最小高价值防线是继续用 focused route tests 固定 Q&A-first、non-operable、no-interrupt、localized answer 与 location lookup 的边界，再用 diagnostics/localization tests 锁住资料包计数和文档 overclaim。
