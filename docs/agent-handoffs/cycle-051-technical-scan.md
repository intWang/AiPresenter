# Cycle 051 Technical Scan

## Selected Slice

Implement `qa alias overlap` inside package diagnostics.

## Current Touchpoints

- `MaterialPackage.qa_question_candidates` exposes normalized Q&A prompts and item identity.
- `MaterialPackage.entrypoint_question_aliases` exposes normalized aliases, languages, and entrypoint IDs.
- `diagnose_configuration()` already appends package checks through `_diagnose_material_package()`.
- Runtime matching intentionally checks Q&A before entrypoint aliases and should not change in this cycle.

## Implementation Shape

- Build aliases by `normalized_alias`.
- Group Q&A candidates by `(normalized_question, id(item))` so duplicate prompts inside the same Q&A item do not create repeated warnings.
- For each exact overlap, compare alias entrypoint IDs with the Q&A item's `related_entrypoint_ids`.
- Warn only when one or more alias entrypoints are not represented by the Q&A related IDs.
- Report OK with the current Q&A prompt count when no unsafe overlaps exist.

## Alternative Deferred Slice

Normalize Q&A prompt candidates with `strip().casefold()`, skip blank prompts, and guard blank exact lookups. That remains a strong Cycle 052 candidate because it compounds the exact Q&A index and duplicate Q&A diagnostics.

## Risks

- A noisy diagnostic would erode trust in doctor, so this cycle uses exact normalized overlap only.
- Same-entrypoint Q&A/alias overlap must stay allowed for intentional safety Q&A such as recording.
