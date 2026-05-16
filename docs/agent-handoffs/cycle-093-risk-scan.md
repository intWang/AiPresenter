# Cycle 093 Risk Scan: RingCentral Video Control Map Raise Hand JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-raise-hand`.

Current baseline after cycle 092 is Japanese localization `43/51`, with `meeting-control-map-demo` at `14/22`; the first missing step is `control-map-raise-hand`. This slice is safety-sensitive because `Raise hand` is a visible meeting signal and an actual toggle. Unlike opening an explanatory panel, clicking it changes participant state and may leave a hand indicator visible to other attendees until it is lowered.

The existing route is intentionally executable but must remain narrow:

- `action.entrypointId: ringcentral.video.toolbar.raise-hand`
- `action.operation: toggle`
- entrypoint target `Raise hand`
- alternate target `onconf.reactions.REMOVE_RAISE_HAND`
- match `controlType: button`
- cleanup `toggle`
- `narration.placement: during`
- `narration.actionOffsetMs: 350`

The core safety rule is: the control can be explained without raising a hand. If the scripted demo actually toggles it, the demo owns cleanup and must lower the hand immediately after showing the state. In a real meeting, AiPresenter must not raise or lower the user's hand unless the user explicitly asks in the current context.

## Allowed behavior

- Explain that `Raise hand` is for moderated conversation and attention or speaking-turn requests without interrupting the current speaker.
- State that it is a visible meeting signal, not a private note or local-only marker.
- State that it is a toggle: pressing once raises the hand, pressing again lowers it.
- In a reviewed scripted demo, toggle the hand only if the flow's existing action requires it and cleanup is verified by the same route.
- After any confirmed demonstration, lower the hand again using the same control or its lowered-state label `onconf.reactions.REMOVE_RAISE_HAND`.
- Prefer explain-only behavior when the user is just asking where the control is or what it does.
- Keep the step distinct from `Reactions`: Reactions are quick feedback choices; `Raise hand` is a persistent attention/speaking-turn state until lowered.

## Forbidden behavior

- Do not leave the hand raised after the control-map step.
- Do not raise a hand in a real meeting without explicit user instruction.
- Do not lower a user's already-raised hand unless the user explicitly asks, except to clean up a state AiPresenter just created during an approved demo.
- Do not imply `Raise hand` is private, invisible, temporary like an emoji reaction, or automatically cleared by the system.
- Do not describe `Raise hand` as sending approval, applause, celebration, agreement, availability, mood, attendance, voting intent, or any other reaction-like sentiment.
- Do not infer from meeting context that the user wants attention, wants to speak, agrees, disagrees, or should raise a hand.
- Do not broaden this slice into Reactions behavior, participant controls, host moderation, chat, notes, recording, security, leave/end, or later `meeting-control-map-demo` steps.
- Do not add Japanese aliases, Q&A, presenter notes, source-index wording, or other documentation unless a separate implementation task explicitly assigns them.

## Japanese wording guardrails

Safe Japanese copy should make the toggle and cleanup explicit while staying neutral about user intent. Prefer wording like:

- `Raise hand は、進行役のいる会議で発言機会や注目を求めたいときに使う、会議中に見えるシグナルです。`
- `これはトグル操作なので、一度押すと手を上げた状態になり、もう一度押すと手を下げます。`
- `実演する場合は、表示を確認したあと必ずもう一度押して手を下げます。`
- `ユーザーが明示的に求めるまで、実際に手を上げたり下げたりしません。`
- `Reactions のような一時的なフィードバックではなく、下げるまで残る挙手状態です。`

Useful terms to keep:

- `Raise hand`
- `挙手`
- `手を上げる`
- `手を下げる`
- `トグル操作`
- `発言機会`
- `注目`
- `会議中に見えるシグナル`
- `表示を確認したあと`
- `必ずもう一度押して`
- `ユーザーが明示的に求めるまで`

Avoid wording that sounds like AiPresenter is taking user intent, changing state without consent, or confusing Raise hand with Reactions:

