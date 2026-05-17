# Cycle 198 Demand Analysis: Language/Provider Lifecycle Matrix

Date: 2026-05-17

## User Value

AiPresenter has several language readiness states that are easy to conflate:
package localization, runtime language selection, provider compatibility, local
voice assets, and live RingCentral acceptance. A repo-wide language/provider
lifecycle matrix gives maintainers one compact source for deciding whether a
language is merely localized, runnable, speakable through a given provider, or
accepted for live RingCentral use.

This follows Cycle 197's tone matrix. It reduces false readiness claims,
especially around Spanish: package localization is complete and OpenAI runtime
speech is supported, but local SAPI/Piper support and live RingCentral
acceptance remain unproven.

## Recommended Slice

Update the existing durable doc:
`docs/knowledge/language-lifecycle.md`.

Add a `## Current Language State Matrix` that distinguishes:

- Runtime presenter language support: current runtime accepts `en`, `zh`, `ja`,
  and `es`.
- Package localization readiness: RingCentral Chinese, Japanese, and Spanish
  required package localization are complete; Spanish entrypoint display
  metadata remains partial.
- Speech provider compatibility: English supports local routes; Chinese
  requires OpenAI or `windows-sapi-zh`; Japanese requires OpenAI; Spanish
  requires OpenAI.
- Local limitations: SAPI checks are voice-asset dependent, Piper is local
  English-only in practice unless a future provider slice expands and tests it,
  and Spanish local SAPI/Piper is not ready.
- Live RingCentral acceptance: runtime support is not live acceptance evidence.

## Acceptance Criteria

- The durable doc includes a language/provider lifecycle matrix for `en`, `zh`,
  `ja`, `es`, plus a package-only future-language row.
- The doc explicitly separates `localization-report --require-complete`,
  `doctor --require-localization`, `demo/controller --language`, voice asset
  checks, and dated live acceptance.
- Spanish is documented as package-complete and OpenAI-runtime-supported, but
  not local SAPI/Piper-ready and not live-accepted.
- Chinese local support names the `windows-sapi-zh`/Huihui boundary.
- Japanese support names the OpenAI-only boundary.
- The doc links readiness claims to dated acceptance expectations instead of
  claiming acceptance.
- A focused test guards key phrases and the current runtime language/provider
  contract.

## Non-Goals

- No runtime behavior changes.
- No package YAML, aliases, Q&A, localization count, locator, or route changes.
- No new provider support, SAPI voices, Piper assets, or OpenAI prompt changes.
- No live RingCentral acceptance claim or evidence-level promotion.
- No expansion of package localization scope.

## Privacy / Routing Constraints

Language and provider selection must not affect RingCentral safety routing.
Q&A-first matching, `questionPolicy`, `can_operate`, answer-only guards, and
interrupt creation remain unchanged. Localized prompts must not make private
surfaces operable. Live acceptance evidence must include date, environment,
route, result, cleanup, and privacy notes before any accepted claim.

## Suggested Verification

```powershell
rg -n "Spanish|OpenAI|windows-sapi-zh|Piper|live RingCentral|package-only|require-complete" docs/knowledge/language-lifecycle.md
.\.venv\Scripts\python.exe -m pytest --override-ini addopts= --no-cov -p no:cacheprovider -q tests/unit/test_cli.py::test_language_lifecycle_matrix_matches_runtime_language_contract
git diff --check
```
