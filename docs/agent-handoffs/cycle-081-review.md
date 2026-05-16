# Cycle 081 Review: JA Control Map Network Quality

Date: 2026-05-16

## Verdict

Approved for commit.

The reviewed changes satisfy the Cycle 081 scope: `meeting-control-map-demo` now has Japanese narration for `control-map-network`, while the control action, route, safety posture, and next localization gap remain aligned with the requested constraints.

## Findings

- Blocking: None.
- Major: None.
- Minor: None.

Review checks performed:

- JA demo localization coverage advanced from the prior expected `31/51` to `32/51`.
- `meeting-control-map-demo` advanced from `2/22` to `3/22`.
- The first remaining JA demo gap is `control-map-views`.
- `control-map-network` still opens `ringcentral.video.top.network-quality` with operation `open`.
- Narration timing remains `placement: during` and `actionOffsetMs: 350`.
- `ringcentral.video.top.network-quality` still uses `clickWindowRelative` targeting `Network quality` at `x: '68'`, `y: '21'`, with `cleanup: escape`.
- The Japanese narration describes Network quality as a meeting-health entry point for checking whether audio/video/sharing instability is related to packet loss, jitter, or latency.
- The narration does not promise repair or improvement, change settings, switch devices, submit Report issue, or read/record specific network, IP, provider, device, account, or meeting values.
- No reviewed diff changed locator/openSteps/cleanup/aliases/Q&A/runtime behavior or later `control-map-*` steps.

## Verification Notes

Main-session verification recorded in `cycle-081-summary.md`:

- Focused validation: `5 passed`.
- Full pytest: `674 passed, 1 warning`.
- Ruff: passed.
- Mypy: passed.
- Doctor: `11 ok, 1 info`.
- zh localization: `51/51`.
- ja localization: `32/51`, with `meeting-control-map-demo: 3/22`.
- ja `--require-complete`: expected exit `1`.
- `git diff --check`: exit `0`, with only CRLF working-copy warnings.

Reviewer spot-checks:

- Ran `.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja`: confirmed `32/51 demo steps`, `meeting-control-map-demo: 3/22`, and first missing step `control-map-views`.
- Ran `.venv\Scripts\ai-presenter localization-report --package ringcentral-video --language ja --require-complete`: confirmed expected exit `1` with incomplete JA demo coverage.
- Inspected the YAML route and demo step directly for action, timing, target, coordinates, cleanup, and next-step preservation.

## Commit Scope Notes

Expected commit candidates:

- `packages/ringcentral-video.yaml`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/ringcentral-video/source-index.md`
- `docs/agent-handoffs/cycle-081-*.md`, including this review note

Do not stage or commit `.coverage`; it is a test artifact and is currently present as a working-tree modification.
