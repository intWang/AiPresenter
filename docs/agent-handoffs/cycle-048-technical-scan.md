# Cycle 048 Technical Scan

## Current State

`MaterialPackage` already precomputes runtime-only structures for entrypoints, demo flows, package-owned aliases, Q&A candidates, and entrypoint match candidates. `_match_qa()` still performs a linear scan to find exact normalized Q&A question matches before fragment and token-overlap matching.

## Implementation Plan

- Add `_qa_questions_by_normalized` as a `PrivateAttr` on `MaterialPackage`.
- Build it from existing `QuestionAnswerMatchCandidate.normalized_question` values to avoid normalization drift.
- Preserve first-match behavior with `setdefault`.
- Expose it through a `MappingProxyType` property.
- In `_match_qa()`, use the index only for exact matches, then keep the existing fragment and overlap scans unchanged.

## Tests

- Read-only index contains English and localized question keys.
- Duplicate normalized questions keep the first Q&A item.
- `with_demo_flow()` rebuilds the index against copied Q&A objects.
- Runtime indexes do not leak into `model_dump(by_alias=True)`.
- Exact Q&A matching works even when candidate scans are unavailable.

## Risk Notes

The index is an exact-match optimization only. It must not replace fragment matching or bypass `_can_match_qa_fragment()`, because Cycle 046 relies on those safeguards for `participants`, host-control, and recording-safety behavior.

