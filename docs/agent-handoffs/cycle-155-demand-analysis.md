# Cycle 155 Demand Analysis: Microphone Button Alias

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next small RingCentral Video knowledge-pack increment
the deferred `microphone button` package-owned alias.

Add an exact English alias, `microphone button`, to the existing
`ringcentral.video.toolbar.audio` entrypoint so the user question
`Where is the microphone button?` routes to the toolbar microphone control
instead of the audio device menu.

This is the best next slice because Cycle 154 already handled the sharper
Notes, Transcript, and captions action phrasing risk. The remaining microphone
alias is a contained route-quality fix: it improves a common location question
without changing runtime matcher scoring, question policy, operability, demo
steps, privacy behavior, or live RingCentral Video claims.

Do not choose the recording prompt slice first. Recording has real follow-up
value, but it needs a separate policy pass to distinguish action requests
(`Record this meeting`, `Start recording`, `Stop recording`), status questions
(`Are we recording?`, `Recording status`), and location guidance. That is a
slightly larger answer-only design problem. The microphone button alias is
smaller, already analyzed, and safe to land as a package/test-only increment.

## Current Evidence

Cycle 154 demand selected an answer-only Notes, Transcript, and captions Q&A
slice, while the technical scan identified the microphone alias as a different
small candidate. The Cycle 154 implementation followed demand and explicitly
deferred the microphone alias.

Current read-only routing probes show:

- `Where is the microphone button?` routes to
  `ringcentral.video.toolbar.audio-menu`, `can_operate=False`, with no interrupt
  step.
- `record this meeting` returns no match.
- `start recording`, `are we recording?`, and `recording status` route to
  `ringcentral.video.more.recording`, `can_operate=False`, with no interrupt
  step.
- `share system audio` routes to the audio menu, which may be reasonable enough
  to analyze later because device and audio-output language overlaps with that
  menu.

The microphone result is a clear mismatch in user vocabulary: "button" points
to the toolbar mute/unmute control, while the current route describes the
microphone and speaker device menu.

## User Value

Operators ask short, visual questions during a live demo. If they ask where the
microphone button is, they expect help finding the bottom-toolbar privacy
switch they check before speaking. Returning the microphone and speaker menu is
nearby, but it nudges the presenter toward device recovery instead of the
primary mute/unmute control.

The value is practical and small:

- The answer points to the control the user meant.
- The route stays non-operable because the microphone control remains a risky
  mute/unmute toggle.
- No automatic mute, unmute, device switch, or interrupt step is introduced.
- Device-recovery phrases can continue to route to the audio menu.
- The knowledge pack becomes more precise without broadening matching through
  aliases such as `mic`, `microphone`, or `audio`.

## Candidate Comparison

`microphone button` is the recommended Cycle 155 slice. It is one exact
package-owned alias plus focused tests. It fixes a currently observed wrong
route while preserving the existing safety boundary.

Recording answer-only prompts are a good later candidate. They may deliver more
safety value, especially for `record this meeting`, but the first recording
slice should decide whether exact prompts belong in Q&A, in non-operable
entrypoint routing, or split between action/status/location handling. That is
not quite as small as the microphone alias.

`share system audio` is also worth a later scan, but it is ambiguous without
product evidence about the RingCentral Video sharing surface. Do not combine it
with the microphone alias.

## Recommended Minimum Scope

Implement a package/test-only slice:

- Modify `packages/ringcentral-video.yaml`.
- Under `ringcentral.video.toolbar.audio`, add `questionAliases.en` with exactly
  one alias: `microphone button`.
- Modify `tests/unit/test_questions.py` to prove
  `Where is the microphone button?` routes to
  `ringcentral.video.toolbar.audio`, keeps `can_operate is False`, and produces
  no question interrupt step.
- Preserve audio-menu routing for device-recovery phrasing such as
  `microphone and speaker menu`, `audio options`, or `switch microphone`.
- Update diagnostics or CLI count assertions only if required by the new
  package-owned alias count. With exactly one added entrypoint alias, expect the
  RingCentral package-owned alias count to move from `156` to `157`.

No runtime source change should be necessary.

## Do Not Touch

- Do not edit `.coverage`.
- Do not revert or clean up other workers' edits.
- Do not edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, durable knowledge, or existing
  handoff docs.
