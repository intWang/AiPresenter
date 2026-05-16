# Cycle 061 Demand Analysis: meeting-controls-tour / explain-report-issue JA narration

## 需求判断

建议单独为 `meeting-controls-tour` 的 `explain-report-issue` 增加日语 narration，并保持单步切片推进。

依据：

- 第060轮已把 `meeting-controls-tour` 的日语覆盖推进到前四个 top-bar 步骤；`docs/knowledge/ringcentral-video/source-index.md` 也记录当前日语覆盖停在 `meeting-controls-tour` 前四步。
- `packages/ringcentral-video.yaml` 中 `explain-report-issue` 当前英文 narration 已说明 Report 会打开 audio、video、screen sharing、joining、notes、transcript 或 other issues 的 troubleshooting dialog，并且该 dialog 会阻挡 meeting controls，需要关闭后再继续。
- 同一位置已有中文 `localizedText.zh`，但缺少 `localizedText.ja`，因此这是清晰、可验证、低范围的本地化缺口。
- 该步骤的动作是 `operation: open`，会打开 report/troubleshooting dialog，风险高于前四个纯说明或轻量 top-bar 控件；单独处理能集中审查隐私措辞、阻挡状态和关闭边界。

结论：应做，但不应顺手扩到后续 `explain-add-coworkers` 或其他 meeting controls tour 步骤。

## 用户价值

- 日语演示从 top-bar 基础说明自然延伸到故障反馈入口，减少第五步突然回退英文的体验断层。
- 日语用户能听懂 Report 的适用范围：音声、ビデオ、画面共有、参加、ノート、文字起こし、その他の問題。
- narration 可明确提示该窗口是升级反馈/故障报告入口，而不是自动诊断或自动提交问题。
- 该步骤会遮挡会议控制区，日语 narration 应同步说明讲解后需要关闭，降低用户误以为会议控制失效的困惑。

## 范围 / 非目标

范围：

- 仅为 `packages/ringcentral-video.yaml` 中 `meeting-controls-tour` / `explain-report-issue` 的 narration 增加 `localizedText.ja`。
- 保持现有英文、中文、`placement: during`、`actionOffsetMs: 450` 和 action 行为不变。
- 如测试需要，只覆盖该步骤对应的 localization 断言。

非目标：

- 不改 Report entrypoint locator、openSteps、cleanup 或 runtime action executor。
- 不添加新的日语 questionAliases、Q&A 或 report issue 问答路由。
- 不扩展后续 demo steps 的日语 narration。
- 不改变 dialog 内问题类型选择、提交按钮、附件、日志或任何可能发送反馈的行为。
- 不宣称已完成实际 RingCentral build 的手工验收。

## 隐私与状态边界

- Report/troubleshooting dialog 可能暴露问题类型、诊断上下文、会议相关元数据、notes/transcript 相关入口或用户输入区域；日语 narration 只说明入口和类别，不读取或总结可见字段值。
- 不应暗示 AiPresenter 会自动判断故障原因；没有观测值时仍应避免推断 audio/video/network 的具体原因。
- 不应自动选择类别、填写表单、上传日志、提交 report，或读取用户输入的 issue description。
- 该 dialog 会阻挡 meeting controls；演示路径应继续遵守“讲解后关闭再前进”的状态边界。
- 如果用户只是浏览控件，Report 步骤应停留在 explain/open/close 层面；任何真正提交反馈都需要用户明确请求。

## 验收口径

可接受结果：

- `meeting-controls-tour` 的 `explain-report-issue` 包含非空 `localizedText.ja`。
- 日语文本准确覆盖三点：Report 打开故障反馈/トラブルシューティング窗口；适用范围包含 audio/video/screen sharing/joining/notes/transcript/other issues；窗口会遮挡会议控制区，因此说明后需要关闭。
- 文案保持隐私安全：不读取会议值、不推断原因、不承诺提交、不指导自动选择或发送报告。
- JA demo narration 计数应从 `11/51` 增加到 `12/51`，`meeting-controls-tour` 从 `4/22` 增加到 `5/22`。
- 相关测试名可作为后续实现参考：
  - `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - `test_meeting_controls_tour_has_japanese_top_bar_narration`
  - `test_meeting_controls_tour_has_japanese_report_issue_narration`
  - `test_short_ringcentral_demo_flow_renders_chinese_narration_text` / `test_meeting_controls_tour_renders_chinese_narration_text` 仅作现有 localized narration 渲染模式参考，不要求本轮扩展中文。

## 后续建议

下一轮实现建议保持最小切片：只补 `explain-report-issue` 的 `localizedText.ja`，并运行 package localization 相关单测。若通过，再更新 source index 的 localization 覆盖描述，把 `meeting-controls-tour` 日语覆盖从“前四个 top-bar steps”调整为“前五个 top-bar/report steps”。

后续不要连续批量补完整 `meeting-controls-tour`。从 `explain-add-coworkers` 开始涉及邀请、人员、聊天、共享、reactions、leave 等不同隐私和状态风险，仍应按风险面分批做需求判断。
