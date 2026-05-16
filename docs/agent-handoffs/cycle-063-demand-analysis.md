# Cycle 063 Demand Analysis: meeting-controls-tour / explain-invite JA narration

## Demand Judgment

Proceed with a single-step Japanese localization slice for `meeting-controls-tour` step `explain-invite`.

Cycle 062 advanced Japanese coverage to `13/51` demo steps, `meeting-controls-tour: 6/22`, and the first missing `meeting-controls-tour` JA step is now `explain-invite`. This is the correct next slice because it continues the tour order and covers the regular active-meeting toolbar entrypoint for inviting someone, distinct from the empty-room `Add coworkers` callout completed in Cycle 062.

Do not batch this with `explain-participants`, `explain-chat`, sharing, reactions, notes, recording, leave, or the rest of `meeting-controls-tour`. Those controls have different privacy, state, cleanup, and side-effect boundaries.

## User Value

- Japanese presenters can continue from empty-room people setup into the normal toolbar Invite path without falling back to English.
- The localized tour will teach the active-meeting entrypoint users are most likely to use after other attendees are present.
- The slice reinforces invite privacy in Japanese while preserving UI label matching for `Invite`.
- It reduces confusion between the empty-room Add coworkers surface and the toolbar Invite button.

## Strict Scope

- Add only `narration.localizedText.ja` for `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-invite`.
- Keep the existing action unchanged: `entrypointId: ringcentral.video.toolbar.invite`, `operation: open`.
- Keep placement and timing unchanged unless tests explicitly require otherwise.
- Preserve existing English and Chinese narration.
- Update only localization accounting/tests/docs that are required by the implementation owner for this exact single-step change.
- If source-index maintenance is in scope for implementation, update the localization note from the first six `meeting-controls-tour` steps to the first seven through toolbar Invite.

## Non-Goals

- Do not localize `explain-participants`, `explain-chat`, `explain-microphone`, `explain-share`, or later steps in this pass.
- Do not add Japanese `questionAliases` for Invite.
- Do not change Q&A answers, runtime behavior, adaptive routing, locators, cleanup modes, openSteps, or state extraction.
- Do not validate or change live modal close behavior as part of the narration slice.
- Do not send invites, select suggestions, enter names or email addresses, copy links, or imply that the presenter performs those actions automatically.

## Privacy And State Boundaries

- `explain-invite` is the active-meeting toolbar entrypoint. It should say the toolbar `Invite` button opens the same invite flow and is the regular place to bring someone into an active meeting.
- The flow may expose names, email addresses, contact suggestions, meeting links, and invite details. These remain private by default.
- Japanese wording should explain the workflow without reading private invite content unless the user explicitly asks and visible content has been verified.
- The narration may mention searching coworkers, adding someone, copying or using meeting details at a high level, but must not say AiPresenter reads, copies, sends, or confirms private details by default.
- The Invite dialog can block meeting controls. If the localized text mentions the open dialog, it should also fit the existing cleanup expectation that the surface is closed after explanation.
- This slice is separate from `Add coworkers`: Add coworkers is the empty-room canvas callout; Invite is the toolbar path for active meetings.
- Participants and Chat must remain separate because they expose roster names, roles, attendee controls, public/private messages, and separate side-panel cleanup behavior.

## Acceptance Criteria

- `meeting-controls-tour` step `explain-invite` has a Japanese `narration.localizedText.ja`.
- The Japanese text preserves the visible product label `Invite`.
- The Japanese text identifies toolbar Invite as the active-meeting entrypoint, not the empty-room Add coworkers callout.
- The Japanese text includes a privacy boundary for names, email addresses, suggestions, meeting links, or invite details.
- The Japanese text does not claim AiPresenter sends invitations, selects people, enters emails, copies links, or reads suggestions by default.
- No Japanese text is added to `explain-participants`, `explain-chat`, or any later `meeting-controls-tour` step in this slice.
- Expected localization movement after implementation: JA demo narration `13/51` -> `14/51`; `meeting-controls-tour` `6/22` -> `7/22`; first missing step should advance from `explain-invite` to `explain-participants`.
- Q&A localization remains `12/12` questions and `12/12` answers; `questionAliases.ja` remains `3/27 entrypoints (9 aliases)` unless a separate alias task is explicitly approved.

## Next-Step Recommendations

- Implementation should use a narrow TDD pass that first proves `explain-invite` is the missing JA step, then adds only that localized narration and updates expected coverage.
- A suitable Japanese narration should be concise and active-meeting specific, for example: `ツールバーの Invite は、進行中の会議に相手を招待するための通常の入口です。同僚を追加したり会議情報を確認したりできますが、名前、メールアドレス、候補、非公開の招待リンクは、ユーザーが明示的に求め、表示内容が確認されるまで読み上げません。説明したら、このダイアログを閉じます。`
- After implementation, run focused localization tests and the Japanese localization report.
- Treat `explain-participants` as the next independent demand/risk slice because it opens the roster panel and has different privacy boundaries from Invite.

## Sources Reviewed

- `packages/ringcentral-video.yaml`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/knowledge/ringcentral-video/privacy-matrix.md`
- `docs/knowledge/ringcentral-video/state-matrix.md`
- `docs/knowledge/ringcentral-video/evidence-index.md`
- `docs/knowledge/ringcentral-video/locator-matrix.md`
- `docs/agent-handoffs/cycle-062-summary.md`
- `docs/agent-handoffs/cycle-062-implementation.md`
- `docs/agent-handoffs/cycle-062-review.md`