- Do not edit Q&A items for this slice.
- Do not add broad aliases such as `microphone`, `mic`, `mute`, `audio`, or
  `audio button`.
- Do not change `can_operate`, `questionPolicy`, `openSteps`, operation IDs,
  locators, demo flow steps, narration, localized text, or safety wording.
- Do not combine this with recording, transcript, Notes, captions, share,
  participants, network-quality, or system-audio routing work.
- Do not claim live RingCentral Video acceptance, microphone-state validation,
  device-switching capability, or audio-provider readiness.

## Acceptance Criteria

The implementation is complete when these repo-local contracts hold:

- `Where is the microphone button?` matches
  `ringcentral.video.toolbar.audio`.
- `Where is the microphone button?` no longer matches
  `ringcentral.video.toolbar.audio-menu`.
- The matched response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None`.
- The package adds exactly one English alias, `microphone button`, under
  `ringcentral.video.toolbar.audio`.
- No broad microphone, mic, mute, or audio aliases are added.
- Existing device-menu questions still route to
  `ringcentral.video.toolbar.audio-menu`.
- RingCentral diagnostics still report question aliases OK, Q&A questions OK,
  Q&A alias overlap OK, and substring risk as reviewed INFO rather than WARN or
  FAIL.
- If count assertions need updates, package-owned aliases move from `156` to
  `157` and Q&A prompt counts remain `87`.
- The final implementation diff is limited to package YAML and focused tests
  required for this slice.

Suggested focused verification for the implementation worker:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py -k "microphone_button or package_aliases or audio_menu"
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py::test_diagnostics_reports_question_aliases_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_questions_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_overlap_ok_for_ringcentral_package tests\unit\test_diagnostics.py::test_diagnostics_reports_qa_alias_substring_info_for_ringcentral_package tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
git status --short
```

The final status may still show the pre-existing `.coverage` modification from
another worker. This slice must not modify or stage it.

## Implementation Handoff Prompt

```text
Cycle155 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage`.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the smallest RingCentral Video knowledge-pack routing increment
after the Notes, Transcript, and captions Q&A slice. Add the deferred exact
package-owned microphone button alias so a visual location question selects the
toolbar microphone control instead of the audio device menu.

Read first:
- docs/agent-handoffs/cycle-155-demand-analysis.md
- docs/agent-handoffs/cycle-154-technical-scan.md
- docs/agent-handoffs/cycle-154-technical-development.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.toolbar.audio` and
  `ringcentral.video.toolbar.audio-menu`
- tests/unit/test_questions.py around the package-owned alias routing tests
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if alias-count
  assertions need updates

Scope:
- Package/test-only change.
- Add exactly one English alias, `microphone button`, under
  `ringcentral.video.toolbar.audio`.
- Add a focused question-routing test proving
  `Where is the microphone button?` selects
  `ringcentral.video.toolbar.audio`, keeps `can_operate is False`, and returns
  no question interrupt step.
- Preserve existing audio-menu routing for device-recovery wording.
- Update package-owned alias count expectations from `156` to `157` only where
  diagnostics or CLI tests require it. Keep Q&A prompt counts at `87`.

Do not:
- Edit runtime source, package models, session interrupt logic, profiles,
  README, existing docs, provider behavior, or acceptance evidence.
- Add Q&A prompts for this slice.
- Add broad aliases such as `microphone`, `mic`, `mute`, `audio`, or
  `audio button`.
- Change `can_operate`, `questionPolicy`, `openSteps`, locators, operation
  semantics, narration, localized strings, or live RingCentral claims.
- Combine this with recording, transcript, Notes, captions, share, participants,
  network-quality, or system-audio routing improvements.
- Touch `.coverage`.

Acceptance:
- `Where is the microphone button?` routes to
  `ringcentral.video.toolbar.audio`, not
  `ringcentral.video.toolbar.audio-menu`.
- The response is non-operable and creates no interrupt step.
- Device-recovery prompts still route to the audio menu.
- Diagnostics and doctor tests remain green with package-owned alias count
  updated only if needed.
- Diff hygiene passes:
  `git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py`
- Final diff excludes `.coverage`, source, profiles, README, existing docs, and
  unrelated tests.
```
