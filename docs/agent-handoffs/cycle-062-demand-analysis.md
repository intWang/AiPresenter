# Cycle 062 Demand Analysis: meeting-controls-tour / explain-add-coworkers JA narration

## Demand Judgment

Proceed with a single-step Japanese localization slice for `meeting-controls-tour` step `explain-add-coworkers`.

Cycle 061 advanced Japanese `meeting-controls-tour` coverage to `5/22` and the localization report now identifies `explain-add-coworkers` as the first missing JA step. This is a valid next slice because the step is already present in English and Chinese, has a stable entrypoint, and continues the tour in order. It should not be batched with `explain-invite`, `explain-participants`, `explain-chat`, or later controls because Add coworkers crosses into invite/contact privacy and empty-room state handling.

## User Value

- Japanese presenters can continue the meeting controls tour past the Report step without falling back to English.
- The narration explains the empty-meeting Add coworkers callout before the toolbar Invite path, preserving the product distinction between the canvas callout and regular toolbar control.
- The slice improves localization coverage while keeping privacy language specific enough for invite links, contact search, and suggestions.

## Strict Scope

- Add only `narration.localizedText.ja` for `packages/ringcentral-video.yaml` -> `meeting-controls-tour` -> `explain-add-coworkers`.
- Preserve the step id, action, `entrypointId`, operation, placement, `actionOffsetMs`, and existing English/Chinese text.
- Keep the Japanese text narration-only: it should describe what Add coworkers opens and how it is used, not perform or imply invite submission.
- If tests are updated in a later implementation pass, update only localization count/first-missing expectations and a focused assertion for this one step.

## Non-Goals

- Do not localize `explain-invite`, `explain-participants`, `explain-chat`, sharing, reactions, notes, recording, leave, or the rest of `meeting-controls-tour` in the same pass.
- Do not add Japanese `questionAliases` for Add coworkers or Invite.
- Do not change runtime behavior, adaptive routing, openSteps, cleanup behavior, locators, Q&A, or privacy policy structure.
- Do not read or validate live RingCentral UI unless the implementation task explicitly asks for manual observation.

## Privacy And State Boundaries

- The Add coworkers entrypoint opens the same Invite others dialog as toolbar Invite, with name/email search, suggestions, Copy meeting link, Cancel, and Invite.
- Treat names, email addresses, suggested contacts, invite links, meeting links, and copied meeting details as private by default.
- The Japanese narration should not read or imply access to contact names, email addresses, suggestions, invite links, or copied link values unless the user explicitly requests it and the UI text is verified.
- The narration should say the surface is for searching coworkers, copying the meeting link, or inviting someone, but should not say that an invite is sent automatically.
- The callout appears only in the empty-room "first one here" state. If participant tiles or a Participants badge indicate other attendees are present, the demo should skip this canvas callout and use the separate toolbar Invite path in a later slice.
- The invite dialog blocks other meeting controls; any implementation guidance should preserve closing/canceling the dialog before moving on.

## Acceptance Criteria

- `explain-add-coworkers` contains a non-empty `localizedText.ja` under `narration`.
- Japanese wording preserves product labels `Add coworkers` and/or `Invite` where useful for UI matching.
- Japanese wording mentions the empty meeting or empty-room context.
- Japanese wording identifies search/copy/invite capabilities without exposing private values or implying an invite was sent.
- No Japanese text is added to `explain-invite`, `explain-participants`, `explain-chat`, aliases, Q&A, or unrelated steps.
- Expected localization movement after implementation: JA demo narration `12/51` -> `13/51`; `meeting-controls-tour` `5/22` -> `6/22`; first missing step should advance from `explain-add-coworkers` to `explain-invite`.

## Next-Step Recommendation

Implement this as a narrow narration-only pass. Suggested Japanese direction:

`メンバー関連の操作に移ります。空の会議画面にある Add coworkers は Invite others ダイアログを開き、同僚の検索、会議リンクのコピー、招待の送信に使えます。名前、メールアドレス、候補、招待リンクは、ユーザーが明示的に求めるまで読み上げません。`

After that pass, run focused localization tests and the Japanese localization report. Then treat `explain-invite` as a separate demand/risk decision because it shares the dialog but has a different state context: active meeting toolbar entry rather than empty-room canvas callout.
