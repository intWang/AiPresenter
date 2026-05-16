# Cycle 126 Demand Analysis: Accent-Insensitive Spanish Alias Matching

Date: 2026-05-17
Cycle: 126
Scope: demand analysis only. This handoff is the only file this subagent should edit. Do not modify runtime code, package YAML, tests, durable knowledge docs, generated artifacts, or commits in this analysis slice.

## 用户价值

Cycle 125 已经把 RingCentral Video 的西语 package-local 体验推进到一个很好的位置：

- Spanish demo narration: `51/51`
- Spanish localized Q&A questions: `12/12`
- Spanish localized Q&A answers: `12/12`
- `questionAliases.es`: `26/27` entrypoints, `69` aliases
- package-owned aliases total: `156`
- Q&A prompts: `84`
- `demo --language es` 仍按设计拒绝，Spanish 仍不是 runtime presenter language

下一轮最高价值不应优先做 docs hygiene，而应修复 accent-sensitive matching。原因是这已经不是文档陈旧问题，而是用户自然输入会直接错路由或 miss 的体验问题。

当前 package alias 和 Q&A prompt normalization 只做 `strip().casefold()`：

- `src/ai_presenter/packages/models.py` 中 `entrypoint_question_aliases` 使用 `alias.strip().casefold()`。
- `normalize_question_prompt()` 返回 `text.strip().casefold()`。
- `runtime/questions.py` 的 Q&A exact/fragment、package alias substring、final fuzzy token fallback 都依赖这些 normalized 值。
- `diagnostics.py` 的 alias duplicate、Q&A duplicate、Q&A alias overlap、substring risk 也依赖同一批 normalized 值。

这对西语很脆弱。很多用户会省略重音输入 `configuracion`, `reunion`, `boton`, `camara`, `menu`, `informacion`。当前行为不是简单地“匹配不上”，而是可能退到英文/拉丁 token fallback 后命中错误 entrypoint。

我用当前代码做了一个小探针，结果如下：

| 无重音西语输入 | 当前结果 | 用户期望 |
| --- | --- | --- |
| `Donde esta el menu de camara en la reunion?` | `ringcentral.video.toolbar.audio-menu` | camera menu |
| `Donde esta el boton de levantar la mano?` | no match | raise hand |
| `Donde esta el menu de audio de la reunion?` | `ringcentral.video.toolbar.audio-menu` | audio menu |
| `Donde esta la configuracion avanzada de video?` | `ringcentral.video.settings.video` | video settings |
| `Donde esta el panel de informacion de la reunion?` | `ringcentral.video.toolbar.participants` | meeting information |
| `Donde esta el panel de chat de la reunion?` | `ringcentral.video.toolbar.chat` | chat |

这说明 accent-insensitive matching 是 Cycle 126 的最高价值目标：它直接提升西语用户提问成功率，并减少无重音输入被错误 token fallback 捕获的风险。相比之下，knowledge docs 更新能降低维护误读，但不会改善用户在 Q&A/控制定位中的实际结果。

## 推荐目标

推荐 Cycle 126 做一个窄而系统的 normalization slice：让 package-owned aliases、localized Q&A prompts、entrypoint token matching、doctor diagnostics 在比较文本时支持 accent-insensitive matching，同时保持 Spanish runtime unsupported。

建议实现方向：

- 在 `src/ai_presenter/packages/models.py` 中引入共享 normalization helper，例如 `normalize_match_text(text: str) -> str`。
- 使用 Unicode decomposition 去除 combining marks，再 `casefold()` 和 `strip()`。目标是折叠拉丁重音，不做翻译、不做同义词、不做模糊拼写纠错。
- 让 `normalize_question_prompt()` 调用同一 helper。
- 让 `MaterialPackage` 构建 `EntrypointQuestionAlias.normalized_alias` 时调用同一 helper。
- 让 Q&A candidate 的 `normalized_question` 通过同一 helper 构建。
- 评估并推荐同时让 `match_field_tokens()` 基于同一 helper，否则 `cámara` 这类词会被 `[a-z0-9]+` 拆成 `c` / `mara`，final token fallback 仍会有不一致行为。
- 让 legacy alias normalization 也走同一 helper，避免未来 legacy Latin aliases 和 package aliases 行为分裂。
- 保持匹配顺序不变：Q&A exact/safety/fragment 先于 package aliases，package aliases 先于 legacy aliases 和 token fallback。

