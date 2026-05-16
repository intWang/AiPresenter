# Cycle 092 Risk Scan: RingCentral Video Control Map Reactions JA

## Risk summary

Risk review for adding Japanese `localizedText.ja` to `packages/ringcentral-video.yaml` -> `meeting-control-map-demo` -> `control-map-reactions`.

Current baseline after cycle 091 is Japanese localization `42/51`, with `meeting-control-map-demo` at `13/22`; the first missing step is `control-map-reactions`. This slice is safety-sensitive because the Reactions control opens a visible meeting interaction surface. Emoji reactions and `Be right back` are not private notes or local-only markers; sending one can be seen by other meeting participants and may be interpreted as user intent, availability, approval, amusement, applause, or temporary absence.

The safe target is a narrow open-and-explain localization. It is acceptable to open the reaction strip to show where lightweight feedback options live, describe the available option types at a generic level, and close it after the explanation. The implementation must preserve:

- the English and Chinese narration text
- `action.entrypointId: ringcentral.video.toolbar.react`
- `action.operation: open`
- `narration.placement: during`
- `narration.actionOffsetMs: 350`
- the step position after `control-map-share` and before `control-map-raise-hand`

The core safety rule is: opening the reaction strip is allowed for orientation, but clicking an actual reaction is not allowed unless the user explicitly asks to send that specific visible meeting signal. This control-map step should not demonstrate sending a reaction.

## Allowed behavior

- Open the Reactions strip with the existing `ringcentral.video.toolbar.react` entrypoint to show where reactions are found.
- Explain generic reaction categories such as approval, celebration, applause, smile, or `Be right back` without choosing one.
- Say that reactions are visible meeting signals: other participants can see them in the meeting context, so AiPresenter only explains the choices unless the user clearly asks to send one.
- Say that `Be right back` indicates temporary absence or availability status, and should not be sent automatically.
- Close the reaction strip after the explanation, consistent with the route's open-panel cleanup expectations.
- Keep Reactions separate from `Raise hand`: Reactions are quick feedback choices; `Raise hand` is a moderated-attention toggle that must be lowered after a confirmed demonstration.

## Forbidden behavior

- Do not click heart, thumbs up, celebration, clap, smile, `Be right back`, or any other actual reaction during this control-map step.
- Do not send, preselect, recommend, prioritize, or hover-dwell on a specific reaction as if AiPresenter is choosing for the user.
- Do not imply a reaction was sent, will be sent, or is safe to send without explicit user instruction.
- Do not use the reaction strip as a private note, sentiment analysis channel, availability tracker, attendance marker, voting system, or substitute for explicit consent.
- Do not infer the user's emotion, approval, agreement, mood, attention, or availability from the meeting context and convert it into a reaction.
- Do not broaden this slice into Raise hand behavior, participant management, chat messages, meeting moderation, attendance tracking, reactions analytics, transcript notes, recording, host controls, or later control-map steps.
- Do not leave the reaction strip open after the explanation, because it keeps a meeting-visible send surface active and can interfere with the next `Raise hand` step.

## Japanese wording guardrails

Safe Japanese copy should use orientation language and visible-signal caution. Prefer wording like:

- `Reactions は、発話を遮らずに軽いフィードバックを示すためのリアクション欄を開きます。`
- `いいね、祝福、拍手、スマイル、Be right back などの選択肢があります。`
- `リアクションは会議中に見えるシグナルなので、ユーザーが明確に求めるまで送信しません。`
- `このコントロールマップでは場所と選択肢の種類だけを説明し、実際のリアクションは押しません。`
- `説明後はリアクション欄を閉じます。`

Useful terms to keep:

- `Reactions`
- `リアクション欄`
- `軽いフィードバック`
- `発話を遮らずに`
- `いいね`
- `祝福`
- `拍手`
- `スマイル`
- `Be right back`
- `会議中に見えるシグナル`
- `ユーザーが明確に求めるまで`
- `送信しません`
- `押しません`
- `閉じます`

To distinguish from `Raise hand`, prefer:

- `Reactions は一時的なフィードバックの選択肢です。`
- `Raise hand は発言機会や注目を求めるためのトグル操作です。`
- `Raise hand のように手を上げた状態を残す操作とは別です。`

Avoid wording that sounds like AiPresenter sends a reaction, decides intent, or changes meeting state:

