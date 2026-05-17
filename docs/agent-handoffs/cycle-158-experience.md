# Cycle 158 Experience: Reactions And Raise Hand Safety Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- Reactions and Raise hand are visible meeting signals. They are not as
  destructive as recording or ending a meeting, but they are still social,
  externally visible actions inside the live meeting.
- Action-shaped prompts should get Q&A safety guidance first. `Raise my hand`,
  `Lower my hand`, `Send a thumbs up`, `Send a reaction`,
  `React with thumbs up`, and `Can you raise my hand?` should not fall through
  to thin entrypoint copy.
- Location-shaped prompts should keep working as location lookups.
  `Where is Raise hand?` and `Where are Reactions?` should still route to their
  entrypoints, stay non-operable, and explain where the controls live.
- The user experience problem was subtle: the unsafe behavior was not an
  accidental click. It was action phrasing getting a generic control answer
  that sounded too ready to operate.
- This cycle is package and unit-test evidence only. It does not prove live
  RingCentral reaction-strip behavior, current hand state, participant
  visibility, or host/client UI state.

## Q&A-First Action Phrasing

- Treat visible meeting signal commands as safety questions, even when they are
  short imperative phrases rather than explicit questions.
- Exact Q&A prompts are the right tool for this slice because they preserve the
  visible-signal boundary without broadening entrypoint aliases.
- Avoid adding English entrypoint aliases such as `react`, `reaction`,
  `thumbs`, `hand`, `raise`, `lower`, or `send`. Those words are too broad and
  can steal future safety-sensitive phrasing.
- Keep the answer centered on consent and cleanup: AiPresenter can explain the
  controls, should not send a reaction or raise/lower a hand from these prompts,
  should close the reaction strip during exploration, and should lower the hand
  after any confirmed demonstration.
- Do not imply current hand state is known. `Lower my hand` is still an
  action-shaped request, not proof that a hand is currently raised.

## Preserve Location Lookups

- Do not make the safety fix erase useful navigation behavior. Users still need
  to ask where the visible-signal controls are.
- The desired split is:
  - action wording -> visible-signal Q&A answer, `entrypoint_id is None`,
    `can_operate is False`, no interrupt step
  - location wording -> related toolbar entrypoint, `can_operate is False`,
    no interrupt step
- This split helps the Presenter sound decisive without pretending a live
  meeting signal has been sent.
- Future localized work needs the same distinction. A short translated phrase
  may mean either "where is the control?" or "perform the action"; action-shaped
  phrasing should stay in Q&A unless a separate confirmed-action workflow is
  deliberately built.

## Red-Test Lesson

- Use red tests for subtle entrypoint fallback, not only for operability. Before
  this slice, `Lower my hand` and `React with thumbs up` could stay
  non-operable while still returning weak entrypoint text.
- The important regression is: these prompts must not return generic strings
  such as `Raise hand: Raise or lower hand to request attention.` or
  `Reactions: Send meeting reactions without interrupting speech.`
- Test assertions should prove the answer is the visible-signal safety Q&A,
  `entrypoint_id is None`, `can_operate is False`, and
  `create_question_interrupt_step(...) is None`.
- Keep location-question tests beside the action-prompt tests. They prevent a
  future overcorrection where all reaction/raise-hand wording becomes only a
  Q&A answer and users lose control discovery.
- Higher-layer controller/session tests remain useful for future cycles because
  package routing can be safe while a presenter layer accidentally queues an
  interrupt.

## Diagnostics And Count Hygiene

- The six exact English Q&A prompts intentionally increased Q&A inventory.
  Current doctor output reports `109` Q&A question prompts.
- Current doctor output also reports `157` package-owned aliases, `109` Q&A
  prompts with no unsafe package-owned alias overlaps, an existing substring
  `INFO` count of `11`, and overall `11 ok, 1 info, 0 warnings, 0 failed`.
- Count expectations in diagnostics and CLI tests should be updated from actual
  doctor output, not guessed from the number of prompts added.
- Localization completion did not need to change for this English exact-prompt
  slice. Current reports remain complete for Japanese and Chinese Q&A coverage:
  `13/13 Q&A questions` and `13/13 Q&A answers`.
- Avoid running broad coverage-producing commands for this narrow slice. If
  `.coverage` is dirty already, leave it alone.

## Privacy And Safety Wording

- Safe wording: "Routes exact English reaction and raise-hand action prompts to
  answer-only visible-signal safety guidance."
- Safe wording: "Reactions and raised hands are visible meeting signals and
  require explicit user intent before any live action."
- Safe wording: "Location questions still route to the Reactions and Raise hand
  toolbar entrypoints, but remain non-operable."
- Safe wording: "This is unit and package-routing evidence, not live
  RingCentral acceptance evidence."
- Avoid saying AiPresenter sent a thumbs-up, sent any reaction, raised the
  user's hand, lowered the user's hand, or verified the current hand state.
- Avoid saying the reaction strip was opened or closed unless a live demo or
  explicit acceptance pass actually verified that behavior.

## Verification Lessons

- The focused safety test should cover all six exact prompts:
  `Raise my hand`, `Lower my hand`, `Send a thumbs up`, `Send a reaction`,
  `React with thumbs up`, and `Can you raise my hand?`.
- The same verification should keep the location tests for
  `Where is Raise hand?` and `Where are Reactions?`.
- Diagnostics tests should assert the current `109` Q&A count and overlap
  behavior only after rerunning doctor.
- Use targeted commands with `--override-ini addopts= -p no:cacheprovider` for
  review cycles so the test run does not rewrite coverage state.
- Do not make tests pass by weakening risky-word gating, making the toolbar
  entrypoints operable, adding `openSteps`, or turning the exact prompts into
  broad aliases.

## Candidate Next-Cycle Gaps

- Add higher-layer presenter controller/session checks for the six exact prompts
  so action-shaped visible-signal questions cannot queue or start a demo.
- Consider localized exact Q&A prompts for reaction and raise-hand commands,
  but only after language-specific safety review. Do not translate these as
  broad entrypoint aliases.
- Review the existing `qa alias substring risk` `INFO` list and document which
  items are expected Q&A-first cases versus true future cleanup candidates.
- Design any confirmed-action reaction or raise-hand workflow as a separate
  product slice with explicit confirmation, visible target inspection, cleanup,
  and live acceptance evidence.
- Keep expanding the same pattern to other meeting-visible but non-destructive
  controls where command phrasing can otherwise fall back to thin location text.
