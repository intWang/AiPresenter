# Cycle 093 Demand Analysis

## User need

Target the next narrow Japanese localization slice: `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-raise-hand` -> `narration.localizedText.ja`.

The user value is meeting etiquette and orientation. In RingCentral Video, users need to know where `Raise hand` lives because it is the non-interruptive way to ask for attention or a speaking opportunity when a meeting is moderated, crowded, or actively led by a host. The control map should teach that this is not a decorative reaction: it changes the participant's visible meeting state and can affect the host's speaking queue or facilitation rhythm.

This step is sensitive because `Raise hand` is both visible and durable until lowered. A raised hand may be interpreted as "I want to speak", "I have a question", "I need host attention", or "please call on me". Leaving it raised after a demo can create social noise, distract the presenter, or incorrectly signal that the user still wants the floor. The Japanese narration should therefore explain the entry point and toggle behavior while making cleanup explicit.

Boundary with adjacent controls:

- `Reactions` is for lightweight feedback such as approval, applause, celebration, smiles, or `Be right back`; it should not request the floor.
- `Raise hand` is for moderated conversation and attention management. It asks to be recognized and remains visible until lowered.
- `Raise hand` is a toggle: pressing it raises the hand, and pressing it again lowers the hand.
- If AiPresenter demonstrates the toggle only after explicit confirmation, it must lower the hand again and leave no active raised-hand state behind.

## Presenter behavior

The presenter should treat `control-map-raise-hand` as a `toggle` operation on `ringcentral.video.toolbar.raise-hand`. In a scripted map demo, the narration can say that this is the place to raise or lower the hand, but it must avoid acting like a raised hand is casual feedback.

Required behavior in real meeting context:

- Explain that `Raise hand` is used to request attention or a speaking turn without interrupting the current speaker.
- Make clear that this is separate from `Reactions`.
- State or clearly imply that the raised hand is visible to the meeting.
- Explain the toggle model: one activation raises the hand; the next lowers it.
- Do not raise the hand in a real meeting unless the user explicitly confirms that action.
- If a demonstration raises the hand, lower it again before moving on.
- Do not leave the hand raised after an explanation, demo, interruption, or recovery path.

The narration should frame the cleanup as part of respectful meeting operation, not as an alarm. Good semantics: "this helps ask for a turn without speaking over someone; because it is visible and remains active, I lower it again after a confirmed demo." Avoid language that suggests AiPresenter can decide that the user wants to speak, that raising a hand is the same as applauding or liking something, or that the state can be left active as a reminder.

## Localization tone

Use natural Japanese product-demo narration consistent with the existing `meeting-control-map-demo` style: calm, concise, and explicit about meeting-visible side effects. Keep the UI label `Raise hand` in English when naming the control, then explain the behavior in Japanese.

Recommended tone points:

- Use `Raise hand` plus Japanese explanation such as `発言機会を求める`, `注目してほしいことを知らせる`, or `手を上げた状態`.
- Distinguish from reactions with direct but light phrasing: `リアクションとは別の、会議中に見える合図です`.
- Prefer `トグル操作` or `もう一度押すと手を下げます` for the toggle boundary.
- Use polite safety wording: `ユーザーの明確な指示なしに手を上げません`.
- Include cleanup in the presenter voice: `実演した場合は、最後に手を下げます`.
- Keep the line usable as spoken narration. It should sound like a meeting coach, not a policy notice.

Suggested semantic shape, not a required final string:

```text
Raise hand は、発話を遮らずに発言機会や注目を求めるための入口です。リアクションとは別の、会議中に見える合図で、押すと手を上げた状態になり、もう一度押すと手を下げます。ユーザーの明確な指示なしに手は上げません。実演した場合も、説明後は必ず手を下げて、見える状態を残しません。
```

## Out of scope

- Do not edit `packages/ringcentral-video.yaml` in this demand-analysis handoff.
- Do not add Japanese narration for `control-map-more`, `control-map-recording`, `control-map-notes`, `control-map-background`, `control-map-settings`, `control-map-leave`, or `control-map-summary`.
- Do not change Chinese, English, Q&A, aliases, presenter notes, locator metadata, operation definitions, cleanup behavior, source-index text, or tests in this handoff.
- Do not rework the existing `meeting-controls-tour` step `explain-raise-hand`, though the implementation agent may use it as a style and boundary reference.
- Do not conflate `Raise hand` with `Reactions`, `Be right back`, participant status, host moderation controls, chat messages, or applause/approval feedback.
- Do not imply AiPresenter can infer from meeting content that the user wants to speak.
- Do not add new behavior that leaves a persistent visible state active after the step.

## Acceptance criteria

For the next implementation slice, acceptance should confirm:

- Exactly one new Japanese demo-step narration is added: `meeting-control-map-demo` -> `control-map-raise-hand` -> `narration.localizedText.ja`.
- Japanese localization advances from `43/51` to `44/51` overall and `meeting-control-map-demo` advances from `14/22` to `15/22`.
- The first remaining missing Japanese step in `meeting-control-map-demo` becomes `control-map-more`.
- The Raise hand step remains `entrypointId: ringcentral.video.toolbar.raise-hand`, `operation: toggle`, `placement: during`, and `actionOffsetMs: 350`.
- The Japanese text mentions `Raise hand`, requesting attention or a speaking opportunity, visible meeting signal/state, toggle behavior, and lowering the hand after any confirmed demonstration.
- The Japanese text clearly says or implies that AiPresenter does not raise the hand without the user's explicit instruction.
- The text distinguishes `Raise hand` from `Reactions`.
- The text does not say or imply that AiPresenter decides the user wants to speak, leaves the hand raised, treats it as applause/approval, or uses it as a durable reminder.

Useful negative assertions for implementation tests:

```python
assert "ja" in raise_hand_step.narration.localized_text
assert "ja" not in more_step.narration.localized_text
assert "Raise hand" in ja_text
assert "リアクション" in ja_text or "Reactions" in ja_text
assert "別" in ja_text
assert "手を上げ" in ja_text
assert "手を下げ" in ja_text
assert "明確" in ja_text
assert "上げたまま" not in ja_text
assert "拍手" not in ja_text
assert "いいね" not in ja_text
assert "Be right back" not in ja_text
assert "自動" not in ja_text
```

## Next handoff notes

Implementation should be a narrow localization update only. Start from the current baseline after cycle 092: Japanese demo coverage `43/51`, `meeting-control-map-demo: 14/22`, first missing `control-map-raise-hand`.

The closest existing reference is the already-localized `meeting-controls-tour` step `explain-raise-hand`, which says Raise hand is a meeting-visible attention signal, separate from reactions, and must be lowered after a confirmed demonstration. The control-map version can be shorter, but it should preserve the same user-intent and cleanup boundary.

The previous `control-map-reactions` slice intentionally kept Raise hand separate. This slice should now complete that adjacent story from the other side: Reactions are quick feedback; Raise hand is a moderated-attention toggle. The host-rhythm risk should be expressed as practical etiquette: do not create a false speaking request, do not interrupt the flow of facilitation, and do not leave a visible raised-hand state active.

After implementation, update only the files required by the implementation task and tests. This demand-analysis handoff intentionally does not commit and does not touch package YAML, tests, or other docs.
