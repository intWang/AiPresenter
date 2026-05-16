# Cycle 103 Technical Scan: Japanese aliases for Reactions and Raise hand

Scope: read-only technical handoff for evaluating Japanese package-owned `questionAliases` on `ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`. This scan did not modify YAML, runtime code, or tests.

## Baseline

- Current Japanese alias coverage is `9/27` entrypoints and `26` aliases. Verified with `.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja`.
- Current total package-owned alias count is `79`. Verified with `.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`.
- `ringcentral.video.toolbar.react` currently has no `questionAliases`. Its entrypoint has `title: Reactions`, `purpose: Send meeting reactions without interrupting speech`, one `clickWindowControl` open step targeting `React`, `cleanup: escape`, and presenter notes that say reactions are visible lightweight feedback and the strip should be closed with Escape if no reaction should be sent.
- `ringcentral.video.toolbar.raise-hand` currently has no `questionAliases`. Its entrypoint has `title: Raise hand`, `purpose: Raise or lower hand to request attention`, one `clickWindowControl` open step targeting `Raise hand`, `alternateTargets: onconf.reactions.REMOVE_RAISE_HAND`, `cleanup: toggle`, and presenter notes that it toggles state and should be clicked again to lower the hand after demonstration.
- Existing Japanese narration already covers both routes in `meeting-controls-tour` and `meeting-control-map-demo`: `explain-reactions`, `explain-raise-hand`, `control-map-reactions`, and `control-map-raise-hand`.
- Existing Q&A already has an answer-only safety item: `Can AiPresenter send a reaction or raise my hand safely?`, with Japanese prompt `リアクションを送ったり手を上げたりできますか` and localized answer saying AiPresenter can explain location but should not send a reaction or raise/leave a hand unless explicitly asked.

## Candidate YAML Patch Shape

Recommended conservative alias shape:

```yaml
- id: ringcentral.video.toolbar.react
  title: Reactions
  area: Meeting toolbar
  purpose: Send meeting reactions without interrupting speech.
  questionAliases:
    ja:
    - リアクション欄
    - Reactions の場所
    - クイックフィードバック
  openSteps:
  # existing openSteps unchanged

- id: ringcentral.video.toolbar.raise-hand
  title: Raise hand
  area: Meeting toolbar
  purpose: Raise or lower hand to request attention.
  questionAliases:
    ja:
    - Raise hand の場所
    - 挙手ボタン
    - 発言機会の合図
  openSteps:
  # existing openSteps unchanged
```

These six aliases are location/control-label oriented. They avoid exact overlap with existing Q&A prompts and avoid the most tempting broad aliases `リアクション` and `手を上げ`, which would be substrings of the existing Japanese safety Q&A prompt and could increase the current `qa alias substring risk` INFO count.

## Runtime Behavior

- `answer_question()` normalizes the prompt, checks Q&A first, then falls back to entrypoint matching.
- `_match_qa()` uses exact Q&A prompts, fragment containment, then token overlap. This means the existing full safety question `リアクションを送ったり手を上げたりできますか` remains answer-only before package-owned entrypoint aliases are considered.
- `_match_entrypoint_alias()` checks package-owned aliases before the legacy hard-coded alias table. Adding these aliases to YAML is enough for Japanese matching even if `_ENTRYPOINT_ALIASES` is monkeypatched empty in tests.
- `MaterialPackage` trims and casefolds aliases, skips blanks, and sorts alias matching by descending normalized alias length before original order.
- `_can_operate()` returns `False` for `None`, explain-only ids, empty `openSteps`, or any risky word found in the entrypoint id/title/purpose.
- `react` has executable `openSteps`, but its title/purpose contains risky terms: `Send` and `reactions` hit `_RISKY_ENTRYPOINT_WORDS` entries `send` and `reaction`. Expected `can_operate` is `False`.
- `raise-hand` also has executable `openSteps`, but its title/purpose contains `Raise hand` and `lower hand`, both risky words. Expected `can_operate` is `False`.
- Therefore new aliases should route location-style questions to the two entrypoints, but controller/session question handling should stay text-only rather than queueing an operation.

## Test Plan

- Update `tests/unit/test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes` to include exact alias sets for `ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`.
- Update `test_meeting_control_map_has_japanese_reactions_narration` and `test_meeting_control_map_has_japanese_raise_hand_narration`: replace current `assert "ja" not in ...question_aliases` checks with exact alias-list assertions, and update local report expectations from `9` / `26` to `11` / `32`. Keep existing `openSteps` and `presenterNotes` assertions.
- Extend `tests/unit/test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table` with Japanese routing cases such as `リアクション欄はどこですか`, `Reactions の場所はどこですか`, `クイックフィードバックはどこですか`, `Raise hand の場所はどこですか`, `挙手ボタンはどこですか`, and `発言機会の合図はどこですか`. All should match the expected entrypoint with `can_operate is False`.
- Keep or extend `test_ringcentral_localized_reaction_and_raise_hand_safety_questions_are_answer_only` to assert the full Japanese safety prompt still returns `entrypoint_id is None` and `can_operate is False`.
- Update CLI and diagnostics count assertions:
  - `test_localization_report_outputs_japanese_demo_and_qa_coverage`: `questionAliases.ja present on 11/27 entrypoints (32 aliases)`.
  - `test_doctor_loads_profile_package_and_flow`: `85 package-owned aliases have no cross-entrypoint duplicates`.
  - `test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`: same `85` detail.
- If implementation uses broader aliases like `リアクション`, `手を上げる`, or `手を上げ`, re-check `qa alias substring risk`; the count may move from `11` to `12` because the existing Japanese safety Q&A prompt contains those concepts.

Recommended focused verification after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_reactions_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_raise_hand_narration tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_ringcentral_localized_reaction_and_raise_hand_safety_questions_are_answer_only tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

## Expected Counts

- Baseline: `questionAliases.ja present on 9/27 entrypoints (26 aliases)`.
- Candidate adds `2` new Japanese-covered entrypoints and `6` Japanese aliases.
- Expected Japanese coverage: `11/27` entrypoints and `32` aliases.
- Baseline total package-owned aliases: `79`.
- Expected total package-owned aliases: `85`.
- `operationEntrypoints` remains `27`.
- Demo and Q&A localization totals should remain `51/51` demo steps, `12/12` Q&A questions, and `12/12` Q&A answers for Japanese.
- Q&A prompt candidate count should remain `71`.
- With the conservative aliases above, `qa alias overlap` should remain OK and `qa alias substring risk` is expected to remain INFO at `11` prompts. This should still be verified by diagnostics after the YAML change.

## Risks

- The main behavioral risk is accidentally turning a state-changing control into an operable question result. Current runtime prevents that through risky-word scanning, but add explicit tests for `can_operate is False` on both Japanese alias routes.
- The main diagnostics risk is choosing too-broad aliases. Exact Q&A alias overlap would produce a WARN; substring overlap would remain runtime-safe because Q&A matches first, but it can change the existing INFO count and test expectations.
- `raise-hand` is a toggle. Even though question routing should stay non-operable, scripted demos still use `operation: toggle`; preserve the existing cleanup/toggle assumptions and presenter-note checks.
- Future copy changes to title/purpose could remove `send`, `reaction`, `raise hand`, or `lower hand`; that would weaken the current `_can_operate()` protection. Tests should assert the final question response is non-operable, not merely that the current words exist.
- No runtime code changes appear necessary for this slice. Package-owned aliases already take precedence over the legacy alias table and are exercised with the legacy table disabled in the Japanese alias routing test.
