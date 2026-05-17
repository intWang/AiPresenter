# Cycle 166 Test Review: Caption Text Privacy Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Role: Cycle166 test-review subagent

## Findings

### [P2] `Can you read the captions?` still routes to meeting-info privacy

The current package/test diff lands the four-prompt slice in
`packages/ringcentral-video.yaml:1916` through `packages/ringcentral-video.yaml:1919`,
and the focused tests cover those four prompts. That slice is internally
consistent at the expected `165` Q&A count.

The handoff set is broader than the landed diff, though. Demand analysis names a
final six-prompt set and calls `Can you read the captions?` the highest-value
addition because it routes to meeting-info privacy instead of the
captions/transcript boundary (`docs/agent-handoffs/cycle-166-demand-analysis.md:37`,
`docs/agent-handoffs/cycle-166-demand-analysis.md:44`,
`docs/agent-handoffs/cycle-166-demand-analysis.md:53`). The new experience note
also classifies `Can you read the captions?` as a caption text readout prompt
and leaves it as the first future backlog item if this four-prompt slice lands
unchanged (`docs/agent-handoffs/cycle-166-experience.md:17`,
`docs/agent-handoffs/cycle-166-experience.md:22`,
`docs/agent-handoffs/cycle-166-experience.md:45`).

Current probe:

```text
'Can you read the captions?' -> entrypoint='ringcentral.video.top.meeting-info' can_operate=False interrupt=False answer='Meeting IDs and links are private meeting details...'
'Can you read captions?' -> entrypoint='ringcentral.video.top.meeting-info' can_operate=False interrupt=False answer='Meeting IDs and links are private meeting details...'
```

This does not create an interrupt, but it is still the wrong privacy answer for
a caption readout request. If Cycle166 acceptance is the four-prompt technical
slice, document this as a deliberate follow-up. If acceptance follows demand
analysis, add `Can you read the captions?` and likely `Show caption text` under
the same existing captions Q&A, then recompute counts from `165` to the actual
new total.

### [P3] Current caption test does not pin content-leak negatives

`tests/unit/test_questions.py:1087` through `tests/unit/test_questions.py:1114`
asserts the landed prompts are answer-only, non-operable, produce no interrupt,
include `Notes and Transcript`, `Settings`, `explicitly asks`, `verified`, and
`caption or transcript text`, and avoid the observed Audio, Meeting information,
and no-match fallback text. That covers the primary regression.

The residual gap is content-leak wording. The risk scan recommends negative
assertions such as `The caption says`, `Here are the captions`, `copied`,
`exported`, and `turned on` (`docs/agent-handoffs/cycle-166-risk-scan.md:49`,
`docs/agent-handoffs/cycle-166-risk-scan.md:93` through
`docs/agent-handoffs/cycle-166-risk-scan.md:100`). The current answer passes
those negatives, but the test would not fail if future answer copy started
claiming a readout, copy/export, or start action while still preserving the
existing positive boundary tokens.

## Review Notes

- Package edit: four exact English prompts were added under the existing
  captions/live transcription Q&A, not entrypoint aliases.
- Question test: the four landed prompts are mirrored in
  `test_ringcentral_captions_and_translation_questions_are_answer_only`.
- Answer-only checks are present: `entrypoint_id is None`, `can_operate is
  False`, and `create_question_interrupt_step(package, response) is None`.
- Fallback checks are present for the four landed prompts:
  `Microphone control:`, `Meeting information:`, and
  `I could not find a matching control`.
- Caption/transcript privacy copy is pinned with `Notes and Transcript`,
  `Settings`, `explicitly asks`, `verified`, and
  `caption or transcript text`.
- Diagnostics/doctor counts moved from `161` to `165` in both
  `tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py`, matching the
  four added Q&A prompts.
- Package-owned alias count remains `157`; substring-risk count remains `11`.
- Handoff docs are understandable but split scope: technical/risk scans verify
  the four-prompt `165` slice, the technical-development handoff reports the
  same implementation scope, and demand/experience docs preserve the
  six-prompt/follow-up framing.

## Focused Verification Run

Command run with pytest addopts and cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

Result:

```text
13 passed in 3.32s
```

`git diff --check` over the current package/test/handoff files reported only
existing line-ending warnings. I did not run the full suite, edit code/tests,
stage, commit, or intentionally touch `.coverage`. The worktree already had
`.coverage` dirty before this review, and it remains dirty.

## Coordinator Resolution

- Accepted the P2 finding for `Can you read the captions?` and
  `Can you read captions?`; both prompts were added to the existing captions
  Q&A and mirrored in the caption privacy test.
- Accepted the P3 leak/action guard recommendation; the caption privacy test now
  rejects invented caption readouts and success/action words such as `copied`,
  `exported`, and `turned on`.
- Final Cycle166 Q&A prompt count is `167`, not the earlier four-prompt `165`
  intermediate state.
- `Show caption text` remains a future exact-variant candidate if user language
  suggests the singular form is common enough to pin separately.
