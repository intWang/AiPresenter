# Cycle 057 Demand Analysis

## 本轮需求判断

建议本轮补齐 `meeting-basics-demo` 的日语 narration。

理由是第056轮已经把日语 demo narration 从 0 起步推进到 `vbg-blur-demo`，而 `docs/knowledge/ringcentral-video/source-index.md` 仍明确记录“其他 demo-flow narration 仍是 future work”。`meeting-basics-demo` 只有三步，且覆盖实时会议中最基础、最常用、风险较低但价值很高的动作：麦克风、参与者、聊天。它是比完整 `meeting-controls-tour` 更适合继续推进日语覆盖的小切片。

## 用户价值

- 面向日语演示者，能用日语自然解释会议开始后最常见的三个入口，降低英语 narration 打断演示节奏的概率。
- 麦克风步骤帮助演示者确认本地音频状态，强调发言前的可听性检查。
- Participants 步骤帮助演示者确认会议房间状态和参会概况，但不默认朗读姓名、角色或其他身份信息。
- Chat 步骤帮助演示者说明文字协作通道，同时把隐私边界放进默认话术：不朗读聊天内容，除非用户明确要求且内容已经验证。

## 建议范围

- 只为 `packages/ringcentral-video.yaml` 中 `meeting-basics-demo` 的三步 narration 增加 `localizedText.ja`：
  - `show-mic`
  - `show-participants`
  - `show-chat`
- 不改变英文原文、中文 narration、entrypoint、openSteps、cleanup、action placement 或 action offset。
- 不新增或修改测试，除非实现 subagent 发现已有日语 coverage 报告需要同步验收。
- 不扩大到 `meeting-controls-tour` 或 entrypoint `questionAliases.ja`。

## 验收口径

- `meeting-basics-demo` 三个 step 均存在非空 `localizedText.ja`。
- 日语文本应是可直接朗读的自然演示话术，而不是逐词翻译。
- `show-chat` 日语 narration 必须包含隐私默认值：聊天内容不应默认朗读；只有用户明确要求且内容已验证时才可继续。
- `show-participants` 日语 narration 不应承诺读取参会者姓名、角色或私人信息；只说明入口和可用于确认房间状态。
- `show-mic` 日语 narration 应围绕本地麦克风状态和发言前确认，不暗示可随意改变他人状态。
- 现有中文 localization 相关测试应保持通过；如果有 localization report，则应体现 `meeting-basics-demo: 3/3 narration localized`。

## 后续扩展建议

- 下一步可考虑为 `meeting-controls-tour` 做分段日语覆盖，但应按风险分组推进：先 explain-only 控制，再处理会改变会议状态的动作。
- 可单独规划 `questionAliases.ja`，让日语用户问题更稳定地路由到麦克风、Participants、Chat 等入口。
- 对 Chat、Participants、Invite、Meeting information、Notes/Transcript 等敏感表面，继续把“只解释入口，不默认朗读私人内容”作为日语 narration 和 Q&A 的一致原则。
- 若后续新增自动验收，建议把短 demo flow 的日语覆盖率作为逐轮目标，而不是一次性要求所有 51 个 demo step 完整日语化。
