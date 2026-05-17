# Cycle 166 Risk/Test Scan: Caption Text Privacy Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `62b0f750232e1eb75bac29561a376816f1eef4a3`
Role: Cycle166 risk/test-scan subagent

## Scope

- Reviewed risk and test strategy for caption and live-caption text privacy prompt variants.
- Only wrote this handoff: `docs/agent-handoffs/cycle-166-risk-scan.md`.
- Did not edit code, tests, package YAML, `.coverage`, staging, or commits.
- Did not run the full suite. Used read-only `rg`, `git diff`, and tiny non-pytest probes with `PYTHONDONTWRITEBYTECODE=1`.
- Initial workspace status already showed `.coverage`, `packages/ringcentral-video.yaml`, and `tests/unit/test_questions.py` modified. Treated those as concurrent work and left them alone.
- Final workspace status also showed concurrent `tests/unit/test_cli.py`, `tests/unit/test_diagnostics.py`, `docs/agent-handoffs/cycle-166-demand-analysis.md`, and `docs/agent-handoffs/cycle-166-technical-scan.md` changes. This scan did not write or edit those files.

## Current Worktree Snapshot

Current concurrent caption diff adds these English prompts under the existing Q&A item `Where are captions, live transcription, and translation controls?`:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`

`tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only` mirrors those four prompts and now asserts answer-only behavior plus no Audio, Meeting information, or no-match fallback text.

Read-only diagnostics probe on the current worktree reported:

- Q&A question prompts: `165`
- Package-owned aliases: `157`
- Q&A duplicate prompt check: `OK | 165 Q&A question prompts have no cross-item duplicates`
- Q&A alias-overlap check: `OK | 165 Q&A question prompts have no unsafe package-owned alias overlaps`
- Q&A alias substring-risk check: `INFO | 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`

Early in this scan, the count-bearing diagnostics and doctor assertions still expected `161` Q&A prompts. A final read-only check showed another worker had updated those strings to `165`. Keep them at `165` if the current four caption prompts remain; recompute if the prompt set changes.

## Risk Matrix

| Risk | Likelihood | Impact | Recommended guard |
| --- | --- | --- | --- |
| Diagnostics and doctor count strings drift from the final prompt count | Medium in shared worktree | Medium | For the current four-prompt diff, both diagnostics strings and both CLI doctor strings should be `165`; do not change package-owned alias count `157` or substring-risk count `11` unless diagnostics detail changes. |
| `Show live caption text` regresses to Audio fallback | Medium without exact assertion | High | Assert `entrypoint_id is None`, `entrypoint_id != "ringcentral.video.toolbar.audio"`, and `Microphone control:` absent. |
| Caption read/show prompts regress to no-match fallback | Medium | Medium | Assert `I could not find a matching control` absent and answer includes the captions/transcript privacy boundary. |
| `Read captions aloud` is treated as narration permission instead of private content | Medium | High | Keep it in the same privacy Q&A and assert no interrupt, no operation, and answer says not to read caption or transcript text unless explicitly asked and visible context is verified. |
| Location/discovery prompts become over-hardened or misrouted | Low/Medium | Medium | Preserve `Where are captions?`, `Can I use live transcription?`, `How do I translate captions?`, and `Turn on captions` on the existing answer-only captions Q&A. |
| Notes/transcript location lookups are accidentally swallowed by content-read privacy prompts | Low | Medium | Keep `Where are Notes and transcript` routed to `ringcentral.video.more.notes` with no interrupt. |
| Broad aliases such as `caption`, `text`, `read`, `show`, or `live` steal unrelated routes | Medium if aliases are added | High | Use exact Q&A prompts only. Do not add entrypoint `questionAliases` or runtime matcher changes for this slice. |
| Tests prove routing but miss content leakage | Medium | High | Add negative answer assertions for sample readout/action language such as `The caption says`, `Here are the captions`, `copied`, `exported`, and `turned on`. |
| Localized caption-content asks rely on matcher safety instead of exact prompt coverage | Low for English-only slice, Medium for multilingual follow-up | Medium | If localized prompt variants are added, keep them under the same existing Q&A item and verify item-based localization counts remain stable. |

## Recommended Assertions

Primary privacy prompts to keep covered:

```python
@pytest.mark.parametrize(
    "question",
    [
        "Read caption text",
        "Show captions text",
        "Show live caption text",
        "Read captions aloud",
    ],
)
```

Core answer-only assertions:

```python
assert response.entrypoint_id is None
assert response.entrypoint_id != "ringcentral.video.toolbar.audio"
assert response.entrypoint_id != "ringcentral.video.more.notes"
assert response.entrypoint_id != "ringcentral.video.top.meeting-info"
assert response.can_operate is False
assert create_question_interrupt_step(package, response) is None
```

Positive answer-boundary assertions:

```python
assert "Notes and Transcript" in response.answer_text
assert "Settings" in response.answer_text
assert "read caption or transcript text" in response.answer_text
assert "explicitly asks" in response.answer_text
assert "verified" in response.answer_text
```

Negative fallback and leak assertions:

```python
assert "Microphone control:" not in response.answer_text
assert "Notes and transcript:" not in response.answer_text
assert "Meeting information:" not in response.answer_text
assert "I could not find a matching control" not in response.answer_text
assert "The caption says" not in response.answer_text
assert "Here are the captions" not in response.answer_text
assert "copied" not in response.answer_text.casefold()
assert "exported" not in response.answer_text.casefold()
assert "turned on" not in response.answer_text.casefold()
```

Optional variant probes if the implementation owner wants broader confidence without adding more package prompts:

- `Read live caption text`
- `Read the live caption text`
- `Show live captions`
- `Read live captions aloud`
- `Can you read the captions aloud?`
- `Read the live transcript text`
- `Show transcript text`

The current worktree routes each of those optional probes to the same answer-only captions/transcript privacy Q&A, but they are not all pinned by exact test parameters.

## Positive And Negative Controls

Positive controls for the caption privacy answer:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`
- `Where are captions?`
- `Can I use live transcription?`
- `How do I translate captions?`
- `Turn on captions`

