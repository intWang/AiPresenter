# Cycle 203 Lessons: Accepted Evidence Traceability

## Reusable Lesson

For evidence promotion, do not search whole free-form sections for route IDs. Promotion guards should require explicit tested-route fields, such as `Entrypoint IDs tested`, so follow-up notes or failure notes cannot accidentally validate a different route.

## Prompt Pattern

When reviewing RingCentral acceptance guards, ask: "Can a target route be marked accepted if it appears only in follow-up, failure, privacy, or notes text for another passing run?" If yes, the guard is too broad. Require explicit tested-route fields plus outcome, promotion eligibility, rationale, recovery/cleanup, and privacy notes in the same dated manual acceptance section.

## Test Lesson

A positive synthetic acceptance fixture is not enough. Pair it with a false-positive fixture where another route passes and the target route appears only in follow-up. That regression proves the parser is checking the authoritative field, not incidental text.

## Follow-Up Candidates

- Wire `acceptance_text` into CLI/catalog evidence validation paths where the docs are available.
- Add a small parser helper test for multiple `Entrypoint IDs tested` values once a real multi-route accepted run exists.
- Consider rendering the promotion-guard requirements in generated validation target output without adding acceptance-claim wording to draft templates.
