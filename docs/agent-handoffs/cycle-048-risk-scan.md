# Cycle 048 Risk Scan

## Findings

- The exact index should replace only `normalized_question == candidate.normalized_question`; fragment and overlap scans should continue over `qa_question_candidates`.
- Duplicate normalized questions must preserve source order. `setdefault` keeps the first declared Q&A, matching the previous linear scan behavior.
- The index should use `QuestionAnswerMatchCandidate.normalized_question` rather than re-normalizing raw strings, so authored whitespace behavior does not drift.
- `MaterialPackage` remains mutable after validation, but this matches the repo's existing runtime-index contract. Do not add new copy paths or mutation APIs in this slice.
- The public property should return `MappingProxyType`, and the private attr must remain absent from model dumps.
- The index must include localized questions, not only English primary questions.

## Recommended Regression Coverage

- English and localized exact keys resolve through the index.
- Duplicate exact keys keep the first item.
- `with_demo_flow()` points index entries to copied Q&A objects.
- Cycle 046 regressions stay green: `recording` safety Q&A, `participants` generic route, and host-controls answer-only route.
- Cycle 047 regressions stay green: meeting-info questions remain explain-only.

