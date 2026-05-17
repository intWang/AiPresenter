# Cycle 161 Test Review: Invite And Meeting ID Privacy Q&A

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Findings

No blocking issue found for the dirty diff's implemented prompt set.

- Invite prompts route to toolbar invite privacy Q&A. `Read the invite link`, `Invite John`, `Send the invite`, and `Who can I invite?` resolve to `ringcentral.video.toolbar.invite`, return the authored invite privacy answer, keep `can_operate=False`, and produce no question interrupt.
- Meeting link/ID prompts route to meeting-info privacy Q&A for the prompts covered by the diff. `Copy meeting link` and `Can you read the meeting ID?` resolve to `ringcentral.video.top.meeting-info`, return the authored meeting ID/link privacy answer, keep `can_operate=False`, and produce no question interrupt.
- Thin entrypoint answer labels are explicitly guarded against. The new tests reject `Invite participants:` for invite privacy prompts and `Meeting information:` for meeting ID/link privacy prompts.
- Diagnostics and localization expectations were updated consistently with the new Q&A inventory: localized Q&A totals move from `14/14` to `15/15` for zh/ja/es, and duplicate/alias-overlap diagnostic prompt counts move from `124` to `134`.
- `.coverage` is dirty as a deleted file in the working tree and must not be staged with this package/test change.

Residual risk: the broader Cycle 161 demand handoff also listed `Can you copy the meeting link?`. That exact prompt is not covered by the current dirty diff and still falls back to thin `Meeting information:` text in a direct probe. If the main agent intends to satisfy the full seven-prompt demand, add that exact English Q&A prompt and focused assertion before commit. If Cycle 161 is intentionally narrowed to the six prompts now in tests, record that scope decision in the commit or handoff.

## Reviewed Diff

- `packages/ringcentral-video.yaml`
  - Adds exact English invite prompts under `How can I bring people into the meeting?`.
  - Strengthens the invite answer to block reading private invite links, names, emails, suggestions, and sending invites unless explicitly requested with visible content verified.
  - Adds a new meeting ID/link privacy Q&A item related to `ringcentral.video.top.meeting-info`.
- `tests/unit/test_questions.py`
  - Adds invite privacy Q&A-first coverage with `can_operate is False` and no interrupt.
  - Adds meeting ID/link privacy Q&A-first coverage with `can_operate is False` and no interrupt.
  - Checks that fallback entrypoint labels are absent from these answers.
- `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, `tests/unit/test_material_packages.py`
  - Updates count assertions for the new package Q&A item and prompt inventory.

## Verification

Focused no-coverage pytest command:

```powershell
.\.venv\Scripts\python.exe -m pytest --no-cov tests/unit/test_questions.py::test_ringcentral_english_invite_privacy_questions_stay_qa_first tests/unit/test_questions.py::test_ringcentral_english_meeting_info_privacy_questions_stay_qa_first tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_chinese_coverage tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_japanese_demo_and_qa_coverage tests/unit/test_material_packages.py::test_ringcentral_localization_status_reports_complete_spanish_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests/unit/test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package
```

Result: `11 passed`.

Direct probe notes:

- `Can you copy the meeting link?` still returns thin `Meeting information:` text, with `entrypoint_id=ringcentral.video.top.meeting-info`, `can_operate=False`, and no interrupt.
- Location-style probes such as `where is the meeting ID` and generic `invite people` remain non-operable and no-interrupt; they still use entrypoint fallback text unless they match authored Q&A.

## Residual Risks

- No live RingCentral Video validation was performed. This review only verifies package/runtime routing and unit-test expectations.
- The new meeting-info Q&A protects exact meeting IDs and links, but only for the exact English prompts added to the package.
- The route remains answer-only and non-interrupting because current runtime gates treat `questionPolicy: answerOnly`, missing/unsafe operations, and `can_operate=False` correctly. Future runtime matcher changes should rerun these tests.
- Keep `.coverage` out of the commit. Current status shows `.coverage` deleted before this review doc was written.

## Commit Guidance

Main agent owns commit handling. This review did not run `git add`, `git commit`, or `git reset`, and did not edit source/tests.
