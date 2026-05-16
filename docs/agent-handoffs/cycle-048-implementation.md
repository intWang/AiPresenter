# Cycle 048 Implementation

## Changes

- Added `MaterialPackage._qa_questions_by_normalized` as a runtime-only private index.
- Added `MaterialPackage.qa_questions_by_normalized` as a read-only mapping.
- Built the index from precomputed Q&A candidates using first-match preservation.
- Updated `_match_qa()` to fast-path exact Q&A matches through the index.
- Kept fragment and token-overlap matching unchanged.

## TDD Evidence

Initial red run:

- `test_material_package_exposes_read_only_qa_question_index` failed because `qa_questions_by_normalized` did not exist.
- `test_qa_question_index_keeps_first_duplicate_match` failed for the same missing property.
- `test_with_demo_flow_rebuilds_runtime_indexes_for_appended_flow` failed on the new index assertion.
- `test_exact_qa_match_uses_precomputed_question_index` failed because clearing `_qa_question_candidates` made the host-controls exact question fall back to the Participants entrypoint.

Post-fix focused run:

- The same five tests passed.

## Design Choice

The index maps normalized question text directly to the first matching `QuestionAnswer`. A tuple-of-candidates design would preserve more duplicate detail, but the runtime contract only needs the first exact answer and duplicate diagnostics are out of scope for this performance slice.

