# Cycle 058 Demand Analysis

## 本轮需求判断

建议为 RingCentral Video meeting basics 相关的 3 个基础 toolbar entrypoint 小范围新增 `questionAliases.ja`，但不要扩大到全量 27 个入口。

推荐范围仅限：

- `ringcentral.video.toolbar.audio`
- `ringcentral.video.toolbar.participants`
- `ringcentral.video.toolbar.chat`

理由是第057轮已经把 `meeting-basics-demo` 的日语 narration 推进到 `7/51`，其中正好覆盖麦克风、Participants、Chat 三个基础演示步骤；但 `questionAliases.ja` 仍为 `0/27`。这会造成一个体验落差：日语用户如果用自然问法说“麦克风在哪里”“参加者在哪里”“チャット在哪里”，系统仍缺少包内日语 alias 来稳定路由到对应入口。

本轮需求侧结论是：这 3 个 alias 对日语用户价值明确、范围足够小、可验收；但 Chat 和 Participants 必须只被定义为“定位入口”的问题匹配能力，不能扩展成读取或总结面板内容的能力。

## 用户价值

- 麦克风入口：日语用户常用 `マイク`、`ミュート`、`音声` 来询问本地音频控制。新增 alias 能把“マイクはどこ”“ミュートはどこ”稳定映射到 `ringcentral.video.toolbar.audio`，帮助用户确认发言前的本地音频状态。
- Participants 入口：日语用户可能同时使用产品英文 `Participants`、日语外来词 `参加者`、较自然的 `参加者一覧` 或 `誰が参加しているか`。新增 alias 能帮助用户找到参会者面板入口，尤其适合会议刚开始时确认房间状态。
- Chat 入口：`チャット` 是日语 RingCentral Video 场景中最自然的控件问法。新增 alias 能让“チャットはどこ”“メッセージはどこ”直接定位到 `ringcentral.video.toolbar.chat`，减少用户从英文控件名推断入口的负担。

## 隐私边界

Chat 和 Participants 是本轮的主要需求风险点。alias 只能提高“入口定位”的命中率，不应改变 AiPresenter 对私密内容的默认处理。

- `ringcentral.video.toolbar.chat`：alias 命中后可以打开或指向 Chat 入口，但不能默认朗读、概括、翻译、复述聊天消息。只有用户明确要求，并且内容来源已验证且权限允许时，后续能力才可处理具体聊天内容。
- `ringcentral.video.toolbar.participants`：alias 命中后可以打开或指向 Participants 入口，也可以解释这是查看参会概况的面板；但不能默认朗读参会者姓名、角色、标签、搜索结果或私密身份信息。
- `ringcentral.video.toolbar.audio`：alias 命中后只应帮助定位本地麦克风控制。由于该入口会影响本地会议状态，别把 alias 文案写成“自动解除静音”或“切换设备”的承诺。

需求侧建议把实现验收集中在匹配与文案审读上，而不是让 alias 触发新的内容读取行为。

## 推荐 alias 词形

建议保持每个入口 3-4 个短 alias，优先覆盖高频自然问法和控件名，不加入长句、隐私内容请求或容易跨入口误判的泛词。

### `ringcentral.video.toolbar.audio`

推荐：

- `マイク`
- `ミュート`
- `音声`
- `マイクはどこ`

不建议：

- `録音`: 容易误导到 recording。
- `スピーカー`: 更接近音频设备或 audio menu，不应在本轮塞进基础 mute 入口。
- `全員をミュート`: 涉及主持人控制和他人状态，不属于本地麦克风入口。

### `ringcentral.video.toolbar.participants`

推荐：

- `参加者`
- `参加者一覧`
- `誰が参加しているか`
- `Participants`

不建议：

- `名前を読んで`: 这是读取身份信息请求，不是入口定位 alias。
- `参加者名`: 容易暗示默认朗读姓名。
- `出席者全員`: 可能被理解为枚举完整名单，超出本轮安全边界。

### `ringcentral.video.toolbar.chat`

推荐：

- `チャット`
- `メッセージ`
- `チャットはどこ`
- `Chat`

不建议：

- `チャットを読んで`: 这是读取私密内容请求，不应作为入口 alias。
- `メッセージ内容`: 暗示读取内容。
- `未読メッセージ`: 可能涉及状态或内容读取，不属于只定位入口。

## 验收口径

实现轮建议以以下口径验收：

- 只在 `packages/ringcentral-video.yaml` 的 3 个候选 entrypoint 下新增 `questionAliases.ja`，不新增第 4 个 entrypoint，不碰全量 27 个入口。
- `questionAliases.ja` present count 应从 `0/27` 变为 `3/27`；总 alias 数应等于实现中新增的日语 alias 数。
- 日语 demo narration 仍应保持第057轮后的 `7/51`，Q&A 仍应保持 `12/12` questions 和 `12/12` answers；本轮 alias 不应被描述为日语 localization complete。
- `--require-complete` 对 `ja` 仍应失败，因为 meeting controls narration 和大多数 entrypoint alias 仍未覆盖。
- 人工审读确认 Chat alias 没有包含“读取聊天内容”的词形，Participants alias 没有包含“朗读姓名/角色/名单”的词形。
- 回归问法至少覆盖：
  - `マイクはどこ` -> `ringcentral.video.toolbar.audio`
  - `参加者はどこ` 或 `参加者一覧` -> `ringcentral.video.toolbar.participants`
  - `チャットはどこ` -> `ringcentral.video.toolbar.chat`

## 后续建议

- 如果第059轮进入实现，建议只改 YAML 和对应 localization/report 测试，避免顺手扩展到 audio menu、invite、notes/transcript 或 map demo。
- 如果后续继续推进 `questionAliases.ja`，应按“低隐私入口优先、状态改变入口谨慎、内容读取入口单独评审”的顺序分批，而不是一次性补齐 27 个入口。
- Chat/Participants 的后续任何日语 Q&A 或 narration 扩展，都应复用本轮边界：可以帮用户找到入口，但默认不读取私密内容。
