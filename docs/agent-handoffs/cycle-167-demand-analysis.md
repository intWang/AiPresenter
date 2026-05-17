# Cycle 167 Demand Analysis: Remaining Caption And Live Transcript Variants

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest inspected commit: `2ce39f4`
Role: Cycle167 demand-analysis subagent

## Scope

Inspected the Cycle166 handoffs, `pyproject.toml`, `packages/ringcentral-video.yaml`,
and the RingCentral question, diagnostics, and CLI tests. I did not edit code,
tests, package YAML, staging, commits, or `.coverage`, and I did not run the full
suite.

This handoff writes only `docs/agent-handoffs/cycle-167-demand-analysis.md`.

Workspace note: `.coverage` was already dirty. While inspecting, the shared
worktree also gained concurrent edits in `packages/ringcentral-video.yaml` and
`tests/unit/test_questions.py` that add caption copy/export/save/download prompts.
Treat those as other-agent work; this recommendation does not rely on them and
does not overwrite them.

## Current Baseline

Cycle166 landed the committed six-prompt readout slice under the existing Q&A
item `Where are captions, live transcription, and translation controls?`:

- `Read caption text`
- `Show captions text`
- `Show live caption text`
- `Read captions aloud`
- `Can you read the captions?`
- `Can you read captions?`

The committed diagnostics and doctor count expectations are now `167` Q&A
question prompts. Package-owned aliases remain `157`, and the Q&A alias substring
risk count remains `11`.

The package answer is already the right privacy boundary: use Notes and
Transcript / Settings as discovery surfaces, but do not start notes,
transcription, captions, or translation; do not read caption or transcript text;
and do not promise summaries unless the user explicitly asks and visible context
is verified.

Read-only spot probes against the current worktree showed the remaining candidate
phrases already route to that privacy Q&A today, but they are not exact authored
prompts or test-pinned:

- `Show caption text`
- `Read live captions aloud`
- `Read live caption text`
- `Read the live caption text`
- `Read the live transcript text`

That means current behavior is safe but somewhat accidental. The value of
Cycle167 is to make those exact user phrasings durable without broadening the
matcher.

## Recommendation

Cycle167 should implement one narrow package/test-only slice: add the remaining
exact caption/live-transcript readout variants to the same captions/live
transcription Q&A item.

Recommended exact English prompt variants:

- `Show caption text`
- `Read live captions aloud`
- `Read live caption text`
- `Read the live caption text`
- `Read the live transcript text`

Do not add entrypoint `questionAliases`, runtime matcher changes, new
`relatedEntrypointIds`, or broad aliases such as `caption`, `captions`, `text`,
`read`, `show`, `live`, or `transcript`. These prompts are private-content shaped
and should stay in Q&A-first answer-only routing.

## Expected Answer-Only Behavior

For every Cycle167 prompt variant:

- Return the existing captions/live transcription Q&A answer.
- Keep `entrypoint_id is None`.
- Keep `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None`.
- Include `Notes and Transcript`, `Settings`, `caption or transcript text`,
  `explicitly asks`, and `verified`.
- Do not start notes, transcription, captions, translation, summaries, export,
  save, download, copy, or clipboard actions.
- Do not read, quote, invent, mask, summarize, display, or narrate caption or
  transcript content.
- Do not claim visible caption text, speaker identity, translation state,
  transcript availability, artifact existence, or permission has been verified.
- Do not fall back to `Microphone control:`, `Meeting information:`,
  `Notes and transcript:`, or `I could not find a matching control`.

## Acceptance Criteria

- The five prompt variants are authored under
  `Where are captions, live transcription, and translation controls?`.
- `tests/unit/test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only`
  covers the same five variants.
- Existing Cycle166 readout prompts remain covered and answer-only.
- Existing location/control prompts still pass: `Where are captions?`,
  `Can I use live transcription?`, `How do I translate captions?`,
  `Where are translated captions?`, and `Turn on captions`.
- Existing transcript content tests still pass for `Summarize the transcript`
  and `Read the transcript`.
- Responses contain the privacy boundary tokens listed above and exclude Audio,
  Meeting information, Notes entrypoint fallback, and no-match fallback labels.
- Responses exclude readout/action leak language such as `The caption says`,
  `Here are the captions`, `copied`, `exported`, `saved`, `downloaded`,
  `started`, and `turned on`.
- No runtime code, profiles, README, acceptance evidence, or unrelated tests are
  needed for this slice.
- From committed baseline `2ce39f4`, adding only these five prompts moves Q&A
  prompt-count expectations from `167` to `172`. If the concurrent
  copy/export/save/download prompt work lands first, recompute by adding `5` to
  that final count instead of hard-coding `172`.
- Package-owned alias count should remain `157`; substring-risk count should
  remain `11` unless focused diagnostics report otherwise.
- `.coverage` remains untouched and unstaged.

## Focused Verification Recommendation

Do not run the full suite for this narrow slice unless the coordinator asks.
Use coverage-disabled focused checks:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py::test_ringcentral_captions_and_translation_questions_are_answer_only tests\unit\test_questions.py::test_ringcentral_english_transcript_content_requests_stay_answer_only
```

If prompt counts change, also run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
```

## Future Backlog

1. Review the concurrent caption copy/export/save/download prompt work as a
   separate artifact/action slice. It should not be mixed into this readout
   wording pass unless the coordinator explicitly combines them.
2. Add localized caption/live-caption/live-transcript readout variants after the
   English exact prompts and count expectations are stable.
3. Consider exact transcript-display variants such as `Show transcript text`
   only after deciding whether they belong with live-caption privacy, transcript
   content privacy, or post-meeting artifact privacy.
4. Add higher-layer checks proving privacy Q&A answers cannot become queued demo
   steps, speech readouts of private content, clipboard actions, caption starts,
   transcript starts, downloads, saves, or exports.
5. Keep password/passcode/access-code prompts blocked until product evidence
   confirms RingCentral Video exposes those values in a verified surface and the
   meeting-info privacy answer is updated first.
