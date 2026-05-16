# Cycle 105 Risk Scan: Answer-Only Policy For Sensitive More Entrypoints

## Verdict

Go for a minimal policy-only runtime hardening cycle. Do not add Japanese Notes
or Transcript aliases in the same change.

The smallest safe candidate is to make executable but sensitive informational
entrypoints answer-only for question routing, starting with
`ringcentral.video.more.notes`. This should prevent the controller from queuing
interrupt steps for Notes/Transcript location prompts while preserving the
plain answer text and entrypoint identity.

## Current Baseline

Cycle 104 left Recording in a safe answer-only state. The next risk is Notes and
Transcript:

- `ringcentral.video.more.notes` has executable `openSteps` that open More and
  then the Notes side panel.
- The panel can expose Start notes and Also record this meeting, so opening it
  can move the meeting toward notes, transcript, or recording state.
- Current question routing can return
  `entrypoint_id == "ringcentral.video.more.notes"` with `can_operate is True`.
- `create_question_interrupt_step()` queues a demo step whenever an entrypoint
  has `can_operate is True` and `openSteps`, so the current route can become an
  interrupt action.

Observed read-only counts on the current workspace:

- Japanese localization report: `questionAliases.ja present on 12/27
  entrypoints (32 aliases)`.
- Doctor: `11 ok, 1 info, 0 warnings, 0 failed`.
- Doctor question aliases: `85 package-owned aliases have no cross-entrypoint
  duplicates`.
- Doctor Q&A alias overlap: `71 Q&A question prompts have no unsafe
  package-owned alias overlaps`.
- Doctor substring risk: INFO for the existing `11` Q&A prompts.

The existing test
`test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint`
currently asserts `can_operate is True`. That assertion should be deliberately
flipped in the red phase.

## Privacy And Safety Risks

- Opening Notes and Transcript can reveal private note, transcript, caption, or
  meeting-content surfaces. AiPresenter must not read, summarize, copy, save, or
  infer content without an explicit request and verified visible context.
- Starting notes or selecting Also record this meeting can change meeting state
  and can affect all participants. Location questions should not become
  operational permission.
- Adding Japanese aliases before the policy would broaden the set of natural
  prompts that can open the panel.
- The doctor alias checks do not prove runtime safety. They can stay clean even
  while a matched entrypoint is still executable.
- Localized copy already frames Notes/Transcript as explain-only. Runtime
  `can_operate` should match that product promise.

## Route Ambiguity Risks

- `notes`, `transcript`, `caption`, `live transcription`, and post-meeting
  artifact wording can mean either "where is the control" or "read/open the
  content." The safe default is answer-only.
- English title lookup already routes `Where are Notes and transcript` to the
  Notes entrypoint. After policy hardening it should keep the entrypoint but
  lose operability.
- Chinese package aliases such as meeting-notes wording already route to
  `ringcentral.video.more.notes`; those should also become non-operable.
- Future Japanese aliases should be treated as route expansion only after the
  policy is proven. They should not be used to implement the safety boundary.
- Q&A-first matching must continue to win for captions, transcription,
  post-meeting artifacts, and privacy-sensitive prompts. Entrypoint alias
  fallback should not shadow those answers.

## Red Tests To Write First

Write these before production code and verify that at least the Notes operability
tests fail on the current baseline.

- Flip `tests/unit/test_questions.py::test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint`:
  assert `response.entrypoint_id == "ringcentral.video.more.notes"`,
  `response.can_operate is False`, and
  `create_question_interrupt_step(package, response) is None`.
- Extend `test_notes_matches_notes_entrypoint`: for `question="notes"`, assert
  `can_operate is False` and no interrupt step is created.
- Extend
  `test_ringcentral_chinese_questions_match_package_aliases_without_legacy_table`:
  for the Chinese meeting-notes prompt, assert the Notes entrypoint remains the
  match but `can_operate is False`.
- Add a direct localized route guard with `_ENTRYPOINT_ALIASES` monkeypatched to
  `{}` for existing Chinese aliases and future Japanese-like temporary aliases:
  Notes routing may identify `ringcentral.video.more.notes`, but must not queue
  an interrupt.
- Add a policy independence test mirroring
  `test_meeting_info_privacy_gate_does_not_depend_on_risky_words`: monkeypatch
  `_RISKY_ENTRYPOINT_WORDS` to an empty set and prove Notes still returns
  `can_operate is False`.
- Add a regression test that an unrelated executable informational entrypoint
  that is not policy-listed, such as Network quality, still returns
  `can_operate is True`.
- Keep existing Recording tests green, especially Japanese recording action,
  consent, status, and artifact prompts.

## Negative Prompts

All of these must return `can_operate is False`; if an entrypoint is present,
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
- `ノートはどこですか`
- `ノートと文字起こしはどこですか`
- `文字起こしを読んで`
- `字幕を読んで`
- `会議メモを要約して`
- `Start notes をクリックして`

For policy-only Cycle 105, the Japanese prompts above can be represented in
temporary in-test package aliases or as Q&A prompts. They should not require
editing `packages/ringcentral-video.yaml`.

## Expected Counts

Policy-only Cycle 105 should not change package YAML or localization counts:

- Japanese localization report stays at `12/27` entrypoints and `32` aliases.
- Doctor question aliases stay at `85 package-owned aliases`.
- Doctor Q&A prompts stay at `71`.
- Doctor substring risk should stay INFO at `11`, unless tests add only in-memory
  fixtures.
- No production package alias count tests should be updated in this cycle.

Alias-expansion follow-up, after policy is green:

- If adding six Japanese Notes/Transcript location aliases, expect Japanese
  localization to move to `13/27` entrypoints and `38` aliases.
- Package-owned aliases would move from `85` to `91`.
- Doctor Q&A alias overlap must remain OK for `71` prompts.
- Doctor substring risk may stay INFO at `11` if only related-entrypoint
  substrings are introduced; if it changes, the implementation must explain why
  the new INFO rows are Q&A-first and non-operable.
- The follow-up must update count tests and run localization report plus doctor
  after YAML changes.

## Recommendation

Proceed with a minimal runtime answer-only policy first. Add
`ringcentral.video.more.notes` to the same explicit policy style already used
for Meeting information, or introduce an equivalently explicit sensitive
informational entrypoint set. Keep this scoped to question routing and interrupt
creation. Do not add Japanese Notes/Transcript aliases until the red tests above
are green and the unchanged policy-only counts are confirmed.

Suggested verification after implementation:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_localization_report_outputs_japanese_demo_and_qa_coverage
.\.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
```

This scan changed only this document.
