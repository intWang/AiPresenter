# Cycle 158 Demand Analysis: Reactions and Raise Hand Exact Prompts

Date: 2026-05-17
Repository: `C:\Users\rcadmin\Documents\Repos\AiPresenter`

## Decision

Recommendation: make the next smallest high-value RingCentral Video increment
an exact English visible-signal prompt slice for Reactions and Raise hand.

Add or tighten answer-only coverage for these user prompts:

- `Raise my hand`
- `Lower my hand`
- `Send a thumbs up`
- `Send a reaction`
- `React with thumbs up`
- `Can you raise my hand?`

All six prompts should return visible-meeting-signal safety guidance, stay
non-operable, and create no question interrupt step. This is the right next
slice because Cycle 156 handled recording exact prompts, Cycle 157 handled
leave/end exact prompts, and the remaining high-value visible meeting signals
are reaction sending and hand raising/lowering. These are less destructive than
recording or ending a meeting, but still externally visible to other meeting
participants.

## Current Evidence

`ringcentral.video.toolbar.react` and `ringcentral.video.toolbar.raise-hand`
already exist in `packages/ringcentral-video.yaml`.

- `ringcentral.video.toolbar.react` has `openSteps` that click `React`, with
  `cleanup: escape`, and presenter notes say observed reactions include heart,
  thumbs up, celebration, clap, smile, and Be right back.
- `ringcentral.video.toolbar.raise-hand` has `openSteps` that click `Raise
  hand`, an alternate target for removing raise hand, and `cleanup: toggle`.
- The package already has a safety Q&A item:
  `Can AiPresenter send a reaction or raise my hand safely?`
- That answer says Reactions and Raise hand are visible meeting signals,
  AiPresenter can explain where they are, should not send a reaction or raise a
  hand unless the user explicitly asks, should close the reaction strip without
  sending anything during exploration, and should lower the hand after a
  confirmed demonstration.

Read-only routing probes for the requested exact English prompts show the gap
is consistency and answer quality:

| Prompt | Current behavior |
| --- | --- |
| `Raise my hand` | Already returns the visible-signal safety Q&A; non-operable; no interrupt. |
| `Send a thumbs up` | Already returns the visible-signal safety Q&A; non-operable; no interrupt. |
| `Send a reaction` | Already returns the visible-signal safety Q&A; non-operable; no interrupt. |
| `Can you raise my hand?` | Already returns the visible-signal safety Q&A; non-operable; no interrupt. |
| `Lower my hand` | Routes to `ringcentral.video.toolbar.raise-hand` and returns thin entrypoint text: `Raise hand: Raise or lower hand to request attention.` |
| `React with thumbs up` | Routes to `ringcentral.video.toolbar.react` and returns thin entrypoint text: `Reactions: Send meeting reactions without interrupting speech.` |

The current results are non-operable, which is good. The missed user need is
that action-shaped visible-signal prompts should get the safety answer, not
thin control text that sounds like ordinary location help.

## Why It Matters

Reactions and Raise hand are live meeting signals. They are not destructive in
the same way as recording or ending a meeting, but they are visible to other
participants and can alter the social state of the meeting. A user may issue
these as terse commands while presenting, especially:

- asking to raise a hand to request attention,
- asking to lower a raised hand after being called on,
- asking to send a thumbs-up reaction,
- asking to send a generic reaction.

AiPresenter should recognize the intent immediately, but this cycle should not
turn these prompts into executable meeting actions. The user need is reliable
answer-only guidance that states the boundary clearly and preserves the
existing demo cleanup expectations.

## Recommended Scope

Keep this as a package/test-only Q&A increment.

- Add exact English Q&A aliases to the existing visible-signal safety Q&A item,
  or use an equally narrow package-owned answer-only mechanism if the
  implementation has changed by the time this is picked up.
- Cover exactly the six prompts listed in this document.
- Route all six prompts to the visible-signal safety answer.
- Keep every response `can_operate is False`.
- Ensure `create_question_interrupt_step(package, response) is None` for every
  prompt.
- Preserve the existing entrypoint behavior for location-style questions such
  as `Where is Raise hand?` and `Where are Reactions?`.
- Preserve `ringcentral.video.toolbar.react` and
  `ringcentral.video.toolbar.raise-hand` demo cleanup behavior for explicit
  guided demos.
- Update diagnostics or count expectations only if the authored Q&A alias
  inventory intentionally changes.

No runtime matcher, provider, profile, README, runbook, acceptance-evidence, or
live RingCentral validation change should be necessary.

## Exact User Prompts

Hand-toggle prompts:

- `Raise my hand`
- `Lower my hand`
- `Can you raise my hand?`

Reaction prompts:

- `Send a thumbs up`
- `Send a reaction`
- `React with thumbs up`

These should be tested as exact English prompts. Keep authored coverage narrow;
normalization can handle case or punctuation if it already does so, but this
slice should not add broad aliases.

## Expected Behavior

For `Raise my hand` and `Can you raise my hand?`:

