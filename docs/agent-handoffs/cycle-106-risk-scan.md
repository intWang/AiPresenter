# Cycle 106 Risk Scan: Japanese Notes/Transcript Location Aliases

## Verdict

Go for a narrow alias-only cycle if the change is limited to Japanese location aliases for
`ringcentral.video.more.notes`.

Do not add action, content-reading, summarization, recording, caption-reading, or post-meeting artifact aliases in
the same change. Cycle 105 already made `ringcentral.video.more.notes` answer-only for question responses, so the
remaining risk is routing breadth: new aliases should help users find the Notes and Transcript panel without turning
privacy-sensitive prompts into interrupt actions.

## Evidence Baseline

Cycle 105 committed `adcc876 feat: add answer-only question policy`. The current RingCentral package marks both
`ringcentral.video.top.meeting-info` and `ringcentral.video.more.notes` with:

```yaml
questionPolicy: answerOnly
```

Current verification run for this scan:

- `ai-presenter localization-report --package ringcentral-video --language ja`: `questionAliases.ja present on 12/27 entrypoints (32 aliases)`.
- `ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`: `11 ok, 1 info, 0 warnings, 0 failed`.
- Doctor alias details: `85 package-owned aliases`, `71 Q&A question prompts`, `71 Q&A question prompts have no unsafe package-owned alias overlaps`, existing substring risk remains INFO for `11` prompts.

There is a pre-existing dirty `.coverage` file in the worktree. This scan did not modify it.

## Safe Alias Set Size

Safe set size: six Japanese aliases.

Recommended location-only aliases for `questionAliases.ja` on `ringcentral.video.more.notes`:

- `ノート`
- `文字起こし`
- `会議メモ`
- `ノートの場所`
- `文字起こしの場所`
- `ノートと文字起こしの場所`

Rationale: these are noun or location fragments. They should route to the Notes entrypoint while staying
non-operable because of `questionPolicy: answerOnly`. They avoid verbs such as start, read, summarize, record, copy,
save, enable, or translate.

Do not include the full existing Q&A localized question `ノートと文字起こしはどこにありますか` as an entrypoint alias unless
the team intentionally wants exact Q&A shadowing. Q&A-first matching should continue to own the full-sentence
explain-only response.

## Privacy And Routing Risk

- Notes and Transcript can expose meeting notes, transcript text, captions, recording affordances, and post-meeting
  artifacts. Location aliases must never imply permission to read or summarize content.
- The Notes panel has observed controls for `Start notes` and `Also record this meeting`; both can affect meeting
  state or participant privacy.
- Adding Japanese aliases broadens natural-language routing into an entrypoint with executable `openSteps`, so the
  answer-only policy is the safety boundary. Tests must prove both `can_operate is False` and no interrupt step is
  created.
- Exact Q&A prompts and localized Q&A prompts must keep priority over entrypoint aliases. This matters for captions,
  live transcription, translation, post-meeting artifacts, and explicit content-reading questions.
- The doctor alias checks are necessary but not sufficient. A clean duplicate/overlap report does not prove runtime
  non-operability.

## Negative Prompts That Must Remain Non-Operable

All prompts below must return `can_operate is False`; if an entrypoint is present,
`create_question_interrupt_step(package, response)` must return `None`.

- `Where are Notes and transcript`
- `notes`
- `meeting notes`
- `transcript`
- `Can I use live transcription?`
- `Where are captions, live transcription, and translation controls?`
- `Where can I find post-meeting recordings, transcripts, summaries, or insights?`
- `Can AiPresenter read post-meeting transcripts?`
- `Read the transcript`
- `Summarize the transcript`
- `Start notes`
- `Also record this meeting`
- `会议笔记在哪里`
- `转录在哪里`
- `读取转录内容`
- `总结会议笔记`
- `ノート`
- `文字起こし`
- `会議メモ`
- `ノートの場所`
- `文字起こしの場所`
- `ノートと文字起こしの場所`
- `ノートはどこですか`
- `文字起こしはどこですか`
- `ノートと文字起こしはどこにありますか`
- `文字起こしを読んで`
- `字幕を読んで`
- `会議メモを要約して`
- `Start notes をクリックして`
- `Also record this meeting を押して`

