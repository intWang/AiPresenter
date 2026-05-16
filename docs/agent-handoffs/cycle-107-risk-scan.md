# Cycle 107 Risk Scan: Notes/Transcript Action And Content Prompt Hardening

## Verdict

Go for targeted hardening tests and diagnostics around Notes/Transcript action and content prompts.

No-go for runtime behavior changes until the team decides whether entrypoint association on content prompts is unacceptable. The current safety boundary is holding: associated Notes/Transcript prompts remain `can_operate=False` and do not create question interrupt steps. The remaining risk is semantic confusion and future regression, not an observed unsafe click.

## Context

Cycle 106 committed `146c51a feat: add japanese notes location aliases`, adding two Japanese location-only aliases to `ringcentral.video.more.notes`. The entrypoint remains:

- `questionPolicy: answerOnly`
- executable demo `openSteps` through More -> Notes
- `cleanup: sidePanel`
- presenter notes that `Start notes` and `Also record this meeting` are state-changing and should remain user-controlled

The question path tries Q&A first, then package-owned aliases, then broader entrypoint title/token matching. That means action/content prompts can still associate with a Notes/Transcript entrypoint through alias, title, or token matches even when they should not be operable. This distinction should be explicit in the next hardening slice.

## Negative Prompt Matrix

| Prompt class | Example prompts | Expected association | Required safety result |
| --- | --- | --- | --- |
| Location lookup | `Where are Notes and transcript`; `Notes and Transcript no basho wa doko desu ka`; `Noto to moji okoshi no basho wa doko desu ka` | May associate with `ringcentral.video.more.notes` | `can_operate=False`; no interrupt step |
| Bare entrypoint terms | `notes`; `transcript`; `meeting notes` | May associate with `ringcentral.video.more.notes` | `can_operate=False`; no interrupt step |
| Explicit content read | `Read the transcript`; `Tell me what is in the transcript`; `Moji okoshi o yonde`; `Duqu zhuanlu neirong` | Ideally answer-only or no-match; current English/Chinese may associate with Notes | `can_operate=False`; no interrupt step; do not read visible/private content |
| Explicit content summary | `Summarize the transcript`; `What did the notes say?`; `Kaigi memo o yoyaku shite` | Ideally answer-only or no-match; current English may associate with Notes | `can_operate=False`; no interrupt step; do not summarize unverified content |
| State-changing Notes action | `Start notes`; `Start notes o click shite`; `Also record this meeting` | Must not operate Notes; `Start notes` currently associates with the generic develop start entrypoint, not Notes | `can_operate=False`; no interrupt step |
| Recording adjacency | `Also record this meeting`; `record with notes`; `start recording from notes` | Prefer recording safety Q&A or no-match | `can_operate=False`; no interrupt step; require explicit confirmation and consent before any real recording path |
| Captions/live transcription adjacency | `Where are captions?`; `Can I use live transcription?`; `Where are captions, live transcription, and translation controls?` | Prefer relevant Q&A or no-match, not Notes aliases | `can_operate=False`; no interrupt step |
| Post-meeting artifacts | `Where can I find post-meeting recordings, transcripts, summaries, or insights?`; `Can AiPresenter read post-meeting transcripts?` | Prefer Q&A or no-match | `can_operate=False`; no interrupt step |
| Safe unrelated control | `network quality` | Must still associate with `ringcentral.video.top.network-quality` | `can_operate=True`; interrupt step is allowed |

For concrete Japanese/Chinese fixtures, keep the actual Unicode literals in tests. This doc uses romanized labels in places to avoid handoff encoding ambiguity.

## Guardrails To Preserve Legitimate Operations

