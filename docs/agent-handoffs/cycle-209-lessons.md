# Cycle 209 Lessons

Date: 2026-05-17
Cycle: 209
Role: Lessons and carry-forward notes

## What Changed

- Added `ringcentral-onboarding` as an active runtime presenter skill.
- Loaded the skill in every RingCentral profile after `live-explainer` and
  before `ringcentral-safety`.
- Mirrored the skill into package data and locked parity with unit tests.
- Added provider prompt assertions so runtime narration receives the onboarding
  guidance before the final safety guidance.

## What To Preserve

- `ringcentral-safety` should remain last in RingCentral skill order.
- Runtime presenter skills are active behavior changes; update root profiles,
  packaged profiles, provider prompt tests, and package-copy parity together.
- Package-local French text still does not imply `--language fr` runtime
  support.

## Follow-Up Ideas

- Add a learner-progress rubric for RingCentral onboarding if future demos need
  multi-step training checkpoints.
- Consider a package-local onboarding Q&A cluster only after observing repeated
  user questions in live or manual RingCentral practice.
