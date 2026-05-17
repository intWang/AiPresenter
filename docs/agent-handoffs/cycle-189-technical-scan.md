# Cycle 189 Technical Scan: Evidence Redaction Gap

Date: 2026-05-17

## Findings

- Existing docs already preserve evidence-state boundaries: runbook checkboxes are not proof,
  `Accepted` requires a dated manual/live record, and read-only observation does not prove
  click or cleanup behavior.
- The gap is narrower: manual evidence capture has privacy guidance, but not a reusable
  redaction checklist.
- `acceptance-runs.md` had `Evidence files` and `Privacy notes` fields, while
  `privacy-matrix.md` already defined the capture policy to redact or omit sensitive meeting
  content.
- `acceptance-draft` repeated a generic privacy reminder, but did not structure allowed
  evidence, screenshot policy, raw artifact handling, or privacy-note wording.

## Recommended Implementation

- Add an `Evidence Redaction Checklist` section to
  `src/ai_presenter/acceptance/manual_record.py`.
- Mirror the same checklist in
  `docs/knowledge/ringcentral-video/acceptance-runs.md`.
- Add runbook guidance before live validation steps.
- Keep the change template-only: no runtime automation, no live route validation, and no
  package YAML updates.

## Suggested Checks

- Focused acceptance draft tests.
- Knowledge-doc evidence-boundary tests.
- CLI smoke for `acceptance-draft`.
- Full repository verification before commit.
