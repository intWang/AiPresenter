# Cycle 207 Demand Analysis

Date: 2026-05-17
Cycle: 207
Role: Demand analysis subagent

## Recommended Slice

Add a canonical `instructor` presenter tone as a runtime-only voice expansion.
This gives AiPresenter a clearer mode for onboarding, training, and product
walkthrough narration without changing RingCentral Video routing or permissions.

## User Value

- Operators can select a teaching-oriented tone for demos and enablement.
- The tone is distinct from `coach` by focusing on context-setting and
  instructional pacing instead of encouragement.
- The public `voices` catalog and controller label make the option discoverable.

## Non-Goals

- No RingCentral Video package YAML changes.
- No new entrypoints, Q&A, locators, demo steps, or acceptance evidence.
- No changes to `entrypoint_id`, `can_operate`, `questionPolicy`, Q&A-first
  matching, or interrupt creation.
- No persistent tone mutation from chat prompts.
- No speech provider or live acceptance claim.

## Acceptance Criteria

- `PresenterVoiceSettings(tone="instructor")` normalizes to `instructor`.
- `trainer`, `training`, `teacher`, and `tutorial` normalize to `instructor`.
- English dynamic text uses a short instructor prefix.
- Chinese dynamic text uses a native instructor prefix and keeps SAPI rate `0`.
- Japanese and Spanish localized text do not receive English prefixes.
- `voices` and controller labels expose `Instructor`.
- RingCentral sensitive route parity covers `instructor` and `tutorial`.

## Risk Notes

Keep aliases style-only. Do not add `tutorial` or `training` to package aliases,
because those words could otherwise be mistaken for product routes or training
workflow commands.