高价值测试应证明：

- 有重音和无重音西语 location prompts 都命中同一个 entrypoint。
- 无重音输入不会再退到错误 token fallback。
- 无重音西语 safety/action/content prompts 仍 Q&A-first 或 non-operable。
- diagnostics 在 accent-folded normalized 值上继续捕获 duplicate / overlap / substring risk。

推荐的代表性路由用例：

- `¿Dónde está el menú de cámara en la reunión?` 和 `Donde esta el menu de camara en la reunion?` -> `ringcentral.video.toolbar.video-menu`
- `¿Dónde está el botón de levantar la mano?` 和 `Donde esta el boton de levantar la mano?` -> `ringcentral.video.toolbar.raise-hand`, `can_operate=False`
- `¿Dónde está el panel de información de la reunión?` 和 `Donde esta el panel de informacion de la reunion?` -> `ringcentral.video.top.meeting-info`, `can_operate=False`
- `¿Dónde está la configuración avanzada de video?` 和 `Donde esta la configuracion avanzada de video?` -> `ringcentral.video.settings.video`
- `¿Cómo manejo la grabación de la reunión de forma segura?` 和 `Como manejo la grabacion de la reunion de forma segura?` -> Q&A safety route, `can_operate=False`
- `¿Puede AiPresenter enviar una reacción o levantar la mano de forma segura?` 和 `Puede AiPresenter enviar una reaccion o levantar la mano de forma segura?` -> Q&A safety route, `entrypoint_id is None`, `can_operate=False`

Secondary but useful: after the code slice, open a separate docs hygiene cycle to update stale durable knowledge docs. I would not spend Cycle 126 primarily on that unless the main session values maintainer clarity over user-facing routing quality.

## 非目标

本轮不应启用 runtime Spanish：

- 不改 `PresenterLanguage`、language aliases、voice labels、controller language choices、provider routing、voice assets、profiles 或 `voices` catalog。
- `demo --language es --dry-run` 仍必须失败并包含 `Unsupported presenter language: es`。
- `doctor --require-localization --localization-language es` 仍应允许 package localization OK，同时 runtime language support FAIL。

本轮不应继续扩展 `questionAliases.es` 数量来“补无重音变体”。如果为每个 alias 同时写 accented 和 unaccented 版本，会增加 YAML 噪声、duplicate 风险和 diagnostics 计数漂移，却没有解决 Q&A prompts 和 token fallback 的同类问题。正确修复点是 normalization。

本轮不应改变 matching precedence、`questionPolicy`、`_can_operate(...)`、openSteps、locators、cleanup、demo flow 顺序、action offsets 或 safety wording。

本轮不应把 docs hygiene 和 normalization 改动混在一起。已观察到这些 durable docs 有旧状态：

