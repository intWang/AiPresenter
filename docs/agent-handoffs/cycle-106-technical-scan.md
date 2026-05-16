# Cycle 106 Technical Scan: Japanese Notes/Transcript aliases

## Recommendation

Add the narrow Japanese Notes/Transcript location aliases now that Cycle 105 put `ringcentral.video.more.notes` behind `questionPolicy: answerOnly`.

Recommended technical slice:

1. Add exactly two Japanese `questionAliases.ja` strings to `ringcentral.video.more.notes`.
2. Update the package-owned Japanese alias tests and runtime Japanese question matching tests.
3. Update pinned CLI and diagnostics alias-count expectations.
4. Do not change Notes `openSteps`, demo narration, Q&A text, runtime matching logic, or answer-only policy behavior.

## Current baseline

Verified against commit `adcc876 feat: add answer-only question policy`.

- `packages/ringcentral-video.yaml` has `27` operation entrypoints.
- Package-owned question aliases total `85`.
- Japanese `questionAliases.ja` coverage is `12/27` entrypoints and `32` aliases.
- Total aliases by language:
  - `en`: `1` entrypoint, `4` aliases.
  - `zh`: `15` entrypoints, `49` aliases.
  - `ja`: `12` entrypoints, `32` aliases.
- `ringcentral.video.more.notes` currently has `questionPolicy: answerOnly`.
- `ringcentral.video.more.notes` currently has Chinese aliases only:
  - `笔记`
  - `转录`
  - `会议笔记`
- `ringcentral.video.more.notes` still has executable demo `openSteps`: click `More`, then click `onconf.controls.NOTES` / alternate visible text `Notes`, with `cleanup: sidePanel`.
- Current Japanese localization report says `questionAliases.ja present on 12/27 entrypoints (32 aliases)`.
- Current doctor diagnostics say `85 package-owned aliases have no cross-entrypoint duplicates`.

## Proposed package change

Modify only the Notes/Transcript entrypoint alias block:

`packages/ringcentral-video.yaml`

```yaml
- id: ringcentral.video.more.notes
  questionPolicy: answerOnly
  questionAliases:
    ja:
    - Notes and Transcript の場所
    - ノートと文字起こしの場所
    zh:
    - 笔记
    - 转录
    - 会议笔记
```

Keep these aliases location-only. Do not add broader forms such as `ノート`, `文字起こし`, or `Notes`, because the package already has Japanese Q&A around notes/transcript and broad aliases would be more likely to create substring-risk noise or overmatch content-reading requests.

## Expected count deltas

If adding exactly the two aliases above:

- Japanese `questionAliases.ja`: `12/27` entrypoints and `32` aliases -> `13/27` entrypoints and `34` aliases.
- Total package-owned aliases: `85` -> `87`.
- Chinese aliases: unchanged at `15/27` entrypoints and `49` aliases.
- English aliases: unchanged at `1` entrypoint and `4` aliases.
- Q&A localized coverage: unchanged at `12/12` questions and `12/12` answers.
- Demo-step localized coverage: unchanged at `51/51`.
- Diagnostics `qa questions`: unchanged at `71 Q&A question prompts have no cross-item duplicates`.
- Diagnostics `qa alias overlap`: unchanged at `71 Q&A question prompts have no unsafe package-owned alias overlaps`.
- Diagnostics `qa alias substring risk`: should stay INFO with `11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`.

I checked the proposed two aliases in memory through `diagnose_configuration(...)`; they produce `87` aliases, JA `13` entrypoints / `34` aliases, no duplicate alias warning, no unsafe Q&A alias overlap, and no increase to the current substring-risk count.

## Exact files likely to modify

- `packages/ringcentral-video.yaml`
  - Add the two `questionAliases.ja` values under `ringcentral.video.more.notes`.
- `tests/unit/test_material_packages.py`
  - Add `ringcentral.video.more.notes` to `test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes`.
  - Expected alias set for Notes should be exactly `{"Notes and Transcript の場所", "ノートと文字起こしの場所"}`.
- `tests/unit/test_questions.py`
  - Extend `test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table` with Japanese Notes/Transcript location prompts.
  - Assert the matched entrypoint is `ringcentral.video.more.notes` and `can_operate is False`.
  - Add a focused assertion that `create_question_interrupt_step(package, response) is None` for the Japanese Notes alias response.
