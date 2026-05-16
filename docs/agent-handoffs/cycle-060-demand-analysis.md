# Cycle 060 Demand Analysis: Japanese Narration Slice for Meeting Controls Tour

## 需求判断

建议方向成立，但需要先校准当前仓库状态。

本轮目标是评估是否应为 RingCentral Video `meeting-controls-tour` 选择一个低风险小切片补日语 narration。按 `docs/knowledge/ringcentral-video/source-index.md` 的覆盖说明，Japanese demo narration 仍是后续工作重点；该文件同时强调当前 package 覆盖最强的是 in-meeting attendee controls，敏感入口需要继续保持隐私边界。

不过，当前仓库已经不再是 `meeting-controls-tour` 0/22 的状态。`tests/unit/test_material_packages.py` 里已有 `test_meeting_controls_tour_has_japanese_top_bar_narration`，并断言 `meeting-controls-tour` 前 4 个步骤具备 `localizedText.ja`；同文件的 localization status 断言也显示 `meeting-controls-tour` 为 4/22，JA demo 总覆盖为 11/51。也就是说，如果本轮需求背景里的 0/22 是排期前状态，那么推荐的小切片已经落在当前工作树中。

结论：如果要做“低风险小切片”，应以 `meeting-controls-tour` 前 4 个 top-bar explain/open 步骤为边界；如果以当前仓库为准，本轮不建议再追加 YAML 改动，而应把下一轮实现目标改成补齐验证、文案复核或选择下一段更谨慎的切片。

## 推荐切片

推荐切片是 `meeting-controls-tour` 的前 4 步：

- `meeting-overview`，`ringcentral.video.overview`，`operation: explain`
- `explain-meeting-info`，`ringcentral.video.top.meeting-info`，`operation: open`
- `explain-network-quality`，`ringcentral.video.top.network-quality`，`operation: open`
- `explain-view-layout`，`ringcentral.video.top.views`，`operation: open`

选择这 4 步的原因：

- 它们位于 tour 开头，能自然把日语用户带入会议界面结构。
- `meeting-overview` 是 explain-only，不执行 UI 动作。
- `meeting-info`、`network-quality`、`views` 只是打开信息或布局菜单，不会发送邀请、读取聊天、改变麦克风/摄像头、举手、录制、离会或启动 notes/transcript。
- `views` 仅改变本地显示布局，不改变会议成员、媒体或共享状态。
- 这 4 步已有对应测试名保护，适合作为小切片验收口径。

不建议本轮直接扩大到第 5 步之后：

- `explain-report-issue` 会打开 blocking dialog，虽然可清理，但交互风险高于 top-bar 只读信息入口。
- `explain-add-coworkers`、`explain-invite` 会进入邀请流，可能出现联系人、建议列表、链接等私密内容。
- `explain-participants` 和 `explain-chat` 涉及姓名、角色、消息和私聊内容，即使只讲入口，也更需要隐私文案和测试覆盖。
- `explain-microphone`、`explain-camera`、`explain-raise-hand` 等步骤靠近真实会议状态变更，不适合作为本轮“低风险补 narration”的首选。

## 用户价值

这 4 步能让日语用户先获得完整 tour 的开场体验，而不是在进入 controls tour 后回落到英文旁白。

用户可以用日语理解：

- 会议窗口的控制地图：顶部状态区、中央会议画布、底部工具栏。
- 会议详情入口能说明哪些内容存在，但默认不朗读 Meeting ID、链接、拨入信息等私密值。
- 网络质量入口用于排查 packet loss、jitter、latency。
- Views 入口只影响本地视图布局，不会影响其他参会者或会议状态。

这是一段“说明能力”优先的增量，能提升日语导览连贯性，同时不会把 AiPresenter 推向敏感读取或状态操作。

## 隐私边界

本切片应保持以下边界：

- `meeting-info` 只说明入口和字段类型，不朗读 host、Meeting ID、copy link、dial-in、encryption 具体值，除非用户明确要求且内容已验证。
- `network-quality` 可以解释诊断指标位置和用途，但不在无观察值时推断故障原因。
- `views` 只说明本地 layout 效果，不声称改变参会者、媒体状态或会议成员。
- 不读取聊天消息、参会者姓名、联系人建议、邀请链接、共享屏幕内容、notes/transcript 内容。
- 不点击会改变会议状态的动作，例如发送邀请、开始共享、举手、录制、开启 notes、离会、切换麦克风或摄像头。

## 验收口径

如果从“尚未实现”视角验收该切片，建议口径如下：

- `meeting-controls-tour` 前 4 个 step 都存在 `narration.localizedText.ja`。
- 日语文案非空，包含日文字符，且保留必要产品词，例如 `RingCentral Video`、`Meeting ID`、`Network quality`、`Views`。
- `explain-meeting-info` 的日语文案明确“不主动朗读/默认不读出”私密会议值。
- `explain-view-layout` 的日语文案明确不会影响其他参会者或会议状态。
- localization status 中 `meeting-controls-tour` 的 JA 覆盖从 0/22 或旧值提升到 4/22。
- 相关测试名应覆盖：
  - `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage`
  - `test_meeting_controls_tour_has_japanese_top_bar_narration`

以当前仓库为准，上述验收口径已经被测试名和断言表达；本分析轮不运行测试、不修改 YAML。

## 后续建议

下一轮如果继续补 `meeting-controls-tour`，建议不要简单按顺序补到邀请、参会者和聊天。更稳妥的第二切片可以二选一：

- 继续补 explain-only 或 point-only 的低风险步骤，例如 `explain-microphone`、`explain-camera`、`explain-recording`、`explain-leave`，但文案必须强调“不自动切换/不点击/不开始”。
- 或先为 participants/chat/invite 设计隐私文案验收，再补 narration，确保不读取姓名、消息、私聊、联系人建议或邀请链接。

若当前目标只是让 `meeting-controls-tour` 从 0/22 起步，建议把本轮实现交给已有的前 4 步 top-bar slice；若当前目标是推进 4/22 之后的覆盖，则建议另开一轮需求分析，专门评估 participants/chat/invite 与 media controls 的隐私分层。

## Files Changed

- `docs/agent-handoffs/cycle-060-demand-analysis.md`
