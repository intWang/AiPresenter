# Cycle 167 Risk/Test Scan: Remaining Caption And Live Transcript Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `2ce39f4`
Role: Cycle167 risk/test-scan subagent

## Scope

- Reviewed risk and test strategy for remaining exact caption, live-caption, and live-transcript text variants.
- Wrote only this handoff: `docs/agent-handoffs/cycle-167-risk-scan.md`.
- Did not edit source code, tests, package YAML, `.coverage`, staging, or commits.
- Did not run the full suite. Used read-only `git`, `rg`, and small non-pytest probes with `PYTHONDONTWRITEBYTECODE=1`.
- Initial status showed `.coverage` dirty. During the scan, `packages/ringcentral-video.yaml` and `tests/unit/test_questions.py` also became dirty with concurrent caption action prompt work. Treated those as other-agent changes.

## Current Snapshot

Committed `HEAD` at `2ce39f4` contains the Cycle166 caption readout slice under the existing Q&A item `Where are captions, live transcription, and translation controls?`:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`
- `Can you read the captions?`
- `Can you read captions?`

The current dirty tree adds six more exact prompts to the same Q&A item and mirrors them in `test_ringcentral_captions_and_translation_questions_are_answer_only`:

- `Copy captions`
- `Can you copy the captions?`
- `Export captions`
- `Save captions`
- `Download captions`
- `Download transcript text`

Read-only diagnostics probe on the dirty tree:

- Q&A question prompts: `173`
- Package-owned aliases: `157`
- Q&A duplicate prompt check: `OK | 173 Q&A question prompts have no cross-item duplicates`
- Q&A alias-overlap check: `OK | 173 Q&A question prompts have no unsafe package-owned alias overlaps`
- Q&A alias substring-risk check: `INFO | 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`

Important count risk: `tests/unit/test_diagnostics.py` and `tests/unit/test_cli.py` still assert `167` Q&A prompts. If the dirty +6 prompt work is accepted, those expectations must become `173`.

## Risk Matrix

| Risk | Likelihood | Impact | Recommended guard |
| --- | --- | --- | --- |
| Diagnostics and doctor prompt counts stay at `167` after the dirty +6 prompts land | High if current diff is staged as-is | Medium | Update both diagnostics and doctor assertions to `173`; leave package-owned aliases at `157` and substring-risk at `11` unless diagnostics detail changes. |
| Remaining singular caption wording, especially `Show caption text`, relies on fuzzy Q&A matching instead of exact authored coverage | Medium | Medium | Either add it as an exact prompt under the captions Q&A or pin it as a test-only variant that must stay answer-only and use the captions privacy answer. |
| Live-caption readout variants regress to Audio or no-match fallback after matcher changes | Medium | High | Cover `Read live caption text`, `Read the live caption text`, `Read live captions aloud`, and `Can you read the captions aloud?` with no Audio, no Meeting information, and no no-match fallback assertions. |
| Live-transcript text variants are safe today but under-pinned | Medium | High | Cover `Read the live transcript text`, `Read live transcript text`, `Show transcript text`, and `Show live transcript text` as answer-only privacy prompts. |
| Copy/export/save/download prompts imply completed actions | Medium | High | Add negative answer assertions for `copied`, `exported`, `saved`, `downloaded`, `turned on`, `started`, and readout phrases such as `The caption says`. |
| Live transcript prompts swallow post-meeting artifact questions | Low/Medium | Medium | Keep post-meeting transcript questions on the post-meeting artifacts Q&A; include negative controls for `Where can I find post-meeting transcripts?` and `Can AiPresenter read post-meeting transcripts?`. |
| Location/control prompts get over-hardened by content privacy additions | Low/Medium | Medium | Preserve `Where are Notes and transcript`, microphone, meeting information, and post-meeting artifact routing controls. |
| Broad aliases steal unrelated routes | Medium if aliases are added | High | Use exact Q&A prompts only. Do not add entrypoint `questionAliases`, related entrypoints, or runtime matcher changes for this slice. |

## Recommended Assertions

For any accepted caption/live transcript variants, assert the same answer-only privacy shape:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.video.toolbar.audio"
assert response.entrypoint_id != "ringcentral.video.more.notes"
assert response.entrypoint_id != "ringcentral.video.top.meeting-info"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

Pin the intended privacy answer:

```python
assert "Notes and Transcript" in response.answer_text
assert "Settings" in response.answer_text
assert "caption or transcript text" in response.answer_text
assert "explicitly asks" in response.answer_text
assert "verified" in response.answer_text
```

Keep fallback, wrong-route, and action-leak negatives:

```python
lowered = response.answer_text.casefold()
assert "Microphone control:" not in response.answer_text
assert "Notes and transcript:" not in response.answer_text
assert "Meeting information:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
assert "The caption says" not in response.answer_text
assert "Here are the captions" not in response.answer_text
assert "copied" not in lowered
assert "exported" not in lowered
assert "saved" not in lowered
assert "downloaded" not in lowered
assert "turned on" not in lowered
assert "started" not in lowered
```

Recommended remaining exact/test variants:

- Caption text: `Show caption text`, `Read live caption text`, `Read the live caption text`, `Show live captions`, `Read live captions aloud`, `Can you read the captions aloud?`
- Live transcript text: `Read the live transcript text`, `Read live transcript text`, `Show transcript text`, `Show live transcript text`
- Transcript actions if the dirty +6 prompt slice expands further: `Copy transcript text`, `Export transcript text`, `Save transcript text`, `Download transcript`

Current dirty-tree probes route all of those variants to the captions/transcript privacy Q&A with `entrypoint_id is None`, `can_operate is False`, and no interrupt. The residual risk is regression coverage, not current behavior.

## Positive And Negative Controls

Positive controls that should use the captions/transcript privacy answer:

- Existing committed prompts: `Read caption text`, `Show captions text`, `Show live caption text`, `Read captions aloud`, `Can you read the captions?`, `Can you read captions?`
- Dirty +6 prompts if accepted: `Copy captions`, `Can you copy the captions?`, `Export captions`, `Save captions`, `Download captions`, `Download transcript text`
- Remaining variants listed above, either as exact authored prompts or test-only probes.
- Location/action safety prompts already in the same item: `Where are captions?`, `Can I use live transcription?`, `How do I translate captions?`, `Where are translated captions?`, `Turn on captions`.

Negative controls that should not be captured by new exact prompts:

- `Where are Notes and transcript`: should route to `ringcentral.video.more.notes`, remain non-operable, and start with `Notes and transcript:`.
- `Where is the microphone button?`: should route to `ringcentral.video.toolbar.audio`, remain non-operable, and start with `Microphone control:`.
- `meeting information`: should route to `ringcentral.video.top.meeting-info`, remain non-operable, and start with `Meeting information:`.
- `Where can I find post-meeting transcripts?`: should use the post-meeting artifacts Q&A, not the live captions/transcript control Q&A.
- `Can AiPresenter read post-meeting transcripts?`: should use the post-meeting artifacts privacy Q&A, not claim access to live or saved content.

## Diagnostics Count Guidance

Use committed `HEAD` and dirty-tree state separately:

- Clean `2ce39f4` baseline: `167` Q&A question prompts, `157` package-owned aliases, `11` substring-risk prompts.
- Current dirty tree with the +6 caption action prompts: `173` Q&A question prompts, `157` package-owned aliases, `11` substring-risk prompts.

Count formula:

- If starting from clean `2ce39f4`, expected Q&A count is `167 + accepted_new_exact_prompt_count`.
- If the current dirty +6 prompt work becomes the base, expected Q&A count is `173 + accepted_remaining_exact_prompt_count`.
- Adding exact strings to an existing Q&A item changes Q&A prompt count only. It should not change package-owned alias count.
- Substring-risk count should remain `11` for caption/transcript text variants unless a new prompt contains unrelated package-owned alias text. Re-run focused diagnostics before preserving or changing it.

Files whose count assertions must move together:

- `tests/unit/test_diagnostics.py`: duplicate-prompt and alias-overlap detail strings.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`: matching doctor output strings.

Do not update counts by assumption. Recompute after the final prompt set is chosen.

## Final Verification Checklist

- Confirm every accepted variant is under the existing captions/live transcription Q&A item, not entrypoint aliases.
- Confirm no `relatedEntrypointIds`, open steps, or runtime matcher changes are added for these privacy prompts.
- Confirm caption/live transcript content and action prompts are answer-only, non-operable, and create no interrupt.
- Confirm no answer text claims to read, quote, copy, export, save, download, start, or turn on private meeting text.
- Confirm Audio, Notes location, Meeting information, and post-meeting artifact negative controls still route to their expected answers.
- Confirm diagnostics/doctor counts match the final prompt inventory: `167` for clean HEAD, `173` if the dirty +6 prompt diff is accepted, plus any additional exact variants.
- Run focused verification only, with coverage disabled and cache disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only
```

- If diagnostics or doctor strings changed, run the focused count checks only:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

- Run `git diff --check` before staging in the main implementation pass.
- Run `git status --short` and keep `.coverage` unstaged.
- Do not run the full suite for this restricted slice unless the coordinator explicitly asks for it.
