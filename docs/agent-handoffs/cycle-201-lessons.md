# Cycle 201 Lessons: Failed Runs Are Evidence, Not Acceptance

Date: 2026-05-17

## What Changed

Cycle 201 added a `Status Vocabulary Map` to the RingCentral Video evidence
index and locked it with a docs-contract test.

## Reusable Lesson

A failed live/manual run is still valuable evidence, but it must not upgrade a
route to `Accepted`. `Accepted` requires a dated passing acceptance record with
cleanup and privacy notes.

## Guardrails

- Keep `Do Not Execute Yet` as checklist procedure, not an evidence level.
- Keep `Repo-tested` as local repository confidence only.
- Keep `Observed` as dated environment observation, not click/cleanup proof.
- Keep `Blocked` non-executable until the blocking risk is resolved.
- Record failed runs in `acceptance-runs.md`, but do not raise evidence level to
  `Accepted`.
- Keep `.coverage` out of staged cycle commits.

## Next-Cycle Candidates

- Add a generated status summary for `validation-targets` that counts evidence
  levels without changing acceptance semantics.
- Tighten `acceptance-runs.md` template language around pass/fail outcomes and
  evidence-level updates.
- Continue converting RingCentral evidence lessons into small docs-contract
  tests near the source docs.