- `tests/unit/test_cli.py`
  - Update `test_localization_report_outputs_japanese_demo_and_qa_coverage` from `questionAliases.ja present on 12/27 entrypoints (32 aliases)` to `questionAliases.ja present on 13/27 entrypoints (34 aliases)`.
  - Update doctor CLI expectation from `85 package-owned aliases have no cross-entrypoint duplicates` to `87 package-owned aliases have no cross-entrypoint duplicates`.
- `tests/unit/test_diagnostics.py`
  - Update `test_diagnostics_reports_question_aliases_ok_for_ringcentral_package` from `85 package-owned aliases have no cross-entrypoint duplicates` to `87 package-owned aliases have no cross-entrypoint duplicates`.
- `docs/knowledge/ringcentral-video/source-index.md`
  - If the implementation cycle keeps knowledge docs current, update the localization note so Notes/Transcript is no longer listed among future Japanese alias work.

No model or runtime file should be necessary for this slice. Cycle 105 already added `question_policy` to `OperationEntrypoint` and `_can_operate()` already returns false for `answerOnly`.

## Red tests to write first

1. In `tests/unit/test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes`, add:

```python
"ringcentral.video.more.notes": {
    "Notes and Transcript の場所",
    "ノートと文字起こしの場所",
},
```

Expected RED before package edit: `set(aliases_by_entrypoint) == set(expected_aliases)` fails because `ringcentral.video.more.notes` has no Japanese aliases.

2. In `tests/unit/test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table`, add:

```python
"Notes and Transcript の場所はどこですか": (
    "ringcentral.video.more.notes",
    False,
),
"ノートと文字起こしの場所はどこですか": (
    "ringcentral.video.more.notes",
    False,
),
```

Expected RED before package edit: both prompts return no entrypoint or fail the expected entrypoint assertion.

3. In the same questions test, after the loop, add a focused interrupt assertion for one Japanese Notes prompt:

```python
notes_response = answer_question(
    package=package,
    question="ノートと文字起こしの場所はどこですか",
    voice=PresenterVoiceSettings(language="ja"),
)
assert notes_response.entrypoint_id == "ringcentral.video.more.notes"
assert notes_response.can_operate is False
assert create_question_interrupt_step(package, notes_response) is None
```

Expected RED before package edit: entrypoint is not Notes, so the interrupt assertion cannot pass.

4. In `tests/unit/test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage`, change:

```python
assert "questionAliases.ja present on 13/27 entrypoints (34 aliases)" in result.stdout
```

Expected RED before package edit: CLI still prints `12/27` and `32 aliases`.

5. In `tests/unit/test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package`, change:

```python
"87 package-owned aliases have no cross-entrypoint duplicates"
```

Expected RED before package edit: diagnostics still report `85`.

6. In `tests/unit/test_cli.py` doctor expectations, change the same doctor alias-count string from `85` to `87`.

Expected RED before package edit: doctor stdout still reports `85 package-owned aliases`.

## Verification commands

Focused red/green test command for the alias slice:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_ringcentral_package_owns_japanese_aliases_for_meeting_control_routes tests\unit\test_questions.py::test_ringcentral_japanese_meeting_control_questions_match_package_aliases_without_legacy_table tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package
```

Run the CLI localization report:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
```

Expected post-change lines:

```text
questionAliases.ja present on 13/27 entrypoints (34 aliases)
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Run doctor diagnostics:

```powershell
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video
```

Expected post-change lines:

```text
[OK] question aliases: 87 package-owned aliases have no cross-entrypoint duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 10 ok, 1 info, 0 warnings, 0 failed.
```

Optional broader confidence pass:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage tests\unit\test_cli.py::test_doctor_reports_profile_and_package_ok tests\unit\test_diagnostics.py
```

## Guardrails

- Do not remove or weaken `questionPolicy: answerOnly` on `ringcentral.video.more.notes`.
- Do not remove Notes `openSteps`; scripted demos still need the panel route.
- Do not add operation-like Japanese aliases such as `ノートを開始`, `文字起こしを開始`, `録画`, `要約`, `読み上げ`, or `会議後の記録`.
- Do not add broad bare aliases like `ノート`, `文字起こし`, or `Notes` in this slice.
- Do not change Q&A wording or localized narration for this alias-only slice.
- Keep Q&A-first matching behavior unchanged; the new aliases are only for direct location prompts that are not already covered by exact Q&A.
