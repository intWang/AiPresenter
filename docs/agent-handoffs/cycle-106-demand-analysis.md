# Cycle 106 Demand Analysis: Japanese Notes/Transcript Location Aliases

## Recommendation

Add a minimal two-alias Japanese location set for `ringcentral.video.more.notes` in the next implementation slice:

- `Notes and Transcript の場所`
- `ノートと文字起こしの場所`

This is now a reasonable product move because Cycle 105 added `questionPolicy: answerOnly` to `ringcentral.video.more.notes`. Question routing can identify the Notes and Transcript entrypoint without creating an interrupt step, while the scripted `meeting-control-map-demo` still preserves the existing `openSteps` for demo narration.

Keep the slice alias-only and location-only. Do not change the Notes open route, presenter notes, Q&A answer policy, or any runtime safety behavior in the same cycle unless tests prove the alias addition exposed a blocker.

## Product Demand

Japanese users are likely to ask where meeting notes or transcript controls live during a RingCentral Video walkthrough. The current package already has Japanese Q&A coverage for `ノートと文字起こしはどこにありますか`, but the entrypoint itself still lacks Japanese package-owned aliases. That gap matters for direct control-map discovery, diagnostics coverage, and consistency with other localized meeting controls.

The demand is discovery, not operation:

- Users want to find the Notes and Transcript panel.
- Users may say the English UI label inside a Japanese sentence.
- Users may use the natural Japanese pair `ノートと文字起こし`.
- Users do not need broad aliases that imply reading, summarizing, generating, or starting content.

The recommended pair covers the two highest-value discovery modes:

| Alias | Demand covered | Why it is safe enough |
| --- | --- | --- |
| `Notes and Transcript の場所` | Mixed-language Japanese questions that repeat the visible product label. | It is explicitly a location phrase and does not mention starting, reading, recording, or summarizing. |
| `ノートと文字起こしの場所` | Natural Japanese discovery phrasing for the same combined panel. | It keeps Notes and Transcript paired as one control surface and remains location-only. |

## Aliases To Avoid

Avoid bare or single-feature aliases even if they look convenient:

- `Notes`
- `Transcript`
- `ノート`
- `文字起こし`
- `ノートの場所`
- `文字起こしの場所`
- `トランスクリプトの場所`
- `議事録`

Avoid action, content, and artifact wording:

- `Start notes`
- `ノートを開始`
- `ノートを開始して`
- `文字起こしをオン`
- `文字起こしを読んで`
- `Transcript を読んで`
- `Transcript を要約して`
- `議事録を作って`
- `会議後の文字起こし`
- `会議後の要約`

Avoid indirect menu wording:

- `More`
- `その他`
- `もっと`
- `詳細メニュー`

These alternatives broaden matching beyond location discovery. Some are content requests, some imply state changes, and some are vague More-menu routes that do not answer the user's specific Notes/Transcript question.

## Safety Boundary

The alias slice should rely on Cycle 105's answer-only policy, not on removing executable metadata.

Expected behavior after adding the two aliases:

- Japanese location questions can route to `ringcentral.video.more.notes`.
- `can_operate` remains `False` for question responses.
- `create_question_interrupt_step(...)` returns `None` for these question responses.
- `ringcentral.video.more.notes.openSteps` remains intact for scripted demo flows.
- The answer may explain where the Notes and Transcript panel is, but must not start notes, start transcription, start recording, read transcript or note content, summarize artifacts, or assert artifact availability.

## Success Criteria

Implementation success should be measured narrowly:

- Add only the two recommended aliases under `ringcentral.video.more.notes.questionAliases.ja`.
- Japanese alias coverage moves from `12/27` entrypoints and `32` aliases to `13/27` entrypoints and `34` aliases.
- Package-owned alias count moves from `85` to `87`.
- Doctor reports no cross-entrypoint alias duplicates and no new unsafe overlap warning.
- `answer_question(..., "Notes and Transcript の場所はどこですか", language="ja")` returns `entrypoint_id == "ringcentral.video.more.notes"` and `can_operate is False`.
- `answer_question(..., "ノートと文字起こしの場所はどこですか", language="ja")` returns `entrypoint_id == "ringcentral.video.more.notes"` and `can_operate is False`.
- Both responses produce no question interrupt step.
- Existing Japanese Q&A for `ノートと文字起こしはどこにありますか`, `字幕はどこにありますか`, and `会議後の録画や文字起こしはどこにありますか` remains answer-only.
- Negative prompts such as `ノートを開始して`, `文字起こしを読んで`, `Transcript を要約して`, and `議事録を作って` remain non-operable and do not become package-owned entrypoint alias matches.
- Demo flow tests continue to prove the Notes panel route can be opened from scripted demo steps.

## Handoff Notes

Read-only context checked:

- Cycle 105 committed `adcc876 feat: add answer-only question policy`.
- `ringcentral.video.more.notes` now carries `questionPolicy: answerOnly`.
- Cycle 105 summary reports Japanese aliases still at `12/27` entrypoints and `32` aliases.
- The prior technical scan projected that a two-alias Notes slice should move counts to `13/27`, `34` Japanese aliases, and `87` package-owned aliases.

Workspace note:

- `.coverage` was already modified before this analysis and was not touched.
