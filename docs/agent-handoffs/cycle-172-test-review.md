# Cycle 172 测试 Review

## 范围

本 review 只检查当前 diff 中与 meeting-info 隐私 matcher 相关的运行时代码和测试：

- `src/ai_presenter/runtime/questions.py`
- `tests/unit/test_questions.py`

未修改源码、测试、YAML、`.coverage`，未 stage/commit。

## 已执行验证

先用全局 `pytest` / 全局 `python -m pytest` 尝试运行，均失败，原因是当前 shell 的全局 Python 环境没有 pytest：

- `pytest ...` -> `pytest` command not found
- `python -m pytest ...` -> `No module named pytest`

随后改用仓库 `.venv`，并关闭 coverage、pytest cache、bytecode，避免刷新 `.coverage` 或 cache：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_japanese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_spanish_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests\unit\test_questions.py::test_chinese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable
```

结果：`28 passed in 7.44s`。

另跑了 diff whitespace 检查：

```powershell
git diff --check -- src/ai_presenter/runtime/questions.py tests/unit/test_questions.py
```

结果没有 whitespace error；仅提示工作副本中的 LF 将在 Git 触碰时替换为 CRLF。

## 测试覆盖评价

新增日文/西语参数化测试覆盖了主要动作型隐私请求：

- 日文：会议 ID、会议链接、ミーティングID、ダイヤルイン、ホスト信息，加上读出/复制/分享动作。
- 西语：ID de reunión、enlace de reunión、información del host、datos de marcación，加上 leer/copiar/compartir 动作。
- 断言了 `entrypoint_id == ringcentral.video.top.meeting-info`、`can_operate is False`、命中本地化隐私 QA 文案，并且不退回 `Meeting information:` 入口说明。
- 近邻回归也保留了英文/中文位置查询、中文动作型隐私请求、日文 invite/copy 非操作化保护。

总体看，新增测试能证明 Cycle 172 的动作型日文/西语 meeting-info 私密值请求不会变成可操作入口，也不会泄露真实 meeting value。

## 主会话还需补的验证命令

建议主会话在合并前补跑更宽的 focused set，包含 diagnostics 和本轮新增用例：

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -B -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests\unit\test_questions.py::test_chinese_meeting_link_short_question_uses_privacy_qa tests\unit\test_questions.py::test_chinese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_japanese_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_spanish_meeting_info_action_requests_use_privacy_qa tests\unit\test_questions.py::test_ringcentral_japanese_meeting_info_value_or_copy_requests_stay_non_operable tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

若主会话准备最终收口，还应跑 full pytest，并明确不要 stage 当前已脏的 `.coverage`：

```powershell
$env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest
```

## 可能遗漏的边界

1. 西语位置查询没有直接测试。当前 diff 新增了 `_LOCATION_LOOKUP_TERMS` 的 `donde` / `ubicacion`，但新增 tests 只覆盖动作型隐私请求。只读探针显示：
   - `Donde esta el ID de reunion` 目前返回 `ringcentral.video.top.meeting-info`，但 answer_text 命中的是西语 encryption status QA，而不是 meeting-info 位置/角色说明。
   - `Ubicacion del enlace de reunion` 当前没有匹配入口，返回 no-match。
   这说明新增 location fragments 的行为面还没有被测试锁住。

2. 西语同义词覆盖仍偏窄。已覆盖 `ID/enlace/informacion/datos de marcacion/host`，但未覆盖 `vínculo`, `liga`, `url`, `número de reunión`, `copiar y pegar` 等可能真实说法。

3. 日文覆盖了典型汉字/片假名写法，但未覆盖空格/大小写混排、`参加リンク`, `招待リンク`, `URL`, `読み上げ`, `貼って` 等变体。已有旧测试只保证部分日文 copy/invite 请求保持 non-operable，不保证命中 meeting-info privacy QA。

4. 新增 action token 使用 substring 匹配。西语 `lee` 可能匹配到非动作词片段的风险较低，但仍建议至少保留 diagnostics alias-overlap 验证，避免未来短 token 和其他 QA/alias 互相抢路由。

## 是否有必须修复的问题

本轮新增动作型日文/西语隐私 QA tests 通过，我没有发现这些新增测试本身的阻塞问题。

但我建议主会话在收口前必须处理或显式接受西语位置查询边界：既然 diff 新增了 `donde/ubicacion`，应补测试证明 `Dónde está el ID/enlace de reunión` 和 `Ubicación del enlace de reunión` 会落到正确的 meeting-info 安全说明，而不是 encryption status QA 或 no-match。这个问题不一定会泄露隐私值，但会给用户错误/缺失的回答，属于本 diff 引入行为面的明显测试缺口。