- AiPresenter should answer with visible-signal safety guidance.
- It should not click `Raise hand`.
- It should not claim the hand is raised.
- It should explain that a real hand raise should require explicit user intent
  and that a confirmed demonstration should be cleaned up afterward.

For `Lower my hand`:

- AiPresenter should not click the toggle or assume the hand is currently
  raised.
- It should answer with the same visible-signal safety guidance instead of thin
  entrypoint text.
- It should avoid claiming the hand was lowered or that the current hand state
  was verified.

For `Send a thumbs up`, `Send a reaction`, and `React with thumbs up`:

- AiPresenter should answer with visible-signal safety guidance.
- It should not open the reaction strip as a question response.
- It should not click thumbs up or any other reaction.
- It should not claim a reaction was sent.
- It should explain that exploration should close the reaction strip without
  sending anything.

## What To Avoid

- Do not make Reactions or Raise hand operable from these question prompts.
- Do not add or change `openSteps` for this slice.
- Do not click `React`, `Raise hand`, `thumbs up`, heart, celebration, clap,
  smile, Be right back, remove raise hand, or any reaction-strip item.
- Do not claim a reaction was sent, a hand was raised, or a hand was lowered.
- Do not claim visible hand or reaction state has been verified.
- Do not leave a hand raised after any demo.
- Do not leave the reaction strip open after an exploratory demo.
- Do not add broad aliases such as `react`, `reaction`, `thumbs`, `hand`,
  `raise`, `lower`, `send`, or `signal`.
- Do not combine this with recording, Notes, Transcript, captions, leave/end,
  participants, host controls, chat, share, microphone, background, settings,
  runtime matcher changes, or acceptance work.
- Do not touch `.coverage` or unrelated dirty files.

## Implementation Handoff Prompt

```text
Cycle158 implementation task. You are not alone in the repo; do not revert
other workers' edits and do not touch `.coverage` or unrelated dirty files.

Repository: C:\Users\rcadmin\Documents\Repos\AiPresenter

Goal: implement the next smallest high-value RingCentral Video user-need gap:
exact English Reactions/Raise hand visible-signal prompts that return safe
answer-only guidance without sending reactions or toggling the user's hand.

Read first:
- docs/agent-handoffs/cycle-158-demand-analysis.md
- packages/ringcentral-video.yaml around
  `ringcentral.video.toolbar.react`,
  `ringcentral.video.toolbar.raise-hand`, and the Q&A item
  `Can AiPresenter send a reaction or raise my hand safely?`
- tests/unit/test_questions.py around existing reaction/raise-hand safety
  tests and location-question tests
- tests/unit/test_diagnostics.py and tests/unit/test_cli.py only if Q&A prompt
  or alias count assertions need updates

Scope:
- Package/test-only change.
- Cover exactly these English prompts: `Raise my hand`, `Lower my hand`,
  `Send a thumbs up`, `Send a reaction`, `React with thumbs up`, and
  `Can you raise my hand?`.
- Prefer adding exact English aliases to the existing visible-signal safety
  Q&A item, unless the package model requires an equally narrow canonical Q&A
  addition.
- Route all covered prompts to the visible-signal safety answer.
- Keep responses non-operable and ensure no question interrupt step is created.
- Preserve location questions such as `Where is Raise hand?` and
  `Where are Reactions?`.
- Preserve existing explicit-demo cleanup behavior for the React strip and the
  Raise hand toggle.

Do not:
- Edit runtime matcher source, package models, session interrupt logic,
  providers, profiles, README, runbooks, existing handoff docs, or acceptance
  evidence.
- Make Reactions or Raise hand operable from these question prompts.
- Add or change `openSteps`.
- Click or queue `React`, `Raise hand`, thumbs up, any reaction item, or remove
  raise hand from these question prompts.
- Claim a reaction was sent, a hand was raised, a hand was lowered, or visible
  signal state has been verified.
- Add broad aliases such as `react`, `reaction`, `thumbs`, `hand`, `raise`,
  `lower`, `send`, or `signal`.
- Combine this with recording, Notes, Transcript, captions, leave/end,
  participants, host controls, chat, share, microphone, background, settings,
  runtime matcher changes, or acceptance work.
- Touch `.coverage`.

Acceptance:
- `Raise my hand`, `Lower my hand`, `Send a thumbs up`, `Send a reaction`,
  `React with thumbs up`, and `Can you raise my hand?` all return the
  visible-signal safety answer.
- Each response keeps `can_operate is False`.
- `create_question_interrupt_step(package, response) is None` for each prompt.
- `Lower my hand` no longer returns thin `ringcentral.video.toolbar.raise-hand`
  entrypoint text.
- `React with thumbs up` no longer returns thin
  `ringcentral.video.toolbar.react` entrypoint text.
- No response claims a live reaction or hand-state action happened.
- Existing location-question behavior and explicit-demo cleanup behavior are
  preserved.
- Diagnostics remain green, with count expectations updated only for the exact
  authored Q&A inventory change.
- Final diff excludes `.coverage`, runtime source, profiles, README,
  acceptance evidence, and unrelated tests.
```
