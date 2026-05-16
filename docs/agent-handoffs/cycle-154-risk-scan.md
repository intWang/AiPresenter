# Cycle 154 Risk Scan: RingCentral Video Package Question Aliases

Date: 2026-05-17
Cycle: 154
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Scope

Documentation-only risk scan for future work that adds RingCentral Video
package question aliases or Q&A aliases.

This scan does not edit source, tests, README, packages, profiles, existing
docs, generated artifacts, or `.coverage`.

Relevant current routing shape:

- `answer_question(...)` normalizes the user question, checks package Q&A
  first, then package-owned entrypoint aliases, then legacy aliases, then
  entrypoint token scoring.
- Package-owned aliases live under `operationEntrypoints[*].questionAliases`
  and can select an entrypoint.
- Q&A prompts and aliases are answer content and should remain the preferred
  path for privacy, recording, transcript, notes, shared-content, consent, and
  post-meeting artifact questions.
- `can_operate` is false when no entrypoint is selected, the selected
  entrypoint has `questionPolicy: answerOnly`, the selected entrypoint has no
  `openSteps`, or the selected entrypoint text contains risky action words.
- Current doctor expectations include 156 package-owned aliases with no
  cross-entrypoint duplicates, 84 Q&A prompts with no cross-item duplicates, no
  unsafe Q&A/alias overlap, and an informational Q&A alias substring-risk
  report.

## Risk Summary

The useful goal is narrow: make more natural user questions resolve to already
curated RingCentral Video answers or entrypoints without changing the operation
boundary.

The main risk is that alias growth silently changes behavior. A new package
alias can turn a question that used to be answer-only into an entrypoint match.
If that entrypoint is operable, `create_question_interrupt_step(...)` can
become eligible. A new Q&A alias can also shadow an entrypoint alias and change
which answer or related entrypoint is selected. Both changes may be correct,
but they must be intentional, tested, and described as deterministic package
routing only.

The highest-risk topics are recording, Notes and Transcript, live transcription
or captions, shared-screen content, chat messages, participant names, meeting
information, invite, share, reactions, raise hand, leave/end, settings,
background, post-meeting recordings, summaries, insights, and any wording that
sounds like privacy or consent assurance.

Do not let alias coverage become a proxy claim for live RingCentral behavior,
provider behavior, privacy compliance, transcript access, recording consent,
or broad semantic understanding.

## Safe Wording

Preferred wording:

- "Adds curated package-owned aliases for the covered RingCentral Video
  questions."
- "Keeps Q&A-first routing for privacy-sensitive, recording, notes,
  transcript, shared-content, and post-meeting artifact prompts."
- "The change expands deterministic package matching for explicit authored
  prompts; it does not expand live automation authority."
- "Answer-only prompts still return `can_operate=False` and do not create a
  question interrupt step."
- "Operable prompts remain limited to entrypoints that already have safe
  `openSteps` and are not blocked by `questionPolicy` or risky action wording."
- "Doctor diagnostics continue to guard duplicate aliases, duplicate Q&A
  prompts, unsafe Q&A/alias overlap, and substring risk."
- "This is package-routing evidence, not live RingCentral Video acceptance."
- "Provider output, speech routing, virtual microphone behavior, live UI
  locators, meeting privacy, and RingCentral acceptance remain out of scope."

Use narrow verbs such as `adds`, `matches`, `routes`, `keeps`, `guards`,
`preserves`, and `reports`. Avoid verbs such as `proves`, `validates`,
`certifies`, `understands`, or `protects` unless a separate dated evidence
surface proves that exact claim.

## No-Go Claims

Do not claim or imply:

- New aliases prove live RingCentral Video acceptance.
- New aliases prove RingCentral UI locators, windows, menus, or cleanup
  behavior work in the current live app.
- New aliases expand what AiPresenter may click, open, start, stop, send,
  leave, record, transcribe, summarize, read, copy, invite, or share.
- New Q&A coverage proves privacy safety, privacy compliance, consent handling,
  or safe handling of meeting messages, participant names, transcripts, notes,
  recordings, summaries, insights, or shared-screen content.
- `can_operate=False` proves privacy compliance or consent correctness.
- `can_operate=True` proves a live action is safe in a real meeting.
- A recording, transcript, captions, translation, notes, or post-meeting
  artifact answer means AiPresenter can access that artifact or read its
  contents.
- A location alias for a sensitive control means AiPresenter should perform the
  sensitive action.
- Q&A-first routing means the model semantically understands every privacy,
  consent, recording, transcript, or shared-content paraphrase.
- Provider behavior, OpenAI behavior, SAPI behavior, Piper behavior, speech
  quality, virtual microphone routing, or audio acceptance changed.
