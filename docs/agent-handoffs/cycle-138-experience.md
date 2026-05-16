# Cycle 138 Experience: Package-Local CLI Language Alias UX

Date: 2026-05-16

## What Changed

Package-local CLI commands now normalize known presenter language aliases before
inspecting package metadata. `entrypoints --language Spanish` and
`entrypoints --language es-MX` resolve to package key `es`, matching
`entrypoints --language es` output. `localization-report` uses the same
canonical package key behavior.

Unknown package keys remain raw lookup keys. For example, `--language de` is
still accepted as `de` rather than rejected as an unsupported runtime language.

## Why It Matters

This improves CLI UX after the README documented
`entrypoints --language es`. Users who naturally type `Spanish` or a regional
alias such as `es-MX` now see the expected Spanish package-local display
metadata instead of misleading all-zero or fallback-only reports.

The change does not expand runtime support. It keeps package inspection
convenient while preserving the boundary between package metadata lookup and
runtime voice/provider validation.

## Verification Signals

Known so far:

- Implementation red/green covered the new alias normalization tests.
- Focused green run: `3 passed in 1.41s` for the new CLI tests.
- Regression green run: `7 passed in 2.01s` for related CLI and voice tests.
- Manual probes confirmed `Spanish` and `es-MX` print `Language: es`, while
  `de` remains `Language: de`.
- Ruff passed for `src/ai_presenter/cli.py` and `tests/unit/test_cli.py`.
- `git diff --check` passed, with only existing CRLF normalization warnings.

Full verification remains pending.

## Residual Risks

- Package-local alias behavior now depends on the presenter language alias
  table.
- Unknown package keys can still produce all-zero reports when no matching
  package localization exists.
- Spanish optional entrypoint display metadata remains partial at `5/27`.
- Runtime Spanish support remains OpenAI-only; local SAPI/Piper Spanish support
  and live RingCentral Video Spanish acceptance are still unproven.

## Next-Cycle Suggestions

- Consider the safe Spanish display metadata wedge from the demand scan:
  audio menu, video menu, and Background optional display copy.
- If alias normalization later affects more README examples, consider a small
  docs/count guard that keeps package-key examples aligned with CLI output.
