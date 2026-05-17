# Cycle 202 Lessons: RingCentral Acceptance Evidence

## Reusable Lesson

For RingCentral evidence docs, separate logged evidence from promotion evidence. Failed, blocked, incomplete, skipped, automated-only, dry-run, `doctor`, and read-only observation records are valid history, but they must not justify `Accepted`.

`Accepted` should require all of:

- Dated live/manual route run
- Outcome is `pass`
- Current build and route under test are identified
- Cleanup/restoration notes are complete
- Privacy/redaction notes are complete
- Promotion rationale is explicit

## Prompt Pattern

Review the RingCentral evidence docs for promotion-boundary drift. Confirm that non-passing or non-live/manual evidence may be logged but cannot promote a route to `Accepted`. Check templates, upgrade rules, and evidence-index references for any wording that lets automated, dry-run, `doctor`, read-only, blocked, failed, incomplete, or skipped evidence imply acceptance. Preserve useful history while requiring dated passing live/manual route evidence for promotion.

## Test Lesson

The RED/GREEN string-guard test worked well because the risk was documentation wording drift, not runtime behavior. Exact required strings made the acceptance contract visible and regression-resistant. Keep these tests narrow and canonical: assert the promotion rule phrases that must exist, and assert against misleading phrases that would blur automated/read-only evidence into live acceptance.

## Follow-Up Candidates

- Add a guard that `evidence-index.md` cannot move RingCentral routes to `Accepted` unless `acceptance-runs.md` contains a dated passing live/manual entry.
- Consider a small taxonomy table for `pass`, `fail`, `blocked`, `incomplete`, `skipped`, `automated-only`, `dry-run`, `doctor`, and `read-only`.
- Keep `.coverage` uncommitted unless a future cycle intentionally changes coverage artifact policy.
- Add an example failed or blocked run entry showing useful logging without promotion.
- Add a privacy/cleanup checklist snippet shared by acceptance-run templates and validation checklist docs.
