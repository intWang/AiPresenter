# Cycle 102 Technical Scan: Japanese questionAliases next slice

Scope: read-only technical handoff for the next Japanese `questionAliases.ja` expansion. This scan did not modify YAML, code, tests, or git history.

## Verified baseline

- `packages/ringcentral-video.yaml` has `27` `operationEntrypoints`.
- Current `questionAliases.ja`: `7/27` entrypoints, `21` aliases.
- Current total package-owned aliases across all languages: `74`.
- `ai-presenter localization-report --package ringcentral-video --language ja` reports:
  - `51/51` demo steps localized.
  - `12/12` Q&A questions localized.
  - `12/12` Q&A answers localized.
  - `questionAliases.ja present on 7/27 entrypoints (21 aliases)`.
- `ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo` reports:
  - `[OK] question aliases: 74 package-owned aliases have no cross-entrypoint duplicates`.
  - `[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps`.
  - Existing `[INFO] qa alias substring risk` remains at `11` Q&A prompts.

Focused baseline tests run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests\unit\test_questions.py::test_meeting_info_privacy_gate_does_not_depend_on_risky_words tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_summary_narration
```

Observed result: `8 passed`.

## Runtime safety findings

`ringcentral.video.top.meeting-info` is explain-only for question routing at runtime even though the YAML entrypoint has one coordinate `openSteps` route. The hard gate is in `src/ai_presenter/runtime/questions.py`:

- `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS` contains `ringcentral.video.top.meeting-info`.
- `_can_operate()` checks that denylist before it checks `open_steps`.
- Therefore package-owned aliases for meeting-info should match the entrypoint, but `QuestionResponse.can_operate` must stay `False`.

The current tests are:

- `tests/unit/test_questions.py::test_meeting_info_privacy_questions_are_answer_only`
- `tests/unit/test_questions.py::test_meeting_info_privacy_gate_does_not_depend_on_risky_words`

These already prove English/Chinese meeting-info routing is answer-only. The next implementation should extend them or add a nearby Japanese-specific test so Japanese aliases also prove:

- `entrypoint_id == "ringcentral.video.top.meeting-info"`.
- `can_operate is False`.
- The answer is generic and does not include an exact meeting ID, exact URL, dial-in number, or copied meeting link value. It may still contain generic labels like `meeting ID` and `copy link` because `_render_entrypoint_answer()` renders the entrypoint title and purpose, not live UI contents.

`ringcentral.video.overview` is also non-operable. It has `openSteps: []` in `packages/ringcentral-video.yaml`, so `_can_operate()` returns `False` by the normal empty-open-steps rule. Existing overview coverage is in:

- `tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_overview_narration`
- `tests/unit/test_material_packages.py::test_meeting_control_map_has_japanese_summary_narration`

The summary test currently asserts `overview_entrypoint.open_steps == []` and `ja` is not yet present in overview aliases. If overview gets Japanese aliases, keep the empty `openSteps` assertion and replace the no-`ja` assertion with an exact alias list assertion.

## Recommended narrow implementation

Prefer a two-entrypoint slice: meeting-info plus overview/control-map. This is the safest useful next step because neither route should cause runtime operation from question routing:

| Entrypoint | Add `questionAliases.ja` | Why this slice |
| --- | --- | --- |
| `ringcentral.video.top.meeting-info` | `会議情報`, `会議IDの場所`, `会議リンクの場所` | Covers the privacy-sensitive ID/link lookup path while preserving the explicit runtime explain-only gate. |
| `ringcentral.video.overview` | `コントロールマップ`, `会議画面の概要` | Adds natural control-map/overview lookup without any UI operation because `openSteps` is empty. |

Expected count changes for this recommended `+5` alias slice:

- `questionAliases.ja`: `7/27`, `21 aliases` -> `9/27`, `26 aliases`.
- Total package-owned aliases: `74` -> `79`.
- `operationEntrypoints` stays `27`.
- Doctor `question aliases` detail should become `79 package-owned aliases have no cross-entrypoint duplicates`.
- CLI localization report should become `questionAliases.ja present on 9/27 entrypoints (26 aliases)`.
- `qa alias overlap` should stay `71 Q&A question prompts have no unsafe package-owned alias overlaps`.
- `qa alias substring risk` should remain INFO at `11` prompts for these exact aliases based on in-memory simulation.

Pure minimum alternative: add only two aliases to meeting-info, for example `会議情報` and `会議IDの場所`, plus the two overview aliases. That would produce `9/27`, `25` Japanese aliases and `78` package-owned aliases. I do not recommend that as the main target because it leaves the meeting-link privacy alias path untested.

## In-memory validation of candidate aliases

I validated the recommended `+5` set by loading the package, appending the aliases in memory, and running the package model plus diagnostic helpers without writing the YAML.

Expected simulated diagnostics:

- `[OK] question aliases: 79 package-owned aliases have no cross-entrypoint duplicates`
- `[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps`
- `[INFO] qa alias substring risk: 11 Q&A question prompts ...`

Expected simulated Japanese routing with legacy aliases disabled or irrelevant:

| Question | Expected entrypoint | Expected `can_operate` |
| --- | --- | --- |
| `会議情報はどこですか` | `ringcentral.video.top.meeting-info` | `False` |
| `会議IDの場所はどこですか` | `ringcentral.video.top.meeting-info` | `False` |
| `会議リンクの場所はどこですか` | `ringcentral.video.top.meeting-info` | `False` |
| `コントロールマップはどこですか` | `ringcentral.video.overview` | `False` |
| `会議画面の概要を教えて` | `ringcentral.video.overview` | `False` |

## Files to update in the next implementation

Only these implementation files should need changes:

- `packages/ringcentral-video.yaml`
  - Add `questionAliases.ja` under `ringcentral.video.top.meeting-info`.
  - Add `questionAliases.ja` under `ringcentral.video.overview`.
  - Do not change `openSteps`, locators, cleanup, demo flow actions, Q&A, or runtime code.
- `tests/unit/test_material_packages.py`
  - Update `test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage` from `7/21` to `9/26`.
  - Update `test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes` so its exact expected alias map includes meeting-info and overview.
  - Update `test_meeting_control_map_has_japanese_meeting_info_narration` to assert the exact meeting-info Japanese aliases.
  - Update `test_meeting_control_map_has_japanese_summary_narration` to replace `assert "ja" not in overview_entrypoint.question_aliases` with the exact overview alias list, while keeping `overview_entrypoint.open_steps == []`.
  - Keep unrelated high-risk assertions unchanged for Share, Recording, Notes, Leave, broad Settings, More, direct camera toggle, reactions, and raise-hand.
- `tests/unit/test_questions.py`
  - Extend `test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table` with the five routing cases above.
  - Add or extend meeting-info privacy coverage so Japanese `会議IDの場所` and `会議リンクの場所` route to meeting-info with `can_operate is False`.
  - Add negative answer assertions that no concrete meeting ID/link is exposed, for example no `https://`, no `ringcentral.com`, no fake exact ID such as `123456789`, and no dial-in-looking exact value. Keep the assertion targeted to concrete values rather than generic labels.
- `tests/unit/test_cli.py`
  - Update localization report assertion to `questionAliases.ja present on 9/27 entrypoints (26 aliases)`.
  - Update doctor assertion to `79 package-owned aliases have no cross-entrypoint duplicates`.
  - Keep the Q&A and substring-risk assertions at `71` and INFO unless implementation aliases differ.
- `tests/unit/test_diagnostics.py`
  - Update `test_diagnostics_reports_question_aliases_ok_for_ringcentral_package` to `79 package-owned aliases have no cross-entrypoint duplicates`.
  - Keep `test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package` at `71 Q&A question prompts have no unsafe package-owned alias overlaps` for the recommended aliases.
- `docs/knowledge/ringcentral-video/source-index.md`
  - Update the localization bullet so it names the new coverage: meeting information and control-map/overview in addition to microphone, Participants, Chat, Network quality, View layout, audio menu, and camera menu.
  - Keep the note that higher-risk or privacy-sensitive operation remains future work; meeting-info aliases are allowed only because question routing remains answer-only.

## Suggested test commands for the next cycle

Red command before YAML changes:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_meeting_info_narration tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_summary_narration tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table tests\unit\test_questions.py::test_meeting_info_privacy_questions_are_answer_only tests\unit\test_questions.py::test_meeting_info_privacy_gate_does_not_depend_on_risky_words tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Green verification after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

Stale-expectation scan:

```powershell
rg -n "questionAliases\.ja present on 7/27|entrypoints_with_aliases == 7|alias_total == 21|74 package-owned aliases" tests docs
```

Expected post-change CLI/doctor strings:

```text
questionAliases.ja present on 9/27 entrypoints (26 aliases)
[OK] question aliases: 79 package-owned aliases have no cross-entrypoint duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
```

## Review checklist for the next agent

- Confirm only the two recommended entrypoints gained Japanese aliases.
- Confirm meeting-info `can_operate` stays `False` through `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS`, not merely through risky-word heuristics.
- Confirm overview `can_operate` stays `False` because `openSteps` remains empty.
- Confirm no exact meeting ID, meeting URL, dial-in number, participant name, email, invite suggestion, or copied link appears in the Japanese answer tests.
- Confirm package-owned alias totals move exactly to `9/27`, `26`, and `79`.
- Confirm source-index describes the new Japanese alias coverage and still distinguishes answer-only privacy surfaces from operable controls.
- Do not include `.coverage` or unrelated docs in the next implementation diff.
