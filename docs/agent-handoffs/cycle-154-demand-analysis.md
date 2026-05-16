# Cycle 154 Demand Analysis: Notes and Transcript Action Phrasings

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next RingCentral Video knowledge-pack increment an
English answer-only Q&A prompt slice for common Notes, Transcript, and captions
action wording.

Add exact English prompts to the existing Q&A item:
`Where are captions, live transcription, and translation controls?`

Recommended prompts:

- `Start meeting notes`
- `Summarize meeting notes`
- `Turn on captions`

Do not add entrypoint aliases for this slice. Do not change runtime matching.
These prompts should route to the existing safety answer that explains Notes
and Transcript as the discovery surface while warning not to start notes,
transcription, captions, translation, or read transcript content unless the user
explicitly asks and visible context is verified.

This is smaller and safer than expanding participants, recording, invite/share,
or network routing in the same cycle. It is also directly user-valuable because
one common operator phrase currently looks like a meeting-start request instead
of a notes request.

## User Value

Operators ask short, task-like questions while presenting a live RingCentral
Video room. The most useful next improvement is to keep sensitive notes and
transcript requests from falling into either a generic location answer or the
wrong meeting-start surface.

Observed current behavior from a local routing probe:

- `start meeting notes` routes to `ringcentral.develop.video.start`.
- `summarize meeting notes` routes to `ringcentral.video.more.notes`.
- `turn on captions` returns no match.

All three are better handled as answer-only safety guidance. The user-visible
value is clearer boundaries: AiPresenter can explain where these controls live,
but it does not imply it started notes, enabled captions, read transcript text,
or summarized meeting content.

## Operator Phrasing Scan

Meeting info is already strong enough for the next cycle to skip. Common
phrases such as `show meeting details`, `where is the meeting ID`, `copy meeting
link`, `read the meeting link`, and `what is the meeting id` route to
`ringcentral.video.top.meeting-info`, which is already `answerOnly`.

Participants has useful future demand, especially `who is in the meeting` and
`how many people are here`, but that needs a policy choice between opening the
Participants panel for a visible count and staying answer-only to avoid names
and roles. Defer it rather than slipping privacy semantics into an alias.

Invite and share are mostly covered. `invite someone`, `send the invite`,
`share my screen`, and `present my screen` route to the expected surfaces.
`share system audio` tends toward the audio menu today; that is a reasonable
future alias-only candidate for Share, but it is lower risk than notes and
transcript action wording.

Recording has useful follow-up demand. `record this meeting` currently has no
match, while `start recording`, `are we recording`, and `recording status` stay
non-operable but can return thin entrypoint text. A future answer-only recording
Q&A prompt slice would be useful, but the current wrong-route risk is sharper
for `start meeting notes`.

Notes and transcripts are the recommended slice. Existing safety handling
covers `Start notes`, `Click Start notes`, `Read the transcript`, and localized
Chinese/Japanese variants, but ordinary English meeting-notes wording still has
gaps. Exact Q&A prompts fix the gap without broad aliases.

Network quality is also mostly covered. `network quality`, `call quality`,
`audio is choppy`, and `check packet loss` route well. `video is lagging` and
`connection is unstable` are good future network-quality aliases, but Network
quality is intentionally operable, so it is not the best answer-only follow-up.

## Recommended Minimum Scope

Implement a package/test-only slice:

- Modify `packages/ringcentral-video.yaml`.
- Under the Q&A item `Where are captions, live transcription, and translation
  controls?`, add the three exact English `localizedQuestions.en` prompts
  listed in this handoff.
- Modify `tests/unit/test_questions.py` to prove those prompts are answer-only
  and do not queue an interrupt step.
- Update diagnostic or CLI count assertions only if the package prompt count
  changes as expected. With exactly three new Q&A prompts, the current
  `84 Q&A question prompts` assertions are expected to become `87 Q&A question
  prompts`.

No source change should be necessary. No package-owned entrypoint alias should
be added.

## Do Not Touch

- Do not edit `.coverage`.
- Do not revert or clean up other workers' changes.
- Do not edit runtime source for this slice.
- Do not edit profiles, README, existing handoff docs, acceptance evidence, or
  provider configuration.
