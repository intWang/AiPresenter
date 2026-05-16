# Cycle 103 Risk Scan: Japanese Reactions And Raise Hand Aliases

## Risk Verdict

Proceed only with a narrow location-only Japanese alias slice for
`ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`.

The safe path is not to make these aliases mean "send a reaction" or "raise my
hand". They may only help the user ask where the UI control is. Both entrypoints
already have meeting-visible side effects in their executable routes:

- `ringcentral.video.toolbar.react` opens the reaction strip and must close it
  with Escape when no reaction is sent.
- `ringcentral.video.toolbar.raise-hand` toggles hand state and must not leave
  the hand raised after a confirmed demo.

Runtime question routing should keep `can_operate=False` for these entrypoints.
That is currently supported by the risky-word gate, but implementation tests
must assert it directly.

I simulated the final +4 candidate set in memory without writing YAML. Expected
post-implementation counts are:

- `questionAliases.ja`: `9/27` entrypoints and `26` aliases -> `11/27`
  entrypoints and `30` aliases.
- Total package-owned aliases: `79` -> `83`.
- Doctor `question aliases`: OK with `83 package-owned aliases have no
  cross-entrypoint duplicates`.
- Doctor `qa alias overlap`: OK with `71 Q&A question prompts have no unsafe
  package-owned alias overlaps`.
- Doctor `qa alias substring risk`: remains the existing INFO-level `11` prompt
  summary for this exact +4 set.

## Safe Alias Candidates

Recommended aliases for `ringcentral.video.toolbar.react`:

- `React ボタンの場所`
- `リアクション欄の場所`

Recommended aliases for `ringcentral.video.toolbar.raise-hand`:

- `挙手ボタンの場所`
- `挙手の場所`

These are deliberately location nouns with `場所`, `ボタン`, or `欄`. They avoid
bare action labels and do not appear as substrings in the existing Japanese
Reactions / Raise hand safety Q&A prompt.

Do not add `Raise hand の場所` in this slice. In the current matcher, the mixed
English phrase is caught by Q&A-first token matching against the existing
English safety prompts for "raise hand" and returns the answer-only safety Q&A
instead of the entrypoint. Keep that behavior as a negative test unless the
question matcher is deliberately redesigned.

## Forbidden Alias Patterns

Do not add aliases that can be read as sending a visible reaction:

- `リアクション`
- `リアクションを送る`
- `リアクションを送って`
- `いいね`
- `いいねして`
- `拍手`
- `拍手して`
- `ハートを送る`
- `絵文字を送る`
- `反応する`
- `Be right back`

Do not add aliases that can be read as toggling or preserving hand state:

- `手を上げる`
- `手を上げて`
- `手を下げる`
- `手を下げて`
- `挙手して`
- `挙手を取り消す`
- `挙手を下げる`
- `手を上げたまま`
- `Raise hand の場所`

Do not add aliases that ask for participant identity or meeting moderation:

- `誰がリアクションしたか`
- `誰が手を上げていますか`
- `参加者の名前`
- `挙手している人`
- `ホストとして手を下げる`
- `全員の手を下げる`
- `参加者をミュート`
- `主催者コントロール`

Do not add aliases that exactly equal or are broad substrings of the existing
safety Q&A prompt `リアクションを送ったり手を上げたりできますか`. Bare
`リアクション` and `手を上げ` patterns would expand the doctor substring-risk
surface and are not needed for a location-only slice.

## Required Tests

Add or update package alias assertions:

- Extend `test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes`
  with the exact +4 alias set above.
- Assert Japanese alias counts move exactly to `11/27` entrypoints and `30`
  aliases.
- Update the existing Reactions and Raise hand narration tests that currently
  assert `"ja" not in entrypoint.question_aliases`; replace those with exact
  alias-list assertions while preserving open-step cleanup assertions.

Add route tests with `_ENTRYPOINT_ALIASES` monkeypatched to `{}`:

- `React ボタンの場所はどこですか` routes to
  `ringcentral.video.toolbar.react` with `can_operate is False`.
- `リアクション欄の場所はどこですか` routes to
  `ringcentral.video.toolbar.react` with `can_operate is False`.
- `挙手ボタンの場所はどこですか` routes to
  `ringcentral.video.toolbar.raise-hand` with `can_operate is False`.
- `挙手の場所はどこですか` routes to
  `ringcentral.video.toolbar.raise-hand` with `can_operate is False`.

Add negative route tests:

- `リアクションを送ったり手を上げたりできますか` remains answer-only:
  `entrypoint_id is None`, `can_operate is False`, and the Japanese safety
  answer mentions explicit user intent and cleanup.
- `Raise hand の場所はどこですか` must not become an entrypoint alias in this
  slice; it should remain answer-only or otherwise non-operable.
- `リアクションを送って`, `いいねして`, `拍手して`, and `ハートを送って` must
  remain non-operable and must not route to `ringcentral.video.toolbar.react`.
- `手を上げて`, `挙手して`, `手を下げて`, and `挙手を取り消して` must remain
  non-operable and must not route to `ringcentral.video.toolbar.raise-hand`.
- `誰がリアクションしたか教えて`, `誰が手を上げていますか`, and
  `挙手している人を教えて` must remain non-operable and must not disclose or
  infer participant identity.
- `ホストとして全員の手を下げて` and `主催者として参加者をミュートして` must
  remain non-operable and must not imply host/moderator control.

Add doctor and CLI expectation updates:

- `test_diagnostics_reports_question_aliases_ok_for_ringcentral_package` should
  expect `83 package-owned aliases have no cross-entrypoint duplicates`.
- `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` should
  remain `71 Q&A question prompts have no unsafe package-owned alias overlaps`.
- `test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package`
  should remain INFO with the existing `11` prompt summary for this exact +4
  alias set. If the count changes, inspect the added aliases before accepting
  the new count.
- CLI localization-report expectations should move to
  `questionAliases.ja present on 11/27 entrypoints (30 aliases)`.

## Verification Commands

Focused tests after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_reactions_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_raise_hand_narration tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_localized_reaction_and_raise_hand_safety_questions_are_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Add the new negative tests described above to `tests\unit\test_questions.py` and
include them in the focused command once named.

Diagnostics and report checks:

```powershell
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Stale-count search:

```powershell
rg -n "questionAliases\.ja present on 9/27|entrypoints_with_aliases == 9|alias_total == 26|79 package-owned aliases" tests docs
```

Expected post-implementation strings:

```text
questionAliases.ja present on 11/27 entrypoints (30 aliases)
[OK] question aliases: 83 package-owned aliases have no cross-entrypoint duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
```

## Handoff Notes

This risk scan changed only this handoff document. It did not edit code, YAML,
or tests.

The next implementation should be a small YAML/test/docs count update only. Do
not alter matcher semantics, route execution, cleanup behavior, Q&A wording, or
presenter safety skills as part of the alias slice.

The important overlap rule is Q&A-first matching. Exact Q&A prompts must stay
answer-only, and package-owned aliases must not shadow safety Q&A prompts. The
doctor exact overlap check should stay OK; the substring-risk check should
remain INFO-only and unchanged for the recommended +4 set. Any new Japanese
substring conflict involving Reactions or Raise hand means the alias wording is
too broad.

Keep Reactions separate from Raise hand. Reactions open a strip of visible
signals; Raise hand is a state toggle. Neither alias family may identify
participants, read meeting-visible state about who reacted or raised a hand, or
claim host/moderator authority.