Expected result: `entrypoint_id is None`, `can_operate is False`, no interrupt, answer includes `Notes and Transcript`, `read caption or transcript text`, `explicitly asks`, and `verified`.

Negative controls that should not be captured by the new caption prompts:

- `Where are Notes and transcript`: should route to `ringcentral.video.more.notes`, stay non-operable, and start with `Notes and transcript:`.
- `Where is the microphone button?`: should route to `ringcentral.video.toolbar.audio`, stay non-operable, and start with `Microphone control:`.
- `Can you share system audio?`: should stay on screen-share privacy guidance, not captions.
- `meeting information`: should stay on `ringcentral.video.top.meeting-info`, not captions.

These controls protect the matcher boundary: content-read caption requests get privacy guidance, while nearby control/location questions still reach their intended entrypoint guidance.

## Diagnostics Count Guidance

Current committed baseline at `62b0f75` has the participant-role work already integrated and expects:

- Q&A prompt count: `161`
- Q&A alias-overlap prompt count: `161`
- Package-owned alias count: `157`
- Q&A alias substring-risk count: `11`

Count formula for this slice:

- Adding `N` exact English prompts to the existing captions Q&A changes both Q&A prompt-count expectations from `161` to `161 + N`.
- The current worktree adds four prompts, so expected count is `165`.
- If `Read captions aloud` is removed and only the three Cycle165-recommended prompts remain, expected count is `164`.
- If an additional exact transcript-text prompt is added on top of the current four, expected count is `166`.

What should not change for the current data-only slice:

- Package-owned alias count should remain `157` because no entrypoint aliases were added.
- Q&A alias substring-risk count should remain `11` based on the read-only diagnostics probe. Re-run focused diagnostics before updating this number.
- Q&A localization item totals should remain item-based. Adding English prompt variants to an existing localized Q&A item should not create a new top-level localization item.

Files that should carry `165` if the four-prompt caption diff stays:

- `tests/unit/test_diagnostics.py`: both `Q&A question prompts...` strings.
- `tests/unit/test_cli.py::test_doctor_loads_profile_package_and_flow`: both doctor output strings.

Final read-only check showed another worker had already changed these four strings to `165`. Leave that work intact unless the package prompt delta changes.

Avoid count changes driven by assumption. Update exact strings only after the package prompt delta is final.

## Final Verification Checklist

- Confirm the caption prompts are under the existing captions/live transcription Q&A item, not entrypoint `questionAliases`.
- Confirm no `relatedEntrypointIds` were added to the captions privacy Q&A for these content-read prompts.
- Confirm no runtime matcher code changed for this narrow slice.
- Confirm `Read caption text`, `Show captions text`, `Show live caption text`, and `Read captions aloud` are answer-only, non-operable, and produce no interrupt.
- Confirm no Audio, Notes location, Meeting information, or no-match fallback text appears for caption content-read prompts.
- Confirm nearby negative controls still route to Audio, Notes/transcript, Share, and Meeting information as appropriate.
- Update diagnostics/CLI counts to `165` if the current four prompts remain.
- Run focused verification only, with coverage disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only
```

- If count strings changed, run the focused diagnostics/doctor checks only:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

- Run `git diff --check` before handoff or staging.
- Run `git status --short` and confirm `.coverage` remains unstaged and untouched by the implementation pass.
- Do not run the full suite for this restricted caption prompt slice unless the coordinator explicitly asks for it.

## Coordinator Update After Review

The final Cycle166 slice added two more exact caption readout prompts after
test review:

- `Can you read the captions?`
- `Can you read captions?`

The final Q&A prompt count is `167`. Package-owned alias count remains `157`,
and substring-risk count remains `11` unless a later diagnostics run reports
otherwise.