- Do not add broad aliases such as `notes`, `meeting notes`, `transcript`, or
  `captions`.
- Do not add aliases to `ringcentral.video.more.notes` for action requests.
- Do not make Notes, Transcript, captions, translation, or recording operable
  from questions.
- Do not combine this with participants, invite/share, recording, or network
  alias expansion.
- Do not change localized Chinese, Japanese, or Spanish Q&A unless a failing
  test proves the English prompt addition requires a count-only update.
- Do not claim live RingCentral Video acceptance or transcript-reading
  capability.

## Acceptance Criteria

The implementation is complete when these repo-local contracts hold:

- `start meeting notes` matches the captions/live transcription safety Q&A.
- `start meeting notes` does not route to `ringcentral.develop.video.start`.
- `summarize meeting notes` matches the same answer-only safety Q&A.
- `summarize meeting notes` does not route to `ringcentral.video.more.notes`.
- `turn on captions` matches the same answer-only safety Q&A instead of no
  match.
- For all three prompts, `entrypoint_id is None`, `can_operate is False`, and
  `create_question_interrupt_step(package, response) is None`.
- The answer text still mentions `Notes and Transcript`, warns against starting
  notes, transcription, captions, or translation, and keeps the explicit-request
  plus verified-context boundary.
- Existing location prompts still work: `where is the transcript` and `Show me
  where Notes and Transcript is` continue to route to
  `ringcentral.video.more.notes` with `can_operate is False`.
- Diagnostics keep question aliases OK, Q&A alias overlap OK, and substring
  risk INFO rather than WARN or FAIL.
- The final implementation diff is limited to the package YAML and focused
  tests needed for this slice.

Suggested focused verification for the implementation worker:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py -k "notes_action_requests or captions_and_translation or notes_location"
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
git status --short
```

The final status may still show the pre-existing `.coverage` modification from
another worker. This slice must not modify or stage it.

## Implementation Handoff Prompt

```text
Cycle154 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage`.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the smallest user-valuable RingCentral Video knowledge-pack
increment after the tone alias/routing work: add exact English answer-only Q&A
prompts for Notes, Transcript, and captions action phrasings.

Read first:
- docs/agent-handoffs/cycle-154-demand-analysis.md
- packages/ringcentral-video.yaml around the Q&A item
  `Where are captions, live transcription, and translation controls?`
- tests/unit/test_questions.py around the English notes/transcript/captions
  safety tests
- tests/unit/test_diagnostics.py around RingCentral Q&A prompt counts
- tests/unit/test_cli.py around `test_doctor_loads_profile_package_and_flow`

Scope:
- Package/test-only change.
- Add exactly these `localizedQuestions.en` prompts to the existing captions,
  live transcription, and translation Q&A:
  - `Start meeting notes`
  - `Summarize meeting notes`
  - `Turn on captions`
- Add or extend focused question-routing tests proving each prompt is
  answer-only: `entrypoint_id is None`, `can_operate is False`, and
  `create_question_interrupt_step(...) is None`.
- Prove `start meeting notes` no longer routes to
  `ringcentral.develop.video.start`.
- Prove `summarize meeting notes` no longer routes to
  `ringcentral.video.more.notes`.
- Keep existing location lookups for Notes and Transcript routed to
  `ringcentral.video.more.notes`.
- Update Q&A prompt count expectations from 84 to 87 only where diagnostics or
  CLI tests require it.

Do not:
- Edit runtime source, profiles, README, existing docs, provider behavior, or
  acceptance evidence.
- Add broad entrypoint aliases or package-owned aliases for `notes`,
  `meeting notes`, `transcript`, or `captions`.
- Change Chinese, Japanese, or Spanish content for this slice.
- Combine this with participants, invite/share, recording, or network-quality
  routing improvements.
- Touch `.coverage`.

Acceptance:
- Focused tests pass:
  `$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py -k "notes_action_requests or captions_and_translation or notes_location"`
- Diagnostics and doctor count tests pass if count expectations changed:
  `$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow`
- Diff hygiene passes:
  `git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
- Final diff excludes `.coverage`, source, profiles, README, existing docs, and
  unrelated tests.
```
