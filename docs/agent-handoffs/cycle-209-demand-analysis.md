# Cycle 209 Demand Analysis

Date: 2026-05-17
Cycle: 209
Role: Demand analysis subagent

## Recommendation

Add a narrow active runtime presenter skill for RingCentral onboarding and
training. The skill should make AiPresenter better at teaching first-time users
without changing package routes, acceptance evidence, or language support.

## User Value

- Turns RingCentral Video demos into repeatable learner-oriented walkthroughs.
- Complements the Instructor tone with concrete product-teaching behavior.
- Gives future cycles a runtime skill pattern that can be tested through
  profile loading and provider prompt assertions.

## Non-Goals

- No package route, flow, alias, Q&A, locator, or acceptance-evidence changes.
- No claim that French is runtime-supported.
- No replacement for `app-director`, `live-explainer`, or
  `ringcentral-safety`.
- No live RingCentral acceptance claim.

## Acceptance Criteria

- `ringcentral-onboarding` is present in repo and packaged skill directories.
- Every active RingCentral profile loads it after `live-explainer`.
- `ringcentral-safety` remains the final skill in the active prompt order.
- Presenter context and provider prompt tests assert that the skill is loaded.
