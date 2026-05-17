# Cycle 192 Risk Scan: Scan Telemetry

Date: 2026-05-17

## Main Risks

- Telemetry could leak private window titles or control names from arbitrary desktop apps.
  Mitigation: log only process, window class, pid, counts, package id, and flow id.
- Error telemetry could leak exception text. Mitigation: log `status=error` and bounded metadata
  only, then re-raise for existing controller error handling.
- UI status could reveal the selected window title unnecessarily. Mitigation: status names the
  generated package id, control count, entrypoint count, and elapsed time.
- Counting safe controls could drift from generated package behavior. Mitigation: derive
  openable/explain-only counts from generated operation entrypoints.
- Telemetry could be mistaken for performance optimization. Mitigation: this cycle measures scan
  cost; it does not make scanning asynchronous or cached.

## Scope Guard

Do not change package YAML, RingCentralVideo evidence state, language/tone runtime behavior, or
question routing.
