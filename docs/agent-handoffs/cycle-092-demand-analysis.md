# Cycle 092 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-reactions` -> `narration.localizedText.ja`.

The user value is orientation, not action. In a live RingCentral Video meeting, users need to know where lightweight feedback lives so they can acknowledge a speaker, celebrate, clap, smile, or briefly signal "Be right back" without taking the floor or interrupting the current speaker. The control map should teach Reactions as the low-friction interaction area after Share and before Raise hand.

This step is sensitive because reactions are visible meeting signals. Even though they feel small, sending one can be socially meaningful: a thumbs up may imply agreement, applause may imply approval, celebration may look enthusiastic, and Be right back may imply the participant is temporarily away. The Japanese narration should therefore explain the entry point and available signal types without implying that AiPresenter chooses or sends a reaction during the tour.

Boundary with adjacent controls:

- `Reactions` is for lightweight, momentary feedback that does not request the floor.
- `Raise hand` is for moderated conversation and asks for attention or a speaking opportunity. It is a separate toggle with cleanup expectations.
- `Be right back` may appear in the Reactions panel, but it should be described as a visible meeting status-style signal, not as a generic emoji or as something sent automatically.
- Actual reaction sending is outside the orientation step. The presenter may open the Reactions panel to show where the options live, then close it without selecting anything unless the user explicitly asks to send a specific reaction.

## Presenter behavior

The presenter should treat `control-map-reactions` as an `open` operation on `ringcentral.video.toolbar.react`. It can open the Reactions panel during the control map, name the categories of quick feedback at a high level, and then continue the tour.

Required behavior in real meeting context:

- Explain that Reactions is the entry point for quick feedback while someone else is speaking.
- Mention examples such as approval/thumbs up, celebration, applause, smile, and Be right back.
- State or clearly imply that these are visible meeting signals.
- Do not send any reaction during the tour unless the user gives an explicit instruction naming the desired reaction.
- If the panel is opened only for explanation, close it without selecting a reaction.
- Do not conflate the Reactions panel with Raise hand. Raise hand remains the next separate step and should keep its own toggle/cleanup story.

The narration should avoid wording that sounds like the presenter is about to click a reaction, choose one for the user, or broadcast feedback on the user's behalf. Prefer "場所と役割を説明します" / "選択肢を確認できます" style over "送ります" / "選びます" / "クリックします".

## Localization tone

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` Japanese style: calm, explicit, and safety-aware, while keeping English UI labels like `Reactions`, `Raise hand`, and `Be right back` where they match the interface.

Recommended tone points:

- Reactions can be rendered as `Reactions` plus Japanese explanation, or `リアクション` when describing the concept.
- "Lightweight interaction" should sound conversational, for example `発話を遮らずに短い反応を示す`.
- Be right back should stay as the UI label `Be right back`; explain it as a signal that the participant will step away briefly or return soon.
- Use polite but concise safety phrasing: `ユーザーの明確な指示なしに送信しません`.
- Avoid over-heavy compliance language. The step should feel like a meeting coach pointing out a useful tool, not a legal warning.

Suggested semantic shape, not a required final string:

```text
Reactions は、発話を遮らずに短い反応を示すための入口です。いいね、祝福、拍手、スマイル、Be right back などを確認できますが、これらは会議中に見えるシグナルです。ここでは場所と役割だけを説明し、ユーザーが明確に求めるまでリアクションは送信しません。説明後は送信せずに閉じます。
```

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not add Japanese narration for `control-map-raise-hand`, `control-map-more`, `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change Chinese, English, Q&A, aliases, presenter notes, locator metadata, operation definitions, cleanup behavior, source-index text, or tests in this handoff.
- Do not rework the existing `explain-reactions` Japanese narration, though the implementation agent may use it as a style and boundary reference.
- Do not treat Be right back as Raise hand or as a durable participant status unless verified by the product behavior.
- Do not imply AiPresenter can infer the socially appropriate reaction from meeting content.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-reactions` -> `narration.localizedText.ja`.
- Japanese localization advances from `42/51` to `43/51` overall and `meeting-control-map-demo` advances from `13/22` to `14/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-raise-hand`.
- The Reactions step remains `entrypointId: ringcentral.video.toolbar.react`, `operation: open`, `placement: during`, and `actionOffsetMs: 350`.
- The Japanese text mentions the Reactions/React entry point, lightweight feedback, visible meeting signal behavior, and examples including at least approval/like, celebration or applause, and `Be right back`.
- The Japanese text clearly says reactions are not sent without the user's explicit instruction.
- The text does not say or imply that AiPresenter sends, clicks, chooses, or recommends a reaction during the tour.
- Adjacent `control-map-share` and `control-map-raise-hand` remain semantically separate and unchanged.

Useful negative assertions for implementation tests:

```python
assert "ja" in reactions_step.narration.localized_text
assert "ja" not in raise_hand_step.narration.localized_text
assert "送信しません" in ja_text
assert "明確" in ja_text
assert "Be right back" in ja_text
assert "Raise hand" not in ja_text or "別" in ja_text
assert "送信します" not in ja_text
assert "選びます" not in ja_text
assert "クリックします" not in ja_text
assert "自動" not in ja_text
```

## Next handoff notes

Implementation should be a narrow localization update only. Start from the current baseline after cycle 091: Japanese demo coverage `42/51`, `meeting-control-map-demo: 13/22`, first missing `control-map-reactions`.

The closest existing reference is the already-localized `meeting-controls-tour` step `explain-reactions`, which frames React as a panel for heart/thumbs up/celebration/clap/smile/Be right back and explicitly says not to send a visible meeting signal without user instruction. The control-map version can be slightly shorter, but should preserve that same safety boundary.

After implementation, update only the files required by the implementation task and tests. This demand-analysis handoff intentionally does not commit and does not touch package YAML, tests, or other docs.