## Test Matrix

| Area | Prompts or fixture | Expected result |
| --- | --- | --- |
| Japanese alias routing | Six recommended aliases with `_ENTRYPOINT_ALIASES` monkeypatched to `{}` | Routes to `ringcentral.video.more.notes`, `can_operate is False`, no interrupt step |
| Full localized Q&A priority | `ノートと文字起こしはどこにありますか` | Prefer Q&A answer if it remains an exact Q&A prompt; no entrypoint interrupt |
| English baseline | `Where are Notes and transcript`, `notes` | Still routes to Notes where applicable, remains non-operable |
| Chinese baseline | `会议笔记在哪里`, `转录在哪里` | Existing Chinese Notes/Transcript prompts remain non-operable |
| Action denial | `Start notes`, `Start notes をクリックして`, `Also record this meeting を押して` | Non-operable; no queued click/open steps |
| Content privacy | `文字起こしを読んで`, `字幕を読んで`, `会議メモを要約して` | Q&A or fallback answer only; no operation |
| Adjacent Q&A | captions, live transcription, translation, post-meeting artifact prompts | Q&A-first answer remains non-operable and does not become an entrypoint alias route |
| Policy independence | Monkeypatch `_RISKY_ENTRYPOINT_WORDS` to empty | Japanese Notes aliases still non-operable through `questionPolicy` |
| Non-sensitive control guard | `network quality` | Remains operable, proving alias addition did not globally disable safe informational controls |
| Counts and diagnostics | CLI localization report and doctor | Counts change only as expected below; doctor remains no warnings/failures |

Suggested focused verification:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

## Expected Count Changes

If exactly the six recommended aliases are added:

- Japanese localization report moves from `12/27` entrypoints to `13/27` entrypoints.
- Japanese alias count moves from `32` to `38`.
- Doctor question aliases move from `85 package-owned aliases` to `91 package-owned aliases`.
- Q&A prompt count remains `71`.
- Q&A alias overlap should remain OK for `71 Q&A question prompts`.
- Doctor summary should remain `11 ok, 1 info, 0 warnings, 0 failed`.
- The existing substring-risk INFO should remain `11` if the six aliases are treated as related-entrypoint substrings or do not introduce new unsafe substrings. If it changes, treat that as a review point and document exactly which Q&A prompt gained a new substring match.

If fewer than six aliases are accepted, the expected alias deltas should reduce one-for-one. The entrypoint coverage
delta should still be `+1` as long as `ringcentral.video.more.notes` gains at least one Japanese alias.

## Residual Risks

- Japanese users may phrase action requests as location questions. Keep action verbs out of aliases and rely on
  answer-only policy plus negative tests.
- `文字起こし` can refer to live transcription, captions, or post-meeting transcripts. Q&A-first tests must keep
  caption, translation, and post-meeting artifact answers from being swallowed by a broad entrypoint alias.
- The Notes panel remains executable in scripted demos. This is acceptable for curated flows, but question interrupt
  creation must stay blocked.
- Future UI text may rename Notes and Transcript. If RingCentral changes the panel label, aliases may still route while
  `openSteps` become stale; doctor will not catch visual/UIA drift by itself.
- Adding aliases only improves routing, not permission handling. AiPresenter still must not read, copy, summarize, or
  infer note/transcript content without explicit user request and verified visible context.

## Recommendation

Proceed with the six-alias Japanese location set only. Update count assertions deliberately, run the focused question
and diagnostics matrix, and stop if any Notes/Transcript prompt becomes operable or queues an interrupt step.
