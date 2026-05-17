# Cycle 166 Demand Analysis: Caption Text Privacy Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `62b0f750232e1eb75bac29561a376816f1eef4a3`
Role: Cycle166 demand-analysis subagent

## Scope

Inspected recent Cycle 165 handoffs, `packages/ringcentral-video.yaml`, and
question/diagnostics/doctor tests around RingCentral Video Q&A routing. I did
not edit source code, package tests, run the full suite, stage, commit, or touch
`.coverage`.

This pass writes only `docs/agent-handoffs/cycle-166-demand-analysis.md`.

Current shared worktree note: `.coverage` was already dirty, and another
Cycle166 worker appears to have in-flight edits in `packages/ringcentral-video.yaml`,
`tests/unit/test_questions.py`, `tests/unit/test_diagnostics.py`, and
`tests/unit/test_cli.py`. Those edits add four caption prompts and move Q&A
prompt-count expectations from `161` to `165`. Treat them as other-agent work.

## Recommendation

Cycle166 should finish the caption/caption-text privacy slice as a package/test
only change under the existing Q&A item:

`Where are captions, live transcription, and translation controls?`

Keep these as exact English Q&A prompts, not entrypoint `questionAliases`, not
runtime matcher changes, and not new broad aliases. Caption text is live meeting
content, so the right behavior is answer-only privacy guidance, not opening a
control or reading content aloud.

## Recommended Exact Prompt Variants

Recommended final six-prompt set:

- `Read caption text`
- `Show caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`
- `Can you read the captions?`

The current in-flight worktree already contains four of these:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`

Highest-value addition: `Can you read the captions?` currently routes to the
Meeting IDs and links privacy Q&A instead of the captions/transcript privacy
boundary. `Show caption text` is the natural singular form and should be pinned
as an exact prompt rather than relying on fuzzy matching.

Avoid broad aliases such as `caption`, `captions`, `text`, `read`, `show`,
`live`, `copy`, or `export`. They can steal harmless location questions or route
private-content asks to thin entrypoint fallback text.

## Expected Answer-Only Behavior

For every accepted prompt variant:

- Return the existing captions/live transcription Q&A answer.
- Keep `entrypoint_id is None`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Include the current boundary terms: `Notes and Transcript`, `Settings`,
  `caption or transcript text`, `explicitly asks`, and `verified`.
- Do not start notes, transcription, captions, or translation.
- Do not read, quote, invent, mask, copy, save, export, or summarize caption or
  transcript content.
- Do not claim visible caption text, speaker identity, translation state, or
  transcript availability has been verified.
- Do not fall back to `Microphone control:`, `Meeting information:`, or
  `I could not find a matching control in the active app context.`

Observed routing snapshot from the current in-flight worktree:

- The four already-added prompts route correctly to the captions Q&A.
- `Show caption text`, `Read live captions aloud`, and
  `Read the live transcript text` also route correctly today, but are not all
  exact authored prompts.
- `Can you read the captions?` routes incorrectly to meeting-info privacy.
- `Copy captions` routes to thin Meeting information fallback, and
  `Export captions` no-matches. Keep copy/export as a later wording expansion
  only if answer copy is broadened beyond read/show text.

## User Value

Caption text can expose participant speech, names, customer details, internal
topics, health or accessibility context, and other live meeting content. A user
asking to read or show captions is asking for content disclosure, not just the
location of a control.

This slice makes AiPresenter predictable: it can explain where caption and
transcript controls live, while refusing to expose live text unless a future
workflow proves explicit user intent, visible-content verification, and any
needed consent boundary.

## Acceptance Criteria

- Prompt variants are authored under the existing captions/live transcription
  Q&A item, not entrypoint aliases.
- No runtime matcher, profile, open-step, or presenter-session code changes are
  needed.
- The captions Q&A answer may remain unchanged for read/show text prompts
  because it already names `read caption or transcript text`.
- Each final prompt returns answer text containing `Notes and Transcript`,
  `Settings`, `caption or transcript text`, `explicitly asks`, and `verified`.
- Each final prompt has `entrypoint_id is None`, `can_operate is False`, and no
  interrupt step.
- Responses do not contain `Microphone control:`, `Meeting information:`, or
  the no-match fallback.
- Responses do not contain private-content-looking fixture values, speaker
  names, URLs, email addresses, or claims such as `copied`, `saved`, `exported`,
  `started`, or `verified` as a completed action.
- Existing location prompts continue to pass: `Where are captions?`,
  `Can I use live transcription?`, `How do I translate captions?`,
  `Where are translated captions?`, and `Turn on captions`.
- Existing transcript and notes privacy tests continue to pass for
  `Read the transcript`, `Summarize the transcript`, and meeting-notes start
  variants.
- From committed baseline `62b0f75`, a six-prompt caption slice moves Q&A prompt
  expectations from `161` to `167`; the current four-prompt in-flight slice
  moves them to `165`. Update diagnostics/CLI count strings only to the actual
  prompt delta that lands.
- Package-owned alias count should remain `157`; substring-risk count should be
  checked but not changed unless diagnostics show real drift.
- Do not stage `.coverage`.

## Focused Verification Recommendation

Do not run the full suite for this narrow slice unless the coordinator asks.
Suggested focused checks, with coverage disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only tests\unit\test_questions.py::test_ringcentral_english_notes_action_requests_do_not_match_start_meeting
```

If prompt counts change:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

## Future Backlog

1. Password/passcode prompts only after product evidence confirms RingCentral
   Video exposes password, passcode, or access-code values in Meeting
   information or another verified surface.
2. If confirmed, add exact prompts under
   `How should AiPresenter handle meeting IDs and links safely?`, such as
   `What is the meeting password?`, `Read the meeting password`,
   `Copy the meeting password`, `What is the meeting passcode?`,
   `Read the meeting passcode`, and `Copy the meeting passcode`.
3. Update English and localized meeting-info privacy answers before adding those
   prompts so passwords/passcodes are explicitly classified as private meeting
   access details.
4. Caption copy/export prompts, such as `Copy captions` or `Export captions`,
   should wait for answer-copy expansion and product evidence around whether
   captions are live text, transcript artifacts, downloadable artifacts, or all
   three in the target RingCentral build.
5. Localized caption-text privacy variants can follow after the English exact
   prompt slice is stable.
6. Higher-layer checks should eventually prove privacy Q&A answers cannot become
   queued demo steps, speech readouts of private content, clipboard actions,
   transcript starts, caption starts, or export/save actions.

## Coordinator Resolution

The final Cycle166 implementation accepted the broader caption-readout demand
after test review. In addition to the original four caption text prompts, it
adds:

- `Can you read the captions?`
- `Can you read captions?`

Final Q&A prompt count is `167`. `Show caption text` remains a future exact
variant candidate.
