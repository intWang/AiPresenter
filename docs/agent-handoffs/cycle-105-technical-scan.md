# Cycle 105 Technical Scan: answer-only policy for sensitive More entrypoints

## Recommendation

Implement a small runtime/package policy field before adding Japanese Notes/Transcript aliases. The first slice should make question-triggered responses for sensitive informational entrypoints answer-only, while leaving scripted demo flow execution unchanged.

Recommended technical slice:

1. Add package-owned operation policy metadata to `OperationEntrypoint`.
2. Mark `ringcentral.video.more.notes` as question answer-only.
3. Keep `ringcentral.video.top.meeting-info` answer-only through the same policy path.
4. Update question/session tests to assert `can_operate=False` and `create_question_interrupt_step(...) is None` for Notes/Transcript question responses.
5. Only after that, add the Japanese Notes/Transcript aliases as a separate package/test slice.

## Current baseline after Cycle 104

- `packages/ringcentral-video.yaml` has `27` operation entrypoints.
- Package-owned question aliases total `85`.
- Japanese `questionAliases.ja` coverage is `12/27` entrypoints and `32` aliases.
- `ringcentral.video.more.recording` now has Japanese aliases:
  - `Start recording の場所`
  - `録画ボタンの場所`
- `ringcentral.video.more.notes` still has no Japanese aliases.
- `ringcentral.video.more.notes` has executable `openSteps`: click `More`, then click `onconf.controls.NOTES` / `Notes`, with `cleanup: sidePanel`.
- `ringcentral.video.top.meeting-info` has executable `openSteps`, but `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS` hard-blocks question interrupts for that entrypoint.

## Minimal implementation surface

### Data model

The narrowest durable model change is an optional field on `OperationEntrypoint`, for example:

```yaml
questionPolicy: answerOnly
```

or:

```yaml
questionAnswerOnly: true
```

`questionPolicy` is more extensible and avoids future boolean drift if later states are needed, such as `confirmBeforeOperate`. A minimal Pydantic shape could be:

```python
question_policy: Literal["default", "answerOnly"] = Field(
    default="default",
    alias="questionPolicy",
)
```

This belongs in `src/ai_presenter/packages/models.py`, not in the RingCentral-only runtime constants. It keeps sensitive policy package-owned and lets other packages opt in without editing `questions.py`.

### Runtime

Update `src/ai_presenter/runtime/questions.py` so `_can_operate()` checks the entrypoint policy before `open_steps` and risky-word heuristics:

```python
entrypoint = package.entrypoint_by_id(entrypoint_id)
if entrypoint.question_policy == "answerOnly":
    return False
```

Then migrate the existing `ringcentral.video.top.meeting-info` constant to YAML metadata and remove or deprecate `_QUESTION_EXPLAIN_ONLY_ENTRYPOINT_IDS`. The safest incremental path is to support both for one cycle, with tests proving the package policy works independent of the old hardcoded set, then remove the constant in a cleanup cycle.

No change is needed in `src/ai_presenter/runtime/session.py` if `QuestionResponse.can_operate` is correct. `create_question_interrupt_step()` already refuses to create a step when `can_operate` is false.

### Package

Mark these entrypoints answer-only for question responses:

- `ringcentral.video.top.meeting-info`: exposes meeting ID/link/copy-link surfaces.
- `ringcentral.video.more.notes`: opens a side panel that may expose notes/transcript content and contains `Start notes` plus `Also record this meeting`.

Do not remove `openSteps` from `ringcentral.video.more.notes`; demo flows currently use the executable route intentionally. The policy needs to affect question interrupts, not scripted package demos.

Do not mark `ringcentral.video.more.recording` only because it is already non-operable through `openSteps: []` plus risky wording. It can later receive explicit metadata for clarity, but that is not required for the minimal Notes/Transcript blocker.

## Tests to update or add

Primary question/runtime tests:

- Update `tests/unit/test_questions.py::test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint`.
  - Current assertion: `can_operate is True`.
  - New assertion: `entrypoint_id == "ringcentral.video.more.notes"`, `can_operate is False`, and `create_question_interrupt_step(package, response) is None`.
- Add a focused package-policy test with `_RISKY_ENTRYPOINT_WORDS` emptied to prove Notes is blocked by explicit policy, not incidental wording.
- Extend Japanese privacy-sensitive coverage to include Notes/Transcript location prompts once aliases are added.

Session coverage:

- Add or extend a `tests/unit/test_controller_session.py` case proving a Notes/Transcript answer cannot create an interrupt step, even though the package entrypoint has executable `openSteps`.

Material/package tests:

- Add assertions in `tests/unit/test_material_packages.py` that `meeting-info` and `more.notes` carry the new policy field.
- Preserve the existing `more.notes.open_steps` assertions so demo executability is not accidentally removed.

Diagnostics and CLI count tests if Japanese Notes aliases are later added:

- `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`
  - Current: `questionAliases.ja present on 12/27 entrypoints (32 aliases)`.
  - If adding two Notes aliases: `questionAliases.ja present on 13/27 entrypoints (34 aliases)`.
- `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`
  - Current: `85 package-owned aliases have no cross-entrypoint duplicates`.
  - If adding two Notes aliases: `87 package-owned aliases have no cross-entrypoint duplicates`.
- Many localized material-package tests pin `report.entrypoints_with_aliases == 12` and `report.alias_total == 32`; these move to `13` and `34` only in the later alias slice.

## Later Japanese Notes/Transcript alias slice

After the answer-only policy is in place, the smallest Notes/Transcript alias addition is:

```yaml
- id: ringcentral.video.more.notes
  questionAliases:
    ja:
    - Notes and Transcript の場所
    - ノートと文字起こしの場所
```

Keep aliases location-only. Do not add action, content, summary, download, post-meeting, or value-reading variants.

Expected later count deltas:

- `questionAliases.ja`: `12/27`, `32 aliases` -> `13/27`, `34 aliases`.
- Package-owned aliases: `85` -> `87`.
- Q&A localized coverage remains `12/12` questions and `12/12` answers.
- Demo-step localized coverage remains `51/51`.

## Compatibility hazards

- `OperationEntrypoint` currently has `extra="forbid"` through `CamelModel`; adding YAML metadata before the model field will break package loading.
- If the policy is implemented by removing `openSteps`, scripted demo flows that open Notes will break. Keep execution metadata and gate only question interrupts.
- If the policy stays as another hardcoded set in `questions.py`, future packages cannot declare their own sensitive-but-executable question behavior without runtime edits.
- Existing tests intentionally say English `Where are Notes and transcript` is operable. The policy slice must treat the test change as deliberate, not as incidental fallout.
- `_can_operate()` is used both for Q&A matches and entrypoint matches. Marking Notes answer-only means even an exact Notes Q&A with `relatedEntrypointIds` will return the entrypoint id but no interrupt step. That is the desired safety boundary.
- Diagnostics may need a follow-up check later: aliases pointing at `questionPolicy: answerOnly` are not unsafe by themselves, but the report does not currently surface policy coverage for sensitive executable entrypoints.

## Focused verification commands

For the policy-only slice:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint tests\unit\test_controller_session.py tests\unit\test_material_packages.py::test_meeting_control_map_has_japanese_notes_narration tests\unit\test_questions.py::test_meeting_info_privacy_gate_does_not_depend_on_risky_words
```

For the later Notes alias slice, add:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage
```