- `手を上げます` when it stands alone without the demo-cleanup condition
- `発言したいことを知らせます` if it implies AiPresenter is asserting the user's intent
- `注目を集めます` if phrased as an action AiPresenter performs
- `自動で手を上げます`
- `手を上げたままにします`
- `必要なら下げます`
- `あとで下げます`
- `リアクションとして手を上げます`
- `軽いフィードバック`
- `いいね`
- `拍手`
- `祝福`
- `スマイル`
- `Be right back`
- `送信します`
- `反応します`
- `賛成を示します`
- `同意を示します`

Preferred distinction from Reactions:

- `Reactions は一時的なフィードバックの選択肢です。`
- `Raise hand は、発言機会や注目を求めるためのトグル操作で、下げるまで状態が残ります。`

## Test guardrails

- Localization coverage should advance exactly one Japanese demo step: overall demo coverage from `43/51` to `44/51`, and `meeting-control-map-demo` from `14/22` to `15/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-raise-hand` to `control-map-more`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached only to `meeting-control-map-demo` -> `control-map-raise-hand`, not to `meeting-controls-tour` -> `explain-raise-hand`, Q&A, aliases, presenter notes, Reactions, More, Recording, Notes, Background, Settings, Leave, or Summary.
- Assert `control-map-raise-hand.action.entrypoint_id` remains `ringcentral.video.toolbar.raise-hand`, `operation` remains `toggle`, `placement` remains `during`, and `action_offset_ms` remains `350`.
- Assert the entrypoint keeps one executable open step with target `Raise hand`, alternate target `onconf.reactions.REMOVE_RAISE_HAND`, `controlType: button`, and `cleanup: toggle`.
- Assert adjacent steps remain unchanged: `control-map-reactions` stays an `open` step on `ringcentral.video.toolbar.react`, and `control-map-more` remains the next unlocalized control-map step.
- Assert the Japanese copy includes `Raise hand`, a toggle term such as `トグル操作`, a raise/lower boundary such as `手を上げ` and `手を下げ`, and a cleanup promise such as `必ずもう一度押して` or equivalent.
- Assert the Japanese copy includes a visible-signal boundary such as `会議中に見えるシグナル`.
- Assert the Japanese copy distinguishes Raise hand from Reactions and does not contain reaction-send language such as `いいね`, `拍手`, `祝福`, `スマイル`, `Be right back`, `リアクションを送信`, `軽いフィードバック`, `賛成`, or `同意`.
- Assert the Japanese copy does not promise unsafe persistence or vague cleanup such as `手を上げたまま`, `あとで下げます`, or `必要なら下げます`.
- If live validation is used, fail review if the hand remains raised after the step, the wrong participant-visible signal is sent, the reaction strip is opened unintentionally, or screenshots/logs capture participant-identifying context beyond sanitized control labels.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Reviewer checklist

- Confirm this risk-scan subagent created only `docs/agent-handoffs/cycle-093-risk-scan.md`.
- Confirm no YAML, code, tests, or other documents were changed by this risk-scan subagent.
- Confirm the implementation slice adds only one Japanese narration block for `control-map-raise-hand`.
- Confirm the copy allows explain-only behavior and does not require raising the hand just to describe the control.
- Confirm any scripted toggle demonstration includes immediate lowering and does not leave a visible hand state behind.
- Confirm the copy says `Raise hand` is a visible meeting signal and a toggle.
- Confirm the copy distinguishes `Raise hand` from `Reactions` and does not describe it as emoji feedback, applause, approval, or `Be right back`.
- Confirm no new Japanese aliases, Q&A entries, presenter notes, source-index updates, or later control-map localizations were added unless explicitly assigned.
- Confirm tests lock both localization counts and the action boundary: `toggle` on `ringcentral.video.toolbar.raise-hand` with `cleanup: toggle`.
- Confirm no screenshots, logs, fixtures, snapshots, or review artifacts include unnecessary participant names, meeting identifiers, account details, or live meeting context.
