# Cycle 196 Risk Scan: Repo-Local Protocol

Date: 2026-05-17

## Risks Checked

- Turning repo-local guidance into an active Codex home skill without a separate design cycle.
- Implying the maintenance playbook changes runtime behavior.
- Treating handoffs as evergreen truth instead of cycle-local context.
- Weakening `.coverage` staging protections.
- Repeating RingCentral route policy in a broad playbook instead of linking to canonical docs.

## Mitigations

- The playbook explicitly says this cycle does not install Codex home skills, change runtime
  presenter behavior, update package YAML, or claim live RingCentral acceptance.
- The test guards negative phrases such as `handoffs are evergreen truth` and
  `install codex skills for normal aipresenter cycles`.
- The final-gate command block includes `git diff --cached -- .coverage`.

## Residual Risk

The protocol is documentation, not an executable workflow runner. Future cycles still need agents
to follow it and run the gate.
