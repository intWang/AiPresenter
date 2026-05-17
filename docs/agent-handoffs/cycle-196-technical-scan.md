# Cycle 196 Technical Scan: Maintenance Playbook Guard

Date: 2026-05-17

## Existing Pattern

`tests/unit/test_material_packages.py` already contains Markdown docs-contract tests for durable
RingCentral knowledge boundaries. The closest pattern is
`test_ringcentral_knowledge_docs_preserve_evidence_boundaries()`, which reads Markdown with
`Path(...).read_text(encoding="utf-8")` and asserts stable safety/protocol phrases.

## Test Strategy

Add `test_ai_presenter_maintenance_playbook_preserves_optimization_protocol()` near the existing
docs-contract tests. Keep it narrow:

- Guard stable protocol phrases in `docs/knowledge/ai-presenter-maintenance.md`.
- Guard negative wording that would blur runtime behavior, acceptance evidence, or global skill
  installation.
- Avoid line numbers, broad Markdown linting, or transient cycle wording.

## Risks

- Over-asserting the whole playbook would make useful doc edits noisy.
- The playbook should link to RingCentral-specific docs instead of copying route policy.
- This slice should not create or install a real Codex skill.