- `リアクションを送信します`
- `リアクションします`
- `いいねを押します`
- `拍手します`
- `祝福します`
- `スマイルを送ります`
- `Be right back にします`
- `反応を選びます`
- `おすすめのリアクション`
- `適切なリアクション`
- `自動で反応します`
- `参加者に気持ちを伝えます` when phrased as an action AiPresenter performs
- `同意を示します`
- `賛成します`
- `戻ってきます` when it implies AiPresenter has sent `Be right back`
- `手を上げます`
- `手を下げます`
- `注目を求めます`
- `発言機会を求めます`

The phrase `会議中に見えるシグナル` is preferred for visible meeting signal because it is clear, neutral, and avoids implying persistence beyond the meeting surface. Avoid `公開シグナル`, which can sound public outside the meeting, and avoid `通知`, which can sound like a system notification rather than a participant-visible meeting cue.

## Test guardrails

- Localization coverage should advance exactly one Japanese demo step: overall demo coverage from `42/51` to `43/51`, and `meeting-control-map-demo` from `13/22` to `14/22`.
- The first remaining missing `meeting-control-map-demo` Japanese step should move from `control-map-reactions` to `control-map-raise-hand`.
- Japanese Q&A counts should remain `12/12` questions and `12/12` answers; `questionAliases.ja` should remain `3/27` entrypoints and `9` aliases unless a separate task explicitly assigns alias work.
- Assert the Japanese text is attached only to `meeting-control-map-demo` -> `control-map-reactions`, not to `meeting-controls-tour` -> `explain-reactions`, Q&A, aliases, presenter notes, Share, Raise hand, More, Recording, Notes, Background, Settings, Leave, or Summary.
- Assert `control-map-reactions.action.entrypoint_id` remains `ringcentral.video.toolbar.react`, `operation` remains `open`, `placement` remains `during`, and `action_offset_ms` remains `350`.
- Assert adjacent steps remain unchanged: `control-map-share` stays an `open` step on `ringcentral.video.toolbar.share`, and `control-map-raise-hand` stays a separate `toggle` step on `ringcentral.video.toolbar.raise-hand`.
- Assert the Japanese copy includes `Reactions`, at least one lightweight reaction example such as `いいね` or `拍手`, a visible-signal boundary such as `会議中に見えるシグナル`, and a no-send boundary such as `送信しません` or `押しません`.
- Assert the Japanese copy distinguishes Reactions from Raise hand by not describing reactions as `トグル`, `手を上げ`, `手を下げ`, `注目を求め`, or `発言機会`.
- Assert the Japanese copy does not contain send-action phrases such as `リアクションを送信します`, `いいねを押します`, `拍手します`, `Be right back にします`, `反応を選びます`, `自動で反応します`, `同意を示します`, or `賛成します`.
- If live validation is used, fail review if any reaction is clicked, `Be right back` is sent, meeting state changes because of a reaction, the reaction strip remains open after the step, or screenshots/logs capture participant-identifying meeting context beyond the sanitized control label.
- Japanese `--require-complete` should still fail after this slice because later `meeting-control-map-demo` steps remain untranslated.

## Reviewer checklist

- Confirm the diff is limited to the assigned Japanese narration and directly necessary test/source-index expectation updates in the implementation cycle; this risk-scan handoff itself should be the only file created by cycle 092 risk scan.
- Confirm no YAML, code, tests, or other documents were changed by this risk-scan subagent.
- Confirm opening the reaction strip is treated as allowed orientation behavior, while sending an actual reaction remains blocked without explicit user confirmation.
- Confirm the proposed Japanese narration says reactions are visible meeting signals, not private notes, local-only markers, or hidden status.
- Confirm `Be right back` is described as a visible temporary-absence/availability signal and is not sent automatically.
- Confirm the copy keeps Reactions separate from `Raise hand`: no raise/lower language, no toggle cleanup promise for Reactions, and no hand state left active.
- Confirm the copy does not infer user sentiment, approval, agreement, mood, attention, or availability.
- Confirm the implementation closes the reaction strip before the following `control-map-raise-hand` step.
- Confirm no screenshots, logs, fixtures, snapshots, or review artifacts include unnecessary participant names, meeting identifiers, reaction-send evidence, availability status, account details, or other live meeting context.
