# Cycle 198 Review: Language/Provider Lifecycle Matrix

Date: 2026-05-17

## Review Scope

Reviewed Cycle 198 changes across:

- `docs/knowledge/language-lifecycle.md`
- `tests/unit/test_cli.py`
- `docs/agent-handoffs/cycle-198-*.md`

## Findings And Resolution

| Severity | Finding | Resolution |
| --- | --- | --- |
| P1 | The Spanish lifecycle wording implied incompatible local profiles should fail the `runtime language support` check for `--localization-language es`. Implementation only checks whether runtime recognizes `es`; provider compatibility is checked when `--language es` selects voice output. | Reworded the lifecycle doc to separate `runtime language support` from profile/provider compatibility. |
| P2 | The docs-contract test did not explicitly lock the Spanish local provider rejection phrase or package-only non-acceptance boundary. | Added assertions for local fake/Piper/Windows SAPI rejection of `--language es`, package-only non-evidence, and provider compatibility checked via `--language es`. |
| P2 | `.coverage` is dirty in the working tree. | Keep staging explicit and verify `.coverage` is absent from the cached diff before commit. |

## Review Result

No overclaim of live RingCentral acceptance remains in the new matrix or
handoffs. Spanish stays documented as OpenAI-only for runtime speech, with local
SAPI/Piper support and live acceptance still future work.
