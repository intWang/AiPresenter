# Cycle 055 Risk Scan

## Risks

- Q&A matching runs before entrypoint lookup, so safety prompts can shadow direct control location questions.
- Reactions and Raise hand are visible meeting-state signals; they should not be sent or left active without explicit user intent.
- Diagnostics catch exact package-owned alias overlap but do not catch every fragment collision.
- `.coverage` remains a modified tracked test artifact and must not be staged.

## Controls

- The new Q&A item has no `relatedEntrypointIds`.
- Tests assert safety prompts are answer-only in English, Chinese, and Japanese.
- Tests assert `Where is Raise hand?` and `Where are Reactions?` still route to toolbar entrypoints.
- Counts are checked through localization reports, doctor diagnostics, and unit tests.

## Review Checklist

- Confirm no new executable route or locator was added.
- Confirm `qa questions` and `qa alias overlap` stay OK at `71`.
- Confirm location questions still reach existing entrypoints.
- Confirm `.coverage` is excluded from commit.
