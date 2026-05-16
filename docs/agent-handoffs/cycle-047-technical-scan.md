# Cycle 047 Technical Scan

## Candidate A: Meeting-Info Privacy Gate

The RingCentral package and privacy docs already treat meeting IDs, links, dial-in details, host identity, and encryption details as sensitive. The runtime question safety gate currently blocks obvious side-effect routes by risky words and missing `openSteps`, but `ringcentral.video.top.meeting-info` still has executable `openSteps` and lacks risky words. That makes question-triggered operation permission too permissive for a sensitive popover.

### Proposed Files

- `src/ai_presenter/runtime/questions.py`: add a small explicit explain-only entrypoint set for sensitive question-triggered surfaces.
- `tests/unit/test_questions.py`: add English and Chinese meeting-info safety tests.

### TDD Plan

1. Add failing tests that show meeting-info questions match the entrypoint but return `can_operate is False`.
2. Add the explicit explain-only entrypoint guard in `_can_operate`.
3. Re-run focused question tests and adjacent safety tests.

## Candidate B: Q&A Exact-Match Index

The package model already precomputes candidates, but `_match_qa()` still scans candidates for exact matches. A future performance cycle can add a read-only normalized Q&A index to `MaterialPackage` and use it before fragment/overlap scans.

## Chosen Slice

Cycle 047 chooses Candidate A because it closes a privacy boundary in live question handling. Candidate B remains a good low-risk performance candidate for a later cycle.

## Risks

- The guard should only affect question-triggered `can_operate`; it should not remove package routes, demo definitions, or executable metadata.
- Existing non-sensitive operable routes such as Network quality should remain operable if their open steps are safe.
- Invite/share/recording/leave safety tests should remain unchanged.

