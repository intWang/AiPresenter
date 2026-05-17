# Cycle 189 Technical Development: Acceptance Draft Redaction Checklist

Date: 2026-05-17

## Files Changed

- `src/ai_presenter/acceptance/manual_record.py`
  - Adds a fixed `Evidence Redaction Checklist` section to every manual acceptance draft.
- `tests/unit/test_acceptance_manual_record.py`
  - Adds coverage proving the generated draft includes the redaction checklist while preserving
    draft-only boundaries.
- `docs/runbooks/ringcentral-manual-acceptance.md`
  - Points operators to the redaction checklist before collecting evidence.
- `docs/knowledge/ringcentral-video/acceptance-runs.md`
  - Mirrors the checklist in the reusable manual acceptance template.

## Behavior

No RingCentral actions, package routes, aliases, localization, locator confidence, or runtime
controller behavior changed. The only product behavior change is generated draft text from
`acceptance-draft`.

## Redaction Checklist Content

- Prefer UIA/window metadata and allowlisted product-control labels before screenshots.
- Capture screenshots only with a clear verification need and privacy review path.
- Redact or omit private meeting content and private environment details.
- Name only sanitized artifacts in `Evidence files`.
- State what was redacted or intentionally not captured in `Privacy notes`.
