# Cycle 048 Demand Analysis

## Recommended Slice

Precompute exact Q&A question lookup for `MaterialPackage` and use it before the runtime fragment and token-overlap scans.

## User Value

AiPresenter keeps gaining localized Q&A entries. Exact question matches are common in scripted demos, controller prompts, and regression tests, but the runtime currently scans every Q&A candidate before finding an exact match. A normalized exact-match index reduces repeated work during live controller use while keeping answer behavior deterministic.

## Acceptance Criteria

- `MaterialPackage` builds a runtime-only normalized Q&A index from English and localized Q&A questions.
- `runtime.questions._match_qa()` checks that index before fragment and overlap scans.
- Duplicate normalized questions preserve the current first-declared winner.
- Fragment matching, token overlap, alias fallback, entrypoint fallback, localized answers, tone rendering, and `can_operate` behavior remain unchanged.
- The public index is read-only and does not appear in `model_dump(by_alias=True)`.
- `with_demo_flow()` rebuilds the index so copied package objects point to copied Q&A objects.

## Out Of Scope

- No semantic search or embeddings.
- No trie or global cache.
- No package YAML or Q&A content changes.
- No answer text changes.
- No route safety policy changes.
- No wall-clock benchmark as a pass/fail gate.

