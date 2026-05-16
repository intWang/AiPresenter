# Cycle 107 Review: Notes/Transcript Safety Matcher

## Findings

### Blocking: English unsafe Notes/Transcript prompts still misroute to unrelated or generic entrypoints

The new guard in `src/ai_presenter/runtime/questions.py:67` and `src/ai_presenter/runtime/questions.py:76` only recognizes Notes/Transcript subjects when paired with Japanese action/content terms. That handles the focused Japanese fixtures, but it leaves several examples called out in the Cycle 107 demand and technical handoffs uncovered.

Fresh runtime probes showed:

```text
Start notes
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False
  answer starts with "Start meeting: Start an instant RingCentral Video meeting."

Click Start notes
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False
  answer starts with "Start meeting: Start an instant RingCentral Video meeting."

Summarize the transcript
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
  answer starts with "Notes and transcript: Open the Notes and Transcript side panel."
```

This preserves the mandatory execution safety contract, but it does not satisfy the documented semantic safety goal: unsafe Notes/Transcript action/content prompts should prefer the safety Q&A or no-match, not a Start meeting or generic Notes panel answer. If Cycle 107 is intentionally Japanese-only, this should be explicitly documented as deferred scope; otherwise this is blocking undercoverage.

## Validation Evidence

Focused Cycle 107 tests pass:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_start_meeting_questions_still_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_notes_location_routes_still_match_notes
```

Observed result:

```text
10 passed in 1.91s
```

Focused adjacent regressions pass:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_japanese_recording_location_aliases_are_answer_only tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_localized_caption_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_notes_location_fragment_question_still_routes_to_entrypoint tests\unit\test_questions.py::test_notes_matches_notes_entrypoint tests\unit\test_questions.py::test_start_meeting_answer_is_not_operable
```

Observed result:

```text
12 passed in 2.28s
```

Manual probes for the required Japanese/current-scope behavior:

```text
Start notes をクリックして
  entrypoint=None
  can_operate=False
  interrupt=False
  safety Q&A returned

Transcript を要約して
  entrypoint=None
  can_operate=False
  interrupt=False
  safety Q&A returned

Start meeting をクリックして
  entrypoint=ringcentral.develop.video.start
  can_operate=False
  interrupt=False

Notes and Transcript の場所はどこですか
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False

ノートと文字起こしの場所はどこですか
  entrypoint=ringcentral.video.more.notes
  can_operate=False
  interrupt=False
```

Package YAML did not change. `git diff -- packages/ringcentral-video.yaml` was empty.

Japanese localization counts stayed stable:

```text
questionAliases.ja present on 13/27 entrypoints (34 aliases)
Localization report: 51/51 demo steps, 12/12 Q&A questions, 12/12 Q&A answers localized for ja.
```

Doctor diagnostics stayed stable:

```text
[OK] question aliases: 87 package-owned aliases have no cross-entrypoint duplicates
[OK] qa questions: 71 Q&A question prompts have no cross-item duplicates
[OK] qa alias overlap: 71 Q&A question prompts have no unsafe package-owned alias overlaps
[INFO] qa alias substring risk: 11 Q&A question prompts contain package-owned alias substrings outside related entrypoints
Doctor completed: 10 ok, 1 info, 0 warnings, 0 failed.
```

## Residual Risk

The Japanese guard returns the captions/live-transcription/translation Q&A by exact normalized question lookup. If that package Q&A text changes or is removed later, these unsafe prompts silently fall back to the old broad entrypoint matcher.

The focused tests cover the intended Japanese prompts, Start meeting, and Cycle 106 Notes location routes. They do not cover English unsafe action/content prompts, Chinese content prompts, or location wording such as `Start notes の場所はどこですか`, which can still be semantically noisy even though `can_operate=False` prevents interrupts.

`.coverage` was already dirty in the worktree and remained dirty after test execution. No production files or tests were edited during this review.

## Re-review

Previous blocking finding status: closed. The current diff adds English red coverage for `Start notes`, `Click Start notes`, and `Summarize the transcript`, and expands the Notes/Transcript safety matcher with English subject plus action/content terms. Runtime probes now route those former misses to the captions/live-transcription/translation safety Q&A with `entrypoint_id=None`, `can_operate=False`, and no interrupt step.

Focused tests run:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_english_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_japanese_notes_action_requests_do_not_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_start_meeting_questions_still_match_start_meeting tests\unit\test_questions.py::test_ringcentral_japanese_notes_location_routes_still_match_notes tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_post_meeting_artifact_questions_are_answer_only tests\unit\test_questions.py::test_notes_matches_notes_entrypoint
```

Observed result:

```text
24 passed in 6.13s
```

Manual overmatching probes showed exact and established location/post-meeting routes still behave as expected:

```text
Where are notes and transcript controls?
  entrypoint=ringcentral.video.more.notes
  interrupt=False

Where are Notes and transcript
  entrypoint=ringcentral.video.more.notes
  interrupt=False

Can AiPresenter read post-meeting transcripts?
  entrypoint=None
  post-meeting artifact Q&A returned

Where can I find post-meeting recordings, transcripts, summaries, or insights?
  entrypoint=None
  post-meeting artifact Q&A returned

start meeting
  entrypoint=ringcentral.develop.video.start
  interrupt=False
```

Residual overmatching risk: because `show` is in the action/content term list, location-like prompts such as `Show me where Notes and Transcript is` now return the conservative safety Q&A instead of the Notes entrypoint answer. That does not create an unsafe operation or interrupt path, and I do not consider it blocking for this cycle, but it is the main semantic broadness to watch if the product wants `show me where...` phrasing to remain a location lookup.

Blocking findings on re-review: none.

## Main Session Follow-up

The non-blocking `show me where...` overmatch was addressed before commit:

- Added `test_ringcentral_show_me_where_notes_remains_location_lookup`.
- Added a location-intent exclusion to the Notes/Transcript safety matcher for `where`, `location`, Japanese where/place, and entrance wording.
- Verified `Show me where Notes and Transcript is` now resolves to `ringcentral.video.more.notes`, stays `can_operate=False`, and creates no interrupt.
- Verified transcript content requests still return the safety answer and Cycle 106 Japanese Notes location routes still resolve to Notes.

Focused follow-up command:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_show_me_where_notes_remains_location_lookup tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_japanese_notes_location_routes_still_match_notes
```

Observed result:

```text
5 passed
```
