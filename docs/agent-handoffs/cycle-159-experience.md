# Cycle 159 Experience: Screen Sharing And Shared Content Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## What This Cycle Learned

- Screen-sharing and shared-content prompts sit on a live-meeting boundary.
  Starting or changing sharing can expose private content, while reading shared
  content can imply access to sensitive on-screen material.
- Action-shaped sharing prompts belong in Q&A safety guidance first. Prompts
  such as `Start sharing`, `Share my screen`, `Can you share my screen?`, or
  `Show my screen` should explain confirmation and privacy boundaries instead
  of routing directly to an operable toolbar path.
- Content-reading prompts also need answer-first behavior. Requests like
  `What is being shared?`, `Read the shared screen`, or `Summarize the shared
  content` should not imply AiPresenter can inspect meeting content unless a
  separate visible-content workflow has actually provided that evidence.
- This cycle reinforced that semantic routing quality matters as much as
  operability. A prompt can be non-operable and still be harmful if it lands on
  thin or misleading entrypoint copy.
- This is package, localization, and unit-test evidence only. It does not prove
  live RingCentral Video screen-sharing behavior, current shared-content state,
  permission dialogs, monitor/window picker state, or what participants can see.

## Q&A-First Sharing Boundary

- Use Q&A-first for sharing actions because the user may be asking for a
  privacy-sensitive live action, not just where a control is located.
- The safe answer should say that AiPresenter can explain where sharing controls
  are, but should not start sharing, select a window, expose a screen, or change
  share state without explicit confirmation and visible picker/preview handling.
- Keep exact action prompts narrow. Broad aliases such as `start`, `share`,
  `screen`, `show`, `present`, or `content` are too likely to steal unrelated
  meeting intents or future content-inspection flows.
- Preserve the difference between guidance and execution. Q&A text can describe
  the control and privacy risk; it must not claim the screen was shared, a
  picker was opened, an item was selected, or participants can see anything.
- If a future confirmed sharing workflow is built, it should be a separate
  product slice with explicit confirmation, source selection, preview/state
  verification, cancellation handling, and cleanup wording.

## Shared-Content Reading Prompts

- Treat content-reading prompts as safety-sensitive even when they sound like
  ordinary Q&A. The risk is overclaiming visual access to content that may not
  have been captured, parsed, or consented to.
- The preferred response shape is answer-only: explain that AiPresenter cannot
  read or summarize shared content from the meeting unless an explicit capture
  or provided context is available.
- Do not route content-reading prompts to generic screen-share entrypoint text.
  `What is being shared?` is not the same intent as `Where is Share screen?`.
- Avoid wording that implies the current shared-content state is known. The
  package can provide safety guidance; it cannot prove whether someone is
  currently sharing, what source is visible, or whether system audio is included.
- Keep future visible-content work separate from toolbar routing. If later
  cycles add OCR, screenshots, or meeting-content inspection, those features
  need their own consent and evidence model.

## Semantic Misroute Lessons

- Guard semantic misroutes like `Start sharing` routing to start-meeting or
  meeting-start entrypoints. Token overlap with `start` is plausible, but the
  intent is screen-sharing privacy, not beginning a meeting.
- Route-quality tests should assert the safety Q&A answer, not merely
  non-operability. A wrong related entrypoint with `can_operate is False` can
  still teach the wrong behavior.
- Thin fallback strings are regression signals for this slice. Prompts that ask
  to start, show, read, or summarize sharing should not return generic toolbar
  copy if the real issue is privacy and confirmation.
- Keep tone variants covered. Imperatives, polite questions, and terse command
  phrasing should preserve the same answer-first boundary.
- Higher-layer checks remain useful because package routing can be correct while
  a presenter/session layer accidentally queues or starts an interrupt step.

## Preserve Location Lookups

- Do not let the safety fix erase useful control discovery. Users should still
  be able to ask `Where is Share screen?` or `How do I find the sharing button?`
  and get the related entrypoint guidance.
- The intended split is:
  - action or content-reading wording -> Q&A answer, non-operable, no interrupt
  - location/control-discovery wording -> related toolbar entrypoint,
    non-operable, no interrupt
- Location answers should remain modest: describe where the control is or how to
  identify it, without claiming that sharing has started or content is visible.
- Preserve future location lookups by avoiding broad Q&A aliases that swallow
  every prompt containing `share`, `screen`, or `content`.
- Tests should keep action/content-reading cases beside location cases so future
  edits do not overcorrect in either direction.

## Localization And Count Hygiene

- Synchronize localization and diagnostic counts whenever Q&A prompts or answers
  are added. Exact English prompts may increase inventory even when localized
  entrypoint aliases stay unchanged.
- Update expected Q&A counts only after rerunning the relevant doctor or
  diagnostic command and confirming the new inventory is intentional.
- Localized sharing phrases can collapse several meanings: share the screen,
  start presenting, show content, inspect what is shared, or find the share
  control. Translate with intent boundaries, not word substitution.
- Keep localized action prompts Q&A-first unless a locale-specific review says a
  phrase is purely navigational.
- Console mojibake should not drive localization decisions. Use UTF-8-aware
  files/tests as the source of truth.

## Privacy And Safety Wording

- Safe wording: "Routes exact sharing-action prompts to answer-only screen-share
  privacy guidance."
- Safe wording: "AiPresenter can explain sharing controls, but should not start
  sharing or select a source without explicit confirmation and visible source
  verification."
- Safe wording: "Shared-content reading prompts do not imply AiPresenter can
  inspect or summarize the meeting screen without provided context or an
  explicit capture workflow."
- Safe wording: "Location questions still route to screen-sharing control
  discovery and remain non-operable."
- Avoid saying AiPresenter started sharing, opened a share picker, selected a
  screen/window/tab, read shared content, summarized visible content, confirmed
  someone is sharing, or verified what participants can see.

## Verification Lessons

- Focused tests should cover action prompts, content-reading prompts, semantic
  misroute prompts, and location lookups in the same slice.
- Assert that action/content-reading prompts produce the intended Q&A safety
  answer, have no operable entrypoint, and do not create a question interrupt
  step.
- Assert that location prompts still route to the expected sharing entrypoint,
  remain non-operable, and do not inherit privacy-action answer text.
- Include a regression for `Start sharing` specifically so it cannot drift to a
  start-meeting route through token overlap.
- Do not make tests pass by adding broad sharing aliases, weakening risky-word
  gating, adding `openSteps`, or collapsing action and location semantics.

## Candidate Next-Cycle Gaps

- Review `Share system audio` as the next likely boundary. It is adjacent to
  screen sharing but has its own privacy and meeting-audio risk profile.
- Add higher-layer presenter/session tests for sharing-action and shared-content
  reading prompts so safe package answers cannot become queued demos.
- Consider localized exact Q&A prompts for high-confidence sharing actions only
  after language-specific safety review.
- Design any future confirmed screen-sharing workflow as a separate slice with
  source selection, preview, system-audio state, cancellation, cleanup, and live
  acceptance evidence.
- Keep preserving location lookups as screen-sharing safety coverage expands.