- `docs/knowledge/language-lifecycle.md` 的 Current Spanish State 仍写 Cycle 123 partial/sparse alias state。
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` 仍写 2026-05-16 的旧 counts：`87` aliases、`71` Q&A prompts，未反映 Cycle 125 的 `156` aliases、`84` Q&A prompts 和 Spanish `26/27` alias state。

这些应作为独立 docs-only cleanup 候选，或在 normalization slice 完成后另开一轮更新。

本轮不应提交、stage，尤其不要 stage `.coverage`。当前工作树已有 `.coverage` modified，视为既有本地 artifact。

## 验收标准

Code behavior:

- `normalize_question_prompt()` 对拉丁重音不敏感，例如：
  - `configuración` 和 `configuracion` normalized 相同；
  - `reunión` 和 `reunion` normalized 相同；
  - `botón` 和 `boton` normalized 相同；
  - `cámara` 和 `camara` normalized 相同。
- `EntrypointQuestionAlias.normalized_alias` 使用同一 normalization。
- Q&A candidate normalized prompts 使用同一 normalization。
- `match_field_tokens()` 的 tokenization 不再把 accented Latin words 拆坏；推荐用 accent-folded text 再套现有 `[a-z0-9]+` pattern。
- Legacy alias matching 与 package alias matching 使用一致 normalization。
- CJK aliases/questions 继续按现有行为匹配，不因为 accent folding 受损。

Spanish routing:

- 有重音和无重音版本的 Spanish location prompts 命中同一 entrypoint。
- 重点回归当前探针里的错路由：
  - `Donde esta el menu de camara en la reunion?` 不再命中 `ringcentral.video.toolbar.audio-menu`，应命中 `ringcentral.video.toolbar.video-menu`。
  - `Donde esta el panel de informacion de la reunion?` 不再命中 `ringcentral.video.toolbar.participants`，应命中 `ringcentral.video.top.meeting-info`。
  - `Donde esta el boton de levantar la mano?` 不再 no-match，应命中 `ringcentral.video.toolbar.raise-hand` 且 `can_operate=False`。
- Spanish safety prompts with unaccented text remain non-operable and keep Q&A-first behavior where current authored Q&A owns the intent.

Diagnostics:

- Add focused diagnostics tests proving accent-folded duplicates are caught, e.g. aliases `cámara` and `camara` on different entrypoints should WARN as duplicate normalized aliases.
- Add Q&A duplicate/overlap tests if the normalization change makes Q&A prompt comparison accent-insensitive.
- RingCentral package diagnostics should remain OK/WARN/INFO with intentionally reviewed exact counts:
  - package-owned aliases likely remain `156`;
  - Q&A prompts likely remain `84`;
  - Spanish aliases likely remain `26/27`, `69`;
  - substring risk count should be checked and updated only if accent folding creates a real, reviewed change.

Runtime boundary:

- `localization-report --package ringcentral-video --language es` still reports `51/51`, `12/12`, `12/12`, `26/27`, `69`.
- `localization-report --package ringcentral-video --language es --require-complete` still exits `0`.
- `demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run` still fails with `Unsupported presenter language: es`.
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` still exits nonzero because runtime language support fails, while localization remains OK.

Quality gates:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_cli.py::test_doctor_require_localization_language_overrides_runtime_voice
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

## 交接提示

你是 Cycle 126 技术/实现 subagent。请把本轮当作 matching normalization hardening，不是 Spanish runtime promotion，也不是 alias vocabulary expansion。

先读：

- `src/ai_presenter/packages/models.py`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_diagnostics.py`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-125-experience.md`
- `docs/agent-handoffs/cycle-125-test-review.md`

实现建议：

- TDD-first：先写失败测试，覆盖 accent-folded alias match、Q&A match、tokenization、diagnostics duplicate。
- 只改 shared normalization 和直接依赖测试。不要通过新增 unaccented aliases 解决问题。
- 优先让所有 match/diagnostic normalized strings 共用一个 helper，避免 package aliases、Q&A prompts、runtime question text、legacy aliases 分裂。
- 使用标准库 `unicodedata.normalize("NFKD", text)` 并移除 combining marks 即可；不要引入新依赖。
- 观察 diagnostics count 是否变化。若变化，必须解释是 accent folding 揭示了真实 duplicate/substring risk，还是实现过度扩大了 normalization。
- 保持 `strip()` 语义和 current matching order。

主会话决策建议：

- 若目标是提升 Spanish package-local Q&A/控制发现体验：批准 accent-insensitive alias matching，这是最高价值。
- 若目标是降低后续维护误读：另开 docs hygiene slice，更新 `language-lifecycle.md` 和 `runtime-safety-routing.md` 的 Spanish/current counts。
- 不建议 Cycle 126 优先做 docs hygiene，因为当前已有用户可感知的无重音西语错路由风险。
