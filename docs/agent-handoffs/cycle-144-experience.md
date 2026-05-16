# Cycle 144 Experience: RingCentral Video Evidence Boundary Guard

Date: 2026-05-17
Cycle: 144
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## 本轮优化主题和用户价值

本轮主题是收紧 RingCentral Video 资料包里的证据边界语言，并用一个窄测试守卫防止 `source-index.md` 继续引用不存在的 repo-local test 文件。

用户价值在于降低后续代理误读证据等级的概率：

- repo-local tests、CLI inspection、dry run、`doctor`、package schema 检查只能说明仓库内事实或本地行为假设，不等于 RingCentral 当前构建的 live acceptance。
- read-only observation 只能说明某个日期、构建、locale、DPI、窗口 bounds、角色和会议状态下观察到的 UI/window/UIA 元数据，不证明 click、toggle、cleanup、side effect 或无人值守 live operation 安全。
- validation checklist 和 runbook checkbox 是人工验收程序，不是证明；只有把实际人工/live 结果记录到 `acceptance-runs.md`，才可以作为 dated acceptance evidence。
- runtime readiness 是 AiPresenter profile/provider/language/voice/controller 侧的就绪边界，不自动升级为 RingCentral route、flow、language、profile 或 speech path 的 live acceptance。
- live acceptance 必须是 dated manual/live record，包含目标环境、route/flow、动作类型、cleanup、privacy notes 和 pass/fail 结果。

## 子代理衔接

需求分析先定义了要解决的问题：Cycle142/Cycle143 已经把 `entrypoints --language` 限定为 package-local display metadata inspection，本轮需要把同样的精确边界扩展到 RingCentral Video 资料包中的 repo/package inspection、read-only observation、validation checklist、runtime readiness 和 dated live acceptance。

技术扫描把需求落到可守卫的窄点：检查 `validation-checklist-index.md`、`evidence-index.md`、`acceptance-runs.md`、`source-index.md` 和 `runtime-safety-routing.md` 的关键边界句，并建议在 `tests/unit/test_material_packages.py` 增加相邻的 docs-contract assertion，而不是引入新 parser 或改 runtime 行为。

风险扫描补充了 no-go 语言：不能把 local test、dry run、CLI inspection、doctor、read-only UIA observation、manual checklist 或 runtime/provider readiness 写成 live RingCentral acceptance；也不能顺手改 package YAML、profile、provider、alias、Q&A、matcher、controller、cleanup mode 或 live evidence。

开发实现选择了更窄的 docs-plus-test guard：新增 `test_ringcentral_source_index_test_references_exist`，修正 `source-index.md` 中不存在的 `tests/unit/test_ringcentral_profile.py` 引用；新增 `test_ringcentral_knowledge_docs_preserve_evidence_boundaries`，把现有 durable boundary 句子固定住。

Review 验证了这一轮没有发现问题：聚焦四个 test 通过，`git diff --check` 无 whitespace error，且没有源码、package YAML、profile、runtime behavior、generated artifact 或 live acceptance 改动。

## 学到的经验和规则

1. `source-index.md` 里的 backticked test path 是可测试资产。以后新增 `tests/unit/*.py` 或 `tests/integration/*.py` 引用时，要保证文件真实存在；如果引用的是概念性覆盖而非具体文件，不要伪造路径。
2. repo-local tests 可以证明 package shape、link integrity、runtime factory/profile runner 假设、adapter fixture 或 dry-run style path，但不能证明 RingCentral 当前构建接受了某条 route。
3. read-only observation 的边界要一直带上上下文：build、locale、DPI、window bounds、role、meeting state。没有 action 和 cleanup 记录时，不能说 click-safe、toggle-safe、cleanup-safe 或 live-operable。
4. validation checklist 是 validation target，不是 validation result。`Accepted` 只能来自 `acceptance-runs.md` 中的 dated manual/live record。
5. runtime readiness 和 live acceptance 是两道门。OpenAI-backed Spanish runtime readiness、本地 provider rejection、controller/demo dry run 或 profile runner 测试，都不能替代 RingCentral live route acceptance。
6. `Accepted`、`Observed`、`Repo-tested` 这三个词要按资料包定义使用，避免用泛化的 `validated`、`ready`、`current evidence` 或 `safe to run live` 代替。
7. 自动化 baseline 是 repository baseline。它可以支持 repo confidence，但不能提升 route、flow、language、profile 或 speech path 的 acceptance 等级。
8. 如果以后要改变 live acceptance 声明，必须先有明确的人工作业、实际环境、隐私处理、cleanup 结果和 dated record；否则只能写成 backlog、procedure、repo-tested 或 observed。

## 下轮建议

1. 增加一个窄的 CLI 输出守卫：在现有 `validation-targets` 相关测试里断言输出仍包含 `repo-derived planning list only; not live acceptance evidence`，只验证 wording，不改 CLI 行为。
2. 增加一个 source-index 链接卫生检查：对 `docs/knowledge/ringcentral-video/source-index.md` 中 backticked `docs/knowledge/ringcentral-video/*.md` 引用执行存在性断言，范围只限该文件。
3. 做一次 docs-only wording scan，把 `validated`、`ready`、`current evidence`、`safe to run live` 这类词在 RingCentral Video 知识文档中归类为允许、需限定、或需替换，输出 handoff 即可，不声明 live acceptance。
4. 若要扩展测试，优先扩展 docs-contract assertion，不新增 runtime 行为、不改 package YAML、不改 profile/provider，不运行或记录 live acceptance。

## 验证和提交注意事项

- 不要 stage `.coverage`。本轮状态里 `.coverage` 是并发或既有 dirty artifact，不属于 Cycle144 经验沉淀。
- 每轮 commit 前先确认 scope：`git status --short` 应只包含预期文件和已知无关 dirty artifact。
- 每轮 commit 前跑完整验证，而不是只跑本轮 focused tests：
  - full pytest
  - ruff
  - mypy
  - diff check
- 至少保留本轮 focused check 作为局部验收：
  - `tests/unit/test_material_packages.py::test_ringcentral_source_index_test_references_exist`
  - `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_preserve_evidence_boundaries`
  - `tests/unit/test_material_packages.py::test_ringcentral_validation_checklist_covers_package_routes`
  - `tests/unit/test_material_packages.py::test_ringcentral_knowledge_docs_are_registered_in_navigation_indexes`
- 提交前复查 `git diff --check`。如果出现 LF/CRLF warning 但 exit code 为 0，需要在最终说明中区分 warning 和 whitespace error。
