# Cycle 058 Risk Scan: RingCentral Video Japanese Question Aliases

## Scope

本轮候选是 question alias routing，不是 narration。只评估给以下三个 RingCentral Video entrypoint 增加 `questionAliases.ja` 的风险：

- `ringcentral.video.toolbar.audio`
- `ringcentral.video.toolbar.participants`
- `ringcentral.video.toolbar.chat`

重点风险：Chat 或 Participants 相关隐私问题被 alias fragment matching 路由到入口，而不是命中 answer-only 的隐私边界 Q&A。

## Runtime Findings

- `answer_question()` 的顺序是：先 `_match_qa()`，再 `_match_entrypoint()`，最后才返回 no-match。exact Q&A 会优先于 alias，但非 exact 的输入会进入 Q&A fragment/token fallback，再进入 entrypoint alias fallback。
- package-owned aliases 在 `_match_package_entrypoint_alias()` 中按长度降序匹配，只要 `alias.normalized_alias in normalized_question` 就返回 entrypoint。因此日语 alias 一旦过短或语义过宽，会命中包含该片段的隐私问题。
- Q&A fragment 对 answer-only 项有保护：如果输入足够具体，或没有 entrypoint match，则可以命中 Q&A；但如果用户输入很短，且同时包含 alias，可能直接走 entrypoint alias。
- `_is_entrypoint_title_lookup()` 只保护英文 `where is` / `where are` + entrypoint title 的定位问题；它不会保护日语定位问法，也不会区分日语“位置查询”和“可否读内容/姓名”的隐私边界问题。
- `_can_operate()` 当前只把 meeting-info 强制 explain-only，并通过英文 risky words 判断是否可操作。`Chat panel` 和 `Participants panel` 不含 risky words，alias 路由后很可能 `can_operate=True`，会打开面板；`Microphone control` 因 purpose 含 `Toggle` 和 `mute`，通常会保持 `can_operate=False`，风险低于 Chat/Participants。

## Risk List

- **High: Chat 隐私 Q&A 被短 alias 截走。** 现有 Q&A `Can the presenter read meeting messages or participant names?` 的日语问题是“チャット内容や参加者名を読み上げられますか”，应该 answer-only。如果给 Chat 增加过短 alias，例如 `チャット`，且 Q&A exact 文案没有覆盖用户变体，例如“チャットを読めますか”“チャット内容を読んで”，runtime 可能先未命中 Q&A，再由 alias fallback 返回 `ringcentral.video.toolbar.chat`。
- **High: Participants 隐私 Q&A 被短 alias 截走。** 同一 Q&A 覆盖 participant names，host-controls Q&A 也明确“不读姓名和角色、不自动静音/移除/锁定”。如果 Participants aliases 包含 `参加者`、`参加者名`、`誰がいる` 这类片段，用户问“参加者名を読み上げられますか”或“参加者の名前を教えて”可能被当作 Participants panel 路由。
- **Medium: host/control 问题从 Q&A 变成 panel open。** `Where are host controls for participants?` 有日语 Q&A“主催者は参加者を管理するにはどうすればいいですか”。如果 alias 覆盖 `参加者` 或 `主催者`，某些非 exact 变体可能绕过 Q&A 的限制语言，直接打开 Participants。
- **Medium: diagnostics 覆盖不足。** `question aliases` 只抓跨 entrypoint 的 normalized duplicate；`qa alias overlap` 只抓 exact normalized Q&A prompt 与 alias 完全相同的 overlap。它不会发现 alias 是 Q&A prompt 的子串，也不会发现“チャット”出现在隐私 Q&A 里但不是完整 prompt。
- **Low: Audio alias 风险较小但仍需防误触。** Audio Q&A `How do I make sure my audio and video are ready?` 已有关联 `audio/audio-menu/video/video-menu`，且 audio entrypoint 一般不可操作。但日语 alias 如 `ミュート`、`マイク` 仍应验证“マイクをオンにして”“ミュート解除して”不会给出可操作 toggle 路径或暗示自动改变会议状态。

