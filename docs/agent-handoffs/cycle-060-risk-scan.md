# Cycle 060 Risk Scan

## Scope

审视给 `meeting-controls-tour` 前段步骤补日语 narration 的风险，候选步骤为：

- `meeting-overview`
- `explain-meeting-info`
- `explain-network-quality`
- `explain-view-layout`

本扫描只评估内容、隐私、状态影响和验证风险；不建议本轮扩大到后续 toolbar、recording、notes、invite、chat、participants 等更高风险步骤。

## Risks

- **会议信息隐私风险最高。** `explain-meeting-info` 会打开 host、Meeting ID、copy link、dial-in information、encryption status 等内容。日语 narration 如果说成“確認できます/共有できます/コピーします”，容易越界为读取、公开或转发会议号和链接。应保持“入口说明 + 默认私密 + 未经用户明确要求不读出”的边界。
- **Network quality 不应推断原因。** `explain-network-quality` 只允许说明 packet loss、jitter、latency 等诊断值的位置。日语文案如果说“原因はネットワークです”“音声不良の原因を特定できます”，会从可观察指标越界到未经验证的故障归因。
- **View layout 是本地视图说明，不应改变会议状态。** `explain-view-layout` 的 action 是打开 `Views` 菜单。日语 narration 应说明 Gallery view、Full screen 等只影响本地显示；避免暗示会改变其他参会者视图、角色、会议内容或通话状态。
- **Overview 容易把能力讲得过满。** `meeting-overview` 是 `operation: explain`，不打开敏感面板。风险较低，但日语文案仍应只描述 meeting canvas、top bar、bottom toolbar 的组织方式，不承诺识别身份、读取 private content 或自动操作会议控制。
- **当前工作区存在内容/测试同步风险。** 扫描时 `tests/unit/test_material_packages.py` 已出现 `demo_localized_steps == 11` 和 `test_meeting_controls_tour_has_japanese_top_bar_narration`，但 `packages/ringcentral-video.yaml` 的候选四步片段仍只看到 `localizedText.zh`，未看到对应 `localizedText.ja`。如果这是并行修改的中间态，推进前必须先消除 YAML、测试和 CLI 报告之间的不一致。
- **计数变化容易漏改。** 若只补这四步，日语 demo narration 应从上一轮总结的 `7/51` 变为 `11/51`，并且 `meeting-controls-tour` 应为 `4/22`。任何 `--require-complete` 仍应失败，因为完整日语 demo localization 还未完成。
- **编码与人工审读风险。** 近期 handoff 中出现过 Windows console 非 ASCII 输出问题；日语文案和测试断言应避免依赖会在控制台乱码的未转义错误详情，同时人工审读必须使用 UTF-8 视图确认真实日文内容。

## Mitigations

- 只在四个现有 narration block 下新增 `localizedText.ja`；不改 action、entrypointId、operation、placement、actionOffsetMs、openSteps、aliases、Q&A 或 runtime 逻辑。
- `meeting-overview` 日语文案保持概览性质：说明上方栏、下方工具栏和会议画布的区域，不加入隐私内容读取或控制承诺。
- `explain-meeting-info` 日语文案必须明确：Meeting ID、链接、拨入信息等默认视为非公开信息；除非用户明确要求且内容已确认，否则不读出、不复制、不分享。
- `explain-network-quality` 日语文案只说“查看诊断指标/确认数值的位置”；如提到不稳定，只能说“用于确认指标”，不能推测根因或保证能定位故障。
- `explain-view-layout` 日语文案明确“本地显示/自分の画面”边界；避免“改变会议/影响其他参会者”的表达。
- 测试应覆盖四步均有非空 `localizedText.ja`，并专门断言 meeting info 含隐私边界、network quality 不含原因断定、view layout 含本地显示/不影响他人边界。
- 若当前测试已提前改到 `11/51`，实现者应先确认 YAML 是否也已经补齐；不要让 repository 保持“测试期待已变、包内容未变”的半完成状态。

## Must Verify

- 人工审读四段日语 narration，确认语气自然、简短、适合朗读，且没有主动读取会议号、会议链接、拨入信息、参会者身份或私人内容。
- `explain-meeting-info` 文案包含明确隐私边界：未获用户明确要求时不读出 Meeting ID、链接或拨入信息。
- `explain-network-quality` 文案没有“原因是”“特定できます”“必ず改善”之类未经验证的诊断或保证。
- `explain-view-layout` 文案明确只影响本地显示，不影响其他参会者或会议状态。
- `ai-presenter localization-report --package ringcentral-video --language ja` 应显示 `11/51 demo steps`，`meeting-controls-tour: 4/22 narration localized`，Q&A 仍为 `12/12`，`questionAliases.ja` 仍为 `3/27 entrypoints (9 aliases)`。
- `ai-presenter localization-report --package ringcentral-video --language ja --require-complete` 仍应失败，并报告 Japanese localization incomplete。
- 相关 unit tests 应与实际 YAML 一致：material package status、CLI localization report、diagnostics failure detail 不应出现 `7/51` 与 `11/51` 混用。
- 确认没有修改 runtime 行为：四步仍是原来的 `explain/open` 操作，`view layout` 只是打开视图菜单，不自动选择 Gallery、Full screen 或其他布局项。

## Recommendation

建议推进，但只推进这四个前段步骤，并把它视为 package-content-only 的小切片。该范围风险可控：一个 overview、三个 top-bar explain/open 步骤，且不触发实际会议状态修改。推进条件是先守住 meeting info 隐私边界、network quality 不猜测原因、view layout 只讲本地视图，并在合入前消除当前工作区显现的 YAML/测试/报告计数同步风险。

## Changed Files

- `docs/agent-handoffs/cycle-060-risk-scan.md`
