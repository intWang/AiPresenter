# Cycle 139 Experience: Package Alias Lifecycle Docs Guard

Date: 2026-05-17

## What Changed

Lifecycle docs now document package-local known language alias normalization for
inspection commands: aliases such as `Spanish`, `es-MX`, and `zh-CN` resolve to
canonical package keys before package metadata lookup.

Unknown package-only language keys remain raw lookup keys, so future package
metadata can be inspected without requiring runtime voice support. A focused
test guard was added to keep the lifecycle doc from reverting to stale raw-key
wording.

## Why It Matters

This preserves the Cycle138 CLI UX for `entrypoints` and `localization-report`
while keeping runtime boundaries clear. It also prevents durable docs from
sliding back to the old raw-key-only explanation after the CLI behavior changed.

## Verification Signals Known So Far

- Implementation red/green was recorded: new doc guard failed before the
  lifecycle wording update, then passed after it.
- Main-session focused verification passed the 4-test CLI slice.
- Ruff passed for `tests/unit/test_cli.py`.
- Full verification remains pending.

## Residual Risks

- Package-local aliases depend on the presenter language alias table.
- Unknown raw package keys can intentionally report all-zero coverage.
- Spanish optional display metadata remains partial at `5/27`.
- Runtime Spanish remains OpenAI-only.
- Local SAPI/Piper Spanish support and live RingCentral acceptance remain
  unproven.

## Next-Cycle Suggestion

Use the safe Spanish display metadata wedge from demand/risk if counts, durable
docs, and tests move together: add `localizedTitles.es` and
`localizedPurposes.es` for `audio-menu`, `video-menu`, and `more.background`
only.
