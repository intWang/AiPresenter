# Cycle 126 Experience: Accent-Insensitive Match Normalization

Date: 2026-05-17

## 本轮结论

Cycle 126 的核心经验是：无重音西语输入不是 alias 词表缺口，而是 matching normalization 边界问题。正确修复点是在比较文本时生成一致的 match key，让 package aliases、Q&A prompts、runtime question text、diagnostics indexes 和 token fallback 对拉丁重音采用同一套保守折叠规则，同时保留原始 authored text。

这轮不应被理解为 Spanish runtime promotion。Spanish 仍是 package-local localization/Q&A/alias 能力，`--language es` 仍然 unsupported。normalization 只是让用户自然输入如 `configuracion`、`reunion`、`boton`、`camara` 能命中已经策划好的西语内容。

## Matching Normalization 的边界

本轮 normalization 的边界要窄而一致：

- 保留 `strip()` 和 `casefold()` 语义。
- 只在 match key 上折叠拉丁字母重音和组合音标。
- 不改 package YAML 的 alias 原文，不把 accented/unaccented 变体写回词表。
- 不做翻译、同义词、词干化、编辑距离、语义检索或 LLM intent routing。
- 不做中文/日文罗马化、转写、ASCII-only 清洗或宽窄字符归并。
- 不改变 matching precedence、`questionPolicy`、`_can_operate()`、open steps、cleanup、locators、demo flow 或 runtime language support。

实现上最重要的约束是“存储文本”和“比较 key”分离。`EntrypointQuestionAlias.alias` 继续保留作者写下的 accented Spanish 文本；`normalized_alias` 成为 runtime/diagnostics 使用的 canonical match key。这样既保护可读性和本地化质量，也避免靠复制无重音 alias 扩词表制造 YAML 噪声。

## 为什么 Runtime 与 Diagnostics 要共用 Match Key

runtime 和 diagnostics 必须共享同一个 canonicalizer。否则会出现最危险的分裂：用户输入在 runtime 中已经被折叠并命中某个 entrypoint，但 doctor 仍以旧 key 判断，漏报 duplicate、Q&A overlap 或 substring risk。

典型风险包括：

- `cámara` 与 `camara` 在 runtime 等价，但 diagnostics 不等价，会漏掉跨 entrypoint alias collision。
- unaccented Q&A prompt 在 runtime 可能 Q&A-first，diagnostics 若不用同 key，就无法发现 Q&A 与 alias 的 exact overlap。
- `grabación`、`transcripción`、`reacción`、`levantar la mano` 这类 safety-adjacent intent 如果只扩 alias matching，不扩 Q&A/diagnostic matching，用户问题可能绕过 authored Q&A。

因此本轮最终经验是：match key 不是某个调用点的局部实现细节，而是 package model 的行为契约。runtime route、Q&A exact/fragment、package alias substring、legacy alias precompute、tokenization 和 doctor indexes 都应依赖同一条 normalization 路径；doctor 报告仍展示原始 alias/prompt 和 language 信息，便于人工审查。

## 无重音西语与 Q&A-First 的关系

无重音西语会扩大 alias 可命中的输入面，这本身有价值，但也会放大短词和通用词的误路由风险，例如 `menu`、`boton`、`mas`、`reunion`、`grabacion`、`transcripcion`。所以 Q&A-first 不是附带行为，而是安全边界。

本轮需要保护的顺序仍然是：

1. Q&A exact match。
2. recording / notes / transcript 等 safety Q&A heuristics。
3. Q&A fragment/token matching。
4. package-owned entrypoint aliases。
5. legacy aliases。
6. entrypoint token scoring。

经验点：如果 alias matching 支持 `camara` 命中 `cámara`，Q&A matching 至少也要支持 `grabacion` 命中 `grabación`。否则用户问“如何安全处理录制”这类问题时，Q&A 可能 miss，然后落到更宽的 control alias。无重音西语修复必须包含 Q&A-first regression，尤其是 recording、chat/participants privacy、shared-screen content、notes/transcript、reaction/raise-hand 这几类安全问题。

## 未来语言扩展建议

后续扩展到法语、葡语、德语等拉丁脚本语言时，可以沿用本轮“保守拉丁重音折叠”的思路，但不要默认扩大到所有 Unicode normalization 行为。新增语言前建议先确认：

- runtime alias matching 是否仍是 language-agnostic；如果是，diagnostics 必须继续做全局 cross-entrypoint duplicate 检查。
- 该语言中去重音是否会改变词义或制造高频短词 collision。
- Q&A prompts 是否与 aliases 使用同一 match key。
- diagnostic 输出是否足够呈现 language、entrypoint、原始文本和 folded key，方便人工判断是合理本地变体还是真实冲突。
- 不要用新增 unaccented alias 代替 canonicalizer；词表应该表达作者意图，normalization 负责输入容错。

对中文/日文等非拉丁脚本，继续保持“不转写、不罗马化、不 ASCII 过滤”的边界。已有 CJK exact substring 和 Q&A-first 行为应由回归测试保护。

## 文档卫生建议

本轮主线是用户可感知的 routing 修复，不建议把 durable docs cleanup 混进同一改动。后续可以单独开 docs-only slice，更新这些容易误导后续维护者的旧状态：

- `docs/knowledge/language-lifecycle.md` 的 Spanish current state 仍可能停留在 Cycle 123 partial/sparse alias 叙述。
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md` 仍可能记录旧 alias/Q&A counts，需要同步 Cycle 125/126 的 package-local Spanish 状态。

文档更新时要明确区分三件事：Spanish localization complete、Spanish package aliases/Q&A usable、Spanish runtime presenter language unsupported。不要把 localization-report 通过误写成 runtime language enabled。

## 保留的验证命令

建议保留本轮最终验证组合，先跑受影响单测，再跑 CLI 边界和静态检查：

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language
.\.venv\Scripts\ruff check --no-cache src\ai_presenter\packages\models.py src\ai_presenter\runtime\questions.py tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_diagnostics.py
.\.venv\Scripts\mypy --no-incremental src tests
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
git diff --check
git status --short
```

期望边界：

- affected unit tests pass。
- doctor baseline 保持 `0 warnings, 0 failed`，除非 folded key 暴露真实 collision；若发生变化，应审查具体 alias/Q&A pair，而不是降低 severity。
- localization-report 仍显示 Spanish package-local 完整度，例如 `51/51` narration、`12/12` Q&A questions、`12/12` Q&A answers、`26/27 (69 aliases)`。
- `demo --language es --dry-run` 仍失败，并包含 `Unsupported presenter language: es`。
- 不 stage、不提交，不纳入 `.coverage` 等本地 artifact。