## Mitigations

- 只添加 location/intention 明确的日语 aliases，避免把 privacy/action wording 放进 alias：
  - Chat 候选应偏向“Chat はどこ”“チャットパネル”“チャットの場所”，避免只用 `チャット` 作为唯一依赖，也避免 `チャット内容`、`読む`、`読み上げ`、`メッセージ内容`。
  - Participants 候选应偏向“Participants はどこ”“参加者パネル”“参加者一覧の場所”，避免 `参加者名`、`名前`、`役割`、`管理`、`ミュート`、`削除`、`ロック`。
  - Audio 候选应偏向“マイクの場所”“マイクボタン”“音声状態”，避免 `ミュート解除して`、`オンにして` 等明确状态变更请求。
- 在新增 alias 的同一轮补充 runtime regression，而不是只更新 YAML：
  - 日语 Chat/Participants 隐私问题必须继续 `entrypoint_id is None`、`can_operate is False`，并返回日语隐私 Q&A 答案。
  - 日语 location 问题才应路由到对应 entrypoint；Chat/Participants route 可打开面板，但回答必须仍只说明入口。
  - Audio 状态变更类问法必须不可操作，且不能承诺自动 toggle。
- 增加或手工执行一个 substring-collision 探针：对每个新增 `questionAliases.ja`，检查它是否是任意 answer-only Q&A 日语 prompt 的子串，尤其是 chat/participant/privacy/host-controls 项。现有 doctor 的 exact overlap 不足以拦住本轮最高风险。
- 若不改 runtime，本轮应把 alias 集控制在最小集合：每个目标 entrypoint 先加 1-2 个强 location alias，验证通过后再扩大。

## Must Verify

- `pytest tests/unit/test_questions.py -k "japanese or chat or participants or audio or alias"`。
- `pytest tests/unit/test_diagnostics.py -k "question_aliases or qa_alias_overlap"`，并更新期望计数：新增 3 个 entrypoint 的 `questionAliases.ja` 后，RingCentral package-owned aliases 应从 `53` 增加到新增 alias 总数对应的值，Japanese alias coverage 应从 `0/27` 变为 `3/27`。
- `pytest tests/unit/test_material_packages.py -k "localization_status or question_aliases or ringcentral_package_owns"`，确认 `questionAliases.ja` coverage 和 alias index 正确。
- 必须新增/确认以下行为探针：
  - “チャット内容や参加者名を読み上げられますか”仍命中 answer-only 隐私 Q&A。
  - “チャットを読めますか”“チャット内容を読んで”“メッセージを読めますか”不路由到 `ringcentral.video.toolbar.chat`。
  - “参加者名を読み上げられますか”“参加者の名前を教えて”“参加者の役割を読めますか”不路由到 `ringcentral.video.toolbar.participants`。
  - “主催者は参加者を管理するにはどうすればいいですか”仍返回 host-controls Q&A，而不是直接打开 Participants。
  - “チャットはどこですか”“参加者パネルはどこですか”“マイクボタンはどこですか”分别路由到 Chat、Participants、Audio。
  - “マイクをオンにして”“ミュート解除して”不可操作，不自动切换会议媒体状态。
- 手工或脚本确认新增日语 aliases 不与现有 ja Q&A prompts exact overlap，也不作为 answer-only privacy prompts 的危险子串出现，除非对应测试证明 Q&A 优先。

## Recommendation

建议谨慎推进，但不建议一次性加入宽泛日语短 alias。可接受的推进条件是：只加 location-only aliases，并在同一轮补齐上述隐私和定位回归。Chat 与 Participants 的短词 alias 是本轮最高风险；如果没有 substring-collision 测试，建议先只推进 Audio，或将 Chat/Participants aliases 延后到 matcher/diagnostics 能识别隐私子串冲突之后。

## Files Changed

- `docs/agent-handoffs/cycle-058-risk-scan.md`
