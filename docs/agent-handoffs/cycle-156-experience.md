# Cycle 156 Experience: Recording Exact Q&A Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- The five exact English recording prompts belong in Q&A, not operation aliases:
  `Record this meeting`, `Start recording`, `Stop recording`,
  `Are we recording?`, and `Recording status`.
- Q&A is the right surface because these prompts are safety-sensitive. Three
  sound like live start/stop commands, and two ask for meeting recording state.
  The useful behavior is a clear recording-safety answer, not a route that
  feels ready to click `Start recording`.
- The existing safety Q&A item already had the right boundary:
  `How do I handle meeting recording safely?` explains that recording changes
  meeting state and requires explicit confirmation, role permission, and
  participant consent or meeting agreement.
- Adding exact English `localizedQuestions.en` prompts to that Q&A item lets
  Q&A-first matching win before entrypoint-label fallback. That keeps the route
  associated with `ringcentral.video.more.recording` while returning the safety
  answer instead of generic `Start recording:` text.
- The operation surface did not need to change. `ringcentral.video.more.recording`
  remains explain-only, has no executable open steps in this slice, stays
  non-operable, and should not create a question interrupt step.

## Q&A Over Operation Aliases

- Use Q&A prompts when the user wording asks for policy, safety, status,
  consent, permission, or a state-changing action that the assistant must not
  perform immediately.
- Use operation aliases only for narrow, location/control wording where routing
  to an entrypoint is the intended answer shape and the alias will not steal
  safety, status, or artifact questions.
- Recording is not like the Cycle 155 `microphone button` alias. `microphone
  button` was a visual-location phrase for an existing toolbar control; these
  recording prompts include imperative and status-shaped requests.
- Broad English aliases such as `record`, `recording`, `meeting recording`,
  `recorded`, `status`, or `meeting status` would be harder to reason about.
  They can capture post-meeting artifact, transcript, notes, consent, or status
  questions that should stay answer-only.
- Duplicating the same normalized text across Q&A prompts and entrypoint aliases
  should be avoided unless there is a very deliberate reason. Q&A-first routing
  can protect behavior, but mixed ownership makes diagnostics and future edits
  less clear.

## Diagnostic Count Hygiene

- This cycle intentionally changes Q&A prompt inventory, not operation alias
  inventory.
- The RingCentral Q&A prompt diagnostics move from `87` to `92` because five
  exact English Q&A prompts were authored.
- The package-owned question alias count should stay at `157`. If that count
  changes during this slice, it likely means someone added operation aliases or
  touched unrelated inventory.
- Count updates are evidence, not cleanup. Before changing expectations, prove
  whether the new number comes from an intentional authored prompt or alias.
- Keep duplicate, overlap, and substring-risk checks meaningful after a count
  bump. Do not relax them just because the expected total changed.
- Use `--no-cov` for focused verification when possible so this kind of package
  and test slice does not rewrite `.coverage`.

## Privacy And Safety Wording

- Safe wording: "Routes exact English recording prompts to answer-only
  recording safety guidance."
- Safe wording: "Recording changes meeting state and requires explicit
  confirmation, role permission, and participant consent or meeting agreement
  before any real action."
- Safe wording: "The covered prompts remain non-operable and create no question
  interrupt step."
- Safe wording: "This is package-routing and unit-test evidence only; it does
  not prove live RingCentral Video recording behavior."
- Avoid saying AiPresenter started, stopped, toggled, enabled, disabled,
  verified, or confirmed recording.
- Avoid saying the meeting is recording, is not recording, or has a known
  recording status unless a separate visible-state inspection feature has
  actually verified that UI state.
- Avoid implying host permission, admin policy, organization consent,
  participant consent, legal permission, or meeting agreement has been checked.
- Avoid promising access to post-meeting recordings, transcripts, summaries,
  insights, chat, participants, or shared-screen content.

## Verification Lessons

- The key behavior test should cover every exact prompt and assert:
  `entrypoint_id == "ringcentral.video.more.recording"`,
  `can_operate is False`, recording-safety answer text is present,
  generic `Start recording:` fallback text is absent, and
  `create_question_interrupt_step(package, response) is None`.
- Diagnostics and CLI doctor expectations should move only for the Q&A prompt
  count: `92 Q&A question prompts have no cross-item duplicates` and
  `92 Q&A question prompts have no unsafe package-owned alias overlaps`.
- Keep the package/test diff narrow. No runtime matcher, provider, profile,
  README, acceptance evidence, or live RingCentral automation should be needed
  for exact Q&A prompt coverage.

## Candidate Next-Cycle Gaps

- Recording status could eventually get a visible-state inspection design, but
  that should be a separate product decision with explicit UI evidence and
  tests. It should not be inferred from the Q&A route.
- Stop-recording wording may deserve more specific copy later. It should still
  avoid claiming a recording is active or that AiPresenter can stop it without a
  confirmed operation workflow.
- Post-meeting recording artifacts remain separate from in-meeting recording
  controls. Questions about recording files, transcripts, summaries, and
  insights should stay in their own safety and permission lane.
- Localized exact prompts for recording can be evaluated later, but should not
  be added mechanically. Each language should preserve the same no-operation,
  no-state-claim boundary.
- A future confirmed-action recording workflow would need new requirements:
  explicit user confirmation, role/permission handling, participant consent or
  meeting-agreement language, visible UI validation, and live acceptance
  evidence. It should not piggyback on this Q&A prompt slice.
