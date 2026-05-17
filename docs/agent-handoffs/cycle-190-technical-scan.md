# Cycle 190 Technical Scan: Validation Targets Output

Date: 2026-05-17

## Flow

- `src/ai_presenter/cli.py` loads the package, checklist, and evidence index for
  `validation-targets`.
- `src/ai_presenter/acceptance/validation_targets.py::render_validation_target_lines`
  owns the header and target output.
- `_render_target_block` already suppresses draft commands for blocked routes.
- `acceptance-draft` already emits the full `Evidence Redaction Checklist`.

## Implementation Shape

- Keep the reminder in the `validation-targets` header, after the non-evidence note.
- Render it at most once.
- Gate it to `ringcentral-video` catalogs with selected, unblocked P0/P1 targets.
- Avoid the word `acceptance-draft` in the reminder so blocked-only output keeps the no-draft
  guarantee.

## Tests To Touch

- Renderer tests for P0/P1 show and P2/blocked/non-RingCentral suppression.
- CLI tests for P0 output and reminder placement before `draft:`.
- Existing knowledge-doc boundary test for the runbook command reminder.