- Spanish, Chinese, Japanese, or any other localized alias coverage means a
  broader runtime language or provider capability is enabled.
- Doctor, localization-report, dry-run, or unit-test output is live acceptance
  evidence.

Avoid wording such as `privacy-safe aliases`, `recording-safe`, `transcript
ready`, `RingCentral accepted`, `provider validated`, `semantic coverage`,
`understands user intent`, `consent aware`, `live-ready`, or `safe in live
meetings`.

## Test-Risk Guidance

Safe test patterns:

- Add failing tests before alias changes when behavior is expected to change.
- For every new package-owned alias, assert the selected `entrypoint_id`,
  `can_operate`, and whether `create_question_interrupt_step(...)` returns a
  step.
- For every new Q&A alias or prompt, assert that the intended Q&A wins before
  package-owned entrypoint aliases when the topic is privacy-sensitive or
  action-sensitive.
- Cover negative forms as well as location forms, for example "read the
  transcript" versus "where are Notes and Transcript".
- Keep answer-text assertions focused on boundary phrases only when needed,
  such as "does not read transcript text" or "does not start recording"; avoid
  broad snapshots that turn copy into the real contract.
- Re-run diagnostics that cover duplicate question aliases, duplicate Q&A
  prompts, Q&A alias overlap, and Q&A alias substring risk.
- Re-run focused question-routing tests for recording, notes/transcript,
  shared-screen content, chat/participant privacy, invite, share, reactions,
  raise hand, leave/end, participants, and network quality when aliases touch
  those concepts.
- Keep package alias counts and Q&A prompt counts updated only in assertions
  that intentionally track diagnostics output.
- If a new alias intentionally changes `can_operate`, document why the
  entrypoint is allowed to operate and include an interrupt-step assertion.

No-go test patterns:

- Do not relax `can_operate` for recording, transcript, notes, shared-content,
  invite, share, reactions, raise hand, leave, settings, or post-meeting
  artifact prompts just to make a new alias pass.
- Do not make tests assert broad semantic understanding, privacy safety, live
  acceptance, provider stability, or compliance.
- Do not add live RingCentral automation to prove a package alias change.
- Do not add provider, speech, virtual microphone, SAPI, Piper, or OpenAI calls
  to prove alias routing.
- Do not treat substring-risk diagnostics as noise. Review each reported
  substring and either keep it related/intentional or move the wording back to
  Q&A where it stays answer-only.
- Do not fix collisions by weakening diagnostics severity without proving the
  collision is benign and same-entrypoint.
- Do not add broad one-word aliases such as `record`, `summary`, `message`,
  `person`, `meeting`, `settings`, `more`, `content`, or `privacy` unless tests
  prove they do not steal Q&A-first or operable routes.

Recommended focused verification for implementation cycles:

```powershell
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_questions.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_diagnostics.py
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_cli.py::test_doctor_loads_profile_package_and_flow
.\.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo
git diff --check -- packages\ringcentral-video.yaml tests\unit\test_questions.py tests\unit\test_material_packages.py tests\unit\test_diagnostics.py tests\unit\test_cli.py
```

Do not run coverage-producing commands for an alias-only slice unless the user
explicitly asks. If `.coverage` is already dirty, leave it untouched.

## Go/No-Go

Go if the alias change:

- Adds curated, explicit aliases that map to already understood package content.
- Preserves Q&A-first behavior for privacy, recording, notes/transcript,
  shared-content, chat/participant privacy, and post-meeting artifact prompts.
- Preserves current operation boundaries for sensitive controls.
- Includes tests for `entrypoint_id`, `can_operate`, and interrupt-step
  eligibility wherever routing can change.
- Keeps doctor diagnostics meaningful and reviews any new overlap or substring
  report.
- Describes the work as deterministic package-routing coverage, not live
  acceptance or provider behavior.

No-go if the alias change:

- Expands operable actions without a deliberate product decision and regression
  tests.
- Lets a privacy, recording, transcript, notes, shared-content, or post-meeting
  artifact prompt bypass answer-only Q&A.
- Relies on broad semantic coverage, fuzzy intent, or one-word aliases without
  proving route and operation boundaries.
- Claims privacy compliance, consent correctness, artifact access, transcript
  reading, recording safety, provider readiness, or live RingCentral
  acceptance.
- Touches unrelated source, tests, README, profiles, existing docs, generated
  artifacts, or `.coverage` as part of the alias slice.

Recommended risk level is medium-high. Alias additions are small YAML or test
edits, but they sit directly on the route that decides whether a user question
is answer-only or can create an interrupt step. Treat every new alias as a
behavior change until tests prove otherwise.
