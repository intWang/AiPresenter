# Cycle 103 Demand Analysis: Japanese Reactions / Raise Hand Location Aliases

## Findings

Cycle 103 should add a narrow Japanese `questionAliases.ja` slice for Reactions and Raise hand, but only as location/entrypoint discovery. User value is real: during a meeting, Japanese users are likely to ask where the reaction button or hand-raise button is, especially when they want to acknowledge the speaker without interrupting. These controls are already covered by Japanese demo narration and safety Q&A, so aliases would make the existing package knowledge easier to reach.

The slice is moderate risk, not low risk. Both entrypoints are meeting-visible signal surfaces:

- `ringcentral.video.toolbar.react` opens a reaction strip where selecting an item would send a visible reaction.
- `ringcentral.video.toolbar.raise-hand` is a toggle that can leave a visible hand state in the meeting.

The current runtime safety posture helps: in-memory simulation of the recommended aliases kept both entrypoints `can_operate=False` because `_can_operate()` treats the relevant id/title/purpose words (`reaction`, `send`, `raise hand`, `toggle`) as risky. The same simulation kept diagnostics clean:

- `questionAliases.ja`: `9/27`, `26 aliases` -> `11/27`, `32 aliases`.
- Total package-owned aliases: `79` -> `85`.
- `question aliases`: OK, no cross-entrypoint duplicates.
- `qa alias overlap`: OK, `71` Q&A prompts remain free of unsafe exact alias overlap.
- `qa alias substring risk`: unchanged INFO at `11` prompts.

This is a better next candidate than Notes, Recording, Share, Invite, Add coworkers, Leave, or broad Settings aliases. Those surfaces touch private content, recording consent, meeting exit, invite/link handling, or state-changing settings. Reactions/Raise hand still need care, but the user intent can be expressed as "where is the button" without asking AiPresenter to operate it.

One important routing wrinkle: do not recommend `Raise hand の場所` as a package alias in this slice. A read-only in-memory probe showed that Japanese questions containing the English tokens `Raise hand` can be captured by the existing reaction/raise-hand safety Q&A before package aliases are considered, returning the safety answer with `entrypoint_id=None`. That is safe, but it makes the alias ineffective as a location route. Prefer Japanese location phrases for Raise hand.

## Recommended Scope

Add `questionAliases.ja` to exactly these two entrypoints.

| Entrypoint | Recommended aliases | User value | Safety posture |
| --- | --- | --- | --- |
| `ringcentral.video.toolbar.react` | `リアクションの場所`<br>`React の場所`<br>`リアクションボタン` | Covers natural Japanese phrasing plus the observed toolbar label `React`. | Location/button wording only; no `送る`, `選ぶ`, `押す`, `いいねして`, or named reaction action. Expected `can_operate=False`. |
| `ringcentral.video.toolbar.raise-hand` | `挙手の場所`<br>`挙手ボタン`<br>`手を挙げるボタン` | Covers the standard Japanese noun `挙手` and a user-facing "raise hand button" phrasing. | Button/location wording only; no direct `挙手して`, `手を挙げて`, `手を下げて`, or participant-status wording. Expected `can_operate=False`. |

Expected count movement for this exact `+6` slice:

- `questionAliases.ja present on 9/27 entrypoints (26 aliases)` -> `questionAliases.ja present on 11/27 entrypoints (32 aliases)`.
- `[OK] question aliases: 79 package-owned aliases have no cross-entrypoint duplicates` -> `[OK] question aliases: 85 package-owned aliases have no cross-entrypoint duplicates`.

Implementation should stay limited to the two alias blocks, directly necessary exact test expectation updates, and any assigned implementation handoff/source-index docs. Do not change `openSteps`, demo flow actions, Q&A answers, locators, runtime matching, or safety policy as part of the demand slice unless the technical/risk agents explicitly require it.

## Deferred Scope

Do not add aliases that imply sending, selecting, clicking, raising, lowering, or restoring a state:

- `リアクションを送って`
- `いいねして`
- `拍手して`
- `リアクションを選んで`
- `挙手して`
- `手を挙げて`
- `手を下げて`
- `Raise hand の場所`

Do not add participant-identification aliases or status-reading prompts:

- `誰が手を挙げていますか`
- `挙手している人`
- `手を挙げた参加者`
- `誰がリアクションしましたか`

Do not expand adjacent risky surfaces in the same implementation:

- `ringcentral.video.toolbar.share`
- `ringcentral.video.toolbar.invite`
- `ringcentral.video.main.add-coworkers`
- `ringcentral.video.more.recording`
- `ringcentral.video.more.notes`
- `ringcentral.video.toolbar.leave`
- `ringcentral.video.more.settings`
- `ringcentral.video.more.background`
- `ringcentral.video.toolbar.more`
- direct camera/video toggle aliases

If the product later wants English-label Japanese phrasing for `Raise hand`, treat it as a separate routing design question. The current Q&A-first token matcher can prefer the safety Q&A for `Raise hand の場所`, so a plain alias may not produce the desired location route.

## Acceptance Signals

The next implementation should demonstrate these signals:

- `packages/ringcentral-video.yaml` adds `questionAliases.ja` only under `ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`.
- The exact alias sets match the Recommended Scope table, or the implementer updates all expected counts and risk notes if they deliberately choose a smaller `+4`/`+5` slice.
- `tests/unit/test_material_packages.py` replaces the current `assert "ja" not in ...question_aliases` checks for Reactions and Raise hand with exact alias-list assertions and updates localization counts to `11/27` and `32`.
- `tests/unit/test_questions.py` proves the six recommended Japanese location prompts route to the intended entrypoint with `can_operate is False`.
- Negative prompts such as `リアクションを送って`, `いいねして`, `挙手して`, `手を挙げて`, `手を下げて`, and `誰が手を挙げていますか` remain non-operable and do not become participant-identification paths.
- Existing localized reaction/raise-hand safety Q&A remains answer-only for `リアクションを送ったり手を上げたりできますか`.
- `tests/unit/test_cli.py` and `tests/unit/test_diagnostics.py` update exact doctor/localization strings to `32 aliases` and `85 package-owned aliases`.
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja` reports `questionAliases.ja present on 11/27 entrypoints (32 aliases)`.
- `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete` still passes.
- `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` remains `0 warnings, 0 failed`, with `qa alias overlap` OK and substring risk no worse than the current INFO baseline.

## Handoff Notes

Read-only checks run for this demand analysis:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Observed baseline:

- Japanese localization report: `51/51` demo steps, `12/12` localized Q&A questions, `12/12` localized Q&A answers, `questionAliases.ja present on 9/27 entrypoints (26 aliases)`.
- Doctor: `11 ok, 1 info, 0 warnings, 0 failed`; `79 package-owned aliases have no cross-entrypoint duplicates`; `qa alias overlap` OK for `71` Q&A prompts.

Useful existing tests to update or preserve:

- `tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_reactions_narration`
- `tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_raise_hand_narration`
- `tests/unit/test_questions.py::test_ringcentral_reaction_and_raise_hand_safety_questions_are_answer_only`
- `tests/unit/test_questions.py::test_ringcentral_localized_reaction_and_raise_hand_safety_questions_are_answer_only`
- `tests/unit/test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table`
- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package`

This handoff changed only `docs/agent-handoffs/cycle-103-demand-analysis.md`.
