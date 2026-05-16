# Cycle 050 Risk Scan

## Findings

- Q&A has no explicit `explainOnly` field. The safest answer-only content path is to omit `relatedEntrypointIds`.
- `ringcentral.video.more.notes` has executable `openSteps`, so linking the new Q&A to Notes could queue a demo.
- Generic translation/caption terms can shadow Settings or Notes questions if they are too broad. Exact English and Chinese prompts should be tested.
- Localization and diagnostics counts are intentionally brittle and must be updated.

## Regression Coverage

- New captions/transcription/translation questions stay `entrypoint_id=None` and `can_operate=False`.
- Existing `notes` and `settings` questions should keep their current entrypoint behavior.
- Meeting-info privacy and host-control answer-only behavior should stay green through the broader question suite.
