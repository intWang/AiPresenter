# Cycle 191 Risk Scan: Entrypoint Draft Examples

Date: 2026-05-17

## Main Risks

- Output noise: adding examples to priority lists would make P1 output too long. Mitigation:
  examples render only in `--target` detail output.
- Evidence confusion: examples could look like acceptance proof. Mitigation: preserve the
  existing non-evidence note and label them as `entrypoint draft examples`.
- Group semantics loss: replacing the group `draft:` command would hide the grouped checklist
  target. Mitigation: keep the canonical group draft and add examples below it.
- Blocked leakage: blocked targets must not show draft commands. Mitigation: examples are only
  produced under the same unblocked draft gate.

## Scope Guard

Do not change package YAML, route evidence, live RingCentral behavior, or the acceptance-draft
template.
