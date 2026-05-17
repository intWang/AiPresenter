# Cycle 165 Demand Analysis: Caption Text Privacy Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `96b0dc9`
Role: Cycle165 demand-analysis subagent

## Scope

This analysis inspected recent Cycle 163 and Cycle 164 handoffs, `pyproject.toml`,
`packages/ringcentral-video.yaml`, `tests/unit/test_questions.py`,
`tests/unit/test_diagnostics.py`, `tests/unit/test_cli.py`, and current
read-only question-routing behavior. I did not edit code or tests, did not run
the full suite, did not stage or commit, and did not touch `.coverage`.

The working tree already had `.coverage` modified before this pass. This
handoff writes only `docs/agent-handoffs/cycle-165-demand-analysis.md`.

## Recommendation

Cycle 165 should implement one narrow package/test-only slice: exact English
caption text privacy prompts under the existing Q&A item,
`Where are captions, live transcription, and translation controls?`.

This is the highest-value next target from the provided backlog:

- Meeting password/passcode prompts still need product evidence. Current
  handoffs repeatedly warn not to add password/passcode variants until the
  observed RingCentral Video Meeting information surface is confirmed to expose
  those values.
- Participant-role prompts are already authored and tested in the current
  Cycle165 working tree:
  `Show participant roles`, `Read participant roles`, `List participant roles`,
  and `Who is host or moderator?` route to the Chat/Participants privacy Q&A.
- Caption text variants remain under-covered even though the existing captions
  Q&A answer already says not to read caption or transcript text unless the
  user explicitly asks and visible context is verified.

## Current Behavior Observed

Read-only spot checks against the current working tree showed the gap:

| Prompt | Current observed behavior |
| --- | --- |
| `Show caption text` | No-match fallback, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Read caption text` | No-match fallback, `entrypoint=None`, `can_operate=False`, no interrupt. |
| `Show live caption text` | Routes to `ringcentral.video.toolbar.audio` fallback text, `can_operate=False`, no interrupt. |
| `Read live captions aloud` | Routes to the Meeting information privacy Q&A, `can_operate=False`, no interrupt. |

These are non-operable today, which is good, but the answers are not reliably
the caption/transcript privacy boundary. Users asking for caption content should
not hear Audio or Meeting information guidance.

## Exact Prompt Variants

Add these exact English Q&A prompts to the existing captions/live transcription
Q&A item:

- `Read caption text`
- `Show caption text`
- `Show live caption text`
- `Can you read the captions?`
- `Read live captions aloud`

Avoid broad aliases such as `caption`, `captions`, `text`, `live`, `read`, or
`show`. Those can steal harmless location questions, Audio toolbar questions,
or unrelated live-meeting controls.

## Expected Answer-Only Behavior

For every prompt above:

- Return the existing captions/live transcription Q&A answer, not the no-match
  fallback, Audio fallback, Meeting information privacy answer, or
  `Notes and transcript:` entrypoint fallback.
- Keep `entrypoint_id is None`, matching the existing
  `test_ringcentral_captions_and_translation_questions_are_answer_only`
  behavior for this Q&A item.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Include the safety boundary already present in the answer: `Notes and
  Transcript`, `Settings`, `read caption or transcript text`, `explicitly asks`,
  and `verified`.
- Do not start captions, notes, transcription, or translation.
- Do not read, summarize, invent, mask, quote, copy, save, export, or expose
  actual caption or transcript text.
- Do not claim visible caption text, speaker identity, translation state, or
  transcript availability has been verified.

## User Value

Caption text is live meeting content. It may expose participant speech,
names, topics, confidential customer details, or sensitive accessibility
context. A user asking "read caption text" is not asking where the control is;
they are asking AiPresenter to reveal meeting content. The system should answer
with the same privacy boundary it already uses for transcript content instead
of drifting to Audio, Meeting information, or generic no-match text.

This keeps the RingCentral safety model predictable: controls can be explained,
but live private content is not read aloud unless a future workflow has explicit
intent, visible-content verification, and any needed consent boundary.

## Acceptance Criteria

- The five prompt variants are authored under the existing Q&A item
  `Where are captions, live transcription, and translation controls?`, not under
  entrypoint `questionAliases`.
- The existing Q&A answer may remain unchanged because it already covers
  caption and transcript text privacy.
- Each prompt returns an answer containing `Notes and Transcript`, `Settings`,
  `explicitly asks`, and `verified`.
- Each prompt has `entrypoint_id is None`.
- Each prompt has `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- No response contains the no-match fallback
  `I could not find a matching control in the active app context.`
- No response starts with or contains unrelated fallback labels such as
  `Microphone control:`, `Meeting information:`, or `Notes and transcript:`.
- No response contains private-content-looking fixture values, quoted caption
  content, speaker names, URLs, email addresses, or success claims such as
  `read`, `copied`, `saved`, `exported`, `started`, or `verified` as a claim of
  completed action. The existing answer's conditional word `verified` is fine
  when used only as a boundary.
- Existing caption-location prompts continue to pass:
  `Where are captions?`, `Can I use live transcription?`,
  `How do I translate captions?`, `Where are translated captions?`, and
  `Turn on captions`.
- Existing transcript content tests continue to pass for `Summarize the
  transcript` and `Read the transcript`.
- Existing Audio toolbar, Meeting information privacy, participant privacy, and
  diagnostics/doctor checks continue to pass.
- Because this adds five authored English Q&A prompts, update exact Q&A prompt
  inventory expectations from `157` to `162` in diagnostics and CLI tests only
  if all five prompts are added.
- Do not edit runtime matcher code, profiles, README, acceptance evidence,
  `.coverage`, or unrelated tests for this slice.

## Suggested Focused Verification

Do not run the full suite for this narrow implementation. Suggested focused
checks for the implementation agent, with coverage disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only
```

If prompt counts change:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

## Next Backlog

1. Meeting password/passcode private-value prompts, only after confirming
   product evidence that RingCentral Video Meeting information exposes those
   fields. If confirmed, add exact prompts to the Meeting information privacy
   Q&A and update answer/localized answer copy so passcodes/passwords are
   explicitly included.
2. Localized caption text variants in Chinese, Japanese, and Spanish after the
   English exact-prompt slice is stable.
3. State/status prompts for encryption, meeting lock, waiting room, and security
   controls. These need state-verification wording, not private-content wording.
4. Higher-layer presenter/session checks proving privacy Q&A responses cannot
   become queued demo steps, live interrupts, clipboard actions, speech readouts,
   note/transcript starts, caption starts, or export/save actions.