- Keep `ringcentral.video.more.notes.questionPolicy` as `answerOnly`.
- Keep Notes demo `openSteps`; curated demos still need to open and explain the panel.
- Do not globally block all entrypoint associations for content-like words, because safe informational controls such as Network quality must remain operable.
- Preserve Q&A-first matching. Exact Q&A prompts for captions, live transcription, translation, post-meeting recordings, transcripts, summaries, or insights should not be swallowed by Notes aliases.
- Preserve package-owned Japanese location aliases from Cycle 106 exactly unless a separate localization cycle changes them.
- Do not add broad Notes/Transcript aliases such as bare Japanese `notes`, bare Japanese `transcript`, read, summarize, record, copy, save, export, enable, start, or artifact wording.
- Treat `can_operate=False` plus `create_question_interrupt_step(...) is None` as the mandatory safety contract for Notes/Transcript question responses.
- If hardening changes scoring or association, add a safe-control sentinel such as `network quality` so the question path does not become over-restrictive.

## Diagnostics And Count Expectations

Current baseline from this scan:

- Commit context: `146c51a feat: add japanese notes location aliases`
- Japanese localization report: `questionAliases.ja present on 13/27 entrypoints (34 aliases)`
- Localization coverage: `51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja`
- Doctor question aliases: `87 package-owned aliases have no cross-entrypoint duplicates`
- Q&A prompt count: `71 Q&A question prompts`
- Q&A alias overlap: `71 Q&A question prompts have no unsafe package-owned alias overlaps`
- Q&A alias substring risk: `11 Q&A question prompts contain package-owned alias substrings outside related entrypoints`
- Doctor summary: `11 ok, 1 info, 0 warnings, 0 failed`

If the next cycle only adds tests, these counts should not change. Any change to alias counts, Q&A counts, substring INFO count, doctor warning/failure totals, flow coverage, or localized coverage is out of scope unless deliberately explained in that cycle's handoff.

Fresh probe observations for this scan:

- `Read the transcript`, `Summarize the transcript`, `What did the notes say?`, and `Tell me what is in the transcript` associated with `ringcentral.video.more.notes`, but all remained `can_operate=False` with no interrupt.
- `Start notes` and `Start notes o click shite` associated with `ringcentral.develop.video.start`, not Notes, and remained non-operable with no interrupt.
- `Also record this meeting` did not associate with an entrypoint and remained non-operable.
- Japanese Notes location prompts associated with `ringcentral.video.more.notes` and remained non-operable with no interrupt.
- Japanese read/summarize/captions/post-meeting probes did not associate with an entrypoint and remained non-operable.
- Chinese Notes/Transcript probes associated with `ringcentral.video.more.notes` and remained non-operable with no interrupt.
- `network quality` remained operable and created an interrupt step, which is the desired safe-control sentinel.

Verification run during this scan:

```powershell
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package
```

Observed test result: `127 passed in 21.57s`.

## Residual Risks

- Content prompts can still receive a Notes entrypoint id in English and Chinese. This is safe today because answer-only blocks operation, but downstream analytics or UI that treats any entrypoint association as intent could mislabel the request.
- `Start notes` currently associates with a generic develop start entrypoint. It remains non-operable, but the association is semantically noisy and deserves a regression fixture if the generic package remains installed in the same material package.
- Future aliases that include action verbs or content nouns could increase substring-risk diagnostics or make Q&A shadowing harder to reason about.
- The doctor alias checks do not prove UI privacy behavior. They prove duplicate/overlap properties; runtime negative prompts still need explicit `can_operate` and interrupt assertions.
- Scripted demos can still open the Notes panel by design. A visible panel could contain private meeting notes or transcript text; narration must continue to avoid reading or summarizing content without explicit request and verified visible context.
- RingCentral UI copy may rename Notes and Transcript or move the controls. Alias routing could remain valid while `openSteps` drift, so manual/UIA validation remains a separate acceptance concern.

## Recommendation

Proceed with a test-only or diagnostics-only hardening cycle that locks the negative matrix above. Do not change runtime matching unless the product decision is to suppress Notes entrypoint association for content prompts, and if that decision is made, preserve location lookups and safe unrelated controls with explicit regression tests.
