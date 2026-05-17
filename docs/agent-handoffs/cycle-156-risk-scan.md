# Cycle 156 Risk Scan: RingCentral Video Recording Exact Questions

Date: 2026-05-17
Cycle: 156
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`
Latest related commit: `c8b2c2e`

## Scope

Documentation-only risk scan for future RingCentral Video question-routing work
around these exact English prompts:

- `Record this meeting`
- `Start recording`
- `Stop recording`
- `Are we recording?`
- `Recording status`

This scan does not edit source, tests, packages, profiles, existing docs,
generated artifacts, or `.coverage`.

## Current Runtime Baseline

Verified against the current package/runtime:

| Prompt | Current route | `can_operate` | Interrupt step | Current answer shape |
| --- | --- | --- | --- | --- |
| `Record this meeting` | no match | `False` | none | no-match fallback |
| `Start recording` | `ringcentral.video.more.recording` | `False` | none | generic entrypoint answer |
| `Stop recording` | `ringcentral.video.more.recording` | `False` | none | generic entrypoint answer |
| `Are we recording?` | `ringcentral.video.more.recording` | `False` | none | generic entrypoint answer |
| `Recording status` | `ringcentral.video.more.recording` | `False` | none | generic entrypoint answer |

The most important current safety boundary is that
`ringcentral.video.more.recording` has `openSteps: []`. Even when a prompt
routes there, `create_question_interrupt_step(...)` returns `None`.

The runtime also blocks operation for risky entrypoint wording. `_can_operate`
rejects entrypoints whose id, title, or purpose includes words such as
`record`, `recording`, `start`, or `stop`. This is a useful defense in depth,
but the empty `openSteps` boundary is still the clearer structural guarantee.

## Risk Summary

The useful goal is answer quality, not live recording authority.

The current behavior is safe from accidental UI execution, but not ideal UX:
four of the five exact prompts route to the recording entrypoint and answer
with `Start recording: Start recording the meeting.` That answer is too action-
shaped for `Stop recording`, `Are we recording?`, and `Recording status`; it can
sound as if AiPresenter knows or controls the live recording state. The prompt
`Record this meeting` currently misses, which is safer than operating but may
feel unhelpful and inconsistent with the other recording prompts.

Future work should make these prompts resolve to explicit recording-safety Q&A
copy. It should not add executable recording behavior, claim current recording
state, or imply that AiPresenter can start or stop recording without a separate
confirmed operation design.

Recommended risk level: high. The code change may be small, but the language is
adjacent to consent, policy, host permissions, and meeting-wide state.

## Answer-Only Boundary

Keep all five exact prompts answer-only unless a separate product decision,
test plan, and live acceptance boundary explicitly authorize operation.

Safe answer behavior:

- `Record this meeting`: explain that recording changes meeting state and
  requires explicit confirmation, allowed role/policy, and participant consent.
- `Start recording`: same safety answer; do not phrase the response as if the
  click has happened or will happen next.
- `Stop recording`: explain that stopping recording is also a state-changing
  action that requires explicit confirmation and visible context.
- `Are we recording?`: do not answer yes or no unless a verified observation
  source has checked the visible recording indicator. Default to explaining
  where to check and what preconditions apply.
- `Recording status`: same as status question; explain the visible status
  boundary without inventing state.

Do not create a question interrupt step for any of these prompts in the current
slice. Do not add `openSteps` to `ringcentral.video.more.recording` as part of
exact-question UX work.

## No-Go Claims

Do not claim or imply:

- AiPresenter started, stopped, toggled, enabled, disabled, verified, or
  confirmed recording.
- The meeting is recording, is not recording, or has a known recording state.
- RingCentral accepted a recording command.
- The current user has host/moderator permissions to record.
- Participant consent, organization policy, legal permission, or meeting
  agreement has been obtained.
- A package route proves live RingCentral UI state, button availability, or
  recording indicator state.
- Unit tests, doctor output, localization reports, or dry-run routing prove
  live recording behavior.
- Post-meeting recording artifacts exist, can be read, can be summarized, or are
  available to the current user.

Avoid release/test wording such as `recording status verified`, `start
recording supported`, `stop recording supported`, `recording control wired`,
`recording ready`, `host recording available`, `live recording checked`, or
`RingCentral recording accepted`.

## Duplicate Alias And Matching Risks

The current package has a recording entrypoint alias inventory for Spanish,
Japanese, and Chinese, but no English package-owned recording aliases on
`ringcentral.video.more.recording`. The English route today comes from token
scoring against the entrypoint title and purpose, not from a curated English
alias or exact Q&A prompt.

If exact English prompts are added as package Q&A, Q&A-first matching should be
preserved. This is the safer route because a Q&A item can provide non-operable
safety copy while still referencing `ringcentral.video.more.recording` for
context.

Risks to watch:

- Adding `recording`, `record`, or `start recording` as broad English
  entrypoint aliases can keep rendering the generic entrypoint answer instead
  of the safer Q&A answer.
- Adding the same normalized prompt to both `localizedQuestions.en` and
  `questionAliases.en` can create a diagnostic overlap. If the Q&A references
  the same entrypoint, diagnostics may allow it, but the design remains harder
  to reason about.
- Adding `record` as a short alias can steal post-meeting artifact questions or
  safety questions that should remain answer-only Q&A.
- `Stop recording`, `Are we recording?`, and `Recording status` should not be
  treated as synonyms for the title `Start recording`; they need status/control
  caveats in the answer.
- Existing legacy Chinese aliases still include recording terms in runtime code.
  Future package-owned English aliases should not expand or depend on the
  legacy alias table.

Preferred implementation shape for a future source change: add or extend a
recording-safety Q&A item with exact English prompts, localized prompts only if
intentionally in scope, and `relatedEntrypointIds:
["ringcentral.video.more.recording"]`. Keep the entrypoint itself unchanged.

## Localization And Count Diagnostics

Current verified localization baseline:

- `ja`: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers;
  `questionAliases.ja` on `13/27` entrypoints with `34` aliases.
- `zh`: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers;
  `questionAliases.zh` on `15/27` entrypoints with `49` aliases.
- `es`: `51/51` demo steps, `12/12` Q&A questions, `12/12` Q&A answers;
  `questionAliases.es` on `26/27` entrypoints with `69` aliases.

Doctor baseline:

- `question aliases`: `157` package-owned aliases, no cross-entrypoint
  duplicates.
- `qa questions`: `92` Q&A question prompts, no cross-item duplicates.
- `qa alias overlap`: `92` prompts, no unsafe package-owned alias overlaps.
- `qa alias substring risk`: existing `INFO` with `11` prompts; Q&A-first
  matching still applies.
- Overall: `11 ok, 1 info, 0 warnings, 0 failed`.

If future work adds exact English Q&A prompts, Q&A prompt counts should change.
If future work adds English entrypoint aliases instead, alias counts should
change. Do not update expected counts mechanically; rerun diagnostics and
explain whether any new overlap or substring-risk report is expected.

## Test-Risk Guidance

Recommended focused tests for a future implementation:

- For each exact prompt, assert `entrypoint_id ==
  "ringcentral.video.more.recording"`, `can_operate is False`, and
  `create_question_interrupt_step(...) is None`.
- Assert each answer uses recording-safety copy, not the generic entrypoint
  prefix `Start recording:`.
- Assert `Record this meeting` no longer falls through to the no-match fallback
  if the UX goal is to answer it.
- Assert `Stop recording`, `Are we recording?`, and `Recording status` do not
  claim actual live state or command execution.
- Include tone invariance if the prompts are meant to behave like existing
  sensitive prompts.
- Include a diagnostic test or CLI doctor expectation update only if counts or
  report details intentionally change.
- Keep post-meeting artifact prompts separate from in-meeting recording control
  prompts.

No-go test patterns:

- Do not make tests pass by relaxing `_RISKY_ENTRYPOINT_WORDS`,
  `questionPolicy`, `_can_operate`, empty `openSteps`, or interrupt-step
  blocking for recording.
- Do not add live RingCentral automation or a UI click to prove exact-question
  routing.
- Do not assert a yes/no answer for recording status without a verified visible
  observation path.
- Do not broaden this cycle into notes, transcript, post-meeting artifact,
  permission, provider, speech, virtual microphone, or live acceptance behavior.

Recommended verification for implementation cycles:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_diagnostics.py tests\unit\test_cli.py
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Do not run coverage-producing commands for this exact-question slice unless the
user explicitly asks. If `.coverage` is already dirty, leave it untouched.

## Go/No-Go

Go if the future implementation:

- Routes all five exact prompts to answer-only recording-safety copy.
- Preserves `can_operate=False` and no question interrupt step.
- Leaves `ringcentral.video.more.recording.openSteps` empty.
- Avoids claiming or inferring actual recording status or control.
- Keeps exact Q&A prompts distinct from broad aliases and post-meeting artifact
  questions.
- Updates diagnostics/count expectations only when the authored inventory truly
  changes.

No-go if it:

- Adds executable recording steps or queues a question interrupt for recording.
- Answers `Are we recording?` or `Recording status` with invented live state.
- Uses broad English aliases that steal unrelated recording, transcript, notes,
  or post-meeting artifact questions.
- Treats `Stop recording` as a simple synonym for `Start recording` without
  stop-specific caution.
- Claims live RingCentral acceptance, host permissions, consent, policy
  compliance, or artifact availability from package/runtime tests alone.
