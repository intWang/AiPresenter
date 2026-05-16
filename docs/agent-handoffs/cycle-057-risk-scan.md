# Cycle 057 Risk Scan

## Scope

本轮风险扫描聚焦 `meeting-basics-demo` 的三段日语 narration 候选补齐：

- `show-mic`
- `show-participants`
- `show-chat`

只评估内容、测试计数和资料索引同步风险；不建议在本轮扩大到 `meeting-controls-tour`、`meeting-control-map-demo` 或 `questionAliases.ja`。

## Risks

- **当前内容与测试期望可能不同步。** 扫描时 `ai-presenter localization-report --package ringcentral-video --language ja` 仍输出 `4/51`，并显示 `meeting-basics-demo: 0/3 missing: show-mic, show-participants, show-chat`；但相关测试已经出现 `7/51`、`meeting-basics-demo: 3/3` 的期望。推进前必须确保 YAML 内容、CLI 报告、diagnostics 断言和 material package 断言一致。
- **Chat 隐私边界是最高风险点。** `ringcentral.video.toolbar.chat` 的 presenter notes 明确要求默认不朗读私人聊天内容；chat explainer 也保持“unless you ask”的边界。`show-chat` 的日语 narration 如果只说“打开聊天/发送消息”，容易被理解成可以展示或朗读聊天内容。
- **Participants 文案可能越界到身份信息。** Participants 相关 notes 允许说明人数、入口和控制区域，但要求不要在未验证和未获允许时识别参会者。日语文案应避免承诺朗读姓名、角色、私聊标签或参会者详情。
- **Mic 文案可能暗示状态修改。** `show-mic` 是 `point` 操作，风险低于打开面板，但日语 narration 仍应只表达“确认本地麦克风状态/发言前确认”，避免暗示会自动切换麦克风或影响他人音频。
- **报告计数容易漏改一处。** 本轮新增 3 个 localized steps 后，日语 demo narration 应从 `4/51` 变为 `7/51`，同时 `vbg-blur-demo` 保持 `4/4`、`meeting-basics-demo` 变为 `3/3`、Q&A 保持 `12/12`、`questionAliases.ja` 仍为 `0/27`。
- **资料包索引可能滞后。** `docs/knowledge/ringcentral-video/source-index.md` 仍描述日语只覆盖现有 Q&A 和四步 vbg blur demo。实现完成后应更新为“vbg blur + meeting basics”覆盖，否则后续 agent 会误判当前范围。
- **日语语气风险。** 三段话会被 live narration 朗读，应短、自然、职业化；避免过度直译英文控件说明，也避免使用过强的保证语气，例如“必ず聞こえます”“全員を確認できます”。

## Mitigations

- 只在 `packages/ringcentral-video.yaml` 的 `meeting-basics-demo` 三个现有 narration block 下新增 `localizedText.ja`，不改 action、entrypoint、placement、offset、openSteps、aliases 或 Q&A routing。
- `show-chat` 日语文案必须显式包含隐私默认值：聊天内容默认保持非公开；只有用户明确要求并且内容已确认时才读取。
- `show-participants` 日语文案只说明 Participants 面板可确认会议房间状态或参会概况，不承诺读取姓名、角色、私人标签或逐个识别参会者。
- `show-mic` 日语文案聚焦本地音声状态和发言前确认，不暗示自动切换设备、解除静音或控制其他参会者。
- 测试更新应覆盖 CLI localization-report、material package localization status 和 diagnostics require-localization failure detail，确保所有计数统一到 `7/51`。
- 资料索引更新只同步覆盖描述，不把日语 localization 标记为 complete；`--require-complete` 仍应失败。

## Must Verify

- `ai-presenter localization-report --package ringcentral-video --language ja` 输出：
  - `Localization report: 7/51 demo steps`
  - `- vbg-blur-demo: 4/4 narration localized`
  - `- meeting-basics-demo: 3/3 narration localized`
  - `- localized questions: 12/12`
  - `- localized answers: 12/12`
  - `questionAliases.ja present on 0/27 entrypoints (0 aliases)`
- `ai-presenter localization-report --package ringcentral-video --language ja --require-complete` 仍失败，并报告日语 localization incomplete。
- `tests/unit/test_material_packages.py` 中 Japanese localization status 断言与实际报告一致：`demo_localized_steps == 7`、`meeting-basics-demo == 3/3`、`required_localization_complete is False`。
- `tests/unit/test_cli.py` 中 Japanese localization report 断言与实际 CLI 输出一致。
- `tests/unit/test_diagnostics.py` 中 require-localization failure detail 报告 `7/51 demo steps`，同时 Q&A 仍为 `12/12`。
- 人工审读 `show-chat` 日语 narration，确认没有主动展示、总结或朗读聊天内容的表达。
- 人工审读 `show-participants` 日语 narration，确认没有默认朗读参会者姓名、角色或私人信息的表达。

## Recommendation

建议推进，但必须先完成内容与测试的同步。候选范围很小，且只增加 narration localization，不改变运行入口、操作动作、匹配逻辑或 alias routing；在 `show-chat` 和 `show-participants` 文案守住隐私边界、报告计数统一到 `7/51` 后，回归风险可控。
